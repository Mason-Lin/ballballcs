import pytest
from fastapi import status

from app.health import router


@pytest.mark.asyncio
async def test_hello(async_app_client):
    response = await async_app_client.get("/")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_ping_route(async_app_client):
    response = await async_app_client.get("/ping")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_health_normal():
    response = await router.health()
    assert response == {"status": "ok"}


@pytest.mark.asyncio
async def test_info(async_app_client):
    response = await async_app_client.get("/info")
    assert response.status_code == status.HTTP_200_OK
