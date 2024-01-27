import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app


@pytest.fixture(scope="module")
def test_app():
    client = TestClient(app)
    yield client


@pytest.fixture(scope="module")
def async_app_client():
    client = AsyncClient(app=app, base_url="http://localhost:8080/")
    yield client
