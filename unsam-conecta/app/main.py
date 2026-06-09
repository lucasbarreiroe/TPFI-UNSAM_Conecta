from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.config import settings
from app.api.v1.api import api_router
from app.core.database import engine, Base

# ---------------------------------------------------------
# CICLO DE VIDA DE LA APLICACIÓN (LIFESPAN)
# ---------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Esto se ejecuta una única vez al iniciar el servidor.
    # Verifica y crea de forma automática las tablas en Supabase si no existen.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Lógica de apagado en caso de ser requerida (limpieza de recursos).

# Inicialización de la aplicación FastAPI conectada al ciclo de vida
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# 1. Configuración de directorios para archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Configuración del motor de renderizado de plantillas Jinja2
templates = Jinja2Templates(directory="templates")

# 3. Configuración de la política CORS para conectividad del Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ajustar a las URLs específicas en entornos de producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Inclusión de las rutas originales de la API
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

# ---------------------------------------------------------
# RUTAS DE CONTROL DE SISTEMA
# ---------------------------------------------------------
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)