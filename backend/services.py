"""Business services: trophies, AI fact generation, background prefill scheduler."""
import os
import json
import uuid
import random
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional

from seed_facts import CATEGORIES
from i18n import LANG_PROMPT_NAME
from image_library import image_for_fact
from deps import db, EMERGENT_LLM_KEY

logger = logging.getLogger("losapevi")


# ==========================================================
# TROPHIES
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
    earned = []
    stats_seen = len(user.get("seen_ids", []))
    stats_bookmarked = len(user.get("bookmarked_ids", []))
    streak = user.get("streak_days", 0)
    ai_generated = user.get("ai_generated_count", 0)

    if stats_seen >= 1: earned.append("first_step")
    if stats_seen >= 10: earned.append("curious")
    if stats_seen >= 50: earned.append("scholar")
    if stats_seen >= 200: earned.append("encyclopedia")
    if stats_bookmarked >= 10: earned.append("collector")
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


# ==========================================================
# AI FACT GENERATION (Claude Sonnet 4.5 via Emergent)
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


# ==========================================================
# BACKGROUND AI PRE-GENERATION SCHEDULER
# ==========================================================
PREFILL_INTERVAL_HOURS = int(os.environ.get("PREFILL_INTERVAL_HOURS", "12"))
PREFILL_BATCH_SIZE = int(os.environ.get("PREFILL_BATCH_SIZE", "10"))
PREFILL_MAX_FACTS = int(os.environ.get("PREFILL_MAX_FACTS", "1000"))

_scheduler = None


async def prefill_run():
    try:
        total = await db.facts.count_documents({})
        if total >= PREFILL_MAX_FACTS:
            logger.info(f"[prefill] Skipped: DB has {total} facts (cap={PREFILL_MAX_FACTS}).")
            return

        pipeline = [{"$group": {"_id": "$category", "n": {"$sum": 1}}}]
        counts = {c["_id"]: c["n"] async for c in db.facts.aggregate(pipeline)}
        ranked = sorted(CATEGORIES, key=lambda c: (counts.get(c, 0), random.random()))
        to_fill = ranked[: PREFILL_BATCH_SIZE]

        added = 0
        for cat in to_fill:
            if await db.facts.count_documents({}) >= PREFILL_MAX_FACTS:
                break
            ai = await generate_fact_ai(cat)
            if not ai:
                continue
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
                "language": "it",
                "created_at": datetime.now(timezone.utc),
            }
            await db.facts.insert_one(doc)
            added += 1
            await asyncio.sleep(0.3)

        new_total = await db.facts.count_documents({})
        logger.info(
            f"[prefill] Added {added} facts across {len(to_fill)} categories. "
            f"DB total now {new_total}/{PREFILL_MAX_FACTS}."
        )
    except Exception as e:
        logger.error(f"[prefill] run failed: {e}")


def start_prefill_scheduler():
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
        prefill_run,
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


def stop_prefill_scheduler():
    global _scheduler
    try:
        if _scheduler is not None and _scheduler.running:
            _scheduler.shutdown(wait=False)
    except Exception:
        pass


# ==========================================================
# FEED RANKING
# ==========================================================
def pick_weighted(user: Dict[str, Any], facts: List[Dict[str, Any]], n: int) -> List[Dict[str, Any]]:
    """Score each fact using category + sub_category weights with diversity cap."""
    if not facts:
        return []
    cat_weights = user.get("interest_weights", {}) or {}
    sub_weights: Dict[str, float] = user.get("sub_interest_weights", {}) or {}

    scored = []
    for f in facts:
        base = max(cat_weights.get(f["category"], 0.3), 0.05)
        sub_key = f"{f['category']}::{f.get('sub_category') or ''}"
        sub_boost = sub_weights.get(sub_key, 0.0)
        score = base + sub_boost + random.random() * 0.25
        scored.append([score, f])

    scored.sort(key=lambda x: -x[0])

    picked: List[Dict[str, Any]] = []
    used_sub_counts: Dict[str, int] = {}
    cap_per_sub = max(2, n // 3)
    leftovers = []
    for sc, f in scored:
        sub_key = f"{f['category']}::{f.get('sub_category') or ''}"
        if used_sub_counts.get(sub_key, 0) >= cap_per_sub:
            leftovers.append(f)
            continue
        picked.append(f)
        used_sub_counts[sub_key] = used_sub_counts.get(sub_key, 0) + 1
        if len(picked) >= n:
            break
    if len(picked) < n:
        picked.extend(leftovers[: n - len(picked)])
    return picked[:n]
