from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import weather, debug

settings = get_settings()

app = FastAPI(
    title="Fidenz Weather Comfort Index API",
    description="Fetches weather data, computes a custom Comfort Index, "
    "caches results, and protects access with Auth0.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(weather.router)
app.include_router(debug.router)


@app.get("/")
async def root():
    return {"status": "ok", "service": "fidenz-weather-comfort-index"}
