"""
Centralized configuration, loaded from environment variables / .env file.
Keeping this in one place means every service reads settings the same way,
and it's the first thing to point to when explaining "how does config work"
in your interview.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # OpenWeatherMap
    openweather_api_key: str
    openweather_base_url: str = "https://api.openweathermap.org/data/2.5"

    # Auth0
    auth0_domain: str          # e.g. dev-xxxx.us.auth0.com
    auth0_api_audience: str    # the API identifier you set up in Auth0
    auth0_algorithms: str = "RS256"
    auth0_issuer: str | None = None  # defaults to https://{domain}/ if not set

    # Caching
    weather_cache_ttl_seconds: int = 300   # 5 minutes, per assignment spec
    processed_cache_ttl_seconds: int = 300

    # CORS
    frontend_origin: str = "http://localhost:5173"

    class Config:
        env_file = ".env"

    @property
    def issuer(self) -> str:
        return self.auth0_issuer or f"https://{self.auth0_domain}/"


@lru_cache
def get_settings() -> Settings:
    return Settings()
