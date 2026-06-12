import enum
from datetime import datetime, timezone
from sqlalchemy import String, Integer, ForeignKey, DateTime, Enum, Text, ARRAY, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

# Enums based on your architecture
class RoleEnum(str, enum.Enum):
    USER = "USER"
    ORGANIZER = "ORGANIZER"
    EXTERNAL_PREMIUM = "EXTERNAL_PREMIUM"
    ADMIN = "ADMIN"

class NotificationChannelEnum(str, enum.Enum):
    EMAIL = "EMAIL"
    PHONE = "PHONE"

class EventStatusEnum(str, enum.Enum):
    PUBLISHED = "PUBLISHED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"

class RegistrationStatusEnum(str, enum.Enum):
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"

# Database Models
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[RoleEnum] = mapped_column(Enum(RoleEnum), default=RoleEnum.USER, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    dni: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    phone: Mapped[str] = mapped_column(String, nullable=True)
    interests: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])
    preferred_notification_channel: Mapped[NotificationChannelEnum] = mapped_column(
        Enum(NotificationChannelEnum), default=NotificationChannelEnum.EMAIL
    )

    # Relationships
    events_organized = relationship("Event", back_populates="organizer")
    registrations = relationship("Registration", back_populates="user")

class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    organizer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    category: Mapped[str] = mapped_column(String, index=True, nullable=False)
    location: Mapped[str] = mapped_column(String, nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    current_enrollment: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[EventStatusEnum] = mapped_column(Enum(EventStatusEnum), default=EventStatusEnum.PUBLISHED)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=[])
    
    # NUEVO: Controles para evitar mandar el mismo recordatorio dos veces
    reminder_24h_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reminder_1h_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    organizer = relationship("User", back_populates="events_organized")
    registrations = relationship("Registration", back_populates="event")

class Registration(Base):
    __tablename__ = "registrations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=False)
    status: Mapped[RegistrationStatusEnum] = mapped_column(
        Enum(RegistrationStatusEnum), default=RegistrationStatusEnum.CONFIRMED
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    user = relationship("User", back_populates="registrations")
    event = relationship("Event", back_populates="registrations")
    review = relationship("Review", back_populates="registration", uselist=False)

class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    registration_id: Mapped[int] = mapped_column(ForeignKey("registrations.id"), unique=True, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    registration = relationship("Registration", back_populates="review")