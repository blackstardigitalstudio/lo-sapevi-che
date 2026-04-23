#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

# ================ ITERATION 7 — MULTILINGUE (IT / EN / ES) ================

iteration_7:
  frontend:
    - task: "Multilingual support (IT/EN/ES) with picker"
      implemented: true
      working: true
      file: "frontend/src/lib/i18n.ts (new), frontend/src/lib/locales/{it,en,es}.json (new), frontend/src/components/LanguagePicker.tsx (new), frontend/app/_layout.tsx, frontend/app/auth/{login,register,forgot}.tsx, frontend/app/(tabs)/profile.tsx"
      comment: |
        - i18next + react-i18next + expo-localization integrati.
        - 3 lingue: Italiano, English, Espa\u00f1ol.
        - ~170 stringhe tradotte per ogni lingua (common, language, auth,
          onboarding, tabs, feed, saved, profile, security).
        - LanguagePicker component (variant "compact" per auth screens,
          variant "row" per profile).
        - Auto-detect lingua device al primo avvio via expo-localization.
        - Persistenza scelta in AsyncStorage (@losapevi_lang).
        - Picker visibile in: Login, Register, Profile.
        - Cambio lingua in runtime senza restart.
        - NOTA: i fatti del DB sono in italiano (per scelta dell'utente -
          solo UI tradotta come da richiesta).
  test_results_iter_7:
    - screenshots verified: login EN ("Sign in"), login ES ("Entrar"),
      modal picker con bandiere, checkmark su lingua attiva. Cambio lingua
      istantaneo (no reload).


# ================ ITERATION 6 — UX: PWD visibility + Persistent auth ================

iteration_6:
  frontend:
    - task: "Password visibility toggle (eye icon)"
      implemented: true
      working: true
      file: "frontend/src/components/PasswordInput.tsx (new), login.tsx, register.tsx, forgot.tsx, security.tsx"
      comment: |
        Componente riutilizzabile PasswordInput con occhio-toggle.
        Applicato a tutti e 5 i campi password dell'app.
    - task: "Persistent auth — app rimane loggata"
      implemented: true
      working: true
      file: "frontend/src/context/AuthContext.tsx, frontend/src/lib/api.ts"
      comment: |
        - Aggiunta cache utente AsyncStorage @losapevi_user_v1.
        - Hydrate da cache immediatamente al mount (no flash di login).
        - Distinzione ApiError con status code: logout reale solo su 401 esplicito.
        - Network/server errors (offline, timeout, 5xx) → mantiene user cached.
        - JWT TTL già 30 giorni lato backend (confermato).


# ================ ITERATION 5 — IMAGE RELEVANCE + LAYOUT FIX ================

iteration_5:
  backend:
    - task: "Keyword-based image matching (51 IT keywords)"
      implemented: true
      working: true
      file: "backend/image_library.py"
      comment: |
        Aggiunto KEYWORD_IMAGES con 51 keywords IT (animali, spazio, natura,
        cibo, personaggi storici). image_for_fact() ora usa regex con word
        boundary per matchare keywords nel title/short_fact prima del
        fallback su sub_category/category.
        Fix: "Napoleone" non matcha più "leone" (word boundary).
        Tutte le 221 URL verificate HTTP 200.
        Migration startup applicata su 178 fatti esistenti.
  frontend:
    - task: "Fix layout feed — immagine copre tutta l'altezza"
      implemented: true
      working: true
      file: "frontend/app/(tabs)/feed.tsx"
      comment: |
        Fix conflitto "flex:1 + height:100%" in styles.bg separando in
        container (flex:1) e imageStyle (width:100%, height:100%).
        L'ImageBackground ora copre tutta la card dal top al tab bar,
        nessuno spazio nero residuo.


# ================ ITERATION 4 — CACHE OFFLINE + PREFILL + EXPANSION ================

