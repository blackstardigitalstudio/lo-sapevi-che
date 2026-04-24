"""Auth routes: register, login, password recovery, security question, language, profile."""
import uuid
from datetime import datetime, timezone, date
from typing import Dict

from fastapi import APIRouter, HTTPException, Depends

from seed_facts import CATEGORIES, SUB_CATEGORIES
from deps import (
    db, hash_password, verify_password, create_token,
    normalize_answer, user_to_public, current_user,
)
from models import (
    RegisterIn, LoginIn, ForgotQuestionIn, ForgotResetIn,
    SetSecurityQuestionIn, SetLanguageIn,
    UpdateInterestsIn, UpdateSubInterestsIn, PushTokenIn,
)
from trophies import TROPHIES, update_trophies_for_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
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


@router.post("/login")
async def login(data: LoginIn):
    email = data.email.lower()
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(401, "Credenziali non valide")
    return {"token": create_token(user["id"]), "user": user_to_public(user)}


@router.post("/forgot/question")
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


@router.post("/forgot/reset")
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


@router.post("/security-question")
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


@router.post("/language")
async def set_user_language(data: SetLanguageIn, user=Depends(current_user)):
    await db.users.update_one({"id": user["id"]}, {"$set": {"language": data.language}})
    updated = await db.users.find_one({"id": user["id"]}, {"_id": 0})
    return {"ok": True, "user": user_to_public(updated)}


@router.get("/me")
async def me(user=Depends(current_user)):
    return user_to_public(user)


@router.post("/interests")
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


@router.post("/push-token")
async def set_push_token(data: PushTokenIn, user=Depends(current_user)):
    await db.users.update_one({"id": user["id"]}, {"$set": {"expo_push_token": data.token}})
    return {"ok": True}


@router.post("/sub-interests")
async def update_sub_interests(data: UpdateSubInterestsIn, user=Depends(current_user)):
    clean: Dict[str, list] = {}
    for cat, subs in data.sub_interests.items():
        if cat in SUB_CATEGORIES:
            clean[cat] = [s for s in subs if s in SUB_CATEGORIES[cat]]
    await db.users.update_one({"id": user["id"]}, {"$set": {"sub_interests": clean}})
    updated = await db.users.find_one({"id": user["id"]}, {"_id": 0})
    return user_to_public(updated)


@router.post("/checkin")
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
