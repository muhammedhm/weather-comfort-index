"""
Server-side caching layer.

Design choice worth explaining in your video: we use TWO separate caches
rather than one.

1. `raw_weather_cache`  - stores the untouched OpenWeatherMap response per
   city id. TTL = 5 minutes (per assignment spec). This is the expensive,
   rate-limited external call, so it's the one that matters most.
2. `processed_cache`    - stores the already-ranked, already-scored list of
   all cities. TTL = 5 minutes too, but it's invalidated independently.

Why split them? If you only cached the final processed list, a single new
city added to cities.json would force you to refetch and reprocess
everything. Splitting means each city's raw data has its own lifetime, and
the processed list is just a cheap recomputation over whatever raw data is
currently fresh (from cache or a live fetch) - recomputation is basically
free (pure math), whereas the HTTP call to OpenWeatherMap is not.

We track hits/misses ourselves (cachetools doesn't do this out of the box)
so the /api/debug/cache-status endpoint can report real numbers.
"""
from cachetools import TTLCache
from threading import Lock


class TrackedTTLCache:
    def __init__(self, maxsize: int, ttl: int):
        self._cache = TTLCache(maxsize=maxsize, ttl=ttl)
        self._lock = Lock()
        self.hits = 0
        self.misses = 0

    def get(self, key):
        with self._lock:
            if key in self._cache:
                self.hits += 1
                return self._cache[key], "HIT"
            self.misses += 1
            return None, "MISS"

    def set(self, key, value):
        with self._lock:
            self._cache[key] = value

    def status(self):
        with self._lock:
            return {
                "size": len(self._cache),
                "maxsize": self._cache.maxsize,
                "ttl_seconds": self._cache.ttl,
                "hits": self.hits,
                "misses": self.misses,
                "keys": list(self._cache.keys()),
            }


# Module-level singletons - imported wherever caching is needed.
raw_weather_cache = TrackedTTLCache(maxsize=200, ttl=300)
processed_cache = TrackedTTLCache(maxsize=50, ttl=300)
