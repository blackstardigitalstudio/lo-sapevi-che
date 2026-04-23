"""Lo Sapevi che? - Backend.

Features:
- JWT auth (register/login/me)
- Users store interests + weights that evolve with like/dislike
- Facts feed personalized via niche weighting
- Bookmarks
- AI generation of new facts via Emergent LLM Key (Claude Sonnet 4.5)
- Push notification token registration
- Gamification: daily streak, trophies
- Sources/citations on facts
- Preview cards per category (for onboarding)
"""
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

import os
import uuid
import json
import random
import logging
import asyncio
from datetime import datetime, timezone, timedelta, date
from typing import List, Optional, Dict, Any

import bcrypt
import jwt
import httpx
from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from motor.motor_asyncio import AsyncIOMotorClient

from seed_facts import SEED_FACTS, CATEGORIES, CATEGORY_EMOJI, CATEGORY_IMAGE_GROUP, IMAGE_URLS, SUB_CATEGORIES
from seed_facts_extra import EXTRA_FACTS
from seed_facts_v3 import V3_FACTS
from i18n import label_for_category, label_for_trophy, LANG_PROMPT_NAME, SUPPORTED_LANGS
from image_library import image_for_fact, first_image_for_category

# ==========================================================
# CONFIG
# ==========================================================
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("losapevi")

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]
JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = 60 * 24 * 30  # 30 days
EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

app = FastAPI(title="Lo Sapevi che?")
api = APIRouter(prefix="/api")


# ==========================================================
# TROPHIES DEFINITION
# ==========================================================
TROPHIES = [
    {"id": "first_step", "name": "Primo passo", "desc": "Hai letto la tua prima curiosità", "icon": "footsteps"},
    {"id": "curious", "name": "Curioso", "desc": "10 curiosità lette", "icon": "search"},
    {"id": "scholar", "name": "Studioso", "desc": "50 curiosità lette", "icon": "school"},
    {"id": "encyclopedia", "name": "Enciclopedia vivente", "desc": "200 curiosità lette", "icon": "library"},
    {"id": "collector", "name": "Collezionista", "desc": "10 curiosità salvate", "icon": "bookmarks"},
    {"id": "flame_3", "name": "Fiamma", "desc": "3 giorni di streak", "icon": "flame"},
    {"id": "flame_7", "name": "Fuoco eterno", "desc": "7 giorni di streak", "icon": "bonfire"},
    {"id": "flame_30", "name": "Leggenda", "desc": "30 giorni di streak", "icon": "trophy"},
    {"id": "explorer", "name": "Esploratore", "desc": "Like in 10+ categorie diverse", "icon": "compass"},
    {"id": "ai_pioneer", "name": "AI Pioneer", "desc": "5 curiosità generate con AI", "icon": "sparkles"},
]


def compute_trophies(user: Dict[str, Any]) -> List[str]:
    """Return list of trophy IDs the user has earned."""
    earned = []
    stats_seen = len(user.get("seen_ids", []))
    stats_bookmarked = len(user.get("bookmarked_ids", []))
    streak = user.get("streak_days", 0)
    ai_generated = user.get("ai_generated_count", 0)

    # Count distinct categories where user liked something
    liked_ids = user.get("liked_ids", [])
    # We can't compute categories without DB lookup here; pass separately in checkin logic

    if stats_seen >= 1:
        earned.append("first_step")
    if stats_seen >= 10:
        earned.append("curious")
    if stats_seen >= 50:
        earned.append("scholar")
    if stats_seen >= 200:
        earned.append("encyclopedia")
    if stats_bookmarked >= 10:
        earned.append("collector")
    if streak >= 3:
        earned.append("flame_3")
    if streak >= 7:
        earned.append("flame_7")
    if streak >= 30:
        earned.append("flame_30")
    if ai_generated >= 5:
        earned.append("ai_pioneer")

    liked_categories = user.get("liked_categories", [])
    if len(set(liked_categories)) >= 10:
        earned.append("explorer")

    return earned


# ==========================================================
# MODELS
# ==========================================================
class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    name: str = Field(min_length=1)
    interests: List[str] = Field(default_factory=list)
    security_question: str = Field(min_length=3, max_length=200)
    security_answer: str = Field(min_length=1, max_length=200)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class ForgotQuestionIn(BaseModel):
    email: EmailStr


class ForgotResetIn(BaseModel):
    email: EmailStr
    security_answer: str = Field(min_length=1, max_length=200)
    new_password: str = Field(min_length=6)


