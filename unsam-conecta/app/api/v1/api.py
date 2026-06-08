from fastapi import APIRouter
from app.api.v1.endpoints import auth, events, registrations

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(events.router, prefix="/events", tags=["Events"])
# Note: Registration routes don't have a prefix here because they are nested 
# under /events and /users inside the file itself to make the URL paths cleaner.
api_router.include_router(registrations.router, tags=["Registrations"])