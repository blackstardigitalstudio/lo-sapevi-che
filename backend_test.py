"""Backend tests for Iteration 8 — multilingual + personalization v2.

Uses EXPO_PUBLIC_BACKEND_URL + /api (no localhost).
"""
import os
import re
import sys
import time
import uuid
import random
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
print(f"[INFO] Testing against {API}")

PASS = []
FAIL = []
WARN = []


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


def warn(name, msg):
    WARN.append((name, msg))
    print(f"[WARN] {name}: {msg}")


def rand_email(prefix="iter8"):
    return f"{prefix}.{uuid.uuid4().hex[:10]}@losapevi-test.it"


def register_user(email=None, interests=None, name="Marco Rossi"):
    email = email or rand_email()
    payload = {
        "email": email,
        "password": "Pippo123!",
        "name": name,
        "interests": interests or ["Scienza", "Storia", "Misteri"],
        "security_question": "Nome del primo animale?",
        "security_answer": "Fido",
    }
    r = requests.post(f"{API}/auth/register", json=payload, timeout=30)
    assert r.status_code == 200, f"register failed {r.status_code}: {r.text}"
    return r.json(), payload


def auth_hdr(token):
    return {"Authorization": f"Bearer {token}"}


STATE = {}


def test_health():
    r = requests.get(f"{API}/health", timeout=20)
    assert r.status_code == 200
    j = r.json()
    assert j.get("ok") is True, j
    assert j.get("facts", 0) >= 200, f"facts <200: {j}"


def test_register_happy_and_lang_default():
    data, payload = register_user(interests=["Scienza", "Storia"])
    STATE["user_main"] = data
    STATE["pwd_main"] = payload["password"]
    STATE["email_main"] = payload["email"]
    token = data["token"]
    user = data["user"]
    assert user.get("language") == "it", f"default language should be 'it': {user}"
    r = requests.get(f"{API}/auth/me", headers=auth_hdr(token), timeout=15)
    assert r.status_code == 200
    me = r.json()
    assert me.get("language") == "it", me
    assert isinstance(me.get("has_security_question"), bool)


def test_register_missing_security_fields():
    payload = {
        "email": rand_email("nosec"),
        "password": "Pippo123!",
        "name": "Test",
        "interests": [],
    }
    r = requests.post(f"{API}/auth/register", json=payload, timeout=20)
    assert r.status_code == 422, f"expected 422, got {r.status_code}: {r.text}"


def test_set_language_endpoint():
    token = STATE["user_main"]["token"]
    r = requests.post(f"{API}/auth/language", json={"language": "xx"}, headers=auth_hdr(token), timeout=15)
    assert r.status_code == 422, f"invalid lang should be 422, got {r.status_code}: {r.text}"
    r = requests.post(f"{API}/auth/language", json={"language": "en"}, timeout=15)
    assert r.status_code == 401, f"no token should 401, got {r.status_code}"
    r = requests.post(f"{API}/auth/language", json={"language": "en"}, headers=auth_hdr(token), timeout=15)
    assert r.status_code == 200, f"lang update failed: {r.text}"
    j = r.json()
    assert j.get("ok") is True
    assert j["user"]["language"] == "en", j
    r = requests.get(f"{API}/auth/me", headers=auth_hdr(token), timeout=15)
    assert r.json().get("language") == "en"


def test_categories_lang():
    r = requests.get(f"{API}/categories", timeout=15)
    assert r.status_code == 200
    items = r.json()
    assert isinstance(items, list) and len(items) == 29, f"expected 29, got {len(items)}"
    for c in items:
        assert "name" in c and "label" in c and "icon" in c
        assert "has_subcategories" in c and "subcategories" in c
    names = {c["name"] for c in items}
    assert "Scienza" in names and "Storia" in names and "Misteri" in names

    r = requests.get(f"{API}/categories?lang=en", timeout=15)
    items_en = r.json()
    by_name = {c["name"]: c for c in items_en}
    assert by_name["Scienza"]["label"] == "Science", by_name["Scienza"]
    assert by_name["Storia"]["label"] == "History"
    assert by_name["Misteri"]["label"] == "Mysteries"
    assert by_name["Scienza"]["name"] == "Scienza"

    r = requests.get(f"{API}/categories?lang=es", timeout=15)
    items_es = r.json()
    by_name = {c["name"]: c for c in items_es}
    assert by_name["Scienza"]["label"] == "Ciencia"
    assert by_name["Storia"]["label"] == "Historia"
    assert by_name["Misteri"]["label"] == "Misterios"
    assert len(items_es) == 29


