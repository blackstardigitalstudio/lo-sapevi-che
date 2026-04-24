"""Background AI pre-generation scheduler (APScheduler, every 12h)."""
import os
import uuid
import random
import asyncio
import logging
from datetime import datetime, timezone, timedelta

from seed_facts import CATEGORIES
from image_library import image_for_fact
from deps import db
from ai import generate_fact_ai

logger = logging.getLogger("losapevi")

PREFILL_INTERVAL_HOURS = int(os.environ.get("PREFILL_INTERVAL_HOURS", "12"))
PREFILL_BATCH_SIZE = int(os.environ.get("PREFILL_BATCH_SIZE", "10"))
PREFILL_MAX_FACTS = int(os.environ.get("PREFILL_MAX_FACTS", "1000"))

_scheduler = None


async def prefill_run():
    """Generate facts cycling through IT/EN/ES to keep all languages balanced.

    Each run rotates languages so the DB fills up evenly over time.
    Also prioritizes low-count (category, language) pairs.
    """
    try:
        total = await db.facts.count_documents({})
        if total >= PREFILL_MAX_FACTS:
            logger.info(f"[prefill] Skipped: DB has {total} facts (cap={PREFILL_MAX_FACTS}).")
            return

        # Rotate language by run: counter persisted in DB meta
        meta = await db.meta.find_one({"_id": "prefill"}) or {"_id": "prefill", "run_count": 0}
        run_count = meta.get("run_count", 0)
        languages = ["it", "en", "es"]
        # Each run picks ONE primary language (round-robin)
        primary_lang = languages[run_count % len(languages)]
        await db.meta.update_one(
            {"_id": "prefill"}, {"$set": {"run_count": run_count + 1}}, upsert=True
        )
        logger.info(f"[prefill] run #{run_count} · primary language: {primary_lang}")

        # Per-language count per category — pick categories with least content
        pipeline = [
            {"$match": {"language": primary_lang}},
            {"$group": {"_id": "$category", "n": {"$sum": 1}}},
        ]
        counts = {c["_id"]: c["n"] async for c in db.facts.aggregate(pipeline)}
        ranked = sorted(CATEGORIES, key=lambda c: (counts.get(c, 0), random.random()))
        to_fill = ranked[: PREFILL_BATCH_SIZE]

        added = 0
        for cat in to_fill:
            if await db.facts.count_documents({}) >= PREFILL_MAX_FACTS:
                break
            ai = await generate_fact_ai(cat, primary_lang)
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
                "language": primary_lang,
                "created_at": datetime.now(timezone.utc),
            }
            await db.facts.insert_one(doc)
            added += 1
            await asyncio.sleep(0.3)

        new_total = await db.facts.count_documents({})
        logger.info(
            f"[prefill] Added {added} {primary_lang}-facts across {len(to_fill)} categories. "
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
