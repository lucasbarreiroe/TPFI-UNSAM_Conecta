import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    payload = {
        "email": "teststudent@unsam.edu.ar",
        "password": "strongpassword123",
        "full_name": "Test Student",
        "dni": "12345678",
        "preferred_notification_channel": "EMAIL"
    }
    
    response = await client.post("/api/v1/auth/register", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "teststudent@unsam.edu.ar"
    assert data["role"] == "USER"

@pytest.mark.asyncio
async def test_register_duplicate_user(client: AsyncClient):
    payload = {
        "email": "duplicate@unsam.edu.ar",
        "password": "strongpassword123",
        "full_name": "Test Student 2"
    }
    
    await client.post("/api/v1/auth/register", json=payload)
    response = await client.post("/api/v1/auth/register", json=payload)
    
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_login_user(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "email": "login@unsam.edu.ar",
        "password": "loginpass123",
        "full_name": "Login User"
    })
    
    response = await client.post("/api/v1/auth/login", data={
        "username": "login@unsam.edu.ar",
        "password": "loginpass123"
    })
    
    assert response.status_code == 200
    assert "access_token" in response.json()