def test_trophies_lang():
    token = STATE["user_main"]["token"]
    r = requests.get(f"{API}/trophies?lang=en", timeout=15)
    assert r.status_code == 401
    r = requests.get(f"{API}/trophies?lang=en", headers=auth_hdr(token), timeout=15)
    assert r.status_code == 200
    lst = r.json()
    assert isinstance(lst, list) and len(lst) == 10
    by_id = {t["id"]: t for t in lst}
    assert by_id["first_step"]["name"] == "First step", by_id["first_step"]
    assert by_id["first_step"]["desc"] == "Read your first fact.", by_id["first_step"]
    assert by_id["curious"]["name"] == "Curious"
    r = requests.get(f"{API}/trophies?lang=es", headers=auth_hdr(token), timeout=15)
    lst = r.json()
    by_id = {t["id"]: t for t in lst}
    assert by_id["first_step"]["name"] == "Primer paso", by_id["first_step"]
    assert by_id["first_step"]["desc"] == "Lee tu primera curiosidad."
    r = requests.get(f"{API}/trophies", headers=auth_hdr(token), timeout=15)
    lst = r.json()
    by_id = {t["id"]: t for t in lst}
    assert by_id["first_step"]["name"] == "Primo passo", by_id["first_step"]


def test_feed_lang_filter_and_fallback():
    token = STATE["user_main"]["token"]
    requests.post(f"{API}/auth/language", json={"language": "it"}, headers=auth_hdr(token), timeout=15)
    r = requests.get(f"{API}/feed?limit=20", headers=auth_hdr(token), timeout=30)
    assert r.status_code == 200
    facts = r.json().get("facts", [])
    assert len(facts) > 0, "empty feed for IT user"
    for f in facts:
        assert f.get("language") == "it", f"fact lang != it: {f.get('language')}"

    r = requests.post(f"{API}/auth/language", json={"language": "en"}, headers=auth_hdr(token), timeout=15)
    assert r.status_code == 200
    r = requests.get(f"{API}/feed?limit=20", headers=auth_hdr(token), timeout=30)
    assert r.status_code == 200, r.text
    facts = r.json().get("facts", [])
    assert len(facts) > 0, "feed fallback empty for EN user"
    for f in facts:
        assert f.get("language") in ("it", "en", "es"), f.get("language")

    requests.post(f"{API}/auth/language", json={"language": "it"}, headers=auth_hdr(token), timeout=15)
    r = requests.get(f"{API}/feed?limit=10", headers=auth_hdr(token), timeout=30)
    assert r.status_code == 200 and len(r.json().get("facts", [])) > 0


def test_personalization_v2_react():
    data, _ = register_user(interests=["Scienza", "Storia"])
    token = data["token"]
    r = requests.get(f"{API}/feed?limit=5", headers=auth_hdr(token), timeout=20)
    assert r.status_code == 200
    facts = r.json().get("facts", [])
    assert len(facts) >= 2, f"need 2 facts, got {len(facts)}"
    fid = facts[0]["id"]
    r = requests.post(f"{API}/facts/{fid}/react", json={"action": "like"},
                      headers=auth_hdr(token), timeout=15)
    assert r.status_code == 200, r.text
    j = r.json()
    assert "new_weight" in j and "new_sub_weight" in j, j
    assert isinstance(j["new_sub_weight"], (int, float))
    assert j["new_sub_weight"] >= 0.0
    fid2 = facts[1]["id"]
    r = requests.post(f"{API}/facts/{fid2}/react", json={"action": "dislike"},
                      headers=auth_hdr(token), timeout=15)
    assert r.status_code == 200, r.text
    j2 = r.json()
    assert "new_sub_weight" in j2, j2
    for _ in range(3):
        rf = requests.get(f"{API}/feed?limit=5", headers=auth_hdr(token), timeout=20)
        assert rf.status_code == 200
        ff = rf.json().get("facts", [])
        if ff:
            lf = ff[0]["id"]
            rr = requests.post(f"{API}/facts/{lf}/react", json={"action": "like"},
                               headers=auth_hdr(token), timeout=15)
            assert rr.status_code == 200


