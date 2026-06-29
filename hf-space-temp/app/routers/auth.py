"""
auth.py - Authentication endpoints and verification logic

Defines API key verification functions used to secure FastAPI routes.
"""

from fastapi import APIRouter, Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from app.config import settings

router = APIRouter()

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def verify_api_key(
    api_key: str = Security(api_key_header)
) -> str:
    """
    Dependency function to authorize incoming HTTP requests using API keys.
    
    Args:
        api_key (str): Extracted header API key value.

    Raises:
        HTTPException: HTTP 403 Forbidden error if key is invalid.

    Returns:
        str: Validated API key value.
    """
    if api_key == settings.BACKEND_API_KEY:
        return api_key
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials. Invalid API key."
    )


@router.post("/auth/verify", response_model=dict)
async def verify_auth_token(api_key: str = Security(verify_api_key)) -> dict:
    """
    Test endpoint to verify API key validity.
    
    Args:
        api_key (str): Validated API key value.

    Returns:
        dict: Success details.
    """
    return {"status": "authenticated", "message": "API key validation successful"}
