from fastapi import APIRouter

from ..cache import raw_weather_cache, processed_cache

router = APIRouter(prefix="/api/debug", tags=["debug"])


@router.get("/cache-status")
async def cache_status():
    """
    Shows current cache HIT/MISS counters and contents for both cache
    layers. Deliberately left unauthenticated so it's easy to demo during
    your recording - if you'd rather lock it down, just add
    Depends(verify_token) like the other routes.
    """
    return {
        "raw_weather_cache": raw_weather_cache.status(),
        "processed_cache": processed_cache.status(),
    }
