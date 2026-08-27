# Fidenz Weather Comfort Index — Full Stack Assignment

A weather analytics dashboard: FastAPI backend (OpenWeatherMap + a custom
Comfort Index + server-side caching + an Auth0-protected API) and a React
(Vite) frontend (Auth0 login/MFA, ranked dashboard, dark mode, temperature
trend chart).

```
backend/    FastAPI app (Python)
frontend/   React + Vite app
```

---

## 1. Setup Instructions

### 1.1 Get an OpenWeatherMap API key
1. Sign up at https://home.openweathermap.org/users/sign_up
2. Go to "API keys" and copy the default key (new keys can take up to a
   couple of hours to activate).
3. Put it in `backend/.env` as `OPENWEATHER_API_KEY`.

`backend/app/cities.json` ships with 12 cities in the format
`{"List": [{"CityCode": "...", "CityName": "...", ...}]}`. If you add or
change any city, confirm its id on openweathermap.org (search the city and
read the id from the URL).

### 1.2 Set up Auth0 (dashboard work — no code)

You need one **Application** (the React SPA) and one **API** (the FastAPI
backend), plus MFA and a closed signup policy.

**Create the tenant** — sign up at https://auth0.com if you don't have one.

**Create an Application**
- Dashboard → Applications → Create Application → type **Single Page Application**
- Settings tab:
  - Allowed Callback URLs: `http://localhost:5173`
  - Allowed Logout URLs: `http://localhost:5173`
  - Allowed Web Origins: `http://localhost:5173`
- Copy the **Domain** and **Client ID** into `frontend/.env`.

**Create an API**
- Dashboard → Applications → APIs → Create API
- Set an **Identifier** (this becomes your `audience`, e.g.
  `https://fidenz-weather-api` — just a unique string, doesn't need to
  resolve to anything real)
- Signing algorithm: **RS256**
- Use this exact identifier for both `backend/.env` (`AUTH0_API_AUDIENCE`)
  and `frontend/.env` (`VITE_AUTH0_AUDIENCE`) — they must match exactly, or
  you'll hit an Auth0 "Service not found" error at login.

  > Tip: grab the identifier from the **Identifier** field on the API's
  > Settings page — not the hex ID that appears in the dashboard's URL bar
  > for that page. Those are two different things and only the former is
  > a valid audience.

**Disable public signups**
- Dashboard → Authentication → Database → your default connection →
  **Disable Sign Ups**

**Whitelist specific users** (since public signup is off)
- Dashboard → User Management → Users → Create User
- Required test user:
  - Email: `careers@fidenz.com`
  - Password: `MC7VR!Nnjjc9zWE` (the password given in the assignment brief
    was rejected by Auth0's password-strength policy, so this was used
    instead for the same account)
- Add your own account too, so you can log in for the screen recording.

**Enable MFA (email)**
- Dashboard → Security → Multi-factor Auth → turn on **Email**, policy set
  to **Always/Required**.
-  **Not yet completed in this submission** — see Known Limitations.

### 1.3 Run the backend
```
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env    # fill in OPENWEATHER_API_KEY, AUTH0_DOMAIN, AUTH0_API_AUDIENCE
uvicorn app.main:app --reload --port 8000
```
Verify at `http://localhost:8000/docs` — you should see `/api/cities`,
`/api/me`, `/api/cities/{id}/forecast`, `/api/debug/cache-status`.

Run tests: `pytest tests/`

### 1.4 Run the frontend
```
cd frontend
npm install
cp .env.example .env    # fill in VITE_AUTH0_DOMAIN, VITE_AUTH0_CLIENT_ID, VITE_AUTH0_AUDIENCE
npm run dev
```
Open `http://localhost:5173`, click **Log in**, and the dashboard should
load ranked cities after authenticating.

---

## 2. The Comfort Index Formula

The Comfort Index is a 0–100 score computed **server-side only**
(`backend/app/comfort_index.py`), using four parameters from the
OpenWeatherMap response:

| Parameter | Weight |
|---|---|
| Temperature | 40% |
| Humidity | 25% |
| Wind speed | 20% |
| Cloudiness | 15% |

**Approach**: rather than one large formula, each parameter is first
converted into its own 0–100 sub-score using a shape that matches how
people actually perceive that variable, and the sub-scores are then
combined with the weights above.

