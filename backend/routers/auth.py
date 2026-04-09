"""
routers/auth.py — Authentication endpoints.

POST /api/auth/verify  — verify Firebase ID-token, return user profile
GET  /api/auth/me      — return the logged-in user's profile
"""
from fastapi import APIRouter, Depends, HTTPException, status
from firebase_admin import auth as firebase_auth
from ..models import TokenVerifyRequest, UserProfile
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/verify", response_model=UserProfile, summary="Verify Firebase ID token")
async def verify_token(body: TokenVerifyRequest):
    """
    Accepts a Firebase ID token from the frontend and verifies it.
    Returns the decoded user profile on success.
    """
    try:
        decoded = firebase_auth.verify_id_token(body.id_token)
    except firebase_auth.ExpiredIdTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except firebase_auth.InvalidIdTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))

    return UserProfile(
        uid=decoded["uid"],
        email=decoded.get("email"),
        display_name=decoded.get("name"),
        photo_url=decoded.get("picture"),
        email_verified=decoded.get("email_verified", False),
    )


@router.get("/me", response_model=UserProfile, summary="Get current user profile")
async def me(current_user: UserProfile = Depends(get_current_user)):
    """Returns the profile of the currently authenticated user."""
    return current_user