class SetSecurityQuestionIn(BaseModel):
    security_question: str = Field(min_length=3, max_length=200)
    security_answer: str = Field(min_length=1, max_length=200)
    current_password: str = Field(min_length=1)


class SetLanguageIn(BaseModel):
    language: str = Field(pattern="^(it|en|es)$")


class UpdateInterestsIn(BaseModel):
    interests: List[str]


class UpdateSubInterestsIn(BaseModel):
    sub_interests: Dict[str, List[str]]


class ReactIn(BaseModel):
    action: str  # "like" | "dislike"


class PushTokenIn(BaseModel):
    token: str


class GenerateIn(BaseModel):
    category: Optional[str] = None


class BulkGenerateIn(BaseModel):
    count: int = Field(default=5, ge=1, le=10)
    category: Optional[str] = None


# ==========================================================
# HELPERS
# ==========================================================
def hash_password(p: str) -> str:
    return bcrypt.hashpw(p.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_MINUTES),
        "type": "access",
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def user_to_public(u: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": u["id"],
        "email": u["email"],
        "name": u["name"],
        "interests": u.get("interests", []),
        "interest_weights": u.get("interest_weights", {}),
        "sub_interests": u.get("sub_interests", {}),
        "stats": {
            "liked": len(u.get("liked_ids", [])),
            "disliked": len(u.get("disliked_ids", [])),
            "bookmarked": len(u.get("bookmarked_ids", [])),
            "seen": len(u.get("seen_ids", [])),
        },
        "streak_days": u.get("streak_days", 0),
        "best_streak": u.get("best_streak", 0),
        "trophies": u.get("trophies", []),
        "ai_generated_count": u.get("ai_generated_count", 0),
        "created_at": u.get("created_at"),
        "has_security_question": bool(u.get("security_question")),
        "language": u.get("language", "it"),
    }


def _normalize_answer(a: str) -> str:
    """Normalize security answer (lowercase, strip, collapse spaces)."""
    return " ".join((a or "").lower().strip().split())


async def current_user(request: Request) -> Dict[str, Any]:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(401, "Not authenticated")
    token = auth[7:]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token scaduto")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Token non valido")
    user = await db.users.find_one({"id": payload["sub"]}, {"_id": 0})
    if not user:
        raise HTTPException(401, "Utente non trovato")
    return user


async def update_trophies_for_user(user_id: str) -> List[str]:
    """Recompute trophies and return newly earned IDs."""
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        return []
    # Compute liked_categories for explorer trophy
    liked_ids = user.get("liked_ids", [])
    categories = []
    if liked_ids:
        cursor = db.facts.find({"id": {"$in": liked_ids}}, {"_id": 0, "category": 1})
        liked_facts = await cursor.to_list(1000)
        categories = [f["category"] for f in liked_facts]
    user["liked_categories"] = categories

    existing = set(user.get("trophies", []))
    earned = set(compute_trophies(user))
    new = earned - existing
    if new:
        await db.users.update_one(
            {"id": user_id},
            {"$set": {"trophies": list(earned)}},
        )
    return list(new)


# ==========================================================
# STARTUP: seed facts + indexes
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
        all_seed = SEED_FACTS + EXTRA_FACTS + V3_FACTS
        for f in all_seed:
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
                "created_at": datetime.now(timezone.utc),
            })
        if docs:
            await db.facts.insert_many(docs)
            logger.info(f"Inserted {len(docs)} seed facts.")
    else:
        # Incremental seed
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
                        "created_at": datetime.now(timezone.utc),
                    })
            if new_docs:
                await db.facts.insert_many(new_docs)
                logger.info(f"Added {len(new_docs)} new seed facts (incremental).")
        except Exception as e:
            logger.warning(f"Incremental seed skipped: {e}")

    # Migration: re-assign per-fact varied images using image_library (with sub_category awareness)
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

    # Start background pre-generation scheduler
    try:
        start_prefill_scheduler()
    except Exception as e:
        logger.warning(f"Scheduler start failed (non-fatal): {e}")


@app.on_event("shutdown")
async def on_shutdown():
    try:
        if _scheduler is not None and _scheduler.running:
            _scheduler.shutdown(wait=False)
    except Exception:
        pass
    client.close()


