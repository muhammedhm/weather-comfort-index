# Fidenz Weather Comfort Index — Backend (FastAPI)

## Setup

1. `python -m venv venv && source venv/bin/activate` (Windows: `venv\Scripts\activate`)
2. `pip install -r requirements.txt`
3. `cp .env.example .env` and fill in:
   - `OPENWEATHER_API_KEY` — from https://openweathermap.org/api (free tier is fine)
   - `AUTH0_DOMAIN`, `AUTH0_API_AUDIENCE` — from your Auth0 API setup (see repo root README)
4. **Important**: verify the city IDs in `app/cities.json`. They were picked from memory
   against OpenWeatherMap's known IDs for major cities — before submitting, cross-check
   each one against OpenWeatherMap's city list (search a city on openweathermap.org and
   read the ID from the URL, or download their `city.list.json.gz`) and swap in any that
   don't resolve.
5. Run: `uvicorn app.main:app --reload --port 8000`
6. Docs at `http://localhost:8000/docs`

## Endpoints

| Endpoint | Auth | Description |
|---|---|---|
| `GET /api/cities` | Bearer token required | Ranked list of all cities, most → least comfortable |
| `GET /api/me` | Bearer token required | Echoes verified token claims (debugging) |
| `GET /api/debug/cache-status` | none | Cache HIT/MISS counters and contents |

## Comfort Index formula

See the module docstring in `app/comfort_index.py` — it's written to be read standalone
and is the primary thing your README/video should reference. Summary: temperature (40%),
humidity (25%), wind speed (20%), cloudiness (15%), each converted to its own 0–100
sub-score using a shape that matches how that variable is actually perceived (peaked
around an ideal value for temp/humidity, decaying past a threshold for wind/cloud), then
combined with weights.

**Trade-off worth naming in your README**: because no single parameter has 100% weight,
a very bad reading on one axis (e.g. freezing temperature) is "cushioned" by good
readings on the others. This is realistic (a cold-but-calm-and-dry day isn't *as* bad as
cold-and-windy-and-humid) but means the score is never as extreme as looking at
temperature alone would suggest — a trade-off between nuance and legibility.

## Caching design

Two independent TTL caches (5 minutes each, per spec):
- `raw_weather_cache`: one entry per city id, holding the untouched OpenWeatherMap
  response. This is the one that actually saves API quota/latency.
- `processed_cache`: the final ranked list, keyed by a single constant key (only one
  "current ranking" exists at a time).

They're separate so that recomputing the ranking (cheap, pure math) doesn't require
refetching from OpenWeatherMap (expensive, rate-limited) unless the raw cache has also
expired. `/api/debug/cache-status` reports size, TTL, and hit/miss counts for both.

## Known limitations

- Auth0 whitelisting (disabling public signup, restricting to specific emails) is
  configured entirely in the Auth0 dashboard — there's no backend code enforcing it,
  which is intentional (Auth0 owns identity), but worth being able to explain.
- The cache is in-process memory, not shared across multiple server instances — fine for
  this assignment's scope, but wouldn't survive a restart or scale horizontally without
  moving to Redis.
- `cities.json` IDs should be double-checked against OpenWeatherMap's current data before
  submission (see Setup step 4).

## Tests

`pytest tests/` — covers the Comfort Index formula: boundary conditions, monotonicity
(more wind/cloud → lower score), and the 0–100 bound guarantee.
