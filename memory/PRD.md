# PRD — Lo Sapevi che?

## Vision
Italian mobile app (Expo React Native) delivering daily curated "Did You Know?" facts across 20 niches. Users refine personalization via like/dislike. Gamification via streak + trophies + sharing. Premium Medium-meets-TikTok reading experience.

## Core Features (v1)
- Auth JWT (email/password)
- Interest onboarding
- Personalized TikTok-style feed
- Like/Dislike algorithm (weights update)
- Approfondimento detail view
- Saved/Bookmarks, Profile
- AI generation (Claude Sonnet 4.5)
- Daily local scheduled notifications

## v2 Features (this iteration)
- **Content**: 96+ curated Italian facts + AI bulk generation (`/api/facts/bulk-generate`). Facts now carry `sources` (list of {title, url}).
- **Richer Onboarding**: preview cards per category with hero image and a sample "Lo sapevi che..." fact pulled from each niche.
- **Deep dive with citations**: Detail view shows a "FONTI" section with tappable links (opens in device browser via `Linking`).
- **Gamification**:
  - Daily streak (`streak_days`, `best_streak`, `last_checkin_date`) via `POST /api/auth/checkin` on app open.
  - 10 trophies: Primo passo, Curioso, Studioso, Enciclopedia vivente, Collezionista, Fiamma (3gg), Fuoco eterno (7gg), Leggenda (30gg), Esploratore (like 10+ cat), AI Pioneer (5 AI facts).
  - Trophy modal pops on app open for newly earned achievements.
  - Profile displays streak card + trophies grid.
- **Social**: native `Share` API — share facts from feed card, detail view, and share your profile stats.

## Tech Stack
- Frontend: Expo SDK 54, expo-router, TypeScript, expo-linear-gradient, expo-notifications, AsyncStorage, expo-haptics.
- Backend: FastAPI, Motor/MongoDB, bcrypt, PyJWT, emergentintegrations (Claude Sonnet 4.5).

## Key API endpoints (all require Bearer auth except register/login/forgot)
- `POST /api/auth/register|login`, `GET /api/auth/me`, `POST /api/auth/interests|push-token|checkin`
- `POST /api/auth/forgot/question|forgot/reset` (no auth) — recupero password via domanda di sicurezza
- `POST /api/auth/security-question` — imposta/aggiorna la domanda (richiede password attuale)
- `GET /api/categories|preview|trophies|feed|facts/bookmarks|facts/liked|facts/{id}`
- `POST /api/facts/{id}/react|bookmark|seen`
- `POST /api/facts/generate|bulk-generate`
- `GET /api/health`

## Test Results
- Iteration 1: 20/20 passed (MVP)
- Iteration 2: 31/31 backend + 100% frontend (gamification + content)
- Iteration 3: 17/17 backend (security-question password recovery)

## Next Ideas
- Remote Expo push notifications (requires EAS projectId)
- Streak restoration items (1 freebie/week)
- Leaderboards, friends/follow
- Premium tier (unlimited AI generation, exclusive deep dives)
