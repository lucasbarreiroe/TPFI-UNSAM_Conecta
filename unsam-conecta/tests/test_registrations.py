import pytest
from httpx import AsyncClient
from sqlalchemy.future import select
from tests.conftest import TestingSessionLocal
from app.models.domain import User, RoleEnum

@pytest.mark.asyncio
async def test_register_for_event(client: AsyncClient):
    # --- PARTE 1: EL ORGANIZADOR CREA EL EVENTO ---
    await client.post("/api/v1/auth/register", json={
        "email": "org_eventos@unsam.edu.ar",
        "password": "password123",
        "full_name": "Org"
    })
    
    # Ascender al usuario usando el ORM
    async with TestingSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == "org_eventos@unsam.edu.ar"))
        user = result.scalar_one()
        user.role = RoleEnum.ORGANIZER
        await session.commit()

    log_org = await client.post("/api/v1/auth/login", data={
        "username": "org_eventos@unsam.edu.ar",
        "password": "password123"
    })
    org_headers = {"Authorization": f"Bearer {log_org.json()['access_token']}"}

    event_payload = {
        "title": "Introducción a FastAPI",
        "description": "Desarrollo Backend",
        "category": "EEyN",
        "location": "Virtual",
        "start_time": "2026-12-10T15:00:00Z",
        "end_time": "2026-12-10T17:00:00Z",
        "capacity": 50
    }
    event_res = await client.post("/api/v1/events/", json=event_payload, headers=org_headers)
    assert event_res.status_code == 201
    event_id = event_res.json()["id"]

    # --- PARTE 2: EL ESTUDIANTE SE ANOTA ---
    await client.post("/api/v1/auth/register", json={
        "email": "estudiante@unsam.edu.ar",
        "password": "password123",
        "full_name": "Estudiante Prueba"
    })
    
    log_estu = await client.post("/api/v1/auth/login", data={
        "username": "estudiante@unsam.edu.ar",
        "password": "password123"
    })
    estu_headers = {"Authorization": f"Bearer {log_estu.json()['access_token']}"}

    # 3. Anotar al estudiante al evento (¡usando la URL de tu api.py!)
    reg_res = await client.post(f"/api/v1/events/{event_id}/register", headers=estu_headers)
    
    assert reg_res.status_code == 201
    reg_data = reg_res.json()
    assert reg_data["event_id"] == event_id
    assert reg_data["status"] == "CONFIRMED"

    # 4. Intentar anotarse de nuevo (debería fallar por duplicado)
    duplicate_res = await client.post(f"/api/v1/events/{event_id}/register", headers=estu_headers)
    assert duplicate_res.status_code == 400