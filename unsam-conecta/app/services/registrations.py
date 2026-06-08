from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.domain import Event, Registration, RegistrationStatusEnum, EventStatusEnum

async def register_user_for_event(db: AsyncSession, user_id: int, event_id: int):
    # 1. Lock the event row to prevent race conditions (Overbooking protection)
    # This ensures that if 100 people click enroll at the same time, PostgreSQL 
    # processes them one by one to accurately check capacity.
    query = select(Event).where(Event.id == event_id).with_for_update()
    result = await db.execute(query)
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.status != EventStatusEnum.PUBLISHED:
        raise HTTPException(status_code=400, detail="Event is not open for registration")
    if event.current_enrollment >= event.capacity:
        raise HTTPException(status_code=400, detail="Event is at full capacity. Join the waitlist.")
        
    # 2. Check if the user is already registered
    reg_query = select(Registration).where(
        Registration.user_id == user_id, 
        Registration.event_id == event_id,
        Registration.status == RegistrationStatusEnum.CONFIRMED
    )
    reg_result = await db.execute(reg_query)
    if reg_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="You are already registered for this event")
        
    # 3. Create registration and update capacity safely
    new_reg = Registration(user_id=user_id, event_id=event_id)
    event.current_enrollment += 1
    
    db.add(new_reg)
    await db.commit()
    await db.refresh(new_reg)
    return new_reg

async def cancel_registration(db: AsyncSession, user_id: int, event_id: int):
    # Lock the event row to safely decrement the capacity
    query = select(Event).where(Event.id == event_id).with_for_update()
    result = await db.execute(query)
    event = result.scalar_one_or_none()
    
    # Find the active registration
    reg_query = select(Registration).where(
        Registration.user_id == user_id, 
        Registration.event_id == event_id,
        Registration.status == RegistrationStatusEnum.CONFIRMED
    )
    reg_result = await db.execute(reg_query)
    registration = reg_result.scalar_one_or_none()
    
    if not registration:
        raise HTTPException(status_code=404, detail="Active registration not found")
        
    # Free up the spot
    registration.status = RegistrationStatusEnum.CANCELLED
    if event and event.current_enrollment > 0:
        event.current_enrollment -= 1
    
    await db.commit()
    return {"detail": "Registration cancelled. Capacity freed."}
    
async def get_user_registrations(db: AsyncSession, user_id: int):
    query = select(Registration).where(
        Registration.user_id == user_id,
        Registration.status == RegistrationStatusEnum.CONFIRMED
    )
    result = await db.execute(query)
    return result.scalars().all()