iteration_4:
  backend:
    - task: "AI background pre-generation scheduler"
      implemented: true
      working: true
      file: "backend/server.py (APScheduler)"
      comment: |
        APScheduler AsyncIOScheduler, ogni 12h, batch=10, cap=1000.
        Selezione categorie least-represented per bilanciamento.
        Avvio su startup (+2min first run). Testato: +22 fatti AI in 2 run.
    - task: "4 new categories + expanded sub-categories"
      implemented: true
      working: true
      file: "backend/seed_facts.py, backend/image_library.py"
      comment: |
        Nuove: Invenzioni/Disastri/Religioni/Misteri. Sub-cat nuove per
        Cucina, Animali. 20 immagini Unsplash (138+20=158) tutte 200 OK.
  frontend:
    - task: "Offline cache + skeleton loader + empty state CTA"
      implemented: true
      working: true
      file: "frontend/app/(tabs)/feed.tsx, src/lib/feedCache.ts, src/components/FeedSkeleton.tsx"
      comment: |
        AsyncStorage cache (ultimi 50 fatti). NetInfo listener auto-refresh.
        Banner offline persistente. FeedSkeleton animato al posto dello
        spinner. Empty state con CTA "Genera con AI".

test_results_iter_4:
  - backend: 36/36 PASSED
  - regression: 17/17 previous security-question tests still pass
  - DB now has 142/1000 facts (scheduler running)


user_problem_statement: |
  Lo Sapevi che? — app Expo + FastAPI + MongoDB di curiosità giornaliere.
  Aggiunta feature: recupero password tramite domanda di sicurezza.

