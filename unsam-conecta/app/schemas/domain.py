from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from app.models.domain import RoleEnum, NotificationChannelEnum, EventStatusEnum, RegistrationStatusEnum

# ---------------------------------------------------------
# ESQUEMAS DE USUARIO
# ---------------------------------------------------------
class UserBase(BaseModel):
    email: str
    full_name: str
    dni: Optional[str] = None
    phone: Optional[str] = None
    interests: List[str] = []
    preferred_notification_channel: NotificationChannelEnum = NotificationChannelEnum.EMAIL
    role: Optional[RoleEnum] = RoleEnum.USER

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

# ---------------------------------------------------------
# ESQUEMAS DE EVENTO
# ---------------------------------------------------------
class EventBase(BaseModel):
    title: str
    description: str
    category: str
    location: str
    start_time: datetime
    end_time: datetime
    capacity: int
    tags: List[str] = []

class EventCreate(EventBase):
    pass

class EventResponse(EventBase):
    id: int
    organizer_id: int
    current_enrollment: int
    status: EventStatusEnum

    model_config = ConfigDict(from_attributes=True)

# ---------------------------------------------------------
# ESQUEMAS DE INSCRIPCIÓN (REGISTRATIONS)
# ---------------------------------------------------------
class RegistrationResponse(BaseModel):
    id: int
    user_id: int
    event_id: int
    status: RegistrationStatusEnum
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ---------------------------------------------------------
# ESQUEMAS DE RESEÑAS (REVIEWS)
# ---------------------------------------------------------
class ReviewCreate(BaseModel):
    rating: int
    comment: Optional[str] = None

class ReviewResponse(BaseModel):
    id: int
    registration_id: int
    rating: int
    comment: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)