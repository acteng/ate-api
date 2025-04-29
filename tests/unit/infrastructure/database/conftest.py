from typing import Generator

import pytest
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.sql.ddl import CreateSchema
from testcontainers.postgres import PostgresContainer

from ate_api.infrastructure.database import BaseEntity


@pytest.fixture(name="database_url", scope="package")
def database_url_fixture() -> Generator[str]:
    with PostgresContainer("postgres:16") as postgres:
        yield postgres.get_connection_url(driver="pg8000")


@pytest.fixture(name="engine", scope="package")
def engine_fixture(database_url: str) -> Engine:
    engine = create_engine(database_url)
    _create_schema(engine)
    return engine


@pytest.fixture(name="data", autouse=True)
def data_fixture(engine: Engine) -> Generator[None]:
    yield
    _delete_all(engine)


def _create_schema(engine: Engine) -> None:
    with engine.begin() as connection:
        connection.execute(CreateSchema("authority"))
        connection.execute(CreateSchema("capital_scheme"))

    BaseEntity.metadata.create_all(engine)


def _delete_all(engine: Engine) -> None:
    with engine.begin() as connection:
        connection.execute(
            text("TRUNCATE authority.authority, capital_scheme.capital_scheme, capital_scheme.scheme_type CASCADE;")
        )
