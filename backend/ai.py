"""AI fact generation via Emergent LLM Key (Claude Sonnet 4.5)."""
import json
import uuid
import logging
from typing import Dict, Any, Optional

from i18n import LANG_PROMPT_NAME
from deps import EMERGENT_LLM_KEY

logger = logging.getLogger("losapevi")


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
