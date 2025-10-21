from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.sql.ddl import CreateSchema
from testcontainers.postgres import PostgresContainer

from ate_api.infrastructure.database import BaseEntity


@pytest.fixture(name="debug", scope="package")
def debug_fixture() -> bool:
    return False


@pytest.fixture(name="database_url", scope="package")
def database_url_fixture() -> Generator[str]:
    with PostgresContainer("postgres:16") as postgres:
        yield postgres.get_connection_url(driver="asyncpg")


@pytest.fixture(name="engine", scope="package")
async def engine_fixture(database_url: str, debug: bool) -> AsyncEngine:
    engine = create_async_engine(database_url, echo=debug)
    await _create_schema(engine)
    return engine


@pytest_asyncio.fixture(name="data", loop_scope="package")
async def data_fixture(engine: AsyncEngine) -> AsyncGenerator[None]:
    yield
    await _delete_all(engine)


async def _create_schema(engine: AsyncEngine) -> None:
    async with engine.begin() as connection:
        await connection.execute(CreateSchema("authority"))
        await connection.execute(CreateSchema("capital_scheme"))
        await connection.execute(CreateSchema("common"))
        await connection.run_sync(BaseEntity.metadata.create_all)


async def _delete_all(engine: AsyncEngine) -> None:
    async with engine.begin() as connection:
        await connection.execute(
            text(
                """
                TRUNCATE
                    authority.authority,
                    capital_scheme.bid_status,
                    capital_scheme.capital_scheme,
                    capital_scheme.intervention_measure,
                    capital_scheme.intervention_type,
                    capital_scheme.milestone,
                    capital_scheme.scheme_type,
                    common.data_source,
                    common.financial_type,
                    common.funding_programme,
                    common.observation_type
                CASCADE;
                """
            )
        )
