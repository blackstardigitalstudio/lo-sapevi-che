"""Backend regression tests for 'Lo Sapevi che?' FastAPI.

Covers:
- Categories endpoint (29 cats, new cats have sub_categories, Cucina/Animali have sub_categories)
- Feed with expanded interests (Invenzioni, Misteri)
- Facts by category (via /api/feed with interests)
- AI generate on new category (Misteri)
- Regressions: /auth/register, /auth/forgot/question, /auth/forgot/reset,
  /auth/security-question, /auth/me, /auth/checkin, /api/health, scheduler log
- Image URL HTTP 200 for 5 random feed facts
"""
import os
import sys
import uuid
import random
import requests

BASE = os.environ.get(
    "BACKEND_URL",
    "https://sapevi-che.preview.emergentagent.com"
) + "/api"

PASS = []
FAIL = []


def record(name: str, ok: bool, detail: str = ""):
    if ok:
        PASS.append(name)
        print(f"PASS  {name}  {detail}")
    else:
        FAIL.append(f"{name} :: {detail}")
        print(f"FAIL  {name}  {detail}")


def req(method, path, **kw):
    url = BASE + path
    try:
        r = requests.request(method, url, timeout=60, **kw)
    except Exception as e:
        return None, None, str(e)
    try:
        j = r.json()
    except Exception:
        j = None
    return r.status_code, j, None


# -----------------------------------------------------------
# 1. Categories endpoint
# -----------------------------------------------------------
def test_categories():
    code, body, err = req("GET", "/categories")
    if err or code != 200 or not isinstance(body, list):
        record("categories_endpoint_200", False, f"code={code} err={err}")
        return
    record("categories_endpoint_200", True, f"n={len(body)}")
    record("categories_count_29", len(body) == 29, f"got {len(body)}")

    names = [c.get("name") for c in body]
    for req_cat in ["Invenzioni", "Disastri", "Religioni", "Misteri"]:
        record(f"new_category_present:{req_cat}", req_cat in names)

    sub_map = {c["name"]: c.get("subcategories") or [] for c in body}
    for cat in ["Invenzioni", "Disastri", "Religioni", "Misteri", "Cucina", "Animali"]:
        subs = sub_map.get(cat) or []
        record(f"sub_categories_non_empty:{cat}", len(subs) > 0, f"subs={len(subs)}")