# ==========================================================
# BACKGROUND AI PRE-GENERATION
# ==========================================================
# Settings:
#   - Runs every PREFILL_INTERVAL_HOURS (default 12h)
#   - Adds PREFILL_BATCH_SIZE new AI facts per run (default 10)
#   - Stops once DB has PREFILL_MAX_FACTS total facts (default 1000)
#   - Picks categories least represented in DB so coverage stays balanced
PREFILL_INTERVAL_HOURS = int(os.environ.get("PREFILL_INTERVAL_HOURS", "12"))
PREFILL_BATCH_SIZE = int(os.environ.get("PREFILL_BATCH_SIZE", "10"))
PREFILL_MAX_FACTS = int(os.environ.get("PREFILL_MAX_FACTS", "1000"))

_scheduler = None


async def _prefill_run():
    """One pre-generation run: add up to PREFILL_BATCH_SIZE AI facts focused on
    under-represented categories."""
    try:
        total = await db.facts.count_documents({})
        if total >= PREFILL_MAX_FACTS:
            logger.info(f"[prefill] Skipped: DB has {total} facts (cap={PREFILL_MAX_FACTS}).")
            return

        # Count facts per category to pick underrepresented ones
        pipeline = [{"$group": {"_id": "$category", "n": {"$sum": 1}}}]
        counts = {c["_id"]: c["n"] async for c in db.facts.aggregate(pipeline)}
        # Ensure every category appears (0 for missing ones)
        ranked = sorted(
            CATEGORIES,
            key=lambda c: (counts.get(c, 0), random.random()),
        )
        to_fill = ranked[: PREFILL_BATCH_SIZE]

        added = 0
        for cat in to_fill:
            if await db.facts.count_documents({}) >= PREFILL_MAX_FACTS:
                break
            ai = await generate_fact_ai(cat)
            if not ai:
                continue
            # Dedup by title
            if await db.facts.find_one({"title": ai["title"]}):
                continue
            img_url = image_for_fact(cat, ai["title"], None)
            doc = {
                "id": str(uuid.uuid4()),
                "title": ai["title"],
                "short_fact": ai["short_fact"],
                "deep_dive": ai["deep_dive"],
                "sources": ai.get("sources", []),
                "category": cat,
                "sub_category": None,
                "image_url": img_url,
                "source": "ai_prefill",
                "created_at": datetime.now(timezone.utc),
            }
            await db.facts.insert_one(doc)
            added += 1
            # tiny delay to avoid hammering the LLM
            await asyncio.sleep(0.3)

        new_total = await db.facts.count_documents({})
        logger.info(
            f"[prefill] Added {added} facts across {len(to_fill)} categories. "
            f"DB total now {new_total}/{PREFILL_MAX_FACTS}."
        )
    except Exception as e:
        logger.error(f"[prefill] run failed: {e}")


def start_prefill_scheduler():
    """Start an AsyncIOScheduler that runs _prefill_run every PREFILL_INTERVAL_HOURS."""
    global _scheduler
    if _scheduler is not None:
        return
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
    except Exception as e:
        logger.warning(f"APScheduler not available: {e}")
        return
    sch = AsyncIOScheduler(timezone="UTC")
    sch.add_job(
        _prefill_run,
        trigger="interval",
        hours=PREFILL_INTERVAL_HOURS,
        next_run_time=datetime.now(timezone.utc) + timedelta(minutes=2),
        id="ai_prefill",
        coalesce=True,
        max_instances=1,
        misfire_grace_time=3600,
    )
    sch.start()
    _scheduler = sch
    logger.info(
        f"[prefill] scheduler started: every {PREFILL_INTERVAL_HOURS}h · "
        f"batch={PREFILL_BATCH_SIZE} · cap={PREFILL_MAX_FACTS}"
    )


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
        "security_answer_hash": hash_password(_normalize_answer(data.security_answer)),
        "interests": data.interests,
        "interest_weights": weights,
        "sub_interests": {},
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
    token = create_token(user_id)
    return {"token": token, "user": user_to_public(doc)}


@api.post("/auth/login")
async def login(data: LoginIn):
    email = data.email.lower()
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(401, "Credenziali non valide")
    token = create_token(user["id"])
    return {"token": token, "user": user_to_public(user)}


@api.post("/auth/forgot/question")
async def forgot_question(data: ForgotQuestionIn):
    """Return the user's security question. Generic error if no question set,
    to avoid user enumeration."""
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
    """Verify security answer and reset password."""
    email = data.email.lower()
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user or not user.get("security_answer_hash"):
        raise HTTPException(404, "Impossibile ripristinare la password per questa email.")
    if not verify_password(_normalize_answer(data.security_answer), user["security_answer_hash"]):
        raise HTTPException(401, "Risposta di sicurezza errata")
    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {"password_hash": hash_password(data.new_password)}},
    )
    # Issue fresh token so user can log in immediately
    token = create_token(user["id"])
    updated = await db.users.find_one({"id": user["id"]}, {"_id": 0})
    return {"token": token, "user": user_to_public(updated)}


