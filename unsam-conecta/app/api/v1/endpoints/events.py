from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.domain import User, RoleEnum, Registration, RegistrationStatusEnum
from app.schemas.domain import EventCreate, EventResponse
from app.services import events as event_service

router = APIRouter()

# --- PUBLIC ROUTES ---

@router.get("/", response_model=List[EventResponse])
async def read_events(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    tag: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve all events. Supports optional filtering by category or tag."""
    events = await event_service.get_events(db, skip=skip, limit=limit, category=category, tag=tag)
    return events

@router.get("/{event_id}", response_model=EventResponse)
async def read_event(event_id: int, db: AsyncSession = Depends(get_db)):
    """Retrieve a specific event by ID."""
    event = await event_service.get_event(db, event_id=event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


# --- PROTECTED ROUTES (ORGANIZERS ONLY) ---

@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_new_event(
    event_in: EventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new event. Strictly restricted to users with ORGANIZER or ADMIN roles."""
    if current_user.role not in [RoleEnum.ORGANIZER, RoleEnum.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have enough privileges to create an event."
        )
    
    event = await event_service.create_event(
        db=db, event_in=event_in, organizer_id=current_user.id
    )
    return event

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an event. Must be the organizer of the event or an admin."""
    event = await event_service.get_event(db, event_id=event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
        
    if event.organizer_id != current_user.id and current_user.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete events that you created."
        )
        
    await event_service.delete_event(db, event_id=event_id)
    return None

# NUEVO: Endpoint para listar nombres completos de los alumnos anotados
@router.get("/{event_id}/attendees")
async def get_event_attendees(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve the list of full names of confirmed attendees for an event. Restricted to the organizer or admin."""
    event = await event_service.get_event(db, event_id=event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
        
    if event.organizer_id != current_user.id and current_user.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view attendees for events that you created."
        )
    
    # Consulta uniendo las inscripciones confirmadas con los usuarios correspondientes
    query = select(User.full_name).join(Registration, User.id == Registration.user_id).where(
        Registration.event_id == event_id,
        Registration.status == RegistrationStatusEnum.CONFIRMED
    )
    result = await db.execute(query)
    attendees = result.scalars().all()
    
    return [{"full_name": name} for name in attendees]