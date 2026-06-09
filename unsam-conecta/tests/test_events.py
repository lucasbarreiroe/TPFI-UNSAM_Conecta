import pytest
from httpx import AsyncClient
from sqlalchemy.future import select
from tests.conftest import TestingSessionLocal
from app.models.domain import User, RoleEnum

@pytest.mark.asyncio
async def test_get_events_empty(client: AsyncClient):
    response = await client.get("/api/v1/events/")
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.asyncio
async def test_create_event_unauthorized(client: AsyncClient):
    event_payload = {
        "title": "Data Science Seminar",
        "description": "Introduction to Bayesian Inference",
        "category": "ECyT",
        "location": "Tornavía",
        "start_time": "2026-11-01T10:00:00Z",
        "end_time": "2026-11-01T12:00:00Z",
        "capacity": 50
    }
    
    response = await client.post("/api/v1/events/", json=event_payload)
    assert response.status_code == 401 

@pytest.mark.asyncio
async def test_create_event_authorized(client: AsyncClient):
    # 1. Registrar un usuario (nace como USER)
    await client.post("/api/v1/auth/register", json={
        "email": "organizador@unsam.edu.ar",
        "password": "securepassword",
        "full_name": "Organizador UNSAM"
    })
    
    # 2. Ascenderlo a ORGANIZER usando el ORM para respetar la validación de PostgreSQL
    async with TestingSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == "organizador@unsam.edu.ar"))
        user = result.scalar_one()
        user.role = RoleEnum.ORGANIZER
        await session.commit()
    
    # 3. Iniciar sesión
    login_res = await client.post("/api/v1/auth/login", data={
        "username": "organizador@unsam.edu.ar",
        "password": "securepassword"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 4. Crear el evento
    event_payload = {
        "title": "Workshop de Python",
        "description": "Aplicaciones en Data Science",
        "category": "ECyT",
        "location": "Aulario",
        "start_time": "2026-12-01T10:00:00Z",
        "end_time": "2026-12-01T12:00:00Z",
        "capacity": 30
    }
    
    response = await client.post("/api/v1/events/", json=event_payload, headers=headers)
    assert response.status_code == 201
    assert response.json()["title"] == "Workshop de Python"