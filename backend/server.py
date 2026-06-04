"""Lo Sapevi che? - Backend API.

Main FastAPI app — wiring only. Business logic is split across:
- deps.py       → DB client, password/JWT helpers, current_user dep
- models.py     → Pydantic request schemas
- services.py   → Trophies, AI generation, prefill scheduler, pick_weighted
- i18n.py       → Category/trophy localization dictionaries
- image_library → Unsplash URL catalog + keyword-aware image picker
- routers/auth.py     → auth + user profile endpoints
- routers/catalog.py  → categories / subcategories / preview / trophies list
- routers/facts.py    → feed / reactions / bookmarks / AI generation
- routers/misc.py     → push notifications test / health check
"""
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

import uuid
import logging
from datetime import datetime, timezone

from fastapi import FastAPI, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from seed_facts import SEED_FACTS
from seed_facts_extra import EXTRA_FACTS
from seed_facts_v3 import V3_FACTS
from image_library import image_for_fact, image_for_fact_async

from deps import db, client
from scheduler import start_prefill_scheduler, stop_prefill_scheduler
from routers import auth as auth_router
from routers import catalog as catalog_router
from routers import facts as facts_router
from routers import misc as misc_router


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("losapevi")

app = FastAPI(title="Lo Sapevi che?")
api = APIRouter(prefix="/api")

PRIVACY_HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Privacy Policy - Lo Sapevi che?</title>
<style>body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;max-width:760px;margin:0 auto;padding:32px 20px;color:#1a1a1a;line-height:1.6}h1{font-size:26px}h2{font-size:17px;margin-top:28px;color:#9a7d00}a{color:#9a7d00}small{color:#777}</style>
</head><body>
<h1>Privacy Policy - Lo Sapevi che?</h1>
<small>Last updated: June 2026</small>
<p>This Privacy Policy explains how the app "Lo Sapevi che?" (the "App"), developed by Black Star Digital Studio, handles your data. Made in Italy.</p>
<h2>1. Data we collect</h2>
<p>- <b>Account data</b>: email, name and password (stored only as a bcrypt hash).<br>
- <b>Preferences and activity</b>: your selected interests, liked/saved curiosities, daily streaks and trophies.</p>
<h2>2. How we use your data</h2>
<p>To create and manage your account, personalize your feed of curiosities, track your streaks and trophies, and send you the daily notifications you enable.</p>
<h2>3. AI processing</h2>
<p>New curiosities are generated in the background by Google Gemini from generic topic categories. Your personal data is never sent to generate content or to train models.</p>
<h2>4. Notifications</h2>
<p>Daily notifications are scheduled locally on your device. You can disable them at any time from the app settings.</p>
<h2>5. Third-party services (data processors)</h2>
<p>Google (Gemini AI), Render (hosting) and MongoDB Atlas (database). The App contains <b>no advertising</b> and we do not sell your personal data.</p>
<h2>6. Storage and security</h2>
<p>Data is stored on MongoDB Atlas. Passwords are hashed with bcrypt and traffic is encrypted in transit (HTTPS).</p>
<h2>7. Data retention and deletion</h2>
<p>To request deletion of your account and data, contact us at the address below and we will comply within the time limits set by applicable law.</p>
<h2>8. Children</h2>
<p>The App is intended for users aged 13 and over.</p>
<h2>9. Contact</h2>
<p>For any privacy request: <a href="mailto:blackstardigitalstudio@gmail.com">blackstardigitalstudio@gmail.com</a></p>
</body></html>"""


@app.get("/privacy", response_class=HTMLResponse, include_in_schema=False)
async def privacy_policy():
    return PRIVACY_HTML


DELETE_ACCOUNT_HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Account &amp; Data Deletion - Lo Sapevi che?</title>
<style>body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;max-width:760px;margin:0 auto;padding:32px 20px;color:#1a1a1a;line-height:1.6}h1{font-size:26px}h2{font-size:17px;margin-top:28px;color:#9a7d00}a{color:#9a7d00}small{color:#777}code{background:#f4f4f4;padding:2px 6px;border-radius:4px}</style>
</head><body>
<h1>Account &amp; Data Deletion - Lo Sapevi che?</h1>
<small>Last updated: June 2026</small>
<p>This page explains how to request deletion of your account and associated data for the app <b>"Lo Sapevi che?"</b>, developed by <b>Black Star Digital Studio</b>. Made in Italy.</p>
<h2>How to request deletion</h2>
<p>Send an email to <a href="mailto:blackstardigitalstudio@gmail.com?subject=Delete%20my%20account%20-%20Lo%20Sapevi%20che">blackstardigitalstudio@gmail.com</a> from the email address linked to your account, with the subject <code>Delete my account</code>. We will permanently delete your account and all associated data within 30 days and confirm by email.</p>
<h2>What data is deleted</h2>
<p>All data tied to your account is permanently deleted: your <b>email</b>, <b>name</b> and <b>password</b> (stored only as a bcrypt hash), and your <b>preferences and activity</b> (selected interests, liked/saved curiosities, daily streaks and trophies).</p>
<h2>Data retention</h2>
<p>No personal data is retained after deletion, except where retention is required by applicable law. Using the App without an account stores no personal data on our servers.</p>
<h2>Contact</h2>
<p><a href="mailto:blackstardigitalstudio@gmail.com">blackstardigitalstudio@gmail.com</a></p>
</body></html>"""


