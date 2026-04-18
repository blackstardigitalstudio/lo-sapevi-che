"""Lo Sapevi che? - Backend.

Features:
- JWT auth (register/login/me)
- Users store interests + weights that evolve with like/dislike
- Facts feed personalized via niche weighting
- Bookmarks
- AI generation of new facts via Emergent LLM Key (Claude Sonnet 4.5)
- Push notification token registration
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
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any

import bcrypt
import jwt
import httpx
from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from motor.motor_asyncio import AsyncIOMotorClient

from seed_facts import SEED_FACTS, CATEGORIES, CATEGORY_EMOJI, CATEGORY_IMAGE_GROUP, IMAGE_URLS

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
# MODELS
# ==========================================================
class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    name: str = Field(min_length=1)
    interests: List[str] = Field(default_factory=list)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class UpdateInterestsIn(BaseModel):
    interests: List[str]


class ReactIn(BaseModel):
    action: str  # "like" | "dislike"


class PushTokenIn(BaseModel):
    token: str


class GenerateIn(BaseModel):
    category: Optional[str] = None


class UserPublic(BaseModel):
    id: str
    email: str
    name: str
    interests: List[str]
    interest_weights: Dict[str, float]
    stats: Dict[str, int]
    created_at: datetime


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
        "stats": {
            "liked": len(u.get("liked_ids", [])),
            "disliked": len(u.get("disliked_ids", [])),
            "bookmarked": len(u.get("bookmarked_ids", [])),
            "seen": len(u.get("seen_ids", [])),
        },
        "created_at": u.get("created_at"),
    }


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
        for f in SEED_FACTS:
            docs.append({
                "id": str(uuid.uuid4()),
                "title": f["title"],
                "short_fact": f["short_fact"],
                "deep_dive": f["deep_dive"],
                "category": f["category"],
                "image_url": f["image_url"],
                "source": f.get("source", "seed"),
                "created_at": datetime.now(timezone.utc),
            })
        if docs:
            await db.facts.insert_many(docs)
            logger.info(f"Inserted {len(docs)} seed facts.")


@app.on_event("shutdown")
async def on_shutdown():
    client.close()


# ==========================================================
# AUTH ROUTES
# ==========================================================
@api.post("/auth/register")
async def register(data: RegisterIn):
    email = data.email.lower()
    if await db.users.find_one({"email": email}):
        raise HTTPException(400, "Email già registrata")

    # Initial weights: 1.0 for selected interests, 0.3 for others
    weights = {c: (1.0 if c in data.interests else 0.3) for c in CATEGORIES}

    user_id = str(uuid.uuid4())
    doc = {
        "id": user_id,
        "email": email,
        "name": data.name.strip(),
        "password_hash": hash_password(data.password),
        "interests": data.interests,
        "interest_weights": weights,
        "liked_ids": [],
        "disliked_ids": [],
        "bookmarked_ids": [],
        "seen_ids": [],
        "expo_push_token": None,
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


@api.get("/auth/me")
async def me(user=Depends(current_user)):
    return user_to_public(user)


@api.post("/auth/interests")
async def update_interests(data: UpdateInterestsIn, user=Depends(current_user)):
    weights = user.get("interest_weights", {})
    # Boost selected categories; reset non-selected to 0.3 minimum but keep learned weights
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


# ==========================================================
# CATEGORIES
# ==========================================================
@api.get("/categories")
async def list_categories():
    return [
        {"name": c, "icon": CATEGORY_EMOJI.get(c, "sparkles")}
        for c in CATEGORIES
    ]


# ==========================================================
# FEED
# ==========================================================
def pick_weighted(user: Dict[str, Any], facts: List[Dict[str, Any]], n: int) -> List[Dict[str, Any]]:
    """Pick n facts from candidates weighted by the user's interest weights."""
    if not facts:
        return []
    weights = user.get("interest_weights", {})
    # score each fact
    scored = []
    for f in facts:
        w = max(weights.get(f["category"], 0.3), 0.05)
        scored.append((w + random.random() * 0.2, f))  # small random perturbation
    scored.sort(key=lambda x: -x[0])
    return [s[1] for s in scored[:n]]


@api.get("/feed")
async def feed(limit: int = 20, user=Depends(current_user)):
    seen = set(user.get("seen_ids", []))
    disliked = set(user.get("disliked_ids", []))
    exclude = seen | disliked
    # Fetch a larger pool then pick weighted top N
    cursor = db.facts.find({"id": {"$nin": list(exclude)}}, {"_id": 0}).limit(200)
    candidates = await cursor.to_list(200)
    if not candidates:
        # If user has seen everything, allow seen but not disliked
        cursor = db.facts.find({"id": {"$nin": list(disliked)}}, {"_id": 0}).limit(200)
        candidates = await cursor.to_list(200)
    picked = pick_weighted(user, candidates, limit)
    return {"facts": picked}


