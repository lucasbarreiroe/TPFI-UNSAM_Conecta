from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from pydantic import BaseModel
from jose import jwt, JWTError

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, create_verification_token
from app.core.config import settings
from app.core.email_utils import send_verification_email
from app.models.domain import User
from app.schemas.domain import UserCreate, UserResponse
from app.api.deps import get_current_user

router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate, 
    background_tasks: BackgroundTasks, 
    db: AsyncSession = Depends(get_db)
):
    query = select(User).where(
        or_(User.email == user_in.email, User.dni == user_in.dni)
    )
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        if existing_user.email == user_in.email:
            raise HTTPException(status_code=400, detail="Este correo electrónico ya está registrado.")
        if existing_user.dni == user_in.dni:
            raise HTTPException(status_code=400, detail="Este DNI ya está registrado en otra cuenta.")
    
    db_user = User(
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        dni=user_in.dni,
        phone=user_in.phone,
        interests=user_in.interests,
        preferred_notification_channel=user_in.preferred_notification_channel,
        role=user_in.role,
        is_verified=False # Nace bloqueado
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    # Crear token y enviar correo en SEGUNDO PLANO
    verification_token = create_verification_token(email=db_user.email)
    background_tasks.add_task(send_verification_email, db_user.email, verification_token)

    # # Crear token y enviar correo de forma ASÍNCRONA (No bloquea la respuesta)
    # verification_token = create_verification_token(email=db_user.email)
    
    # # Agregamos el 'await' aquí:
    # await send_verification_email(db_user.email, verification_token)

    return db_user

# NUEVO: Endpoint para verificar desde el correo
@router.get("/verify")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        if payload.get("type") != "email_verification":
            raise HTTPException(status_code=400, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=400, detail="El enlace ha expirado o es inválido")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    user.is_verified = True
    await db.commit()

    # Redirige al login del frontend avisando que fue exitoso
    return RedirectResponse(url="/login?verified=true")

@router.post("/login", response_model=Token)
async def login(
    db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # NUEVO: Bloqueo si no está verificado
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Por favor, revisa tu correo y verifica tu cuenta antes de iniciar sesión."
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user