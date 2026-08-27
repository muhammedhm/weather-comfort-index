from fastapi import APIRouter, Depends

from ..auth import verify_token
from ..weather_service import get_ranked_cities, fetch_forecast

router = APIRouter(prefix="/api", tags=["weather"])


@router.get("/cities")
async def list_cities(user: dict = Depends(verify_token)):
    """
    Protected: requires a valid Auth0 access token.
    Returns all cities ranked from Most Comfortable to Least Comfortable.
    """
    ranked, _status = await get_ranked_cities()
    return {"count": len(ranked), "cities": ranked}


@router.get("/cities/{city_id}/forecast")
async def city_forecast(city_id: int, user: dict = Depends(verify_token)):
    """Protected: temperature trend points for the frontend chart (bonus)."""
    points, _status = await fetch_forecast(city_id)
    return {"city_id": city_id, "points": points}


@router.get("/me")
async def whoami(user: dict = Depends(verify_token)):
    """Handy for the frontend / debugging: echoes back the verified claims."""
    return {"sub": user.get("sub"), "claims": user}
