from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.domain import User
from app.schemas.domain import EventResponse

from app.services.recommendations import get_recommended_events

router = APIRouter()


@router.get(
    "/me/recommendations",
    response_model=List[EventResponse]
)
async def my_recommendations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await get_recommended_events(
        db,
        current_user.id
    )