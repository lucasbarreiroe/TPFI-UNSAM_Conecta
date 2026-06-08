from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from app.models.domain import RoleEnum, NotificationChannelEnum, EventStatusEnum, RegistrationStatusEnum

# --- USER SCHEMAS ---
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    dni: Optional[str] = None
    phone: Optional[str] = None
    interests: List[str] = []
    preferred_notification_channel: NotificationChannelEnum = NotificationChannelEnum.EMAIL

class UserCreate(UserBase):
    password: str = Field(min_length=8)

class UserResponse(UserBase):
    id: int
    role: RoleEnum
    
    model_config = ConfigDict(from_attributes=True)

# --- EVENT SCHEMAS ---
class EventBase(BaseModel):
    title: str
    description: str
    category: str
    location: str
    start_time: datetime
    end_time: datetime
    capacity: int = Field(gt=0)
    tags: List[str] = []

class EventCreate(EventBase):
    pass

class EventResponse(EventBase):
    id: int
    organizer_id: int
    current_enrollment: int
    status: EventStatusEnum
    
    model_config = ConfigDict(from_attributes=True)

# --- REGISTRATION SCHEMAS ---
class RegistrationResponse(BaseModel):
    id: int
    user_id: int
    event_id: int
    status: RegistrationStatusEnum
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# --- REVIEW SCHEMAS ---
class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None

class ReviewResponse(ReviewCreate):
    id: int
    registration_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)