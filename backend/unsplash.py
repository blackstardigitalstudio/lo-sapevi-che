"""Unsplash image search by keyword, with MongoDB caching.

Replaces the fragile hand-curated photo catalog: every fact gets a real,
relevant, high-quality photo searched by keyword. Results per query term are
cached in `db.image_cache` so we issue at most one Unsplash request per unique
term (well within the free Demo rate limit of 50 req/hour).

If UNSPLASH_ACCESS_KEY is unset or a request fails, callers fall back to the
curated catalog in image_library.py.

Get a free key at https://unsplash.com/developers (Client-ID / Access Key).
"""
import hashlib
import logging
from typing import List, Optional

import httpx

from deps import UNSPLASH_ACCESS_KEY

logger = logging.getLogger("losapevi")

_API = "https://api.unsplash.com/search/photos"

# ---- Italian category -> English Unsplash query (English yields better hits) ----
CATEGORY_QUERY = {
    "Spazio": "outer space galaxy stars",
    "Scienza": "science laboratory research",
    "Tecnologia": "technology computer circuit",
    "Natura": "nature landscape",
    "Storia": "ancient history ruins",
    "Mitologia": "greek mythology statue temple",
    "Cucina": "italian food cuisine",
    "Sport": "sport athlete stadium",
    "Arte": "art painting gallery",
    "Psicologia": "psychology mind brain",
    "Cinema": "cinema movie film",
    "Musica": "music concert instruments",
    "Geografia": "geography world map earth",
    "Medicina": "medicine health hospital",
    "Filosofia": "philosophy books thinking",
    "Economia": "economy finance stock market",
    "Letteratura": "literature books library",
    "Animali": "wild animals wildlife",
    "Matematica": "mathematics equations blackboard",
    "Viaggi": "travel destination landscape",
    "Mafia": "vintage suit noir city night",
    "Guerre": "war history soldiers",
    "Motori": "motorsport race car",
    "Macchine": "sports car automobile",
    "Moto": "motorcycle motorbike",
    "Invenzioni": "invention technology laboratory",
    "Disastri": "natural disaster storm",
    "Religioni": "religion church temple cathedral",
    "Misteri": "mystery fog dark",
}

# ---- keyword stem found in the fact title -> precise English query ----
# (matches plural/declensions: "pinguin" catches pinguino/pinguini)
KEYWORD_QUERY = {
    "pinguin": "penguin", "koala": "koala", "polpo": "octopus", "piovr": "octopus",
    "delfin": "dolphin", "tartarug": "sea turtle", "balen": "whale", "squal": "shark",
    "leone": "lion", "tigre": "tiger", "elefant": "elephant", "giraff": "giraffe",
    "panda": "panda", "orso": "bear", "lupo": "wolf", "volpe": "fox",
    "scimm": "monkey", "serpent": "snake", "formica": "ant", "cavall": "horse",
    "fenicott": "flamingo", "aquil": "eagle", "pesce": "fish",
    "luna": "moon", "marte": "mars planet", "saturn": "saturn planet",
    "giove": "jupiter planet", "buco nero": "black hole space", "galass": "galaxy",
    "cometa": "comet", "vulcan": "volcano eruption", "ocean": "ocean sea",
    "deserto": "desert dunes", "foresta": "forest", "montagn": "mountains",
    "ghiacci": "glacier ice", "pizza": "pizza", "pasta": "pasta italian",
    "caffè": "coffee espresso", "cioccolat": "chocolate", "vino": "wine",
    "leonardo": "renaissance painting da vinci", "napoleon": "napoleon history",
    "piramid": "egypt pyramids", "colosseo": "colosseum rome", "titanic": "titanic ocean ship",
    # ape (bee) needs a trailing space in the curated catalog to avoid matching
    # other words; here we match the standalone stem carefully in _build_query.
}

_API_PARAMS_BASE = {"per_page": 10, "orientation": "landscape", "content_filter": "high"}


def _build_query(category: str, title: str, sub_category: Optional[str]) -> str:
    low = " " + str(title or "").lower() + " "
    # keyword match (most specific) — word-boundary-ish via surrounding spaces/stems
    for kw, q in KEYWORD_QUERY.items():
        if kw in low:
            return q
    # standalone "ape" (bee) — avoid matching inside other words
    if " ape " in low or " api " in low:
        return "bee"
    if sub_category:
        return str(sub_category)
    return CATEGORY_QUERY.get(category, category or "nature")


async def _fetch(query: str) -> List[str]:
    if not UNSPLASH_ACCESS_KEY:
        return []
    headers = {
        "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}",
        "Accept-Version": "v1",
    }
    params = {**_API_PARAMS_BASE, "query": query}
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(_API, params=params, headers=headers)
        if r.status_code == 403:
            logger.warning("[unsplash] rate limited / forbidden (check key).")
            return []
        if r.status_code != 200:
            logger.warning(f"[unsplash] HTTP {r.status_code} for '{query}'.")
            return []
        results = r.json().get("results", [])
        urls = []
        for p in results:
            u = (p.get("urls") or {}).get("regular")
            if u:
                urls.append(u)
        return urls
    except Exception as e:
        logger.warning(f"[unsplash] request error for '{query}': {e}")
        return []


async def _cached_urls(db, query: str) -> List[str]:
    try:
        doc = await db.image_cache.find_one({"_id": query})
    except Exception:
        doc = None
    if doc and doc.get("urls"):
        return doc["urls"]
    urls = await _fetch(query)
    if urls:
        try:
            await db.image_cache.update_one(
                {"_id": query}, {"$set": {"urls": urls}}, upsert=True
            )
        except Exception as e:
            logger.warning(f"[unsplash] cache write failed for '{query}': {e}")
    return urls


async def get_fact_image(db, category: str, title: str, sub_category: Optional[str] = None) -> Optional[str]:
    """Return a relevant Unsplash photo URL for a fact, or None to fall back."""
    query = _build_query(category, title, sub_category)
    urls = await _cached_urls(db, query)
    if not urls:
        return None
    # deterministic pick per fact so the image is stable across reloads
    h = int(hashlib.md5(str(title).encode("utf-8")).hexdigest()[:8], 16)
    return urls[h % len(urls)]