def test_ai_generate_language():
    data, _ = register_user(interests=["Scienza"], name="Luis AI")
    token = data["token"]
    rset = requests.post(f"{API}/auth/language", json={"language": "es"}, headers=auth_hdr(token), timeout=10)
    assert rset.status_code == 200
    r = requests.post(f"{API}/facts/generate", json={"category": "Ciencia"}, headers=auth_hdr(token), timeout=30)
    assert r.status_code == 400, f"expected 400 for translated category, got {r.status_code}: {r.text}"

    r = requests.post(f"{API}/facts/generate", json={"category": "Scienza"}, headers=auth_hdr(token), timeout=120)
    if r.status_code == 503:
        time.sleep(2)
        r = requests.post(f"{API}/facts/generate", json={"category": "Scienza"}, headers=auth_hdr(token), timeout=120)
    if r.status_code == 503:
        warn("ai_generate_language", "AI returned 503 twice — accepting as transient.")
        return
    assert r.status_code == 200, f"AI generate failed: {r.status_code} {r.text}"
    doc = r.json()
    assert doc.get("language") == "es", f"generated fact language != es: {doc.get('language')}"
    assert doc.get("category") == "Scienza"
    assert doc.get("title") and doc.get("short_fact") and doc.get("deep_dive")
    STATE["es_fact_id"] = doc["id"]


def test_auth_login():
    email = STATE["email_main"]
    pwd = STATE["pwd_main"]
    r = requests.post(f"{API}/auth/login", json={"email": email, "password": pwd}, timeout=15)
    assert r.status_code == 200
    j = r.json()
    assert j.get("token") and j.get("user")


def test_forgot_question():
    email = STATE["email_main"]
    r = requests.post(f"{API}/auth/forgot/question", json={"email": email}, timeout=15)
    assert r.status_code == 200
    assert "security_question" in r.json()
    r = requests.post(f"{API}/auth/forgot/question", json={"email": f"no.{uuid.uuid4().hex}@x.it"}, timeout=15)
    assert r.status_code == 404


def test_forgot_reset_flow():
    email = STATE["email_main"]
    r = requests.post(f"{API}/auth/forgot/reset", json={
        "email": email, "security_answer": "wrong", "new_password": "NuovaPwd123!"
    }, timeout=15)
    assert r.status_code == 401, r.text
    r = requests.post(f"{API}/auth/forgot/reset", json={
        "email": email, "security_answer": "  FIDO  ", "new_password": "NuovaPwd123!"
    }, timeout=15)
    assert r.status_code == 200, r.text
    STATE["pwd_main"] = "NuovaPwd123!"
    r = requests.post(f"{API}/auth/login", json={"email": email, "password": "NuovaPwd123!"}, timeout=15)
    assert r.status_code == 200
    STATE["user_main"]["token"] = r.json()["token"]


def test_security_question_update():
    token = STATE["user_main"]["token"]
    r = requests.post(f"{API}/auth/security-question", json={
        "security_question": "Q?", "security_answer": "a", "current_password": "x"
    }, timeout=15)
    assert r.status_code == 401
    r = requests.post(f"{API}/auth/security-question", json={
        "security_question": "Piatto preferito?", "security_answer": "Pizza",
        "current_password": "wrongpwd"
    }, headers=auth_hdr(token), timeout=15)
    assert r.status_code == 401
    r = requests.post(f"{API}/auth/security-question", json={
        "security_question": "Piatto preferito?", "security_answer": "Pizza",
        "current_password": STATE["pwd_main"]
    }, headers=auth_hdr(token), timeout=15)
    assert r.status_code == 200, r.text


