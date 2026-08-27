# Fidenz Weather Comfort Index — Full Stack Assignment

A weather analytics dashboard: FastAPI backend (OpenWeatherMap + custom Comfort
Index + caching + Auth0-protected API) and a React (Vite) frontend (Auth0
login, ranked dashboard, dark mode, temperature trend chart).

```
backend/    FastAPI app  → see backend/README.md for API-specific details
frontend/   React + Vite app
```

---

## 1. Get an OpenWeatherMap API key

1. Sign up at https://home.openweathermap.org/users/sign_up
2. Go to "API keys" and copy the default key (new keys can take up to a
   couple of hours to activate).
3. Put it in `backend/.env` as `OPENWEATHER_API_KEY`.

**Double-check `backend/app/cities.json`** — the city IDs in there were
picked from memory and should be verified against OpenWeatherMap's actual
data before you rely on them (search each city on openweathermap.org and
confirm the id in the URL, or download `city.list.json.gz` from their bulk
data page). Swap in real, current IDs for at least 10 cities.

---

## 2. Set up Auth0 (dashboard work — no code)

You'll create one **Application** (for the React SPA) and one **API** (for
the FastAPI backend), then configure MFA and disable public signup.

### 2.1 Create the tenant
Sign up at https://auth0.com if you don't already have a tenant.

### 2.2 Create an Application
- Dashboard → Applications → Create Application
- Name it (e.g. "Weather Comfort Index"), type **Single Page Application**
- In the app's **Settings** tab, set:
  - **Allowed Callback URLs**: `http://localhost:5173`
  - **Allowed Logout URLs**: `http://localhost:5173`
  - **Allowed Web Origins**: `http://localhost:5173`
- Copy the **Domain** and **Client ID** into `frontend/.env`.

### 2.3 Create an API
- Dashboard → Applications → APIs → Create API
- Name it, set an **Identifier** (this becomes your `audience`, e.g.
  `https://fidenz-weather-api` — it's just a unique string, doesn't need to
  resolve to anything)
- Signing algorithm: **RS256**
- Put the identifier into both `backend/.env` (`AUTH0_API_AUDIENCE`) and
  `frontend/.env` (`VITE_AUTH0_AUDIENCE`) — they must match exactly.

### 2.4 Disable public signups
- Dashboard → Authentication → Database → your default connection →
  **Disable Sign Ups** toggle (this stops anyone from self-registering).

### 2.5 Whitelist specific users
Since public signup is off, create users manually:
- Dashboard → User Management → Users → Create User
- Added the required test user:
  - Email: `careers@fidenz.com`
  - Password: `MC7VR!Nnjjc9zWE` (the passoword given was already being used and was being rejected by Auth0 platform)
- Add yourself too, so you can log in for the recording.

### 2.6 Enable MFA (email)
- Dashboard → Security → Multi-factor Auth
- Turn on **Email** as a factor
- Under policy, set it to **Always** (or "Required") so every login is
  challenged — this satisfies "Enable MFA via email verification."

---

## 3. Run the backend

```
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env   # fill in OPENWEATHER_API_KEY, AUTH0_DOMAIN, AUTH0_API_AUDIENCE
uvicorn app.main:app --reload --port 8000
```

Verify: open http://localhost:8000/docs — you should see `/api/cities`,
`/api/me`, `/api/debug/cache-status`.

Run tests: `pytest tests/`

## 4. Run the frontend

```
cd frontend
npm install
cp .env   # fill in VITE_AUTH0_DOMAIN, VITE_AUTH0_CLIENT_ID, VITE_AUTH0_AUDIENCE
npm run dev
```

Open http://localhost:5173 — click **Log in**, complete Auth0's login +
email MFA challenge, and the dashboard should load ranked cities.



## Known limitations

- In-memory cache: single-process only, resets on restart, won't scale
  horizontally without moving to Redis or similar.
- No automated frontend tests (bonus item — pytest coverage is on the
  Comfort Index only, per the assignment's explicit ask).
- Auth0 rate limits and email-MFA deliverability depend on your tenant's
  plan; the free tier is sufficient for this assignment's scope.(I haven't setup MFA through Mail)
