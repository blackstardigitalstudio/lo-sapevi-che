"""Backend test suite for Lo Sapevi che? - password recovery via security question.

Tests endpoints at http://localhost:8001/api:
- POST /api/auth/register (with security question/answer)
- POST /api/auth/forgot/question
- POST /api/auth/forgot/reset
- POST /api/auth/security-question
- Regression: /api/auth/login, /api/auth/me, /api/feed, /api/facts/generate
"""
import uuid
import json
import sys
import requests

BASE = "http://localhost:8001/api"

results = []


def rec(name, ok, detail=""):
    tag = "PASS" if ok else "FAIL"
    line = f"[{tag}] {name}" + (f" — {detail}" if detail else "")
    print(line)
    results.append((name, ok, detail))


def unique_email(tag="test"):
    return f"{tag}-{uuid.uuid4().hex[:10]}@example.com"


def test_all():
    # ---- 1. REGISTER with security question ----
    email = unique_email("maria")
    password = "Segreto123!"
    payload = {
        "email": email,
        "password": password,
        "name": "Maria Rossi",
        "interests": ["Scienza", "Spazio"],
        "security_question": "Qual è il nome del tuo primo animale domestico?",
        "security_answer": "Pluto",
    }
    r = requests.post(f"{BASE}/auth/register", json=payload, timeout=30)
    ok = r.status_code == 200
    body = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
    user_obj = body.get("user", {})
    rec(
        "register — valid payload with security question returns 200 + has_security_question=true",
        ok and user_obj.get("has_security_question") is True,
        f"status={r.status_code} has_security_question={user_obj.get('has_security_question')} body={body if not ok else ''}",
    )
    token = body.get("token", "")

    # ---- 1b. REGISTER old-format (missing security fields) returns 422 ----
    old_payload = {
        "email": unique_email("oldformat"),
        "password": password,
        "name": "Old Format",
        "interests": ["Scienza"],
    }
    r2 = requests.post(f"{BASE}/auth/register", json=old_payload, timeout=15)
    rec(
        "register — old-format payload (no security Q/A) returns 422",
        r2.status_code == 422,
        f"status={r2.status_code}",
    )

    # ---- 2. FORGOT QUESTION ----
    # 2a. happy path
    r = requests.post(f"{BASE}/auth/forgot/question", json={"email": email}, timeout=15)
    ok = r.status_code == 200 and r.json().get("security_question") == payload["security_question"]
    rec(
        "forgot/question — existing user with question returns 200 + correct question",
        ok,
        f"status={r.status_code} body={r.text[:200]}",
    )

    # 2b. unknown email → 404
    r = requests.post(f"{BASE}/auth/forgot/question", json={"email": unique_email("ghost")}, timeout=15)
    rec(
        "forgot/question — unknown email returns 404",
        r.status_code == 404,
        f"status={r.status_code} body={r.text[:200]}",
    )

    # 2c. pre-migration user without question → create one manually via Mongo
    # We'll simulate by creating a user via register, then unsetting security_question via direct mongo access.
    # Since we can't hit Mongo directly from test easily, we use a different tactic: unknown email already covers the 404 path.
    # But the spec requires testing a user that exists but has no question. Do via pymongo.
    try:
        import os
        from pymongo import MongoClient
        from dotenv import load_dotenv
        load_dotenv("/app/backend/.env")
        mc = MongoClient(os.environ["MONGO_URL"])
        dbname = os.environ["DB_NAME"]
        mdb = mc[dbname]
        # Pick a user and remove security fields, then put them back
        legacy_email = unique_email("legacy")
        # Insert a pre-migration-like user via register first
        reg_payload = {
            "email": legacy_email,
            "password": password,
            "name": "Legacy User",
            "interests": [],
            "security_question": "placeholder",
            "security_answer": "x",
        }
        rr = requests.post(f"{BASE}/auth/register", json=reg_payload, timeout=15)
        assert rr.status_code == 200, f"setup register failed: {rr.text}"
        # Simulate legacy: drop security fields
        mdb.users.update_one(
            {"email": legacy_email},
            {"$unset": {"security_question": "", "security_answer_hash": ""}},
        )
        rq = requests.post(f"{BASE}/auth/forgot/question", json={"email": legacy_email}, timeout=15)
        msg_ok = "domanda" in rq.text.lower() or "configurata" in rq.text.lower()
        rec(
            "forgot/question — user without security question returns 404 with Italian guidance message",
            rq.status_code == 404 and msg_ok,
            f"status={rq.status_code} body={rq.text[:250]}",
        )
    except Exception as e:
        rec("forgot/question — legacy user scenario", False, f"setup error: {e}")

    # ---- 3. FORGOT RESET ----
    # 3a. wrong answer → 401
    r = requests.post(
        f"{BASE}/auth/forgot/reset",
        json={"email": email, "security_answer": "Fido", "new_password": "NuovaPwd1!"},
        timeout=15,
    )
    rec(
        "forgot/reset — wrong answer returns 401",
        r.status_code == 401,
        f"status={r.status_code} body={r.text[:200]}",
    )

    # 3b. correct answer w/ case/space normalization → 200 with token
    new_password = "NuovaPwd1!"
    r = requests.post(
        f"{BASE}/auth/forgot/reset",
        json={"email": email, "security_answer": "  PLUTO  ", "new_password": new_password},
        timeout=15,
    )
    rok = r.status_code == 200
    body = r.json() if rok else {}
    rec(
        "forgot/reset — correct answer with normalization (mixed case + spaces) returns 200 + token",
        rok and bool(body.get("token")),
        f"status={r.status_code} has_token={bool(body.get('token'))} body={r.text[:200] if not rok else ''}",
    )

    # 3c. login with NEW password works
    rnew = requests.post(f"{BASE}/auth/login", json={"email": email, "password": new_password}, timeout=15)
    rec(
        "login — with NEW password after reset returns 200",
        rnew.status_code == 200,
        f"status={rnew.status_code} body={rnew.text[:200]}",
    )

    # 3d. login with OLD password fails 401
    rold = requests.post(f"{BASE}/auth/login", json={"email": email, "password": password}, timeout=15)
    rec(
        "login — with OLD password after reset returns 401",
        rold.status_code == 401,
        f"status={rold.status_code}",
    )

    # 3e. new password too short → 422
    r = requests.post(
        f"{BASE}/auth/forgot/reset",
        json={"email": email, "security_answer": "pluto", "new_password": "abc"},
        timeout=15,
    )
    rec(
        "forgot/reset — new_password too short (<6 chars) returns 422",
        r.status_code == 422,
        f"status={r.status_code}",
    )

    # ---- 4. SET SECURITY QUESTION (auth required) ----
    # First, relogin to get fresh token (though current one still valid)
    rlogin = requests.post(f"{BASE}/auth/login", json={"email": email, "password": new_password}, timeout=15)
    assert rlogin.status_code == 200, "relogin failed"
    token = rlogin.json()["token"]

    # 4a. without token → 401
    r = requests.post(
        f"{BASE}/auth/security-question",
        json={
            "security_question": "Qual è il tuo cibo preferito?",
            "security_answer": "Pizza",
            "current_password": new_password,
        },
        timeout=15,
    )
    rec(
        "security-question — without auth token returns 401",
        r.status_code == 401,
        f"status={r.status_code}",
    )

    # 4b. wrong current_password → 401
    r = requests.post(
        f"{BASE}/auth/security-question",
        json={
            "security_question": "Qual è il tuo cibo preferito?",
            "security_answer": "Pizza",
            "current_password": "wrongpass",
        },
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    ok = r.status_code == 401 and "password attuale" in r.text.lower()
    rec(
        "security-question — wrong current_password returns 401 'Password attuale non corretta'",
        ok,
        f"status={r.status_code} body={r.text[:200]}",
    )

    # 4c. correct current_password → 200 {ok: true}
    new_question = "Qual è il tuo cibo preferito?"
    r = requests.post(
        f"{BASE}/auth/security-question",
        json={
            "security_question": new_question,
            "security_answer": "Pizza",
            "current_password": new_password,
        },
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    ok = r.status_code == 200 and r.json().get("ok") is True
    rec(
        "security-question — correct current_password returns 200 {ok:true}",
        ok,
        f"status={r.status_code} body={r.text[:200]}",
    )

    # 4d. forgot/question now returns the NEW question
    r = requests.post(f"{BASE}/auth/forgot/question", json={"email": email}, timeout=15)
    ok = r.status_code == 200 and r.json().get("security_question") == new_question
    rec(
        "forgot/question — after update returns the NEW question",
        ok,
        f"status={r.status_code} body={r.text[:200]}",
    )

    # ---- REGRESSION ----
    # /api/auth/me with has_security_question
    r = requests.get(f"{BASE}/auth/me", headers={"Authorization": f"Bearer {token}"}, timeout=15)
    ok = r.status_code == 200 and "has_security_question" in r.json() and isinstance(r.json()["has_security_question"], bool)
    rec(
        "auth/me — returns 200 and includes has_security_question boolean",
        ok,
        f"status={r.status_code} has_security_question={r.json().get('has_security_question') if r.status_code==200 else 'N/A'}",
    )

    # /api/feed
    r = requests.get(f"{BASE}/feed?limit=20", headers={"Authorization": f"Bearer {token}"}, timeout=30)
    if r.status_code == 200:
        facts = r.json().get("facts", [])
        all_have_image = all(f.get("image_url", "").startswith("http") for f in facts) if facts else False
        rec(
            "feed?limit=20 — returns 200 with facts having valid image_url",
            bool(facts) and all_have_image,
            f"count={len(facts)} all_have_image={all_have_image}",
        )
    else:
        rec("feed?limit=20 — returns 200", False, f"status={r.status_code} body={r.text[:200]}")

    # /api/facts/generate — Claude AI
    try:
        r = requests.post(
            f"{BASE}/facts/generate",
            json={"category": "Scienza"},
            headers={"Authorization": f"Bearer {token}"},
            timeout=60,
        )
        ok = r.status_code == 200
        detail = ""
        if ok:
            body = r.json()
            detail = f"title='{body.get('title','')[:80]}' category={body.get('category')}"
        else:
            detail = f"status={r.status_code} body={r.text[:300]}"
        rec("facts/generate — Claude AI returns 200 with generated fact", ok, detail)
    except requests.Timeout:
        rec("facts/generate — Claude AI", False, "timeout after 60s")
    except Exception as e:
        rec("facts/generate — Claude AI", False, f"exception: {e}")

    # ---- SUMMARY ----
    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    print(f"\n======= RESULTS: {passed}/{total} passed =======")
    for name, ok, detail in results:
        if not ok:
            print(f"  FAIL: {name} — {detail}")
    return passed == total


if __name__ == "__main__":
    success = test_all()
    sys.exit(0 if success else 1)
