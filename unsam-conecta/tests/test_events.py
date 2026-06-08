import pytest
from httpx import AsyncClient

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