backend:
  - task: "Security question & password reset endpoints"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: |
          Aggiunti: RegisterIn (+ security_question/security_answer obbligatori),
          POST /api/auth/forgot/question, POST /api/auth/forgot/reset,
          POST /api/auth/security-question (auth-only). Risposta normalizzata
          (trim+lowercase+collapse spaces) e hashata con bcrypt. Testato
          end-to-end con script python: register→forgot/question→forgot/reset
          wrong/correct→login new→set-security-question wrong/correct pwd. Tutti PASS.
      - working: true
        agent: "testing"
        comment: |
          Comprehensive backend test suite executed via /app/backend_test.py
          against http://localhost:8001/api. 17/17 tests PASSED.
          Covered:
          - POST /api/auth/register: valid payload → 200 + has_security_question=true; old-format (no Q/A) → 422.
          - POST /api/auth/forgot/question: happy path → 200 with correct question; unknown email → 404;
            pre-migration user (security fields unset directly in Mongo) → 404 with Italian guidance
            ("Nessuna domanda di sicurezza configurata...").
          - POST /api/auth/forgot/reset: wrong answer → 401 ("Risposta di sicurezza errata");
            correct answer with mixed case + extra spaces ("  PLUTO  ") → 200 with token (normalization works);
            login with NEW password → 200, login with OLD password → 401;
            new_password <6 chars → 422.
          - POST /api/auth/security-question: without token → 401; wrong current_password → 401
            ("Password attuale non corretta"); correct → 200 {ok:true}; subsequent forgot/question
            returns the NEW question.
          - Regression: /api/auth/me returns has_security_question boolean; /api/feed?limit=20 returns
            20 facts all with valid image_url; /api/facts/generate (Claude Sonnet 4.5) returned a valid
            generated Italian curiosity for category=Scienza.
          All endpoints working as specified. No major issues found.

  - task: "Image library 404 fixes"
    implemented: true
    working: true
    file: "backend/image_library.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: |
          Verificati 138/138 URL Unsplash che ritornano HTTP 200. Verificati
          78 URL distinti salvati nel DB: tutti mappati alla libreria corrente.

  - task: "4 new categories (Invenzioni/Disastri/Religioni/Misteri) + expanded sub_categories"
    implemented: true
    working: true
    file: "backend/seed_facts.py, backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: |
          Regression test PASSED (36/36) via /app/backend_test.py against
          https://sapevi-che.preview.emergentagent.com/api.
          Verified:
          • GET /api/categories returns exactly 29 categories (was 25).
          • All 4 new categories (Invenzioni, Disastri, Religioni, Misteri)
            present with non-empty subcategories (5, 5, 7, 5 respectively).
          • Cucina now has 5 sub-cats; Animali now has 5 sub-cats.
          • Register user w/ interests=[Invenzioni,Misteri] → /api/feed?limit=20
            returns only those categories, every fact has valid image_url.
          • Sample 5 random image URLs → all HTTP 200.
          • Fresh user w/ interests=[Invenzioni] → feed returns ONLY Invenzioni
            facts (strict category filter working).

  - task: "AI generation for new categories (/api/facts/generate)"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: |
          POST /api/facts/generate {category:"Misteri"} → 200, returned a
          valid Italian AI fact ("Il manoscritto Voynich: il libro che nessuno
          può leggere da..."). Claude Sonnet 4.5 integration works with the
          4 new categories.

  - task: "Background AI prefill scheduler (APScheduler 12h · batch=10 · cap=1000)"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: |
          Verified startup log: "[prefill] scheduler started: every 12h ·
          batch=10 · cap=1000" present in /var/log/supervisor/backend.err.log.
          First run executed at 15:07:03 UTC (next_run_time=startup+2min as
          coded) and added 10 facts across 10 under-represented categories;
          DB total grew from 131 → 141 → 142 during tests.
          GET /api/health reports facts=142 (≥133 regression threshold OK).

  - task: "Regression: register + security-question reset flow + checkin + /auth/me"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: |
          All previously-passing endpoints still PASS. Covered:
          • /auth/register: 422 when security_question/answer missing; 200 with
            has_security_question=true when provided.
          • /auth/forgot/question: 200 happy, 404 unknown email, returns NEW
            question after /auth/security-question update.
          • /auth/forgot/reset: wrong → 401, correct normalized (" PLUTO ")
            → 200 with token; old pwd login → 401, new pwd login → 200.
          • /auth/security-question: 401 w/o token, 401 wrong current_password,
            200 on success.
          • /auth/me: has_security_question bool correct.
          • /auth/checkin: 200, returns streak_days/best_streak/trophies/new_trophies.
          • /health: ok=true, facts=142 (≥133).

frontend:
  - task: "Registration with security question + Forgot password flow"
    implemented: true
    working: true
    file: "frontend/app/auth/register.tsx, frontend/app/auth/forgot.tsx, frontend/app/security.tsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: |
          Register picker (6 preset + custom), Forgot 2-step flow, /security
          screen, Profile row with badge, securityQuestions.ts shared module.
      - working: true
        agent: "testing"
        comment: |
          Full frontend E2E verified via Playwright @ 390x844 (Expo web).
          ALL 4 JOURNEYS PASSED:
          • J1 Registration with preset Q: hint "Serve per recuperare la
            password se la dimentichi." visible with shield icon. All 6
            preset questions rendered correctly in picker modal + "Scrivi
            una domanda personalizzata" option. Default selection is
            preset[0]. Submit → /onboarding → /(tabs)/feed.
          • J2 Registration with CUSTOM question: tapping "Scrivi una
            domanda personalizzata" makes register-question-custom TextInput
            appear. Filled "Il mio colore preferito?" + answer "blu" →
            successful registration → /onboarding.
          • J3 Forgot password flow: "Password dimenticata?" link visible
            and clickable on login → /auth/forgot. Step email → reset:
            correct question displayed ("Qual è il nome del tuo primo
            animale domestico?"). Wrong answer "Sbagliato" → red error
            "Risposta di sicurezza errata". Correct uppercase "PLUTO"
            (normalization test) → "Tutto fatto!" done screen with green
            checkmark + success text "La tua password è stata aggiornata".
            forgot-go-login → /auth/login.
          • J4 Profile → /security: row "Domanda di sicurezza" shown (no
            badge since user already has Q). /security hero shows
            "Aggiorna la tua domanda". Picker works, selecting "Qual è il
            tuo piatto preferito?" updates select text. Submit with answer
            "pizza" + current pwd → save succeeds (verified by subsequent
            forgot/question returning the NEW question "piatto preferito").
          Note: native Alert "Fatto!" was not captured by page.on("dialog")
          — likely rendered as RN-Web modal after the listener was attached,
          but the update itself was confirmed through API side-effect.
          No critical UI issues found at mobile viewport 390x844.

metadata:
  created_by: "main_agent"
  version: "1.1"
  test_sequence: 1
  run_ui: false

test_plan:
  current_focus: []
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

iteration_8_backend_tests:
  - task: "POST /api/auth/language (it|en|es, default it)"
    implemented: true
    working: true
    file: "backend/server.py"
    status_history:
      - working: true
        agent: "testing"
        comment: |
          All cases PASS:
          • Fresh register → user.language defaults to "it", verified via /auth/me.
          • POST /auth/language {"language":"xx"} with valid token → 422 (pattern).
          • POST /auth/language without token → 401.
          • POST /auth/language {"language":"en"} with token → 200 {ok:true, user.language:"en"}.
          • Subsequent /auth/me shows language="en".
  - task: "GET /api/categories?lang= (localized labels, canonical name IT)"
    implemented: true
    working: true
    file: "backend/server.py, backend/i18n.py"
    status_history:
      - working: true
        agent: "testing"
        comment: |
          • /categories (no lang) → 29 items; each has name (canonical IT), label (IT),
            icon, has_subcategories, subcategories.
          • /categories?lang=en → Scienza.label="Science", Storia.label="History",
            Misteri.label="Mysteries" (name still "Scienza", "Storia", "Misteri").
          • /categories?lang=es → Scienza.label="Ciencia", Storia.label="Historia",
            Misteri.label="Misterios". Count still 29.
  - task: "GET /api/trophies?lang= (localized name/desc, requires auth)"
    implemented: true
    working: true
    file: "backend/server.py, backend/i18n.py"
    status_history:
      - working: true
        agent: "testing"
        comment: |
          • Without token → 401.
          • lang=en → first_step.name="First step", desc="Read your first fact.";
            curious.name="Curious". 10 trophies total.
          • lang=es → first_step.name="Primer paso", desc="Lee tu primera curiosidad.".
          • no lang / lang=it → first_step.name="Primo passo".
  - task: "Feed language filter with IT fallback"
    implemented: true
    working: true
    file: "backend/server.py (/api/feed)"
    status_history:
      - working: true
        agent: "testing"
        comment: |
          • User lang=it → /feed?limit=20 returns facts, all with language="it".
          • Switch to lang=en → /feed?limit=20 still returns facts (IT fallback since
            no EN facts seeded), no 500. Every fact has a language field.
          • Switch back to lang=it → feed still non-empty.
  - task: "Personalization v2 — react returns new_weight + new_sub_weight"
    implemented: true
    working: true
    file: "backend/server.py (/api/facts/{id}/react, pick_weighted)"
    status_history:
      - working: true
        agent: "testing"
        comment: |
          • Fresh user with interests=["Scienza","Storia"]; /feed returns ≥2 facts.
          • POST /facts/{id}/react {action:"like"} → 200 with new_weight and
            new_sub_weight (numeric, ≥0.0).
          • POST /facts/{id}/react {action:"dislike"} → 200 with new_sub_weight.
          • Repeated likes + feed calls (3 iterations) do not crash pick_weighted;
            all subsequent /feed requests return 200 with facts.
  - task: "AI fact generation with user language (Spanish)"
    implemented: true
    working: true
    file: "backend/server.py (/api/facts/generate, generate_fact_ai)"
    status_history:
      - working: true
        agent: "testing"
        comment: |
          • User lang=es; POST /facts/generate {"category":"Ciencia"} → 400 (canonical
            IT names enforced, localized input rejected).
          • POST /facts/generate {"category":"Scienza"} → 200 with language="es",
            category="Scienza", title/short_fact/deep_dive present (Claude Sonnet 4.5
            via emergentintegrations, no 503 during testing).
  - task: "Regression: /health, register, login, forgot flow, security-question, checkin, /me, /preview, /subcategories"
    implemented: true
    working: true
    file: "backend/server.py"
    status_history:
      - working: true
        agent: "testing"
        comment: |
          All 10 regression tests PASS on the live preview URL:
          • /health → ok, facts=251 (≥200).
          • /auth/register full payload → 200 with language="it";
            /auth/register without security fields → 422.
          • /auth/login with correct creds → 200 token+user.
          • /auth/forgot/question → 200 happy, 404 unknown email.
          • /auth/forgot/reset wrong answer → 401; correct normalized ("  FIDO  ")
            → 200 token + new_password login works.
          • /auth/security-question → 401 w/o token, 401 wrong pwd, 200 on success.
          • /auth/checkin → 200 with streak_days.
          • /auth/me → has_security_question bool + language field present.
          • /preview → non-empty list with category + image_url.
          • /subcategories/Scienza → 200 with subcategories list;
            /subcategories/NopeCat → 404.

agent_communication:
  - agent: "testing"
    message: |
      === ITERATION 8 — Backend Testing Complete (17/17 PASS) ===
      Target: https://sapevi-che.preview.emergentagent.com/api
      
      NEW FEATURE TESTS:
      ✅ POST /api/auth/language — default "it", 401 w/o token, 422 invalid, 200 valid.
      ✅ GET /api/categories?lang= — 29 items; canonical name IT preserved;
         labels correctly localized (EN: Science/History/Mysteries, ES: Ciencia/
         Historia/Misterios).
      ✅ GET /api/trophies?lang= — requires auth; localized name/desc EN/ES/IT.
      ✅ Feed language filter — IT facts returned for IT user; EN user falls back
         to IT facts (no empty/500). All facts carry a `language` field.
      ✅ Personalization v2 — /facts/{id}/react returns both new_weight and
         new_sub_weight (like +0.25 sub; dislike -0.35 sub). Sequential likes do
         not crash pick_weighted; diversity cap works.
      ✅ AI generation with lang=es — /facts/generate {"Ciencia"} → 400 (canonical
         enforced); {"Scienza"} → 200 Spanish fact saved with language="es"
         (Claude Sonnet 4.5 responded first try).
      
      REGRESSION (all PASS):
      ✅ /health facts=251 ≥200
      ✅ /auth/register (422 without security fields; 200 returns language:"it")
      ✅ /auth/login / forgot/question (200+404) / forgot/reset (401 wrong, 200 
         normalized) / security-question (401/401/200) / checkin / me / preview /
         subcategories.
      
      No critical issues. All 17 backend tests passed on first run.
  - agent: "main"
    message: |
      === ITERATION 8 — Multilingual E2E + Personalization v2 ===
      
      Changes made:
      1. /api/auth/language (POST) — updates user.language (it|en|es)
      2. /api/categories?lang= — returns localized `label` alongside canonical `name`
      3. /api/trophies?lang= — returns localized name/desc
      4. generate_fact_ai(category, language) — prompts Claude in user's language;
         saved fact gets `language` field
      5. Seed facts now store `language: "it"`; migration backfilled 235 legacy facts
      6. /api/feed filters by user.language with fallback to "it" if empty
      7. pick_weighted() now uses sub_interest_weights + diversity cap (max 1/3 of
         feed from same sub_category)
      8. /api/facts/{id}/react updates BOTH interest_weights AND sub_interest_weights
         (like: +0.25 sub, +0.15 cat; dislike: -0.35 sub, -0.20 cat)
      9. Bulk generate now stores language per fact
      10. Index on facts.language added
      
      To test (backend focus):
      - Register user → language defaults to "it"
      - POST /api/auth/language with {"language":"en"} → 200, user.language="en"
      - GET /api/categories?lang=en → `label` localized; `name` canonical (IT)
      - GET /api/trophies?lang=es → `name`, `desc` in Spanish
      - GET /api/feed with user lang=it → returns facts (all 235 are "it" after migration)
      - GET /api/feed with user lang=en → fallback to "it" facts (since DB has none in EN yet)
      - POST /api/facts/{id}/react {action:"like"} → returns new_sub_weight in response
      - POST /api/facts/generate with user lang=es → creates fact with `language: "es"`
         (may fail if litellm is unavailable, treat 503 as acceptable)
      - Regression: /health, /auth/checkin, /auth/me, forgot flow still OK
