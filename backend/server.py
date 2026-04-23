"""Lo Sapevi che? - Backend API.

Main FastAPI app. Business logic is split across:
- deps.py       → DB client, password/JWT helpers, current_user dep
- models.py     → Pydantic request schemas
- services.py   → Trophies, AI generation, prefill scheduler, pick_weighted
- i18n.py       → Category/trophy localization dictionaries
- image_library → Unsplash URL catalog + keyword-aware image picker
"""
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

import uuid
import random
import logging
from datetime import datetime, timezone, date
from typing import Dict, Any

import httpx
from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

from seed_facts import SEED_FACTS, CATEGORIES, CATEGORY_EMOJI, SUB_CATEGORIES
from seed_facts_extra import EXTRA_FACTS
from seed_facts_v3 import V3_FACTS
from i18n import label_for_category, label_for_trophy
from image_library import image_for_fact, first_image_for_category

from deps import (
    db, client,
    hash_password, verify_password, create_token,
    normalize_answer, user_to_public, current_user,
)
from models import (
    RegisterIn, LoginIn, ForgotQuestionIn, ForgotResetIn,
    SetSecurityQuestionIn, SetLanguageIn,
    UpdateInterestsIn, UpdateSubInterestsIn,
    ReactIn, PushTokenIn, GenerateIn, BulkGenerateIn,
)
from services import (
    TROPHIES, update_trophies_for_user,
    generate_fact_ai, pick_weighted,
    start_prefill_scheduler, stop_prefill_scheduler,
)


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("losapevi")

app = FastAPI(title="Lo Sapevi che?")
api = APIRouter(prefix="/api")


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
            new_url = image_for_fact(f["category"], f["title"], f.get("sub_category"))
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
# AUTH ROUTES
# ==========================================================
@api.post("/auth/register")
async def register(data: RegisterIn):
    email = data.email.lower()
    if await db.users.find_one({"email": email}):
        raise HTTPException(400, "Email già registrata")

    weights = {c: (1.0 if c in data.interests else 0.3) for c in CATEGORIES}

    user_id = str(uuid.uuid4())
    doc = {
        "id": user_id,
        "email": email,
        "name": data.name.strip(),
        "password_hash": hash_password(data.password),
        "security_question": data.security_question.strip(),
        "security_answer_hash": hash_password(normalize_answer(data.security_answer)),
        "interests": data.interests,
        "interest_weights": weights,
        "sub_interests": {},
        "sub_interest_weights": {},
        "liked_ids": [],
        "disliked_ids": [],
        "bookmarked_ids": [],
        "seen_ids": [],
        "expo_push_token": None,
        "streak_days": 0,
        "best_streak": 0,
        "last_checkin_date": None,
        "trophies": [],
        "ai_generated_count": 0,
        "language": "it",
        "created_at": datetime.now(timezone.utc),
    }
    await db.users.insert_one(doc)
    return {"token": create_token(user_id), "user": user_to_public(doc)}


@api.post("/auth/login")
async def login(data: LoginIn):
    email = data.email.lower()
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(401, "Credenziali non valide")
    return {"token": create_token(user["id"]), "user": user_to_public(user)}


@api.post("/auth/forgot/question")
async def forgot_question(data: ForgotQuestionIn):
    email = data.email.lower()
    user = await db.users.find_one({"email": email}, {"_id": 0, "security_question": 1})
    if not user or not user.get("security_question"):
        raise HTTPException(
            404,
            "Nessuna domanda di sicurezza configurata per questa email. "
            "Contatta il supporto o accedi e imposta una domanda dalle impostazioni."
        )
    return {"security_question": user["security_question"]}


@api.post("/auth/forgot/reset")
async def forgot_reset(data: ForgotResetIn):
    email = data.email.lower()
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user or not user.get("security_answer_hash"):
        raise HTTPException(404, "Impossibile ripristinare la password per questa email.")
    if not verify_password(normalize_answer(data.security_answer), user["security_answer_hash"]):
        raise HTTPException(401, "Risposta di sicurezza errata")
    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {"password_hash": hash_password(data.new_password)}},
    )
    updated = await db.users.find_one({"id": user["id"]}, {"_id": 0})
    return {"token": create_token(user["id"]), "user": user_to_public(updated)}


@api.post("/auth/security-question")
async def set_security_question(data: SetSecurityQuestionIn, user=Depends(current_user)):
    if not verify_password(data.current_password, user["password_hash"]):
        raise HTTPException(401, "Password attuale non corretta")
    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {
            "security_question": data.security_question.strip(),
            "security_answer_hash": hash_password(normalize_answer(data.security_answer)),
        }},
    )
    return {"ok": True}


