from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.core.config import settings
from app.api.v1.api import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 1. Configurar la carpeta "static" para CSS y archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Configurar el motor de plantillas Jinja2
templates = Jinja2Templates(directory="templates")

# Configure CORS for Frontend connectivity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your specific frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Wire up the API routes
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

# ---------------------------------------------------------
# RUTAS DE SISTEMA
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