# -----------------------------------------------------------
# 2 + 6. Feed with expanded interests + Image URL checks
# -----------------------------------------------------------
def test_feed_and_images():
    email = f"marco.rossi+{uuid.uuid4().hex[:8]}@losapevi.app"
    payload = {
        "email": email,
        "password": "Cur!osita2026",
        "name": "Marco Rossi",
        "interests": ["Invenzioni", "Misteri"],
        "security_question": "Qual è il nome del tuo primo animale domestico?",
        "security_answer": "pluto",
    }
    code, body, err = req("POST", "/auth/register", json=payload)
    if code != 200 or not body or "token" not in body:
        record("register_new_interests", False, f"code={code} body={body}")
        return None
    token = body["token"]
    record("register_new_interests", True,
           f"has_sq={body['user'].get('has_security_question')}")

    headers = {"Authorization": f"Bearer {token}"}

    code, body, err = req("GET", "/feed?limit=20", headers=headers)
    if code != 200 or not body or "facts" not in body:
        record("feed_new_interests_200", False, f"code={code} body={body}")
        return token
    facts = body["facts"]
    record("feed_new_interests_200", True, f"n={len(facts)}")
    record("feed_non_empty", len(facts) > 0, f"n={len(facts)}")

    cats_returned = {f.get("category") for f in facts}
    record("feed_strict_category_filter",
           cats_returned.issubset({"Invenzioni", "Misteri"}),
           f"cats={cats_returned}")

    all_have_img = all(
        isinstance(f.get("image_url"), str) and f["image_url"].startswith("http")
        for f in facts
    )
    record("feed_all_have_image_url", all_have_img)

    # 5 random image URLs return HTTP 200
    sample = random.sample(facts, min(5, len(facts)))
    ok_count = 0
    for f in sample:
        try:
            r = requests.head(f["image_url"], timeout=20, allow_redirects=True)
            if r.status_code == 200:
                ok_count += 1
            else:
                r2 = requests.get(f["image_url"], timeout=20, stream=True)
                if r2.status_code == 200:
                    ok_count += 1
        except Exception:
            pass
    record("image_urls_http_200_sample5",
           ok_count == len(sample), f"{ok_count}/{len(sample)} ok")

    # 3. Feed filtered by single new category
    email2 = f"giulia.bianchi+{uuid.uuid4().hex[:8]}@losapevi.app"
    p2 = {**payload, "email": email2, "interests": ["Invenzioni"]}
    code, b2, _ = req("POST", "/auth/register", json=p2)
    if code == 200:
        h2 = {"Authorization": f"Bearer {b2['token']}"}
        code, body2, _ = req("GET", "/feed?limit=5", headers=h2)
        if code == 200 and body2.get("facts"):
            cats2 = {f["category"] for f in body2["facts"]}
            record("feed_facts_by_category_Invenzioni",
                   cats2 == {"Invenzioni"},
                   f"cats={cats2} n={len(body2['facts'])}")
        else:
            record("feed_facts_by_category_Invenzioni", False,
                   f"code={code} body={body2}")
    else:
        record("feed_facts_by_category_Invenzioni", False, f"register code={code}")

    return token


# -----------------------------------------------------------
# 4. AI generate on new category
# -----------------------------------------------------------
def test_ai_generate(token):
    headers = {"Authorization": f"Bearer {token}"}
    code, body, err = req("POST", "/facts/generate",
                          headers=headers, json={"category": "Misteri"})
    if code != 200 or not body:
        record("ai_generate_Misteri", False, f"code={code} body={body} err={err}")
        return
    ok = (
        body.get("category") == "Misteri"
        and isinstance(body.get("title"), str) and body["title"]
        and isinstance(body.get("short_fact"), str)
        and isinstance(body.get("deep_dive"), str)
    )
    record("ai_generate_Misteri", ok, f"title={body.get('title', '')[:60]}")


