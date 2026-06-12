import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import settings
from app.api.v1.api import api_router
from app.core.database import engine, Base
from app.core.email_utils import process_event_reminders

# ---------------------------------------------------------
# PLANIFICADOR DE TAREAS EN SEGUNDO PLANO
# ---------------------------------------------------------
scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('interval', minutes=1)
async def scheduled_reminders():
    print("🕒 Escaneando eventos próximos para enviar recordatorios...")
    await process_event_reminders()

# ---------------------------------------------------------
# CICLO DE VIDA DE LA APLICACIÓN (LIFESPAN)
# ---------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    # Iniciar el planificador de correos al prender el servidor
    scheduler.start()
    print("✅ Motor de envíos automatizados iniciado.")
    
    yield
    
    # Apagar el planificador de correos de forma segura
    scheduler.shutdown()
    print("🛑 Motor de envíos automatizados detenido.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

# ---------------------------------------------------------
# RUTAS DE LA APLICACIÓN WEB (FRONTEND)
# ---------------------------------------------------------
@app.get("/")
async def serve_frontend(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "UNSAM Conecta"})

@app.get("/registro")
async def serve_register(request: Request):
    return templates.TemplateResponse("registro.html", {"request": request, "title": "Registro"})

@app.get("/login")
async def serve_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "title": "Iniciar Sesión"})

@app.get("/eventos")
async def serve_eventos(request: Request):
    return templates.TemplateResponse("eventos.html", {"request": request, "title": "Eventos"})

@app.get("/crear-evento")
async def serve_crear_evento(request: Request):
    return templates.TemplateResponse("crear_evento.html", {"request": request, "title": "Crear Evento"})

@app.get("/mis-inscripciones")
async def serve_mis_inscripciones(request: Request):
    return templates.TemplateResponse("mis_inscripciones.html", {"request": request, "title": "Mis Inscripciones"})

# ---------------------------------------------------------
# RUTAS DE CONTROL DE SISTEMA
# ---------------------------------------------------------
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "project": settings.PROJECT_NAME, "environment": settings.ENVIRONMENT}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)