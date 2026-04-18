# PRD — Lo Sapevi che?

## Vision
Italian mobile app (Expo React Native) delivering daily curated "Did You Know?" facts across 20 niches. Users refine personalization via like/dislike. Premium Medium-meets-TikTok reading experience.

## Core Features
1. **Auth (JWT)** — email + password register/login, bearer token, 30-day session.
2. **Interest Onboarding** — select 3+ niches from 20 categories.
3. **Personalized Feed** — TikTok-style vertical FlatList (pagingEnabled), full-screen cards with gradient-overlaid images, title/excerpt, double-tap-to-like heart animation.
4. **Like/Dislike Algorithm** — on-device interactions update server-side `interest_weights` per category. Liked = +0.15 (max 3.0), disliked = -0.20 (min 0.05). Feed picks weighted-top candidates from unseen pool.
5. **Approfondimento (Detail)** — premium editorial view with hero image and serif-like typography for deep dives.
6. **Saved / Bookmarks** — dedicated tab.
7. **Profile** — avatar, stats (letti / piaciute / salvate), top-5 weighted interests bar chart, logout.
8. **AI Generation** — FAB ✨ button generates new fact via Claude Sonnet 4.5 (Emergent LLM key) based on top user interest.
9. **Push Notifications** — daily local scheduled notification at 09:00 via `expo-notifications` (CALENDAR trigger), with toggle in Profile.

## Tech Stack
- Frontend: Expo SDK 54, expo-router, React Native, TypeScript, expo-linear-gradient, expo-notifications, expo-device, AsyncStorage, expo-haptics.
- Backend: FastAPI, Motor (MongoDB), bcrypt, PyJWT, emergentintegrations (Claude Sonnet 4.5), httpx.
- DB: MongoDB `lo_sapevi_che` — collections: `users`, `facts`.

## Seed Data
28 curated Italian facts across 20 niches (Scienza, Storia, Tecnologia, Natura, Spazio, Cucina, Sport, Arte, Psicologia, Cinema, Musica, Geografia, Medicina, Filosofia, Economia, Letteratura, Animali, Matematica, Viaggi, Mitologia).

## User Flow
Splash → Login/Register → Onboarding (if interests empty) → Tabs [Feed, Salvati, Profilo] → Detail (approfondimento) → back.
