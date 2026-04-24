"""Miscellaneous routes: push notifications test, health check."""
import random
import logging

import httpx
from fastapi import APIRouter, HTTPException, Depends

from seed_facts import CATEGORIES
from deps import db, current_user

logger = logging.getLogger("losapevi")

router = APIRouter(tags=["misc"])

EXPO_PUSH_API = "https://exp.host/--/api/v2/push/send"


@router.post("/notifications/send-test")
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


@router.get("/")
async def root():
    return {"app": "Lo Sapevi che?", "status": "ok"}


@router.get("/health")
async def health():
    return {
        "ok": True,
        "facts": await db.facts.count_documents({}),
        "users": await db.users.count_documents({}),
    }