@api.post("/facts/{fact_id}/seen")
async def mark_seen(fact_id: str, user=Depends(current_user)):
    await db.users.update_one({"id": user["id"]}, {"$addToSet": {"seen_ids": fact_id}})
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
    return {"ok": True, "new_weight": weights[cat]}


@api.post("/facts/{fact_id}/bookmark")
async def bookmark(fact_id: str, user=Depends(current_user)):
    bookmarked = set(user.get("bookmarked_ids", []))
    if fact_id in bookmarked:
        await db.users.update_one({"id": user["id"]}, {"$pull": {"bookmarked_ids": fact_id}})
        return {"ok": True, "bookmarked": False}
    await db.users.update_one({"id": user["id"]}, {"$addToSet": {"bookmarked_ids": fact_id}})
    return {"ok": True, "bookmarked": True}


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
async def generate_fact_ai(category: str) -> Optional[Dict[str, Any]]:
    """Generate a new 'Lo sapevi che?' fact using Claude Sonnet 4.5."""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
    except Exception as e:
        logger.error(f"emergentintegrations import failed: {e}")
        return None

    system = (
        "Sei un esperto divulgatore italiano. Scrivi curiosità verificate e affascinanti "
        "nel formato 'Lo sapevi che?' Rispondi ESCLUSIVAMENTE con un JSON valido con questi campi: "
        '{"title": "...", "short_fact": "...", "deep_dive": "..."} '
        "Il title deve essere accattivante (max 80 caratteri). "
        "Lo short_fact è una frase di 1-2 righe che sorprende. "
        "Il deep_dive è un approfondimento di 3-5 frasi con dettagli storici, scientifici o curiosi. "
        "Scrivi sempre in italiano impeccabile. Non usare markdown, solo testo piano nel JSON."
    )
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"gen-{uuid.uuid4().hex[:8]}",
            system_message=system,
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")
        prompt = (
            f"Generami UNA nuova curiosità verificata nella categoria: '{category}'. "
            "Evita fatti banali e cerca qualcosa di veramente interessante e poco noto. "
            "Rispondi SOLO con il JSON richiesto."
        )
        resp = await chat.send_message(UserMessage(text=prompt))
        raw = (resp or "").strip()
        # Sometimes models wrap in ```json ... ```
        if raw.startswith("```"):
            raw = raw.strip("`")
            if raw.startswith("json"):
                raw = raw[4:].strip()
        data = json.loads(raw)
        return {
            "title": data["title"][:200],
            "short_fact": data["short_fact"],
            "deep_dive": data["deep_dive"],
        }
    except Exception as e:
        logger.error(f"AI generation error: {e}")
        return None


@api.post("/facts/generate")
async def generate_new_fact(data: GenerateIn, user=Depends(current_user)):
    # Pick category from user's top weights if not provided
    category = data.category
    if not category:
        weights = user.get("interest_weights", {})
        if weights:
            category = max(weights.keys(), key=lambda k: weights[k])
        else:
            category = random.choice(CATEGORIES)
    if category not in CATEGORIES:
        raise HTTPException(400, "Categoria non valida")

    ai = await generate_fact_ai(category)
    if not ai:
        raise HTTPException(503, "Generazione AI non disponibile. Riprova.")

    img_group = CATEGORY_IMAGE_GROUP.get(category, "background_space")
    doc = {
        "id": str(uuid.uuid4()),
        "title": ai["title"],
        "short_fact": ai["short_fact"],
        "deep_dive": ai["deep_dive"],
        "category": category,
        "image_url": IMAGE_URLS[img_group],
        "source": "ai",
        "created_at": datetime.now(timezone.utc),
    }
    await db.facts.insert_one(doc)
    doc.pop("_id", None)
    return doc


# ==========================================================
# PUSH (send via Expo)
# ==========================================================
EXPO_PUSH_API = "https://exp.host/--/api/v2/push/send"


@api.post("/notifications/send-test")
async def send_test_push(user=Depends(current_user)):
    """Send a test push to the current user immediately."""
    token = user.get("expo_push_token")
    if not token:
        raise HTTPException(400, "Nessun token push registrato")
    # Pick a fact matching top interest
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


# Mount router
app.include_router(api)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
