"""Feed ranking algorithm: weighted scoring with sub_category boost + diversity cap."""
import random
from typing import List, Dict, Any


def pick_weighted(user: Dict[str, Any], facts: List[Dict[str, Any]], n: int) -> List[Dict[str, Any]]:
    """Score each fact using:
    - category weight  (0.05..3.0)
    - sub_category weight (additive boost learned from likes)
    - small randomness for diversity
    - diversity cap to avoid stacking same sub_category.
    """
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
