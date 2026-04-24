"""Feed ranking v3 — weighted scoring with sub-category boost, diversity cap,
exploration factor, and recency bias.

Score = base_weight + sub_boost + recency_bonus + jitter
Then:
- Diversity cap: max n/3 from same sub_category
- Exploration slot: ~15% of slots reserved for low-weight categories
  (to avoid filter-bubble)
"""
import random
from datetime import datetime, timezone
from typing import List, Dict, Any


def _compute_score(
    fact: Dict[str, Any],
    cat_weights: Dict[str, float],
    sub_weights: Dict[str, float],
    now_ts: float,
) -> float:
    base = max(cat_weights.get(fact["category"], 0.3), 0.05)
    sub_key = f"{fact['category']}::{fact.get('sub_category') or ''}"
    sub_boost = sub_weights.get(sub_key, 0.0)

    # Recency bonus: facts created within 7 days get up to +0.3
    created = fact.get("created_at")
    recency = 0.0
    if created:
        try:
            if isinstance(created, str):
                ts = datetime.fromisoformat(created.replace("Z", "+00:00")).timestamp()
            else:
                ts = created.timestamp()
            age_days = max(0.0, (now_ts - ts) / 86400.0)
            # Exponential decay: fresh=+0.3, 7d=+0.11, 30d=+0.01
            recency = 0.3 * (2.718 ** (-age_days / 7.0))
        except Exception:
            recency = 0.0

    jitter = random.random() * 0.25
    return base + sub_boost + recency + jitter


def pick_weighted(user: Dict[str, Any], facts: List[Dict[str, Any]], n: int) -> List[Dict[str, Any]]:
    """Intelligently pick facts combining personalization + exploration + diversity."""
    if not facts:
        return []

    cat_weights = user.get("interest_weights", {}) or {}
    sub_weights: Dict[str, float] = user.get("sub_interest_weights", {}) or {}
    now_ts = datetime.now(timezone.utc).timestamp()

    # Score all candidates
    scored = [(_compute_score(f, cat_weights, sub_weights, now_ts), f) for f in facts]
    scored.sort(key=lambda x: -x[0])

    # Separate "top" pool (personalized) and "exploration" pool (low-weight cats)
    avg_weight = sum(cat_weights.values()) / max(len(cat_weights), 1) if cat_weights else 0.5
    exploration_pool = [
        f for _, f in scored
        if cat_weights.get(f["category"], 0.3) < avg_weight * 0.6
    ]
    random.shuffle(exploration_pool)

    # Reserve ~15% of slots for exploration (min 1, max n/4)
    exploration_slots = max(1, min(n // 6, len(exploration_pool))) if n >= 5 else 0

    picked: List[Dict[str, Any]] = []
    used_sub_counts: Dict[str, int] = {}
    cap_per_sub = max(2, n // 3)
    leftovers: List[Dict[str, Any]] = []
    picked_ids = set()

    # Fill top slots (personalized)
    target_top = n - exploration_slots
    for sc, f in scored:
        if len(picked) >= target_top:
            break
        sub_key = f"{f['category']}::{f.get('sub_category') or ''}"
        if used_sub_counts.get(sub_key, 0) >= cap_per_sub:
            leftovers.append(f)
            continue
        picked.append(f)
        picked_ids.add(f["id"])
        used_sub_counts[sub_key] = used_sub_counts.get(sub_key, 0) + 1

    # Fill exploration slots (diverse, low-weight categories)
    explo_added = 0
    for f in exploration_pool:
        if explo_added >= exploration_slots:
            break
        if f["id"] in picked_ids:
            continue
        sub_key = f"{f['category']}::{f.get('sub_category') or ''}"
        if used_sub_counts.get(sub_key, 0) >= cap_per_sub:
            continue
        picked.append(f)
        picked_ids.add(f["id"])
        used_sub_counts[sub_key] = used_sub_counts.get(sub_key, 0) + 1
        explo_added += 1

    # Fill remaining from leftovers / unused
    for sc, f in scored:
        if len(picked) >= n:
            break
        if f["id"] in picked_ids:
            continue
        picked.append(f)
        picked_ids.add(f["id"])
    for f in leftovers:
        if len(picked) >= n:
            break
        if f["id"] in picked_ids:
            continue
        picked.append(f)
        picked_ids.add(f["id"])

    return picked[:n]
