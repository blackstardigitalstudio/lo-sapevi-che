"""Backend-side i18n for category & trophy display labels.

Canonical names stay in Italian (used as DB keys). UI labels are looked up
per user language through `label_for_category` / `label_for_trophy`.
"""

from typing import Dict

SUPPORTED_LANGS = ("it", "en", "es")


def _normalize(lang: str) -> str:
    lang = (lang or "it").lower().split("-")[0]
    return lang if lang in SUPPORTED_LANGS else "it"


CATEGORIES_I18N: Dict[str, Dict[str, str]] = {
    "Scienza":      {"it": "Scienza", "en": "Science", "es": "Ciencia"},
    "Storia":       {"it": "Storia", "en": "History", "es": "Historia"},
    "Tecnologia":   {"it": "Tecnologia", "en": "Technology", "es": "Tecnología"},
    "Natura":       {"it": "Natura", "en": "Nature", "es": "Naturaleza"},
    "Spazio":       {"it": "Spazio", "en": "Space", "es": "Espacio"},
    "Cucina":       {"it": "Cucina", "en": "Cooking", "es": "Cocina"},
    "Sport":        {"it": "Sport", "en": "Sports", "es": "Deportes"},
    "Arte":         {"it": "Arte", "en": "Art", "es": "Arte"},
    "Psicologia":   {"it": "Psicologia", "en": "Psychology", "es": "Psicología"},
    "Cinema":       {"it": "Cinema", "en": "Cinema", "es": "Cine"},
    "Musica":       {"it": "Musica", "en": "Music", "es": "Música"},
    "Geografia":    {"it": "Geografia", "en": "Geography", "es": "Geografía"},
    "Medicina":     {"it": "Medicina", "en": "Medicine", "es": "Medicina"},
    "Filosofia":    {"it": "Filosofia", "en": "Philosophy", "es": "Filosofía"},
    "Economia":     {"it": "Economia", "en": "Economy", "es": "Economía"},
    "Letteratura": {"it": "Letteratura", "en": "Literature", "es": "Literatura"},
    "Animali":     {"it": "Animali", "en": "Animals", "es": "Animales"},
    "Matematica":  {"it": "Matematica", "en": "Math", "es": "Matemáticas"},
    "Viaggi":      {"it": "Viaggi", "en": "Travel", "es": "Viajes"},
    "Mitologia":   {"it": "Mitologia", "en": "Mythology", "es": "Mitología"},
    "Mafia":       {"it": "Mafia", "en": "Mafia", "es": "Mafia"},
    "Guerre":      {"it": "Guerre", "en": "Wars", "es": "Guerras"},
    "Motori":      {"it": "Motori", "en": "Motorsport", "es": "Motor"},
    "Macchine":    {"it": "Macchine", "en": "Cars", "es": "Coches"},
    "Moto":        {"it": "Moto", "en": "Motorbikes", "es": "Motos"},
    "Invenzioni":  {"it": "Invenzioni", "en": "Inventions", "es": "Inventos"},
    "Disastri":    {"it": "Disastri", "en": "Disasters", "es": "Desastres"},
    "Religioni":   {"it": "Religioni", "en": "Religions", "es": "Religiones"},
    "Misteri":     {"it": "Misteri", "en": "Mysteries", "es": "Misterios"},
}

# Trophy definitions are keyed by trophy id (not visible to users).
# name/description get localized.
TROPHIES_I18N: Dict[str, Dict[str, Dict[str, str]]] = {
    "first_step": {
        "name": {"it": "Primo passo", "en": "First step", "es": "Primer paso"},
        "description": {
            "it": "Leggi la tua prima curiosità.",
            "en": "Read your first fact.",
            "es": "Lee tu primera curiosidad.",
        },
    },
    "curious": {
        "name": {"it": "Curioso", "en": "Curious", "es": "Curioso"},
        "description": {
            "it": "Leggi 10 curiosità.",
            "en": "Read 10 facts.",
            "es": "Lee 10 curiosidades.",
        },
    },
    "scholar": {
        "name": {"it": "Studioso", "en": "Scholar", "es": "Estudioso"},
        "description": {
            "it": "Leggi 50 curiosità.",
            "en": "Read 50 facts.",
            "es": "Lee 50 curiosidades.",
        },
    },
    "encyclopedia": {
        "name": {"it": "Enciclopedia vivente", "en": "Living encyclopedia", "es": "Enciclopedia viviente"},
        "description": {
            "it": "Leggi 200 curiosità.",
            "en": "Read 200 facts.",
            "es": "Lee 200 curiosidades.",
        },
    },
    "collector": {
        "name": {"it": "Collezionista", "en": "Collector", "es": "Coleccionista"},
        "description": {
            "it": "Salva 20 curiosità.",
            "en": "Bookmark 20 facts.",
            "es": "Guarda 20 curiosidades.",
        },
    },
    "flame_3": {
        "name": {"it": "Fiamma", "en": "Flame", "es": "Llama"},
        "description": {
            "it": "3 giorni di streak.",
            "en": "3-day streak.",
            "es": "Racha de 3 días.",
        },
    },
    "flame_7": {
        "name": {"it": "Fuoco eterno", "en": "Eternal fire", "es": "Fuego eterno"},
        "description": {
            "it": "7 giorni di streak.",
            "en": "7-day streak.",
            "es": "Racha de 7 días.",
        },
    },
    "flame_30": {
        "name": {"it": "Leggenda", "en": "Legend", "es": "Leyenda"},
        "description": {
            "it": "30 giorni di streak.",
            "en": "30-day streak.",
            "es": "Racha de 30 días.",
        },
    },
    "explorer": {
        "name": {"it": "Esploratore", "en": "Explorer", "es": "Explorador"},
        "description": {
            "it": "Leggi curiosità in 5 categorie diverse.",
            "en": "Read facts in 5 different categories.",
            "es": "Lee curiosidades en 5 categorías distintas.",
        },
    },
    "ai_pioneer": {
        "name": {"it": "AI Pioneer", "en": "AI Pioneer", "es": "Pionero IA"},
        "description": {
            "it": "Genera 5 curiosità con l'AI.",
            "en": "Generate 5 facts with AI.",
            "es": "Genera 5 curiosidades con IA.",
        },
    },
}


def label_for_category(canonical: str, lang: str = "it") -> str:
    lang = _normalize(lang)
    entry = CATEGORIES_I18N.get(canonical)
    if not entry:
        return canonical
    return entry.get(lang) or entry.get("it") or canonical


def label_for_trophy(trophy_id: str, lang: str = "it") -> Dict[str, str]:
    """Return {'name', 'description'} localized."""
    lang = _normalize(lang)
    entry = TROPHIES_I18N.get(trophy_id, {})
    return {
        "name": entry.get("name", {}).get(lang) or entry.get("name", {}).get("it") or trophy_id,
        "description": entry.get("description", {}).get(lang) or entry.get("description", {}).get("it") or "",
    }


# Friendly name used in Claude prompts for fact generation.
LANG_PROMPT_NAME = {
    "it": "italiano",
    "en": "English",
    "es": "español",
}
