"""Clerk JWT authentication middleware."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.config import settings
from loguru import logger
from typing import Optional, Dict, Any

security = HTTPBearer()


class User:
    """User object from Clerk token."""

    def __init__(self, user_id: str, email: Optional[str] = None):
        self.id = user_id
        self.email = email


async def verify_clerk_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """
    Verify Clerk JWT token from Authorization header.

    Args:
        credentials: HTTP Bearer credentials

    Returns:
        User object if valid

    Raises:
        HTTPException: 401 if token is invalid
    """
    token = credentials.credentials

    try:
        # Decode JWT
        # Note: In production, fetch Clerk's public key for proper RS256 verification
        # For now, we'll do basic validation
        payload = jwt.decode(
            token,
            settings.CLERK_SECRET_KEY,
            algorithms=["HS256"],  # Use HS256 for simplicity, RS256 in production
            options={"verify_signature": False},  # TODO: Proper signature verification
        )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: no user ID",
            )

        email = payload.get("email")

        logger.debug(f"Authenticated user: {user_id}")

        return User(user_id=user_id, email=email)

    except JWTError as e:
        logger.warning(f"JWT validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def verify_clerk_token_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
) -> Optional[User]:
    """
    Optional authentication - returns None if no token provided.

    Args:
        credentials: Optional HTTP Bearer credentials

    Returns:
        User object if token provided and valid, None otherwise
    """
    if not credentials:
        return None

    try:
        return await verify_clerk_token(credentials)
    except HTTPException:
        return None
