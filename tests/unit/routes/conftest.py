import pytest
from fastapi import FastAPI, Request

from ate_api.main import app


@pytest.fixture(name="app")
def app_fixture() -> FastAPI:
    return app


@pytest.fixture(name="host")
def host_fixture() -> str:
    return "example.com"


@pytest.fixture(name="http_request")
def http_request_fixture(app: FastAPI, host: str) -> Request:
    return Request({"type": "http", "app": app, "headers": [(b"host", host.encode())]})


@pytest.fixture(name="base_url")
def base_url(host: str) -> str:
    return f"http://{host}"