@api.post("/auth/security-question")
async def set_security_question(data: SetSecurityQuestionIn, user=Depends(current_user)):
    """Authenticated user sets or updates their security question.
    Requires current password to prevent session hijacking."""
    if not verify_password(data.current_password, user["password_hash"]):
        raise HTTPException(401, "Password attuale non corretta")
    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {
            "security_question": data.security_question.strip(),
            "security_answer_hash": hash_password(_normalize_answer(data.security_answer)),
        }},
    )
    return {"ok": True}


@api.post("/auth/language")
async def set_user_language(data: SetLanguageIn, user=Depends(current_user)):
    """Update the user's preferred language (used for AI fact generation & i18n labels)."""
    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {"language": data.language}},
    )
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


@api.post("/auth/checkin")
async def daily_checkin(user=Depends(current_user)):
    """Call on app open. Updates streak and returns trophies newly earned."""
    today = datetime.now(timezone.utc).date().isoformat()
    last = user.get("last_checkin_date")
    streak = user.get("streak_days", 0)
    best = user.get("best_streak", 0)

    if last == today:
        # Already checked in today, nothing to update
        new_trophies = await update_trophies_for_user(user["id"])
    else:
        if last:
            last_date = date.fromisoformat(last)
            today_date = date.fromisoformat(today)
            delta = (today_date - last_date).days
            if delta == 1:
                streak += 1
            elif delta > 1:
                streak = 1
            # if delta == 0 impossible (handled above)
        else:
            streak = 1

        best = max(best, streak)
        await db.users.update_one(
            {"id": user["id"]},
            {"$set": {"streak_days": streak, "best_streak": best, "last_checkin_date": today}},
        )
        new_trophies = await update_trophies_for_user(user["id"])

    updated = await db.users.find_one({"id": user["id"]}, {"_id": 0})
    new_trophy_details = [t for t in TROPHIES if t["id"] in new_trophies]
    return {
        "streak_days": updated.get("streak_days", 0),
        "best_streak": updated.get("best_streak", 0),
        "trophies": updated.get("trophies", []),
        "new_trophies": new_trophy_details,
    }


# ==========================================================
# CATEGORIES & PREVIEW
# ==========================================================
@api.get("/categories")
async def list_categories(lang: str = "it"):
    return [
        {
            "name": c,  # canonical (used as DB filter)
            "label": label_for_category(c, lang),  # localized display
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


@api.post("/auth/sub-interests")
async def update_sub_interests(data: UpdateSubInterestsIn, user=Depends(current_user)):
    # Sanitize: keep only valid categories and their valid sub-cats
    clean: Dict[str, List[str]] = {}
    for cat, subs in data.sub_interests.items():
        if cat in SUB_CATEGORIES:
            valid = [s for s in subs if s in SUB_CATEGORIES[cat]]
            clean[cat] = valid
    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {"sub_interests": clean}},
    )
    updated = await db.users.find_one({"id": user["id"]}, {"_id": 0})
    return user_to_public(updated)


@api.get("/preview")
async def preview_per_category():
    """One sample fact per category, for richer onboarding."""
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
# FEED
# ==========================================================
def pick_weighted(user: Dict[str, Any], facts: List[Dict[str, Any]], n: int) -> List[Dict[str, Any]]:
    if not facts:
        return []
    weights = user.get("interest_weights", {})
    scored = []
    for f in facts:
        w = max(weights.get(f["category"], 0.3), 0.05)
        scored.append((w + random.random() * 0.2, f))
    scored.sort(key=lambda x: -x[0])
    return [s[1] for s in scored[:n]]