def test_checkin():
    token = STATE["user_main"]["token"]
    r = requests.post(f"{API}/auth/checkin", headers=auth_hdr(token), timeout=15)
    assert r.status_code == 200
    j = r.json()
    assert "streak_days" in j


def test_me_fields():
    token = STATE["user_main"]["token"]
    r = requests.get(f"{API}/auth/me", headers=auth_hdr(token), timeout=15)
    assert r.status_code == 200
    j = r.json()
    assert isinstance(j.get("has_security_question"), bool)
    assert j.get("language") in ("it", "en", "es")


def test_preview():
    r = requests.get(f"{API}/preview", timeout=20)
    assert r.status_code == 200
    lst = r.json()
    assert isinstance(lst, list) and len(lst) > 0
    assert "category" in lst[0] and "image_url" in lst[0]


def test_subcategories():
    r = requests.get(f"{API}/subcategories/Scienza", timeout=10)
    assert r.status_code == 200
    j = r.json()
    assert j.get("category") == "Scienza"
    assert isinstance(j.get("subcategories"), list)
    r = requests.get(f"{API}/subcategories/NopeCat", timeout=10)
    assert r.status_code == 404


def test_bookmark_and_liked():
    data, _ = register_user(interests=["Scienza", "Storia"], name="Elena Conte")
    token = data["token"]
    rf = requests.get(f"{API}/feed?limit=5", headers=auth_hdr(token), timeout=20)
    assert rf.status_code == 200
    facts = rf.json().get("facts", [])
    assert len(facts) >= 2
    fid = facts[0]["id"]
    # Bookmark ON
    r = requests.post(f"{API}/facts/{fid}/bookmark", headers=auth_hdr(token), timeout=10)
    assert r.status_code == 200 and r.json().get("bookmarked") is True, r.text
    # GET bookmarks
    r = requests.get(f"{API}/facts/bookmarks", headers=auth_hdr(token), timeout=10)
    assert r.status_code == 200
    bms = r.json().get("facts", [])
    assert any(f["id"] == fid for f in bms), f"bookmark id not in list: {bms}"
    # Toggle OFF
    r = requests.post(f"{API}/facts/{fid}/bookmark", headers=auth_hdr(token), timeout=10)
    assert r.status_code == 200 and r.json().get("bookmarked") is False
    # Like a fact then check /facts/liked
    fid2 = facts[1]["id"]
    r = requests.post(f"{API}/facts/{fid2}/react", json={"action": "like"},
                      headers=auth_hdr(token), timeout=10)
    assert r.status_code == 200
    r = requests.get(f"{API}/facts/liked", headers=auth_hdr(token), timeout=10)
    assert r.status_code == 200
    liked = r.json().get("facts", [])
    assert any(f["id"] == fid2 for f in liked), f"liked id not in list: {liked}"


if __name__ == "__main__":
    tests = [
        ("health", test_health),
        ("register_happy_default_lang_it", test_register_happy_and_lang_default),
        ("register_missing_security_422", test_register_missing_security_fields),
        ("auth_language_endpoint", test_set_language_endpoint),
        ("categories_lang", test_categories_lang),
        ("trophies_lang", test_trophies_lang),
        ("feed_language_filter_and_fallback", test_feed_lang_filter_and_fallback),
        ("personalization_v2_react", test_personalization_v2_react),
        ("ai_generate_language", test_ai_generate_language),
        ("auth_login", test_auth_login),
        ("forgot_question", test_forgot_question),
        ("forgot_reset_flow", test_forgot_reset_flow),
        ("security_question_update", test_security_question_update),
        ("checkin", test_checkin),
        ("me_fields", test_me_fields),
        ("preview", test_preview),
        ("subcategories", test_subcategories),
        ("bookmark_and_liked", test_bookmark_and_liked),
    ]
    for name, fn in tests:
        run(name, fn)
    print("\n========== SUMMARY ==========")
    print(f"PASS: {len(PASS)}")
    print(f"FAIL: {len(FAIL)}")
    print(f"WARN: {len(WARN)}")
    for n, e in FAIL:
        print(f"  FAIL {n} -> {e}")
    for n, e in WARN:
        print(f"  WARN {n} -> {e}")
    sys.exit(0 if not FAIL else 1)