@api.post("/auth/language")
async def set_user_language(data: SetLanguageIn, user=Depends(current_user)):
    await db.users.update_one({"id": user["id"]}, {"$set": {"language": data.language}})
    updated = await db.users.find_one({"id": user["id"]}, {"_id": 0})
    return {"ok": True, "user": user_to_public(updated)}


@api.get("/auth/me")
async def me(user=Depends(current_user)):
    return user_to_public(user)


@api.post("/auth/interests")
async def update_interests(data: UpdateInterestsIn, user=Depends(current_user)):
    weights = user.get("interest_weights", {})
    for cat in CATEGORIES:
        if cat in data.interests:
            weights[cat] = max(weights.get(cat, 0.3), 1.0)
        else:
            weights[cat] = min(weights.get(cat, 0.3), 0.5)
    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {"interests": data.interests, "interest_weights": weights}},
    )
    updated = await db.users.find_one({"id": user["id"]}, {"_id": 0})
    return user_to_public(updated)


@api.post("/auth/push-token")
async def set_push_token(data: PushTokenIn, user=Depends(current_user)):
    await db.users.update_one({"id": user["id"]}, {"$set": {"expo_push_token": data.token}})
    return {"ok": True}


@api.post("/auth/sub-interests")
async def update_sub_interests(data: UpdateSubInterestsIn, user=Depends(current_user)):
    clean: Dict[str, list] = {}
    for cat, subs in data.sub_interests.items():
        if cat in SUB_CATEGORIES:
            clean[cat] = [s for s in subs if s in SUB_CATEGORIES[cat]]
    await db.users.update_one({"id": user["id"]}, {"$set": {"sub_interests": clean}})
    updated = await db.users.find_one({"id": user["id"]}, {"_id": 0})
    return user_to_public(updated)


@api.post("/auth/checkin")
async def daily_checkin(user=Depends(current_user)):
    today = datetime.now(timezone.utc).date().isoformat()
    last = user.get("last_checkin_date")
    streak = user.get("streak_days", 0)
    best = user.get("best_streak", 0)

    if last == today:
        new_trophies = await update_trophies_for_user(user["id"])
    else:
        if last:
            delta = (date.fromisoformat(today) - date.fromisoformat(last)).days
            if delta == 1:
                streak += 1
            elif delta > 1:
                streak = 1
        else:
            streak = 1

        best = max(best, streak)
        await db.users.update_one(
            {"id": user["id"]},
            {"$set": {"streak_days": streak, "best_streak": best, "last_checkin_date": today}},
        )
        new_trophies = await update_trophies_for_user(user["id"])

    updated = await db.users.find_one({"id": user["id"]}, {"_id": 0})
    return {
        "streak_days": updated.get("streak_days", 0),
        "best_streak": updated.get("best_streak", 0),
        "trophies": updated.get("trophies", []),
        "new_trophies": [t for t in TROPHIES if t["id"] in new_trophies],
    }


# ==========================================================
# CATEGORIES / PREVIEW / TROPHIES
# ==========================================================
@api.get("/categories")
async def list_categories(lang: str = "it"):
    return [
        {
            "name": c,
            "label": label_for_category(c, lang),
            "icon": CATEGORY_EMOJI.get(c, "sparkles"),
            "has_subcategories": c in SUB_CATEGORIES,
            "subcategories": SUB_CATEGORIES.get(c, []),
        }
        for c in CATEGORIES
    ]


@api.get("/subcategories/{category}")
async def list_subcategories(category: str):
    if category not in CATEGORIES:
        raise HTTPException(404, "Categoria non trovata")
    return {"category": category, "subcategories": SUB_CATEGORIES.get(category, [])}


@api.get("/preview")
async def preview_per_category():
    out = []
    for cat in CATEGORIES:
        cursor = db.facts.find({"category": cat}, {"_id": 0}).limit(1)
        items = await cursor.to_list(1)
        if items:
            f = items[0]
            out.append({
                "category": cat,
                "icon": CATEGORY_EMOJI.get(cat, "sparkles"),
                "sample_title": f["title"],
                "sample_short": f["short_fact"],
                "image_url": f["image_url"],
            })
        else:
            out.append({
                "category": cat,
                "icon": CATEGORY_EMOJI.get(cat, "sparkles"),
                "sample_title": cat,
                "sample_short": "Scopri curiosità su " + cat.lower(),
                "image_url": first_image_for_category(cat),
            })
    return out


@api.get("/trophies")
async def list_trophies(lang: str = "it", user=Depends(current_user)):
    earned = set(user.get("trophies", []))
    out = []
    for t in TROPHIES:
        loc = label_for_trophy(t["id"], lang)
        out.append({
            **t,
            "name": loc["name"] or t.get("name"),
            "desc": loc["description"] or t.get("desc"),
            "earned": t["id"] in earned,
        })
    return out


