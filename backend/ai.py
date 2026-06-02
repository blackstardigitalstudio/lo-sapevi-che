"""AI fact generation via Google Gemini (free tier).

Standalone replacement for the former Emergent LLM integration. Get a free
API key at https://aistudio.google.com/apikey and set it as GEMINI_API_KEY.
"""
import json
import logging
from typing import Dict, Any, Optional

from i18n import LANG_PROMPT_NAME
from deps import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger("losapevi")

_configured = False


def _ensure_configured() -> bool:
    global _configured
    if not GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not set — AI fact generation disabled.")
        return False
    if not _configured:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        _configured = True
    return True


async def generate_fact_ai(category: str, language: str = "it") -> Optional[Dict[str, Any]]:
    if not _ensure_configured():
        return None

    import google.generativeai as genai

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
    prompt = (
        f"Generate ONE new verified curiosity for the category: '{category}'. "
        "Avoid banal facts and look for something truly interesting and little known. "
        f"Include 1-2 authoritative verifiable sources. Reply ONLY with the JSON. Language: {lang_name}."
    )
    try:
        model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            system_instruction=system,
        )
        response = await model.generate_content_async(prompt)
        raw = (getattr(response, "text", "") or "").strip()
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