@app.get("/delete-account", response_class=HTMLResponse, include_in_schema=False)
async def delete_account_page():
    return DELETE_ACCOUNT_HTML


# ==========================================================
# STARTUP / SHUTDOWN
# ==========================================================
@app.on_event("startup")
async def on_startup():
    await db.users.create_index("email", unique=True)
    await db.facts.create_index("id", unique=True)
    await db.facts.create_index("category")

    count = await db.facts.count_documents({})
    if count == 0:
        logger.info("Seeding facts database...")
        docs = []
        for f in SEED_FACTS + EXTRA_FACTS + V3_FACTS:
            docs.append({
                "id": str(uuid.uuid4()),
                "title": f["title"],
                "short_fact": f["short_fact"],
                "deep_dive": f["deep_dive"],
                "category": f["category"],
                "sub_category": f.get("sub_category"),
                "image_url": f["image_url"],
                "source": f.get("source", "seed"),
                "sources": f.get("sources", []),
                "language": f.get("language", "it"),
                "created_at": datetime.now(timezone.utc),
            })
        if docs:
            await db.facts.insert_many(docs)
            logger.info(f"Inserted {len(docs)} seed facts.")
    else:
        try:
            titles_in_db = set(
                f["title"] for f in await db.facts.find({}, {"_id": 0, "title": 1}).to_list(10000)
            )
            new_docs = []
            for f in SEED_FACTS + EXTRA_FACTS + V3_FACTS:
                if f["title"] not in titles_in_db:
                    new_docs.append({
                        "id": str(uuid.uuid4()),
                        "title": f["title"],
                        "short_fact": f["short_fact"],
                        "deep_dive": f["deep_dive"],
                        "category": f["category"],
                        "sub_category": f.get("sub_category"),
                        "image_url": f["image_url"],
                        "source": f.get("source", "seed"),
                        "sources": f.get("sources", []),
                        "language": f.get("language", "it"),
                        "created_at": datetime.now(timezone.utc),
                    })
            if new_docs:
                await db.facts.insert_many(new_docs)
                logger.info(f"Added {len(new_docs)} new seed facts (incremental).")
        except Exception as e:
            logger.warning(f"Incremental seed skipped: {e}")

    # Backfill legacy facts with language="it"
    try:
        legacy = await db.facts.update_many(
            {"language": {"$exists": False}}, {"$set": {"language": "it"}}
        )
        if legacy.modified_count:
            logger.info(f"Language migration: {legacy.modified_count} facts tagged as 'it'.")
    except Exception as e:
        logger.warning(f"Language migration skipped: {e}")

    try:
        await db.facts.create_index("language")
    except Exception:
        pass

    # Re-assign per-fact varied images
    try:
        cursor = db.facts.find({}, {"_id": 0, "id": 1, "title": 1, "category": 1, "sub_category": 1})
        facts = await cursor.to_list(100000)
        updates = 0
        for f in facts:
            new_url = await image_for_fact_async(db, f["category"], f["title"], f.get("sub_category"))
            await db.facts.update_one({"id": f["id"]}, {"$set": {"image_url": new_url}})
            updates += 1
        if updates:
            logger.info(f"Image migration: updated {updates} facts with varied images.")
    except Exception as e:
        logger.warning(f"Image migration skipped: {e}")

    try:
        start_prefill_scheduler()
    except Exception as e:
        logger.warning(f"Scheduler start failed (non-fatal): {e}")


@app.on_event("shutdown")
async def on_shutdown():
    stop_prefill_scheduler()
    client.close()


# ==========================================================
# ROUTING — all sub-routers mount under /api
# ==========================================================
api.include_router(auth_router.router)
api.include_router(catalog_router.router)
api.include_router(facts_router.router)
api.include_router(misc_router.router)

app.include_router(api)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
