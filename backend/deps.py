"""Shared dependencies and helpers: DB client, password hashing, JWT, auth."""
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

import bcrypt
import jwt
from fastapi import HTTPException, Request
from motor.motor_asyncio import AsyncIOMotorClient


MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]
JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = 60 * 24 * 30  # 30 days
# AI: Google Gemini free tier. Get a key at https://aistudio.google.com/apikey
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]


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


def normalize_answer(a: str) -> str:
    """Normalize security answer (lowercase, strip, collapse spaces)."""
    return " ".join((a or "").lower().strip().split())


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