# -----------------------------------------------------------
# 5. Regression
# -----------------------------------------------------------
def test_regression():
    bad = {
        "email": f"noq+{uuid.uuid4().hex[:6]}@losapevi.app",
        "password": "Cur!osita2026",
        "name": "No Question",
        "interests": ["Scienza"],
    }
    code, _, _ = req("POST", "/auth/register", json=bad)
    record("register_requires_sq_422", code == 422, f"code={code}")

    email = f"lucia.verdi+{uuid.uuid4().hex[:8]}@losapevi.app"
    reg = {
        "email": email,
        "password": "Cur!osita2026",
        "name": "Lucia Verdi",
        "interests": ["Storia", "Arte"],
        "security_question": "Qual è il nome del tuo primo animale domestico?",
        "security_answer": "Pluto",
    }
    code, body, _ = req("POST", "/auth/register", json=reg)
    if code != 200:
        record("reg_regression_flow", False, f"register code={code}")
        return
    token = body["token"]

    code, me, _ = req("GET", "/auth/me",
                      headers={"Authorization": f"Bearer {token}"})
    record("auth_me_has_sq_bool",
           code == 200 and me and me.get("has_security_question") is True,
           f"code={code} sq={me.get('has_security_question') if me else None}")

    code, body, _ = req("POST", "/auth/forgot/question", json={"email": email})
    record("forgot_question_ok",
           code == 200 and body and body.get("security_question"),
           f"code={code}")

    code, _, _ = req("POST", "/auth/forgot/question",
                     json={"email": f"missing+{uuid.uuid4().hex[:6]}@x.it"})
    record("forgot_question_unknown_404", code == 404, f"code={code}")

    code, _, _ = req("POST", "/auth/forgot/reset",
                     json={"email": email, "security_answer": "sbagliato",
                           "new_password": "NewPass!2026"})
    record("forgot_reset_wrong_401", code == 401, f"code={code}")

    code, body, _ = req("POST", "/auth/forgot/reset",
                        json={"email": email, "security_answer": "  PLUTO  ",
                              "new_password": "NewPass!2026"})
    record("forgot_reset_correct_normalized",
           code == 200 and body and body.get("token"),
           f"code={code}")

    code, _, _ = req("POST", "/auth/login",
                     json={"email": email, "password": "Cur!osita2026"})
    record("login_old_pwd_fails", code == 401, f"code={code}")

    code, body, _ = req("POST", "/auth/login",
                        json={"email": email, "password": "NewPass!2026"})
    record("login_new_pwd_ok",
           code == 200 and body and body.get("token"), f"code={code}")
    login_token = body.get("token") if code == 200 and body else None

    code, _, _ = req("POST", "/auth/security-question",
                     json={"security_question": "Il tuo colore preferito?",
                           "security_answer": "blu",
                           "current_password": "NewPass!2026"},
                     headers={"Authorization": f"Bearer {login_token}"})
    record("set_security_question_ok", code == 200, f"code={code}")

    code, _, _ = req("POST", "/auth/security-question",
                     json={"security_question": "Altro?",
                           "security_answer": "x",
                           "current_password": "WRONG!!"},
                     headers={"Authorization": f"Bearer {login_token}"})
    record("set_sq_wrong_current_pwd_401", code == 401, f"code={code}")

    code, _, _ = req("POST", "/auth/security-question",
                     json={"security_question": "a?", "security_answer": "b",
                           "current_password": "x"})
    record("set_sq_no_token_401", code == 401, f"code={code}")

    code, body, _ = req("POST", "/auth/forgot/question", json={"email": email})
    record("forgot_question_returns_new_question",
           code == 200 and body and body.get("security_question") == "Il tuo colore preferito?",
           f"q={body.get('security_question') if body else None}")

    code, body, _ = req("POST", "/auth/checkin",
                        headers={"Authorization": f"Bearer {login_token}"})
    ok = (code == 200 and body and "streak_days" in body
          and "best_streak" in body and "trophies" in body
          and "new_trophies" in body)
    record("auth_checkin_ok", ok,
           f"code={code} streak={body.get('streak_days') if body else None}")

    code, body, _ = req("GET", "/health")
    facts_n = body.get("facts") if body else 0
    record("health_ok", code == 200 and body and body.get("ok") is True,
           f"code={code}")
    record("health_facts_count_ge_133", facts_n >= 133, f"facts={facts_n}")


# -----------------------------------------------------------
# 7. Scheduler startup log
# -----------------------------------------------------------
def test_scheduler_log():
    import subprocess
    try:
        out = subprocess.check_output(
            "grep -h 'scheduler started' /var/log/supervisor/backend.*.log | tail -1",
            shell=True, stderr=subprocess.STDOUT
        ).decode()
    except Exception as e:
        out = str(e)
    ok = ("scheduler started: every 12h" in out
          and "batch=10" in out and "cap=1000" in out)
    record("scheduler_startup_log_present", ok, out.strip()[:200])


if __name__ == "__main__":
    print(f"Backend: {BASE}")
    test_categories()
    token = test_feed_and_images()
    if token:
        test_ai_generate(token)
    else:
        record("ai_generate_Misteri", False, "no token from feed step")
    test_regression()
    test_scheduler_log()

    print("\n" + "=" * 60)
    print(f"PASS: {len(PASS)}    FAIL: {len(FAIL)}")
    if FAIL:
        print("\nFailures:")
        for f in FAIL:
            print(" - " + f)
        sys.exit(1)
    sys.exit(0)
