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

frontend:
  - task: "Registration with security question + Forgot password flow"
    implemented: true
    working: "NA"
    file: "frontend/app/auth/register.tsx, frontend/app/auth/forgot.tsx, frontend/app/security.tsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: |
          - Register: aggiunto picker con 6 domande preimpostate + opzione
            "Domanda personalizzata", campo risposta, hint di sicurezza.
          - Login: aggiunto link "Password dimenticata?".
          - /auth/forgot: flow 2-step (email → domanda, poi risposta+nuova
            password → conferma visiva "Tutto fatto!").
          - /security: schermata per utenti loggati per impostare/aggiornare
            la domanda (richiede password attuale per confermare).
          - Profile: nuovo row "Domanda di sicurezza" con badge giallo "!"
            se has_security_question=false.
          - securityQuestions.ts shared module con elenco 6 domande IT.
          Tutti gli screen renderizzano correttamente (screenshot verificato
          sul web preview 390x844).

metadata:
  created_by: "main_agent"
  version: "1.1"
  test_sequence: 1
  run_ui: false

test_plan:
  current_focus:
    - "Security question & password reset endpoints"
    - "Registration with security question + Forgot password flow"
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

agent_communication:
  - agent: "main"
    message: |
      Ho implementato la feature "recupero password via domanda di sicurezza"
      (opzione scelta dall'utente). Backend testato con script python: tutti
      i casi edge coperti (risposta wrong/right case-insensitive, password
      attuale wrong, utenti senza domanda). Frontend render verificato via
      screenshot. Pronto per test automatizzato backend e/o per test manuale
      utente sul frontend.
  - agent: "testing"
    message: |
      Backend testing completed successfully — 17/17 tests PASSED in
      /app/backend_test.py against http://localhost:8001/api.
      All new password-recovery-via-security-question endpoints work as
      specified:
        • POST /api/auth/register enforces security_question/security_answer (422 if missing).
        • POST /api/auth/forgot/question returns 200 (happy), 404 (unknown email), 404 with Italian
          guidance (legacy user without question).
        • POST /api/auth/forgot/reset verifies normalized answer (case + whitespace insensitive),
          rejects wrong answer (401), enforces min password length (422), issues new token on success,
          and invalidates old password (login OLD → 401).
        • POST /api/auth/security-question requires auth (401), requires correct current_password
          ("Password attuale non corretta"), persists new question retrievable via forgot/question.
      Regression checks: /api/auth/me returns has_security_question boolean; /api/feed?limit=20
      returns 20 facts with valid image_url; /api/facts/generate (Claude Sonnet 4.5) returned a
      valid Italian fact for category=Scienza. No critical or minor issues found on backend.