@api.get("/feed")
async def feed(limit: int = 20, user=Depends(current_user)):
    seen = set(user.get("seen_ids", []))
    disliked = set(user.get("disliked_ids", []))
    exclude = seen | disliked

    interests = user.get("interests", []) or []
    base_query: Dict[str, Any] = {"id": {"$nin": list(exclude)}}
    # STRICT filter: if user selected categories, return ONLY those
    if interests:
        base_query["category"] = {"$in": interests}

    cursor = db.facts.find(base_query, {"_id": 0}).limit(400)
    candidates = await cursor.to_list(400)

    if not candidates:
        # Fallback: allow seen (but not disliked) within same strict filter
        fallback_query: Dict[str, Any] = {"id": {"$nin": list(disliked)}}
        if interests:
            fallback_query["category"] = {"$in": interests}
        cursor = db.facts.find(fallback_query, {"_id": 0}).limit(400)
        candidates = await cursor.to_list(400)

    # Apply sub_interests filter
    sub_interests = user.get("sub_interests", {}) or {}
    if sub_interests:
        def keep(f):
            cat = f["category"]
            prefs = sub_interests.get(cat)
            if not prefs:
                return True
            sub = f.get("sub_category")
            if not sub:
                return True
            return sub in prefs
        candidates = [f for f in candidates if keep(f)]

    picked = pick_weighted(user, candidates, limit)
    return {"facts": picked}


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
    weights = user.get("interest_weights", {})
    current = weights.get(cat, 0.5)
    if data.action == "like":
        weights[cat] = min(3.0, current + 0.15)
        await db.users.update_one(
            {"id": user["id"]},
            {"$addToSet": {"liked_ids": fact_id, "seen_ids": fact_id},
             "$pull": {"disliked_ids": fact_id},
             "$set": {"interest_weights": weights}},
        )
    elif data.action == "dislike":
        weights[cat] = max(0.05, current - 0.2)
        await db.users.update_one(
            {"id": user["id"]},
            {"$addToSet": {"disliked_ids": fact_id, "seen_ids": fact_id},
             "$pull": {"liked_ids": fact_id, "bookmarked_ids": fact_id},
             "$set": {"interest_weights": weights}},
        )
    else:
        raise HTTPException(400, "Azione non valida")
    new_trophies = await update_trophies_for_user(user["id"])
    new_trophy_details = [t for t in TROPHIES if t["id"] in new_trophies]
    return {"ok": True, "new_weight": weights[cat], "new_trophies": new_trophy_details}


@api.post("/facts/{fact_id}/bookmark")
async def bookmark(fact_id: str, user=Depends(current_user)):
    bookmarked = set(user.get("bookmarked_ids", []))
    if fact_id in bookmarked:
        await db.users.update_one({"id": user["id"]}, {"$pull": {"bookmarked_ids": fact_id}})
        result = {"ok": True, "bookmarked": False, "new_trophies": []}
    else:
        await db.users.update_one({"id": user["id"]}, {"$addToSet": {"bookmarked_ids": fact_id}})
        new_trophies = await update_trophies_for_user(user["id"])
        result = {"ok": True, "bookmarked": True,
                  "new_trophies": [t for t in TROPHIES if t["id"] in new_trophies]}
    return result


@api.get("/facts/bookmarks")
async def get_bookmarks(user=Depends(current_user)):
    ids = user.get("bookmarked_ids", [])
    if not ids:
        return {"facts": []}
    cursor = db.facts.find({"id": {"$in": ids}}, {"_id": 0})
    facts = await cursor.to_list(500)
    return {"facts": facts}


@api.get("/facts/liked")
async def get_liked(user=Depends(current_user)):
    ids = user.get("liked_ids", [])
    if not ids:
        return {"facts": []}
    cursor = db.facts.find({"id": {"$in": ids}}, {"_id": 0})
    facts = await cursor.to_list(500)
    return {"facts": facts}


@api.get("/facts/{fact_id}")
async def get_fact(fact_id: str, user=Depends(current_user)):
    fact = await db.facts.find_one({"id": fact_id}, {"_id": 0})
    if not fact:
        raise HTTPException(404, "Fact non trovato")
    fact["is_liked"] = fact_id in user.get("liked_ids", [])
    fact["is_bookmarked"] = fact_id in user.get("bookmarked_ids", [])
    return fact


