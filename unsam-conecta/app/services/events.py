from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.domain import Event
from app.schemas.domain import EventCreate

async def get_events(db: AsyncSession, skip: int = 0, limit: int = 100, category: str = None, tag: str = None):
    query = select(Event)
    if category:
        query = query.where(Event.category == category)
    if tag:
        query = query.where(Event.tags.any(tag))
        
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_event(db: AsyncSession, event_id: int):
    result = await db.execute(select(Event).where(Event.id == event_id))
    return result.scalar_one_or_none()

async def create_event(db: AsyncSession, event_in: EventCreate, organizer_id: int):
    db_event = Event(
        title=event_in.title,
        description=event_in.description,
        category=event_in.category,
        location=event_in.location,
        start_time=event_in.start_time,
        end_time=event_in.end_time,
        capacity=event_in.capacity,
        tags=event_in.tags,
        organizer_id=organizer_id
    )
    db.add(db_event)
    await db.commit()
    await db.refresh(db_event)
    return db_event

async def delete_event(db: AsyncSession, event_id: int):
    event = await get_event(db, event_id)
    if event:
        await db.delete(event)
        await db.commit()
    return event