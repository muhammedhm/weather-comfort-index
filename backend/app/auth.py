"""
Validates Auth0-issued JWT access tokens on incoming requests.

How this fits the OAuth2/OIDC picture (be ready to explain this flow):
  1. React app redirects the user to Auth0's Universal Login (Authorization
     Code Flow with PKCE, handled by @auth0/auth0-react).
  2. Auth0 authenticates the user (and enforces MFA + the whitelist, both
     configured in the Auth0 dashboard, not in this code).
  3. Auth0 redirects back with an authorization code; auth0-react exchanges
     it for an ID token (who the user is) and an ACCESS token (what the
     user can call - scoped to our API's "audience").
  4. The React app attaches the access token as `Authorization: Bearer
     <token>` on every API call.
  5. THIS FILE verifies that token on the backend before letting the
     request through - we never trust the frontend's word that someone is
     logged in.

We verify signature via Auth0's public JWKS (rotating keys, fetched over
HTTPS and cached in-process), plus standard claims: issuer, audience,
expiry. RS256 (asymmetric) is used, not HS256, specifically because it lets
the backend verify tokens with a PUBLIC key while only Auth0 holds the
private signing key - the frontend/backend never need to share a secret.
"""
from functools import lru_cache

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from jose.exceptions import JWTError

from .config import get_settings

security = HTTPBearer()


@lru_cache
def _get_jwks() -> dict:
    settings = get_settings()
    resp = httpx.get(f"https://{settings.auth0_domain}/.well-known/jwks.json", timeout=10)
    resp.raise_for_status()
    return resp.json()


def _get_signing_key(token: str) -> dict:
    unverified_header = jwt.get_unverified_header(token)
    jwks = _get_jwks()
    for key in jwks["keys"]:
        if key["kid"] == unverified_header.get("kid"):
            return key
    # JWKS may have rotated - clear cache and try once more.
    _get_jwks.cache_clear()
    jwks = _get_jwks()
    for key in jwks["keys"]:
        if key["kid"] == unverified_header.get("kid"):
            return key
    raise HTTPException(status_code=401, detail="Unable to find matching signing key")


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    settings = get_settings()
    token = credentials.credentials

    try:
        signing_key = _get_signing_key(token)
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=[settings.auth0_algorithms],
            audience=settings.auth0_api_audience,
            issuer=settings.issuer,
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {e}",
        )
