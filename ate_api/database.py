from functools import lru_cache
from typing import Annotated, Generator

from fastapi.params import Depends
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session
from sqlalchemy.sql.ddl import CreateSchema

from ate_api.infrastructure.database import BaseEntity
from ate_api.settings import Settings, get_settings


@lru_cache
def get_engine(settings: Annotated[Settings, Depends(get_settings)]) -> Engine:
    engine = create_engine(settings.database_url)

    if settings.create_database_schema and not _schema_exists(engine):
        _create_schema(engine)

    return engine


def get_session(engine: Annotated[Engine, Depends(get_engine)]) -> Generator[Session]:
    with Session(engine) as session:
        yield session


def _schema_exists(engine: Engine) -> bool:
    with engine.begin() as connection:
        result = connection.execute(
            text(
                "SELECT EXISTS(SELECT schema_name FROM information_schema.schemata WHERE schema_name = :schema_name);"
            ),
            {"schema_name": "authority"},
        )
        return bool(result.scalar_one())


def _create_schema(engine: Engine) -> None:
    with engine.begin() as connection:
        connection.execute(CreateSchema("authority"))
        connection.execute(CreateSchema("capital_scheme"))

    BaseEntity.metadata.create_all(engine)
