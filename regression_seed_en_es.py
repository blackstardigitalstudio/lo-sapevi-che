"""Regression test for seed_en_es.py — verify EN/ES facts are now served natively
and that previous functionality still works.
"""
import re
import sys
import uuid
import traceback
from pathlib import Path

import requests

env_path = Path("/app/frontend/.env")
BASE_URL = None
for line in env_path.read_text().splitlines():
    m = re.match(r"^EXPO_PUBLIC_BACKEND_URL=(.*)$", line.strip())
    if m:
        BASE_URL = m.group(1).strip().strip('"').rstrip("/")
        break
assert BASE_URL, "EXPO_PUBLIC_BACKEND_URL missing"
API = f"{BASE_URL}/api"
print(f"[INFO] Testing against {API}\n")

PASS, FAIL = [], []


def run(name, fn):
    try:
        fn()
        PASS.append(name)
        print(f"[PASS] {name}")
    except AssertionError as e:
        FAIL.append((name, str(e)))
        print(f"[FAIL] {name}: {e}")
    except Exception as e:
        FAIL.append((name, f"EXC: {e}"))
        print(f"[EXC ] {name}: {e}")
        traceback.print_exc()


def rand_email():
    return f"regr.{uuid.uuid4().hex[:10]}@losapevi-test.it"


def auth_hdr(token):
    return {"Authorization": f"Bearer {token}"}


STATE = {}


def test_health_facts_count():
    r = requests.get(f"{API}/health", timeout=20)
    assert r.status_code == 200, r.text
    j = r.json()
    assert j.get("ok") is True, j
    facts_count = j.get("facts", 0)
    assert facts_count >= 400, f"facts count {facts_count} < 400 (expected after seed_en_es)"
    STATE["facts_count"] = facts_count
    print(f"        → /health reports facts={facts_count}")


def test_register_fresh_user():
    payload = {
        "email": rand_email(),
        "password": "Marco2026!",
        "name": "Alessandro Bianchi",
        "interests": ["Scienza", "Storia", "Misteri", "Animali", "Spazio"],
        "security_question": "Nome del primo animale?",
        "security_answer": "Luna",
    }
    r = requests.post(f"{API}/auth/register", json=payload, timeout=30)
    assert r.status_code == 200, f"register failed: {r.status_code}: {r.text}"
    data = r.json()
    assert data["user"]["language"] == "it", data
    STATE["token"] = data["token"]
    STATE["email"] = payload["email"]


def test_switch_to_english():
    token = STATE["token"]
    r = requests.post(
        f"{API}/auth/language",
        json={"language": "en"},
        headers=auth_hdr(token),
        timeout=15,
    )
    assert r.status_code == 200, r.text
    j = r.json()
    assert j["user"]["language"] == "en", j


def test_feed_returns_english_facts_natively():
    """With ~57 EN facts seeded, feed should return language='en' facts (no IT fallback)."""
    token = STATE["token"]
    r = requests.get(f"{API}/feed?limit=10", headers=auth_hdr(token), timeout=30)
    assert r.status_code == 200, r.text
    facts = r.json().get("facts", [])
    assert len(facts) > 0, "feed empty for EN user"
    langs = [f.get("language") for f in facts]
    print(f"        → /feed returned {len(facts)} facts; langs={set(langs)}")
    # Critical assertion: ALL facts must be EN since DB has 57 EN facts now
    for f in facts:
        assert f.get("language") == "en", (
            f"Expected language='en' for all facts, got '{f.get('language')}' "
            f"on fact title='{f.get('title', '')[:60]}'. "
            f"Full lang distribution: {langs}"
        )


def test_switch_to_spanish_and_feed():
    token = STATE["token"]
    r = requests.post(
        f"{API}/auth/language",
        json={"language": "es"},
        headers=auth_hdr(token),
        timeout=15,
    )
    assert r.status_code == 200, r.text
    assert r.json()["user"]["language"] == "es"

    r = requests.get(f"{API}/feed?limit=10", headers=auth_hdr(token), timeout=30)
    assert r.status_code == 200, r.text
    facts = r.json().get("facts", [])
    assert len(facts) > 0, "feed empty for ES user"
    langs = [f.get("language") for f in facts]
    print(f"        → /feed (es) returned {len(facts)} facts; langs={set(langs)}")
    for f in facts:
        assert f.get("language") == "es", (
            f"Expected language='es' for all facts, got '{f.get('language')}' "
            f"on fact title='{f.get('title', '')[:60]}'. "
            f"Full lang distribution: {langs}"
        )


