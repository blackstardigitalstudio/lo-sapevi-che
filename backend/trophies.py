"""Trophy definitions + eligibility logic."""
from typing import List, Dict, Any

from deps import db


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
    earned = []
    seen = len(user.get("seen_ids", []))
    bookmarked = len(user.get("bookmarked_ids", []))
    streak = user.get("streak_days", 0)
    ai_generated = user.get("ai_generated_count", 0)

    if seen >= 1: earned.append("first_step")
    if seen >= 10: earned.append("curious")
    if seen >= 50: earned.append("scholar")
    if seen >= 200: earned.append("encyclopedia")
    if bookmarked >= 10: earned.append("collector")
    if streak >= 3: earned.append("flame_3")
    if streak >= 7: earned.append("flame_7")
    if streak >= 30: earned.append("flame_30")
    if ai_generated >= 5: earned.append("ai_pioneer")

    liked_categories = user.get("liked_categories", [])
    if len(set(liked_categories)) >= 10:
        earned.append("explorer")
    return earned


async def update_trophies_for_user(user_id: str) -> List[str]:
    """Recompute trophies and return newly earned IDs."""
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        return []
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