# ==========================================================
# FEED / FACTS / REACTIONS
# ==========================================================
@api.get("/feed")
async def feed(limit: int = 20, user=Depends(current_user)):
    seen = set(user.get("seen_ids", []))
    disliked = set(user.get("disliked_ids", []))
    exclude = seen | disliked

    interests = user.get("interests", []) or []
    lang = user.get("language", "it")
    base_query: Dict[str, Any] = {"id": {"$nin": list(exclude)}, "language": lang}
    if interests:
        base_query["category"] = {"$in": interests}

    candidates = await db.facts.find(base_query, {"_id": 0}).limit(400).to_list(400)

    if not candidates:
        fallback: Dict[str, Any] = {"id": {"$nin": list(disliked)}, "language": lang}
        if interests:
            fallback["category"] = {"$in": interests}
        candidates = await db.facts.find(fallback, {"_id": 0}).limit(400).to_list(400)

    if not candidates and lang != "it":
        fallback = {"id": {"$nin": list(disliked)}, "language": "it"}
        if interests:
            fallback["category"] = {"$in": interests}
        candidates = await db.facts.find(fallback, {"_id": 0}).limit(400).to_list(400)

    # Sub-interest filter
    sub_interests = user.get("sub_interests", {}) or {}
    if sub_interests:
        def keep(f):
            prefs = sub_interests.get(f["category"])
            if not prefs:
                return True
            sub = f.get("sub_category")
            return True if not sub else sub in prefs
        candidates = [f for f in candidates if keep(f)]

    return {"facts": pick_weighted(user, candidates, limit)}


@api.post("/facts/{fact_id}/seen")
async def mark_seen(fact_id: str, user=Depends(current_user)):
    await db.users.update_one({"id": user["id"]}, {"$addToSet": {"seen_ids": fact_id}})
    await update_trophies_for_user(user["id"])
    return {"ok": True}


@api.post("/facts/{fact_id}/react")
async def react(fact_id: str, data: ReactIn, user=Depends(current_user)):
    fact = await db.facts.find_one({"id": fact_id}, {"_id": 0})
    if not fact:
        raise HTTPException(404, "Fact non trovato")
    cat = fact["category"]
    sub_key = f"{cat}::{fact.get('sub_category') or ''}"
    weights = user.get("interest_weights", {}) or {}
    sub_weights = user.get("sub_interest_weights", {}) or {}

    if data.action == "like":
        weights[cat] = min(3.0, weights.get(cat, 0.5) + 0.15)
        sub_weights[sub_key] = min(2.0, sub_weights.get(sub_key, 0.0) + 0.25)
        await db.users.update_one(
            {"id": user["id"]},
            {"$addToSet": {"liked_ids": fact_id, "seen_ids": fact_id},
             "$pull": {"disliked_ids": fact_id},
             "$set": {"interest_weights": weights, "sub_interest_weights": sub_weights}},
        )
    elif data.action == "dislike":
        weights[cat] = max(0.05, weights.get(cat, 0.5) - 0.2)
        sub_weights[sub_key] = max(-1.0, sub_weights.get(sub_key, 0.0) - 0.35)
        await db.users.update_one(
            {"id": user["id"]},
            {"$addToSet": {"disliked_ids": fact_id, "seen_ids": fact_id},
             "$pull": {"liked_ids": fact_id, "bookmarked_ids": fact_id},
             "$set": {"interest_weights": weights, "sub_interest_weights": sub_weights}},
        )
    else:
        raise HTTPException(400, "Azione non valida")

    new_trophies = await update_trophies_for_user(user["id"])
    return {
        "ok": True,
        "new_weight": weights[cat],
        "new_sub_weight": sub_weights[sub_key],
        "new_trophies": [t for t in TROPHIES if t["id"] in new_trophies],
    }


@api.post("/facts/{fact_id}/bookmark")
async def bookmark(fact_id: str, user=Depends(current_user)):
    bookmarked = set(user.get("bookmarked_ids", []))
    if fact_id in bookmarked:
        await db.users.update_one({"id": user["id"]}, {"$pull": {"bookmarked_ids": fact_id}})
        return {"ok": True, "bookmarked": False, "new_trophies": []}
    await db.users.update_one({"id": user["id"]}, {"$addToSet": {"bookmarked_ids": fact_id}})
    new_trophies = await update_trophies_for_user(user["id"])
    return {"ok": True, "bookmarked": True,
            "new_trophies": [t for t in TROPHIES if t["id"] in new_trophies]}


@api.get("/facts/bookmarks")
async def get_bookmarks(user=Depends(current_user)):
    ids = user.get("bookmarked_ids", [])
    if not ids:
        return {"facts": []}
    return {"facts": await db.facts.find({"id": {"$in": ids}}, {"_id": 0}).to_list(500)}


