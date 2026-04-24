"""One-shot seed script: generate AI facts for EN and ES languages.

Usage (run in backend dir):
    python3 seed_en_es.py --lang en --per-cat 3
    python3 seed_en_es.py --lang es --per-cat 3

Generates `per-cat` facts per category for the selected language.
Skips facts whose title already exists in DB (dedup).
Takes ~8-12s per fact (Claude Sonnet 4.5 API calls).
Safe to re-run — picks up where it left off.
"""
import asyncio
import argparse
import uuid
import logging
from datetime import datetime, timezone

from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent / ".env")

from seed_facts import CATEGORIES
from image_library import image_for_fact
from deps import db
from ai import generate_fact_ai

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger("seed_en_es")


async def seed_language(lang: str, per_category: int, max_total: int = 200):
    total_added = 0
    for cat in CATEGORIES:
        if total_added >= max_total:
            break

        existing = await db.facts.count_documents({"category": cat, "language": lang})
        need = max(0, per_category - existing)
        if need == 0:
            logger.info(f"[{lang}] {cat}: OK ({existing}/{per_category})")
            continue

        logger.info(f"[{lang}] {cat}: generating {need} fact(s)...")
        for i in range(need):
            if total_added >= max_total:
                break

            ai = await generate_fact_ai(cat, lang)
            if not ai:
                logger.warning(f"[{lang}] {cat} #{i+1}: AI failed, skipping")
                continue

            # Dedup by title
            if await db.facts.find_one({"title": ai["title"]}):
                logger.info(f"[{lang}] {cat} #{i+1}: duplicate title, skipping")
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
                "source": "ai_seed",
                "language": lang,
                "created_at": datetime.now(timezone.utc),
            }
            await db.facts.insert_one(doc)
            total_added += 1
            logger.info(f"[{lang}] +{total_added} '{ai['title'][:60]}'")
            await asyncio.sleep(0.3)

    logger.info(f"[{lang}] Done. Added {total_added} facts for language '{lang}'.")
    final = await db.facts.count_documents({"language": lang})
    logger.info(f"[{lang}] DB has now {final} facts in language '{lang}'.")


async def main():
    p = argparse.ArgumentParser()
    p.add_argument("--lang", choices=["it", "en", "es"], required=True)
    p.add_argument("--per-cat", type=int, default=3, help="target facts per category")
    p.add_argument("--max", type=int, default=200, help="hard cap on total added")
    args = p.parse_args()

    await seed_language(args.lang, args.per_cat, args.max)


if __name__ == "__main__":
    asyncio.run(main())