# ==========================================================
# AI GENERATION (Claude Sonnet 4.5 via Emergent)
# ==========================================================
async def generate_fact_ai(category: str, language: str = "it") -> Optional[Dict[str, Any]]:
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
    except Exception as e:
        logger.error(f"emergentintegrations import failed: {e}")
        return None

    lang_name = LANG_PROMPT_NAME.get(language, "italiano")
    format_hook = {
        "it": "Lo sapevi che?",
        "en": "Did you know?",
        "es": "¿Sabías que?",
    }.get(language, "Lo sapevi che?")
    system = (
        f"You are an expert author of fun, verified trivia. Write exclusively in {lang_name}. "
        f"Use the format '{format_hook}'. Respond ONLY with a valid JSON object with fields: "
        '{"title": "...", "short_fact": "...", "deep_dive": "...", "sources": [{"title": "...", "url": "..."}]}. '
        "Title must be catchy (max 80 chars). short_fact is 1-2 surprising sentences. "
        "deep_dive is 3-5 sentences with historical, scientific or curious details. "
        "sources (1-2 items) must be real, authoritative (Wikipedia, scientific journals, "
        "universities, museums). "
        f"Always write impeccably in {lang_name}. No markdown, pure JSON only."
    )
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"gen-{uuid.uuid4().hex[:8]}",
            system_message=system,
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")
        prompt = (
            f"Generate ONE new verified curiosity for the category: '{category}'. "
            "Avoid banal facts and look for something truly interesting and little known. "
            f"Include 1-2 authoritative verifiable sources. Reply ONLY with the JSON. Language: {lang_name}."
        )
        resp = await chat.send_message(UserMessage(text=prompt))
        raw = (resp or "").strip()
        if raw.startswith("```"):
            raw = raw.strip("`")
            if raw.startswith("json"):
                raw = raw[4:].strip()
        data = json.loads(raw)
        sources = data.get("sources") or []
        if not isinstance(sources, list):
            sources = []
        clean_sources = []
        for s in sources[:3]:
            if isinstance(s, dict) and s.get("title") and s.get("url"):
                clean_sources.append({"title": str(s["title"])[:200], "url": str(s["url"])[:500]})
        return {
            "title": data["title"][:200],
            "short_fact": data["short_fact"],
            "deep_dive": data["deep_dive"],
            "sources": clean_sources,
        }
    except Exception as e:
        logger.error(f"AI generation error: {e}")
        return None


@api.post("/facts/generate")
async def generate_new_fact(data: GenerateIn, user=Depends(current_user)):
    category = data.category
    if not category:
        weights = user.get("interest_weights", {})
        if weights:
            category = max(weights.keys(), key=lambda k: weights[k])
        else:
            category = random.choice(CATEGORIES)
    if category not in CATEGORIES:
        raise HTTPException(400, "Categoria non valida")

    lang = user.get("language", "it")
    ai = await generate_fact_ai(category, lang)
    if not ai:
        raise HTTPException(503, "Generazione AI non disponibile. Riprova.")

    img_url = image_for_fact(category, ai["title"], None)
    doc = {
        "id": str(uuid.uuid4()),
        "title": ai["title"],
        "short_fact": ai["short_fact"],
        "deep_dive": ai["deep_dive"],
        "sources": ai.get("sources", []),
        "category": category,
        "sub_category": None,
        "image_url": img_url,
        "source": "ai",
        "language": lang,
        "created_at": datetime.now(timezone.utc),
    }
    await db.facts.insert_one(doc)
    doc.pop("_id", None)

    # Track AI generation count
    await db.users.update_one({"id": user["id"]}, {"$inc": {"ai_generated_count": 1}})
    new_trophies = await update_trophies_for_user(user["id"])

    return {**doc, "new_trophies": [t for t in TROPHIES if t["id"] in new_trophies]}


@api.post("/facts/bulk-generate")
async def bulk_generate_facts(data: BulkGenerateIn, user=Depends(current_user)):
    """Generate multiple AI facts, optionally for a specific category or rotating categories."""
    cats = [data.category] * data.count if data.category else random.sample(CATEGORIES, min(data.count, len(CATEGORIES)))
    lang = user.get("language", "it")
    created = []
    for cat in cats:
        if cat not in CATEGORIES:
            continue
        ai = await generate_fact_ai(cat, lang)
        if not ai:
            continue
        img_url = image_for_fact(cat, ai["title"], None)
        doc = {
            "id": str(uuid.uuid4()),
            "title": ai["title"],
            "short_fact": ai["short_fact"],
            "deep_dive": ai["deep_dive"],
            "sources": ai.get("sources", []),
            "category": cat,
            "sub_category": None,
            "image_url": img_url,
            "source": "ai",
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
    fact = await db.facts.find_one({"category": cat}, {"_id": 0})
    if not fact:
        fact = await db.facts.find_one({}, {"_id": 0})
    if not fact:
        raise HTTPException(404, "Nessun fact disponibile")
    msg = {
        "to": token,
        "sound": "default",
        "title": "Lo Sapevi che?",
        "body": fact["title"],
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
    facts_count = await db.facts.count_documents({})
    users_count = await db.users.count_documents({})
    return {"ok": True, "facts": facts_count, "users": users_count}


app.include_router(api)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
