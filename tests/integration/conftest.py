import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from ate_api.main import app


@pytest.fixture(name="app")
def app_fixture() -> FastAPI:
    return app


@pytest.fixture(name="client")
def client_fixture(app: FastAPI) -> TestClient:
    return TestClient(app)