@api.get("/facts/liked")
async def get_liked(user=Depends(current_user)):
    ids = user.get("liked_ids", [])
    if not ids:
        return {"facts": []}
    return {"facts": await db.facts.find({"id": {"$in": ids}}, {"_id": 0}).to_list(500)}


@api.get("/facts/{fact_id}")
async def get_fact(fact_id: str, user=Depends(current_user)):
    fact = await db.facts.find_one({"id": fact_id}, {"_id": 0})
    if not fact:
        raise HTTPException(404, "Fact non trovato")
    fact["is_liked"] = fact_id in user.get("liked_ids", [])
    fact["is_bookmarked"] = fact_id in user.get("bookmarked_ids", [])
    return fact


# ==========================================================
# AI GENERATION
# ==========================================================
@api.post("/facts/generate")
async def generate_new_fact(data: GenerateIn, user=Depends(current_user)):
    category = data.category
    if not category:
        weights = user.get("interest_weights", {})
        category = max(weights.keys(), key=lambda k: weights[k]) if weights else random.choice(CATEGORIES)
    if category not in CATEGORIES:
        raise HTTPException(400, "Categoria non valida")

    lang = user.get("language", "it")
    ai = await generate_fact_ai(category, lang)
    if not ai:
        raise HTTPException(503, "Generazione AI non disponibile. Riprova.")

    doc = {
        "id": str(uuid.uuid4()),
        "title": ai["title"],
        "short_fact": ai["short_fact"],
        "deep_dive": ai["deep_dive"],
        "sources": ai.get("sources", []),
        "category": category,
        "sub_category": None,
        "image_url": image_for_fact(category, ai["title"], None),
        "source": "ai",
        "language": lang,
        "created_at": datetime.now(timezone.utc),
    }
    await db.facts.insert_one(doc)
    doc.pop("_id", None)
    await db.users.update_one({"id": user["id"]}, {"$inc": {"ai_generated_count": 1}})
    new_trophies = await update_trophies_for_user(user["id"])
    return {**doc, "new_trophies": [t for t in TROPHIES if t["id"] in new_trophies]}


@api.post("/facts/bulk-generate")
async def bulk_generate_facts(data: BulkGenerateIn, user=Depends(current_user)):
    cats = [data.category] * data.count if data.category else random.sample(CATEGORIES, min(data.count, len(CATEGORIES)))
    lang = user.get("language", "it")
    created = []
    for cat in cats:
        if cat not in CATEGORIES:
            continue
        ai = await generate_fact_ai(cat, lang)
        if not ai:
            continue
        doc = {
            "id": str(uuid.uuid4()),
            "title": ai["title"],
            "short_fact": ai["short_fact"],
            "deep_dive": ai["deep_dive"],
            "sources": ai.get("sources", []),
            "category": cat,
            "sub_category": None,
            "image_url": image_for_fact(cat, ai["title"], None),
            "source": "ai",
            "language": lang,
            "created_at": datetime.now(timezone.utc),
        }
        await db.facts.insert_one(doc)
        doc.pop("_id", None)
        created.append(doc)

    if created:
        await db.users.update_one({"id": user["id"]}, {"$inc": {"ai_generated_count": len(created)}})
        await update_trophies_for_user(user["id"])

    return {"created": len(created), "facts": created}


# ==========================================================
# PUSH
# ==========================================================
EXPO_PUSH_API = "https://exp.host/--/api/v2/push/send"


@api.post("/notifications/send-test")
async def send_test_push(user=Depends(current_user)):
    token = user.get("expo_push_token")
    if not token:
        raise HTTPException(400, "Nessun token push registrato")
    weights = user.get("interest_weights", {})
    cat = max(weights.keys(), key=lambda k: weights.get(k, 0)) if weights else random.choice(CATEGORIES)
    fact = await db.facts.find_one({"category": cat}, {"_id": 0}) or await db.facts.find_one({}, {"_id": 0})
    if not fact:
        raise HTTPException(404, "Nessun fact disponibile")
    msg = {
        "to": token, "sound": "default",
        "title": "Lo Sapevi che?", "body": fact["title"],
        "data": {"fact_id": fact["id"]},
    }
    async with httpx.AsyncClient(timeout=10.0) as http:
        try:
            r = await http.post(EXPO_PUSH_API, json=msg, headers={"Content-Type": "application/json"})
            return {"ok": True, "expo": r.json()}
        except Exception as e:
            logger.error(f"Push error: {e}")
            raise HTTPException(500, "Errore invio push")


# ==========================================================
# HEALTH
# ==========================================================
@api.get("/")
async def root():
    return {"app": "Lo Sapevi che?", "status": "ok"}


@api.get("/health")
async def health():
    return {
        "ok": True,
        "facts": await db.facts.count_documents({}),
        "users": await db.users.count_documents({}),
    }


app.include_router(api)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
