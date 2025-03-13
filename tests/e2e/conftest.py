from typing import Generator

import pytest
from httpx import Client

from ate_api.main import app
from tests.e2e.server import Server


@pytest.fixture(name="server")
def server_fixture() -> Generator[Server, None, None]:
    server = Server(app)
    server.start()
    yield server
    server.stop()


@pytest.fixture(name="client")
def client_fixture(server: Server) -> Client:
    return Client(base_url=server.url)