- **Temperature** — comfort peaks around 22°C and falls off the further you
  move in either direction (too cold *and* too hot both feel bad). Modeled
  as an inverted parabola, clipped to [0, 100], hitting 0 about 12°C away
  from the ideal.
- **Humidity** — comfort peaks around 45% relative humidity; both very dry
  and very humid air feel unpleasant. Same inverted-parabola shape, wider
  spread (±45%).
- **Wind speed** — a light breeze (up to ~3 m/s) is pleasant and scores
  100; comfort then decays linearly, bottoming out at 15 m/s (strong wind).
- **Cloudiness** — up to 50% cloud cover is treated as neutral-to-pleasant
  (it softens harsh sun); beyond that, a linear penalty applies up to full
  overcast.

Final score = weighted sum of the four sub-scores, clipped to [0, 100].
Cities are then sorted descending by this score (rank 1 = most
comfortable).

## 3. Reasoning Behind the Weights

- **Temperature (40%)** is the single biggest driver of how "comfortable"
  outdoor conditions feel, so it gets the largest weight.
- **Humidity (25%)** is the second-biggest driver — it changes how a given
  temperature *feels* (the classic "it's not the heat, it's the humidity"
  effect), so it's weighted close to, but below, temperature.
- **Wind (20%)** and **cloudiness (15%)** are treated as secondary
  modifiers: they meaningfully shift comfort but matter less on their own
  than getting temperature or humidity badly wrong.

These weights are a design opinion, not a physical law — a reasonable
alternative could weight humidity closer to temperature in very humid
climates, or give wind more weight for coastal cities. That's exactly the
kind of trade-off worth being ready to discuss and adjust live.

## 4. Trade-offs Considered

- **Weighted sum vs. a single hard cutoff.** Because no one parameter has
  100% weight, a very bad reading on one axis (e.g. freezing temperature)
  is "cushioned" by good readings on the others. This is realistic (a
  cold-but-calm-and-dry day isn't *as* miserable as cold-and-windy-and-humid)
  but means the score is never as extreme as looking at temperature alone
  would suggest — a trade-off between nuance and legibility of the score.
- **Per-parameter sub-scores vs. one combined equation.** Scoring each
  dimension independently, then weighting, is easier to reason about, test,
  and extend (adding a 5th parameter is one new function + a weight
  rebalance) than a single entangled formula — at the cost of it being a
  slightly less "elegant" single equation.
- **Only 4 of the 7 suggested parameters.** Pressure, visibility, and dew
  point were left out initially to keep the formula easy to defend and
  extend live (per the assignment's Part 3 requirement) rather than
  over-fitting it with every available field. Dew point in particular
  isn't directly returned by the API and would need to be derived.

## 5. Cache Design

Two independent in-memory TTL caches (`backend/app/cache.py`), each 5
minutes per the assignment spec:

1. **`raw_weather_cache`** — one entry per city id (plus a separate
   `forecast:{id}` namespace for trend data), holding the untouched
   OpenWeatherMap response. This is the cache that actually saves API
   quota and latency, since it guards the external HTTP call.
2. **`processed_cache`** — the final ranked list, under one constant key
   (only one "current ranking" exists at a time).

They're deliberately separate: recomputing the ranking is cheap, pure math
over already-fetched data, while refetching from OpenWeatherMap is the
expensive, rate-limited part. Splitting them means a cache layer refresh
never forces an unnecessary external call. Both caches track hit/miss
counts internally, exposed via `GET /api/debug/cache-status` for
inspection (size, TTL, hit/miss counts, current keys).

## 6. Known Limitations

- **Email MFA is not yet enabled** on the Auth0 tenant used for this
  submission — the dashboard toggle described in Setup wasn't switched on
  before submitting, so logins currently succeed without an MFA challenge.
  This is the one Part 2 requirement left incomplete; enabling it is a
  dashboard-only change (Security → Multi-factor Auth → Email → Always).
- **In-memory cache is single-process only** — it resets on server restart
  and won't scale horizontally across multiple instances without moving to
  something like Redis.
- **No automated frontend tests** — unit test coverage (a bonus item) was
  focused on the Comfort Index function specifically, per the assignment's
  explicit ask, rather than the UI.
- **Auth0 free-tier constraints** — email deliverability for MFA and login
  rate limits depend on the tenant's plan; fine for this assignment's
  scope, but worth knowing about if testing feels slow or flaky.