def test_switch_back_to_italian_and_feed():
    token = STATE["token"]
    r = requests.post(
        f"{API}/auth/language",
        json={"language": "it"},
        headers=auth_hdr(token),
        timeout=15,
    )
    assert r.status_code == 200, r.text

    r = requests.get(f"{API}/feed?limit=10", headers=auth_hdr(token), timeout=30)
    assert r.status_code == 200, r.text
    facts = r.json().get("facts", [])
    assert len(facts) > 0, "feed empty for IT user"
    langs = [f.get("language") for f in facts]
    print(f"        → /feed (it) returned {len(facts)} facts; langs={set(langs)}")
    for f in facts:
        assert f.get("language") == "it", (
            f"Expected language='it', got '{f.get('language')}'"
        )
    STATE["sample_it_fact_id"] = facts[0]["id"]


def test_react_like_returns_weights():
    """React(like) should still return new_weight + new_sub_weight."""
    token = STATE["token"]
    # Grab a fresh feed (IT) and react to the first fact
    r = requests.get(f"{API}/feed?limit=5", headers=auth_hdr(token), timeout=20)
    facts = r.json().get("facts", [])
    assert len(facts) > 0
    fid = facts[0]["id"]
    r = requests.post(
        f"{API}/facts/{fid}/react",
        json={"action": "like"},
        headers=auth_hdr(token),
        timeout=15,
    )
    assert r.status_code == 200, r.text
    j = r.json()
    assert "new_weight" in j, j
    assert "new_sub_weight" in j, j
    assert isinstance(j["new_weight"], (int, float))
    assert isinstance(j["new_sub_weight"], (int, float))
    print(f"        → react(like): new_weight={j['new_weight']}, new_sub_weight={j['new_sub_weight']}")


def test_categories_lang_en():
    r = requests.get(f"{API}/categories?lang=en", timeout=15)
    assert r.status_code == 200, r.text
    items = r.json()
    assert isinstance(items, list) and len(items) == 29, f"got {len(items)}"
    by_name = {c["name"]: c for c in items}
    assert by_name["Scienza"]["label"] == "Science", by_name["Scienza"]
    assert by_name["Storia"]["label"] == "History"
    assert by_name["Misteri"]["label"] == "Mysteries"
    assert by_name["Scienza"]["name"] == "Scienza"  # canonical preserved


def test_trophies_lang_en():
    token = STATE["token"]
    r = requests.get(f"{API}/trophies?lang=en", headers=auth_hdr(token), timeout=15)
    assert r.status_code == 200, r.text
    lst = r.json()
    assert isinstance(lst, list) and len(lst) == 10
    by_id = {t["id"]: t for t in lst}
    assert by_id["first_step"]["name"] == "First step", by_id["first_step"]
    assert by_id["first_step"]["desc"] == "Read your first fact."


def test_trophies_lang_es():
    token = STATE["token"]
    r = requests.get(f"{API}/trophies?lang=es", headers=auth_hdr(token), timeout=15)
    assert r.status_code == 200, r.text
    lst = r.json()
    by_id = {t["id"]: t for t in lst}
    assert by_id["first_step"]["name"] == "Primer paso", by_id["first_step"]


def test_count_by_language_via_feed_multiple():
    """Sanity check: walk the feed a few times for each lang and confirm lang purity."""
    token = STATE["token"]
    for lang in ("en", "es", "it"):
        requests.post(
            f"{API}/auth/language",
            json={"language": lang},
            headers=auth_hdr(token),
            timeout=10,
        )
        r = requests.get(f"{API}/feed?limit=20", headers=auth_hdr(token), timeout=30)
        assert r.status_code == 200, r.text
        facts = r.json().get("facts", [])
        assert len(facts) > 0, f"empty feed for lang={lang}"
        mismatched = [f for f in facts if f.get("language") != lang]
        assert not mismatched, (
            f"lang={lang}: {len(mismatched)}/{len(facts)} facts have wrong language: "
            f"{[(m.get('title','')[:40], m.get('language')) for m in mismatched[:3]]}"
        )
        print(f"        → lang={lang}: {len(facts)}/{len(facts)} facts in correct language ✓")


if __name__ == "__main__":
    tests = [
        ("health_facts_count_ge_400", test_health_facts_count),
        ("register_fresh_user", test_register_fresh_user),
        ("switch_to_english", test_switch_to_english),
        ("feed_returns_english_facts_natively", test_feed_returns_english_facts_natively),
        ("switch_to_spanish_and_feed", test_switch_to_spanish_and_feed),
        ("switch_back_to_italian_and_feed", test_switch_back_to_italian_and_feed),
        ("react_like_returns_weights", test_react_like_returns_weights),
        ("categories_lang_en", test_categories_lang_en),
        ("trophies_lang_en", test_trophies_lang_en),
        ("trophies_lang_es", test_trophies_lang_es),
        ("walk_feed_all_langs_purity", test_count_by_language_via_feed_multiple),
    ]
    for name, fn in tests:
        run(name, fn)
    print("\n========== SUMMARY ==========")
    print(f"PASS: {len(PASS)}")
    print(f"FAIL: {len(FAIL)}")
    for n, e in FAIL:
        print(f"  FAIL {n} -> {e}")
    sys.exit(0 if not FAIL else 1)
