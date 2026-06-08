from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.domain import User
from app.schemas.domain import RegistrationResponse
from app.services import registrations as reg_service

router = APIRouter()

@router.post("/events/{event_id}/register", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
async def enroll_in_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """1-Click Register: Enrolls the current user in an event if capacity allows."""
    return await reg_service.register_user_for_event(db, user_id=current_user.id, event_id=event_id)

@router.post("/events/{event_id}/cancel")
async def cancel_event_enrollment(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel registration and free up a spot for someone else."""
    return await reg_service.cancel_registration(db, user_id=current_user.id, event_id=event_id)

@router.get("/users/me/registrations", response_model=List[RegistrationResponse])
async def read_my_registrations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all confirmed registrations for the currently logged-in user."""
    return await reg_service.get_user_registrations(db, user_id=current_user.id)