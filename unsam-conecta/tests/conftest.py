import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool

from app.main import app
from app.core.database import get_db, Base
from app.core.config import settings

TEST_DATABASE_URL = settings.DATABASE_URL.replace("unsam_conecta", "unsam_conecta_test")

# NullPool es clave aquí: fuerza a crear una conexión limpia para cada test
test_engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
TestingSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
async def setup_db():
    # Creamos las tablas
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield # Aquí es donde se ejecuta el test
    
    # Destruimos las tablas
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        
    # Limpiamos el motor para que no queden conexiones fantasma para el siguiente test
    await test_engine.dispose()

@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://testserver"
    ) as ac:
        yield ac