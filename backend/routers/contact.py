"""
routers/contact.py — Contact form stored in Firebase Realtime Database.

POST /api/contact   — save contact message (public)
GET  /api/contact   — list messages        (auth required)
"""
from fastapi import APIRouter, Depends, status
from datetime import datetime, timezone
from typing import List
from ..firebase import get_db
from ..models import ContactMessage, ContactResponse
from ..dependencies import get_current_user, UserProfile

router = APIRouter(prefix="/api/contact", tags=["Contact"])

NODE = "contact_messages"


@router.post(
    "",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit contact form",
)
async def submit_contact(msg: ContactMessage):
    """Saves the contact form to Firebase Realtime Database."""
    root = get_db()
    data = msg.model_dump()
    data["created_at"] = datetime.now(timezone.utc).isoformat()
    data["read"]       = False

    root.child(NODE).push(data)
    return ContactResponse(
        success=True,
        message="Thank you! We'll get back to you within 24 hours.",
    )


@router.get("", summary="List contact messages (admin)")
async def list_messages(_user: UserProfile = Depends(get_current_user)):
    root = get_db()
    raw  = root.child(NODE).get() or {}

    results = []
    for mid, data in raw.items():
        if isinstance(data, dict):
            data["id"] = mid
            results.append(data)

    results.sort(key=lambda m: m.get("created_at", ""), reverse=True)
    return results
