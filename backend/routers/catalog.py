"""Catalog routes: categories, subcategories, preview, trophies list."""
from fastapi import APIRouter, HTTPException, Depends

from seed_facts import CATEGORIES, CATEGORY_EMOJI, SUB_CATEGORIES
from i18n import label_for_category, label_for_trophy
from image_library import first_image_for_category
from deps import db, current_user
from trophies import TROPHIES

router = APIRouter(tags=["catalog"])


@router.get("/categories")
async def list_categories(lang: str = "it"):
    return [
        {
            "name": c,
            "label": label_for_category(c, lang),
            "icon": CATEGORY_EMOJI.get(c, "sparkles"),
            "has_subcategories": c in SUB_CATEGORIES,
            "subcategories": SUB_CATEGORIES.get(c, []),
        }
        for c in CATEGORIES
    ]


@router.get("/subcategories/{category}")
async def list_subcategories(category: str):
    if category not in CATEGORIES:
        raise HTTPException(404, "Categoria non trovata")
    return {"category": category, "subcategories": SUB_CATEGORIES.get(category, [])}


@router.get("/preview")
async def preview_per_category():
    out = []
    for cat in CATEGORIES:
        cursor = db.facts.find({"category": cat}, {"_id": 0}).limit(1)
        items = await cursor.to_list(1)
        if items:
            f = items[0]
            out.append({
                "category": cat,
                "icon": CATEGORY_EMOJI.get(cat, "sparkles"),
                "sample_title": f["title"],
                "sample_short": f["short_fact"],
                "image_url": f["image_url"],
            })
        else:
            out.append({
                "category": cat,
                "icon": CATEGORY_EMOJI.get(cat, "sparkles"),
                "sample_title": cat,
                "sample_short": "Scopri curiosità su " + cat.lower(),
                "image_url": first_image_for_category(cat),
            })
    return out


@router.get("/trophies")
async def list_trophies(lang: str = "it", user=Depends(current_user)):
    earned = set(user.get("trophies", []))
    out = []
    for t in TROPHIES:
        loc = label_for_trophy(t["id"], lang)
        out.append({
            **t,
            "name": loc["name"] or t.get("name"),
            "desc": loc["description"] or t.get("desc"),
            "earned": t["id"] in earned,
        })
    return out
