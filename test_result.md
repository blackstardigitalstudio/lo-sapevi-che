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

# ================ ITERATION 8 — MULTILINGUE BACKEND + PERSONALIZATION v2 + REFACTOR ================

iteration_8:
  backend:
    - task: "Multilingual backend content (language, categories?lang, trophies?lang)"
      implemented: true
      working: true
      file: "backend/i18n.py (new), backend/server.py, backend/models.py, backend/deps.py, backend/services.py"
      stuck_count: 0
      priority: "high"
      needs_retesting: false
      status_history:
        - working: true
          agent: "main"
          comment: |
            - Added POST /api/auth/language {it|en|es} — updates user.language.
            - GET /api/categories?lang= returns canonical `name` + localized `label`.
            - GET /api/trophies?lang= returns localized name/desc.
            - generate_fact_ai(category, language) — Claude Sonnet 4.5 prompted in
              user lang; saved facts get `language` field.
            - Legacy migration: 235 facts backfilled language="it".
            - Added idx on facts.language.
        - working: true
          agent: "testing"
          comment: |
            18/18 backend tests PASSED. Language endpoints working, categories/trophies
            localization correct in EN/ES/IT, Claude generated a valid Spanish fact
            for category=Scienza with language:"es".
    - task: "Feed language filter with fallback"
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
            /feed filters by user.language. 3-tier fallback: 1) exclude seen+disliked;
            2) allow seen within same lang; 3) non-IT users fall back to IT facts
            if no content in their language yet.
        - working: true
          agent: "testing"
          comment: |
            Verified feed returns IT facts for lang=it; for lang=en (no EN facts yet)
            falls back to IT without 500 error. All returned facts carry language field.
    - task: "Personalization v2 — sub_interest_weights + diversity cap"
      implemented: true
      working: true
      file: "backend/services.py (pick_weighted), backend/server.py (/facts/{id}/react)"
      stuck_count: 0
      priority: "medium"
      needs_retesting: false
      status_history:
        - working: true
          agent: "main"
          comment: |
            react endpoint now updates BOTH interest_weights AND sub_interest_weights:
            like→+0.15 cat +0.25 sub; dislike→-0.20 cat -0.35 sub.
            pick_weighted() scores each fact via base category weight + sub boost +
            jitter, then applies diversity cap (max n//3 from same sub_category).
        - working: true
          agent: "testing"
          comment: |
            /react returns {ok, new_weight, new_sub_weight, new_trophies}. Sequential
            likes/dislikes don't crash feed. Sub-category bonuses reflected in pick_weighted.
    - task: "Refactor server.py into models/deps/services modules"
      implemented: true
      working: true
      file: "backend/models.py (new), backend/deps.py (new), backend/services.py (new), backend/server.py (trimmed from 1055→647 lines)"
      stuck_count: 0
      priority: "medium"
      needs_retesting: false
      status_history:
        - working: true
          agent: "main"
          comment: |
            Split monolithic server.py into:
            - models.py (62 lines): all Pydantic schemas
            - deps.py (83 lines): DB client, hash/verify pwd, JWT create/decode, current_user
            - services.py (275 lines): TROPHIES, compute/update trophies,
              generate_fact_ai, prefill scheduler, pick_weighted
            - server.py (647 lines): FastAPI app + routes + startup/shutdown only
        - working: true
          agent: "testing"
          comment: |
            Regression suite 18/18 PASSED post-refactor. No behavior change.
  frontend:
    - task: "Frontend wiring for localized backend data (categories/trophies)"
      implemented: true
      working: true
      file: "frontend/src/lib/api.ts, frontend/src/components/LanguagePicker.tsx, frontend/app/onboarding.tsx, frontend/app/(tabs)/profile.tsx"
      stuck_count: 0
      priority: "high"
      needs_retesting: false
      status_history:
        - working: true
          agent: "main"
          comment: |
            - api.categories(lang) / api.trophies(lang) / api.setLanguage(lang) added.
            - LanguagePicker now POSTs /api/auth/language on change (if authenticated).
            - Onboarding fetches categories with current i18n.language.
            - Profile fetches trophies with current i18n.language and refetches when
              user changes language (added i18n.language to useFocusEffect deps).
            - Fixed duplicate ghostBtn style in profile.tsx (was causing tsc error).
        - working: true
          agent: "testing"
          comment: |
            E2E verified at 390x844: language picker works on login/register/profile;
            UI labels localize in EN/ES; persistent auth keeps user signed in across
            reloads; feed loads facts in the user language with fallback. After fix,
            trophy names also localize correctly (were Italian before the i18n.language
            dep was added to useFocusEffect).


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

iteration_10_frontend_tests:
  - task: "Profile screen full localization (EN)"
    implemented: true
    working: true
    file: "frontend/app/(tabs)/profile.tsx, frontend/src/lib/locales/en.json"
    status_history:
      - working: true
        agent: "testing"
        comment: |
          Verified @ 390x844 with test@test.com/test123 after switching language
          to English via Profile > Language row picker.
          VISUAL CONFIRMATION (screenshot captured):
          • Section title "DAILY NOTIFICATIONS" (uppercased t('profile.dailyNotifications'))
            — NOT "Notifiche giornaliere" ✓
          • Summary line: "4 per day · random times · 0 scheduled" ✓
          • Section "TIME WINDOW (RANDOM TIMES EACH DAY)" ✓
          • Window buttons all in English:
            - "Morning 7-10" ✓
            - "Afternoon 12-16" ✓
            - "Evening 18-22" ✓
            - "Surprise 8-22" ✓
          • Test button: "Test (3 sec)" — NOT "Prova (3 sec)" ✓
          • Account rows: "Edit interests", "Set security question", "Language",
            "Log out" all EN ✓
          • Language row shows "English" with UK flag ✓
          • Footer "Lo Sapevi che? · v1.0" correct ✓
          • Tab bar: "Discover / Saved / Profile" ✓
          • Section titles "TOP INTERESTS" and "TROPHIES" (not TROFEI) ✓
          ZERO Italian leaks detected in EN profile view.
  - task: "Feed UI chrome localization (EN)"
    implemented: true
    working: true
    file: "frontend/app/(tabs)/feed.tsx, frontend/src/lib/locales/en.json"
    status_history:
      - working: true
        agent: "testing"
        comment: |
          Visual screenshot of feed in EN mode shows:
          • Kicker "DID YOU KNOW..." (feed.didYouKnow) — NOT "Lo sapevi che…" ✓
          • CTA button "Learn more →" (feed.learnMore) — NOT "Approfondisci" ✓
          • Tabs "Discover / Saved / Profile" ✓
          NOTE: Fact CONTENT (title + short_fact body) remains Italian because the
          DB contains only Italian facts; EN users are served IT content via the
          documented 3-tier backend fallback. This is expected behavior
          (iteration_8 backend tests) and not a localization bug.
  - task: "Trophy modal + Detail screen translations (keys present)"
    implemented: true
    working: true
    file: "frontend/src/lib/locales/{en,es,it}.json"
    status_history:
      - working: true
        agent: "testing"
        comment: |
          Source-verified translation keys:
          • trophy.unlocked: IT="TROFEO SBLOCCATO", EN="TROPHY UNLOCKED",
            ES="TROFEO DESBLOQUEADO" ✓
          • common.continue: IT="Continua", EN="Continue", ES="Continuar" ✓
          • detail.deepDive: IT="APPROFONDIMENTO", EN="DEEP DIVE" ✓
          • detail.sources: IT="FONTI", EN="SOURCES" ✓
          • detail.like: EN="Like"; detail.liked: EN="Liked" ✓
          • feed.didYouKnow: EN="Did you know..." ✓
          All strings present in all 3 locale files with proper translations.
          Could not force a trophy modal in the live automation run to visually
          confirm the modal text, but translation keys are wired and previous
          iterations confirmed t() resolves correctly on language change.
  - task: "ES / IT locale regression"
    implemented: true
    working: true
    file: "frontend/src/lib/locales/es.json, frontend/src/lib/locales/it.json"
    status_history:
      - working: true
        agent: "testing"
        comment: |
          es.json & it.json contain full parallel keys for:
          profile.dailyNotifications, profile.perDaySummary, profile.timeWindow,
          profile.morningLabel, profile.afternoonLabel, profile.eveningLabel,
          profile.surpriseLabel, profile.nextNotif, profile.testPush,
          profile.footer, profile.editInterests, profile.setSecurityQuestion,
          profile.language, profile.logout, detail.deepDive, detail.sources,
          detail.like, detail.liked, feed.didYouKnow, feed.learnMore,
          trophy.unlocked, common.continue. No missing keys.
          LanguagePicker (row variant) modal dismiss interaction via Playwright
          had a selector timing issue for the "ES" option in the modal overlay
          (30s timeout); manual inspection of es.json confirms all strings are
          translated correctly. Per iteration_8 frontend tests, ES labels were
          observed live ("Perfil", "Curiosidades leídas", "TROFEOS", etc.).

agent_communication:
  - agent: "testing"
    message: |
      === ITERATION 10 — Full App Localization E2E ===
      Target: https://sapevi-che.preview.emergentagent.com/ @ 390x844
      User: test@test.com / test123

      CRITICAL RESULTS:
      ✅ Profile screen in EN — 100% English, ZERO Italian leaks.
         Verified visually: DAILY NOTIFICATIONS, "4 per day · random times · 0
         scheduled", TIME WINDOW, Morning/Afternoon/Evening/Surprise buttons,
         "Test (3 sec)", "Lo Sapevi che? · v1.0" footer, Edit interests / Set
         security question / Language / Log out, TOP INTERESTS, TROPHIES.
      ✅ Feed UI chrome in EN — "DID YOU KNOW...", "Learn more →", tabs
         Discover/Saved/Profile. No Italian UI strings.
      ✅ Translation keys for Trophy modal (TROPHY UNLOCKED/TROFEO DESBLOQUEADO/
         Continue/Continuar) and Detail screen (DEEP DIVE/SOURCES/Like/Liked)
         present and correctly wired in en.json/es.json/it.json.
      ✅ Language switching (Profile → modal picker) working — IT ↔ EN tested.

      NOT A BUG (expected behavior):
      • Fact CONTENT (titles, bodies, deep_dive) shown in Italian when UI is
        EN/ES — DB only has IT facts; backend falls back to IT per the
        documented 3-tier feed strategy (iteration_8 backend).

      MINOR (non-blocking):
      • Playwright ES picker click in the Profile language modal timed out
        once (locator-scoping issue) but ES translation keys are fully
        populated in es.json and live-verified in iteration_8.
      • Test (3 sec) alert was not captured by dialog handler — RN-Web renders
        Alert.alert as an in-DOM modal rather than a native dialog; the button
        itself is rendered with EN label.

      OVERALL: Iteration 10 full localization is COMPLETE for Profile and feed
      chrome. No critical Italian leaks in EN mode. Ready for production.

iteration_9_frontend_tests:
  - task: "Trophy names localization on Profile (FIX verified)"
    implemented: true
    working: true
    file: "frontend/app/(tabs)/profile.tsx"
    status_history:
      - working: true
        agent: "testing"
        comment: |
          CRITICAL BUG FROM ITERATION 8 IS FIXED.
          Verified @ 390x844 with user testlang_ziwdw8@example.com/Pass1234:
          • profile.tsx line 53 now calls `api.trophies(i18n.language)` with
            i18n.language dependency in useFocusEffect (line 55).
          • Switching to English → Profile shows "First step", "Curious" (EN).
          • Switching to Español → Profile shows "Primer paso", "Curioso" (ES)
            and "Perfil".
          • Switching back to Italiano → "Primo passo", "Curioso" (IT).
          • No Italian leak in EN view (checked: "Primo passo" NOT present
            when lang=en).
          • POST /api/auth/language observed 3 times during language cycling
            (backend sync working).
  - task: "Language switch persistent across navigations"
    implemented: true
    working: true
    file: "frontend/src/components/LanguagePicker.tsx"
    status_history:
      - working: true
        agent: "testing"
        comment: |
          lang-picker-row (profile) and lang-picker-compact (auth screens) both
          POST /api/auth/language on change when authenticated. Auth context
          update + i18n.changeLanguage + AsyncStorage persist all working.
  - task: "Onboarding EN localization (regression from IT-only labels)"
    implemented: true
    working: true
    file: "frontend/app/onboarding.tsx, frontend/src/lib/i18n.ts, frontend/src/lib/locales/en.json"
    status_history:
      - working: true
        agent: "testing"
        comment: |
          Registered fresh user in EN locale. Onboarding screen renders 100%
          in English (screenshot captured):
          • Title: "What fascinates you?" (NOT "Cosa ti affascina?")
          • Subtitle: "Pick at least 3 niches. For some you can also choose
            brands or sub-topics." (NOT "Scegli almeno 3 nicchie...")
          • Footer counter: "3 niches selected" (NOT "3 nicchie selezionate")
          • CTA: "Start the adventure" (NOT "Inizia l'avventura")
          • Greeting: "Hi FeedUser 👋" (NOT "Ciao")
          Category labels come from /api/categories?lang=en (Science, History,
          Mysteries, Animals) — confirmed backend returns them and onboarding
          passes i18n.language via api.categories(i18n.language).
          "Refine your taste" / "with filters" / "All" come from i18n keys
          (en.json lines 86-90) and are correctly pulled via t().
  - task: "Stable testIDs feed-like / feed-dislike / feed-bookmark / feed-share on top card"
    implemented: true
    working: true
    file: "frontend/app/(tabs)/feed.tsx (lines 418, 429, 436, 447)"
    status_history:
      - working: true
        agent: "testing"
        comment: |
          Code inspection confirms the fix:
          • Line 418: testID={isActive ? "feed-like" : `like-${fact.id}`}
          • Line 429: testID={isActive ? "feed-dislike" : `dislike-${fact.id}`}
          • Line 436: testID={isActive ? "feed-bookmark" : `bookmark-${fact.id}`}
          • Line 447: testID={isActive ? "feed-share" : `share-${fact.id}`}
          Logic is correct: only the top/visible card carries the stable
          feed-* testID; scrolled-past/future cards keep dynamic id-scoped
          testIDs. This matches the review spec.
          NOTE: End-to-end click verification was partially blocked by the
          onboarding drill-down modal covering the onb-start button during
          Playwright scripting (the fresh user flow needs to complete a
          drill-down for categories with sub-cats before the footer CTA is
          clickable). Manual verification of active tint on click is covered
          by the existing icon-color logic in FactCard (iconColor = liked
          ? theme.primary : "#fff"). /facts/react and /facts/bookmark
          endpoints (backend) were fully verified in iteration_8.
  - task: "Feed language filter — no crash on lang switch"
    implemented: true
    working: true
    file: "frontend/app/(tabs)/feed.tsx"
    status_history:
      - working: true
        agent: "testing"
        comment: |
          Feed loads in both IT and EN (IT fallback used when no EN facts
          seeded). No JS crashes observed during language cycling. Backend
          /api/feed returns non-empty results for both langs (verified in
          iteration_8 backend tests).
  - task: "Persistent auth on reload"
    implemented: true
    working: true
    file: "frontend/src/context/AuthContext.tsx"
    status_history:
      - working: true
        agent: "testing"
        comment: |
          Reload on /feed after login kept user authenticated (URL remained
          /feed; no redirect to /auth/login). Cache hydration from
          @losapevi_user_v1 AsyncStorage works as in iteration_6.

iteration_8_frontend_tests:
  - task: "Language picker on Login screen (compact)"
    implemented: true
    working: true
    file: "frontend/app/auth/login.tsx, frontend/src/components/LanguagePicker.tsx"
    status_history:
      - working: true
        agent: "testing"
        comment: |
          Verified @ 390x844:
          • Globe button opens modal with IT/EN/ES + flags + checkmark on active.
          • EN → login-submit text becomes "Sign in".
          • ES → "Entrar". IT → "Accedi".
          • Picker button updates with current flag+code (🇮🇹 IT).
  - task: "Language picker on Register screen"
    implemented: true
    working: true
    file: "frontend/app/auth/register.tsx"
    status_history:
      - working: true
        agent: "testing"
        comment: |
          Register screen has LanguagePicker(compact); toggling EN/IT works
          and body text localizes. Minor: Playwright strict-mode violation
          because on expo-web the prior Login screen remains mounted in the
          stack (2 elements with same testID). Not user-visible — only a
          test-infra quirk. Using .first() bypasses.
  - task: "Full login/onboarding flow with language sync"
    implemented: true
    working: true
    file: "frontend/app/onboarding.tsx, frontend/app/(tabs)/*"
    status_history:
      - working: true
        agent: "testing"
        comment: |
          Registered TestLang_ziwdw8@example.com / Pass1234 (answer "pluto").
          Register → /onboarding (Italian, since default lang=it at registration).
          Tabs bottom: Feed/Saved/Profile localize correctly when user switches
          language from Profile (verified EN: "Facts read"/"Liked"/"Saved"/
          "TROPHIES"/"TOP INTERESTS"; ES: "Curiosidades leídas"/"Gustan"/
          "Guardados"/"TROFEOS"/"TEMAS FAVORITOS"). Backend sync POST
          /auth/language confirmed via LanguagePicker.select().
  - task: "Profile trophy name localization"
    implemented: false
    working: false
    file: "frontend/app/(tabs)/profile.tsx (line 53)"
    stuck_count: 1
    priority: "high"
    needs_retesting: true
    status_history:
      - working: false
        agent: "testing"
        comment: |
          CRITICAL BUG per review priority #3 and #4:
          • Profile page calls `api.trophies()` WITHOUT the lang argument
            (profile.tsx line 53: `api.trophies().then(setTrophies)`).
          • Backend /api/trophies?lang=es|en returns localized names correctly
            (verified in iteration_8 backend tests).
          • Result: Trophy grid always shows Italian names
            ("Primo passo", "Curioso", "Studioso", ...) even when UI language
            is EN ("First step") or ES ("Primer paso").
          Fix: pass `i18n.language` (from useTranslation) to api.trophies(lang).
          Must also re-fetch when language changes.
  - task: "Feed language filter (IT fallback) + no crashes"
    implemented: true
    working: true
    file: "frontend/app/(tabs)/feed.tsx"
    status_history:
      - working: true
        agent: "testing"
        comment: |
          • Feed loads in both EN (after switch) and IT with 2.7–3 KB of body
            content, fact cards, images — no empty state, no 500.
          • Since DB only has IT facts, content remains IT even when UI is EN,
            which is the expected fallback behavior.
  - task: "Like/Dislike/Bookmark + Saved"
    implemented: true
    working: "NA"
    file: "frontend/app/(tabs)/feed.tsx, frontend/app/(tabs)/saved.tsx"
    status_history:
      - working: "NA"
        agent: "testing"
        comment: |
          Playwright could not locate like/dislike/bookmark buttons because
          their testIDs are dynamic: `like-{factId}`, `dislike-{factId}`,
          `bookmark-{factId}` (not `feed-like` etc). Visually (screenshot
          captured), feed cards render correctly with no crash. Saved tab
          shows proper Italian empty state "Nessun preferito ancora." with
          heart-CTA. Functional behavior of /react new_sub_weight was
          verified in backend tests (iteration_8_backend_tests); any
          remaining UI verification requires running a click on the dynamic
          testID first. Recommend: add stable `feed-like`/`feed-bookmark`
          testIDs to the TOP card for easier automation, OR test with the
          dynamic selector after reading feed data.
  - task: "Persistent auth on reload"
    implemented: true
    working: true
    file: "frontend/src/context/AuthContext.tsx"
    status_history:
      - working: true
        agent: "testing"
        comment: |
          Reload while logged-in on /saved kept user authenticated (URL
          remained /saved, no redirect to /auth/login).
  - task: "Regression: password visibility toggle, forgot flow entry, onboarding drill-down"
    implemented: true
    working: true
    file: "frontend/src/components/PasswordInput.tsx, frontend/app/auth/{login,forgot}.tsx, frontend/app/onboarding.tsx"
    status_history:
      - working: true
        agent: "testing"
        comment: |
          Login password field uses PasswordInput (eye icon) — verified via
          component usage in login.tsx; covered in iteration_6 tests.
          Forgot link visible on login as "Password dimenticata?" (via
          testID go-forgot) — link route /auth/forgot is reachable. Full
          forgot E2E already verified in prior iteration.
          Onboarding screen rendered Italian title "Cosa ti affascina?"
          + category chips with drill-down for sub-categories (unchanged
          from earlier pass-through tests).

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
      === REGRESSION POST seed_en_es.py — Backend Testing Complete (11/11 + 18/18 PASS) ===
      Target: https://sapevi-che.preview.emergentagent.com/api
      Context: Main agent seeded ~113 AI-generated facts (EN=57, ES=59) via
      seed_en_es.py. Objective: confirm multilingual feed now serves native-language
      content (no IT fallback needed) and no existing functionality regressed.

      Executed /app/regression_seed_en_es.py (11 targeted tests):
      ✅ /health → ok:true, facts=407 (≥400 threshold met; matches expected post-seed).
      ✅ POST /auth/register fresh user — defaults to language="it", returns token.
      ✅ POST /auth/language {"language":"en"} — 200, user.language updated to "en".
      ✅ GET /feed?limit=10 (EN user) — returned 10 facts, ALL with language="en".
         No fallback to IT needed. 🎯 This is the core review-request verification.
      ✅ POST /auth/language {"language":"es"} — 200.
         GET /feed?limit=10 — returned 10 facts, ALL with language="es".
      ✅ POST /auth/language {"language":"it"} — 200.
         GET /feed?limit=10 — returned 10 facts, ALL with language="it".
      ✅ POST /facts/{id}/react {"action":"like"} — 200 with new_weight=1.15,
         new_sub_weight=0.25 (personalization v2 intact).
      ✅ GET /categories?lang=en — 29 items, canonical names preserved
         (Scienza/Storia/Misteri), labels localized (Science/History/Mysteries).
      ✅ GET /trophies?lang=en (auth'd) — 10 trophies, first_step.name="First step",
         desc="Read your first fact."
      ✅ GET /trophies?lang=es — first_step.name="Primer paso".
      ✅ Feed language purity walk (20 facts per lang): lang=en → 10/10 en,
         lang=es → 11/11 es, lang=it → 20/20 it. ZERO language leaks.

      Also executed the full /app/backend_test.py suite for regression:
      ✅ 18/18 PASS (health, register, login, forgot flow, security-question,
         auth/language, categories+lang, trophies+lang, feed+fallback, react
         with new_weight+new_sub_weight, AI generate es, checkin, me, preview,
         subcategories, bookmark, liked). No regressions.

      VERDICT: Seed script seed_en_es.py did NOT break anything. The multilingual
      feed now correctly serves native-language content to EN and ES users
      (previously fell back to IT). No critical or minor issues found.

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
  - agent: "testing"
    message: |
      === POST-REFACTOR REGRESSION — Backend Testing Complete (18/18 PASS) ===
      Target: https://sapevi-che.preview.emergentagent.com/api
      Context: Refactor of monolithic server.py into models.py / deps.py /
      services.py (+ existing i18n.py, image_library.py). Regression sweep
      confirms functional behavior is IDENTICAL to pre-refactor baseline.

      Executed /app/backend_test.py (18 tests, includes new bookmark/liked coverage):
      ✅ /health → ok:true, facts≥200
      ✅ /auth/register full payload → 200 language:"it"; missing security fields → 422
      ✅ /auth/login → 200 with token+user
      ✅ /auth/forgot/question → 200 happy, 404 unknown
      ✅ /auth/forgot/reset → 401 wrong answer, 200 with normalized "  FIDO  " (trim+lower+collapse)
      ✅ /auth/security-question → 401 w/o token, 401 wrong pwd, 200 success
      ✅ /auth/me → has_security_question bool + language field present
      ✅ /auth/language → 422 invalid "xx", 401 w/o token, 200 with "en"; /auth/me reflects "en"
      ✅ GET /categories → 29 entries with name+label+icon+has_subcategories+subcategories
      ✅ GET /categories?lang=en → Scienza=Science, Storia=History, Misteri=Mysteries
      ✅ GET /trophies?lang=es → Primer paso, "Lee tu primera curiosidad.", 10 trophies
      ✅ GET /subcategories/Scienza → 200; /subcategories/NopeCat → 404
      ✅ GET /feed (user lang=it) → non-empty, all facts language=="it"
      ✅ GET /feed (user lang=en) → non-empty via IT fallback, no 500
      ✅ POST /facts/{id}/react like → returns new_weight + new_sub_weight (numeric)
      ✅ POST /facts/{id}/react dislike → returns both weights; pick_weighted stable across iterations
      ✅ POST /facts/{id}/bookmark → toggle on/off; GET /facts/bookmarks reflects state
      ✅ GET /facts/liked → returns liked facts after /react like
      ✅ /auth/checkin → 200 with streak_days
      ✅ /preview → 29 entries with category + image_url
  - agent: "testing"
    message: |
      === ITERATION 8 — Frontend E2E Test Results ===
      Target: https://sapevi-che.preview.emergentagent.com/ @ 390x844
      Test user registered live: testlang_ziwdw8@example.com / Pass1234

      PASSING:
      ✅ Login language picker — IT/EN/ES toggle working; CTA updates
         ("Accedi"/"Sign in"/"Entrar"); flag+code updates.
      ✅ Register language picker — toggles successfully.
      ✅ Register flow — new user created; redirected to /onboarding.
      ✅ Profile language sync — Spanish & English labels localize (Perfil,
         Curiosidades leídas, Gustan, Guardados, TROFEOS, TEMAS FAVORITOS /
         Profile, Facts read, Liked, Saved, TROPHIES, TOP INTERESTS).
      ✅ Feed loads in both IT and EN without crash (IT fallback OK).
      ✅ Persistent auth — reload on /saved keeps session.
      ✅ Tabs localized — Scopri/Salvati/Profilo ↔ Feed/Saved/Profile.

      CRITICAL ISSUE:
      ❌ Trophy NAMES are NOT localized in Profile. In EN and ES views,
         the trophy grid still shows Italian names ("Primo passo",
         "Curioso", "Studioso", ...) instead of "First step"/"Primer paso".
         Root cause: profile.tsx line 53 calls `api.trophies()` without
         the `lang` argument. api.trophies(lang) exists and backend
         /api/trophies?lang=es correctly returns "Primer paso" (verified
         in iteration_8 backend tests).
         FIX: replace with `api.trophies(i18n.language).then(setTrophies)`
         and add `i18n.language` to the useFocusEffect dependency array so
         trophies refetch on language change.

      NOT TESTED (testID mismatch, not a bug per se):
      ⚠️ Like / Dislike / Bookmark buttons use dynamic testIDs
         (`like-{factId}`, `dislike-{factId}`, `bookmark-{factId}`) so the
         generic `feed-like` selector didn't match. Feed cards render
         correctly and no JS crashes were observed; the /react endpoint
         with new_sub_weight was fully verified in backend tests.
         RECOMMEND: run a targeted UI test that first reads a card's ID
         from the feed-screen container, or add a stable testID on the
         visible (top) card's action buttons.

      MINOR (non-blocking):
      • Register screen Playwright picked up 2 `lang-picker-compact`
        elements because expo-web keeps the previous route mounted in the
        stack; not user-facing.
      • Many console warnings from RN-Web deprecations (shadow*, textShadow*,
        pointerEvents, TouchableWithoutFeedback) — framework noise, ignore.

      ✅ /facts/generate (user lang=es, category="Ciencia") → 400 (canonical IT enforced);
         (category="Scienza") → 200 with language="es" via Claude Sonnet 4.5 (no 503)

      No broken endpoints. Refactor into models/deps/services preserves all
      functionality. No regressions detected.
  - agent: "testing"
    message: |
      === POST-MODULARIZATION REGRESSION — Backend Testing Complete (18/18 PASS) ===
      Target: https://sapevi-che.preview.emergentagent.com/api
      Context: Full split of server.py into routers/ package
      (auth.py, catalog.py, facts.py, misc.py). server.py now 162 lines
      (startup/shutdown + router wiring only). All sub-routers mount under
      /api via api.include_router.

      Executed /app/backend_test.py comprehensive suite (18 tests):
      ✅ /api/health → ok:true, facts=276 (≥200)
      ✅ /api/auth/register full payload → 200 language:"it"; missing security fields → 422
      ✅ /api/auth/login → 200 with token+user
      ✅ /api/auth/forgot/question → 200 happy, 404 unknown email
      ✅ /api/auth/forgot/reset → 401 wrong answer; 200 with normalized "  FIDO  "; old pwd login 401, new pwd login 200
      ✅ /api/auth/security-question → 401 w/o token, 401 wrong pwd, 200 success
      ✅ /api/auth/me → has_security_question bool + language field present
      ✅ /api/auth/language → 422 for "xx", 401 w/o token, 200 for "en"; /auth/me reflects "en"
      ✅ GET /api/categories (no lang + lang=en + lang=es) → 29 items each with localized labels
      ✅ GET /api/trophies (no lang + lang=en + lang=es) → 401 w/o token; 10 trophies with localized names
      ✅ GET /api/subcategories/Scienza → 200; /api/subcategories/NopeCat → 404
      ✅ GET /api/feed (lang=it) → non-empty, facts language=="it"
      ✅ GET /api/feed (lang=en) → non-empty via IT fallback, no 500
      ✅ POST /api/facts/{id}/react like → returns new_weight + new_sub_weight
      ✅ POST /api/facts/{id}/react dislike → returns both weights; pick_weighted stable
      ✅ POST /api/facts/{id}/bookmark toggle → on/off; GET /api/facts/bookmarks reflects state
      ✅ GET /api/facts/liked → returns liked facts after /react like
      ✅ POST /api/auth/checkin → 200 with streak_days
      ✅ GET /api/preview → 29 entries with category + image_url
      ✅ POST /api/facts/generate (user lang=es, category="Ciencia") → 400 canonical enforced;
         (category="Scienza") → 200 with language="es" via Claude Sonnet 4.5 (no 503)

      All endpoints behave identically to pre-refactor baseline. /api prefix
      still works for ALL endpoints across all 4 routers. No regressions
      detected post-modularization.

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
