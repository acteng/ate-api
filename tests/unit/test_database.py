import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

from ate_api.database import get_engine
from ate_api.settings import Settings


@pytest.fixture(name="engine")
def engine_fixture() -> AsyncEngine:
    return get_engine(Settings())


def test_pool_pings_connections(engine: AsyncEngine) -> None:
    assert engine.pool._pre_ping is True
