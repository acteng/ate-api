import pytest
from fastapi.testclient import TestClient

from ate_api.main import app


@pytest.fixture(name="client")
def client_fixture() -> TestClient:
    return TestClient(app)
