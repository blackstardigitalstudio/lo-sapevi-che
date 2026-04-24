"""Facts routes: feed, reactions (like/dislike), bookmarks, AI generation."""
import uuid
import random
from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Depends

from seed_facts import CATEGORIES
from image_library import image_for_fact
from deps import db, current_user
from models import ReactIn, GenerateIn, BulkGenerateIn
from services import (
    TROPHIES, update_trophies_for_user,
    generate_fact_ai, pick_weighted,
)

router = APIRouter(tags=["facts"])


@router.get("/feed")
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


@router.post("/facts/{fact_id}/seen")
async def mark_seen(fact_id: str, user=Depends(current_user)):
    await db.users.update_one({"id": user["id"]}, {"$addToSet": {"seen_ids": fact_id}})
    await update_trophies_for_user(user["id"])
    return {"ok": True}


@router.post("/facts/{fact_id}/react")
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


@router.post("/facts/{fact_id}/bookmark")
async def bookmark(fact_id: str, user=Depends(current_user)):
    bookmarked = set(user.get("bookmarked_ids", []))
    if fact_id in bookmarked:
        await db.users.update_one({"id": user["id"]}, {"$pull": {"bookmarked_ids": fact_id}})
        return {"ok": True, "bookmarked": False, "new_trophies": []}
    await db.users.update_one({"id": user["id"]}, {"$addToSet": {"bookmarked_ids": fact_id}})
    new_trophies = await update_trophies_for_user(user["id"])
    return {"ok": True, "bookmarked": True,
            "new_trophies": [t for t in TROPHIES if t["id"] in new_trophies]}


@router.get("/facts/bookmarks")
async def get_bookmarks(user=Depends(current_user)):
    ids = user.get("bookmarked_ids", [])
    if not ids:
        return {"facts": []}
    return {"facts": await db.facts.find({"id": {"$in": ids}}, {"_id": 0}).to_list(500)}


@router.get("/facts/liked")
async def get_liked(user=Depends(current_user)):
    ids = user.get("liked_ids", [])
    if not ids:
        return {"facts": []}
    return {"facts": await db.facts.find({"id": {"$in": ids}}, {"_id": 0}).to_list(500)}


@router.get("/facts/{fact_id}")
async def get_fact(fact_id: str, user=Depends(current_user)):
    fact = await db.facts.find_one({"id": fact_id}, {"_id": 0})
    if not fact:
        raise HTTPException(404, "Fact non trovato")
    fact["is_liked"] = fact_id in user.get("liked_ids", [])
    fact["is_bookmarked"] = fact_id in user.get("bookmarked_ids", [])
    return fact


@router.post("/facts/generate")
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


@router.post("/facts/bulk-generate")
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
