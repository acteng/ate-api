from functools import lru_cache
from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.sql.ddl import CreateSchema

from ate_api.infrastructure.database import (
    BaseEntity,
    BidStatusEntity,
    BidStatusName,
    MilestoneEntity,
    MilestoneName,
    ObservationTypeEntity,
    ObservationTypeName,
    SchemeTypeEntity,
    SchemeTypeName,
)
from ate_api.settings import Settings, get_settings


@lru_cache
def get_engine(settings: Annotated[Settings, Depends(get_settings)]) -> AsyncEngine:
    return create_async_engine(settings.database_url)


async def get_session(engine: Annotated[AsyncEngine, Depends(get_engine)]) -> AsyncGenerator[AsyncSession]:
    async with AsyncSession(engine) as session:
        yield session


async def create_database_schema(engine: AsyncEngine) -> None:
    if not await _schema_exists(engine):
        await _create_schema(engine)
        await _create_reference_data(engine)


async def _schema_exists(engine: AsyncEngine) -> bool:
    async with engine.begin() as connection:
        result = await connection.execute(
            text(
                "SELECT EXISTS(SELECT schema_name FROM information_schema.schemata WHERE schema_name = :schema_name);"
            ),
            {"schema_name": "authority"},
        )
        return bool(result.scalar_one())


async def _create_schema(engine: AsyncEngine) -> None:
    async with engine.begin() as connection:
        await connection.execute(CreateSchema("authority"))
        await connection.execute(CreateSchema("capital_scheme"))
        await connection.execute(CreateSchema("common"))
        await connection.run_sync(BaseEntity.metadata.create_all)


async def _create_reference_data(engine: AsyncEngine) -> None:
    async with AsyncSession(engine) as session:
        # common
        session.add_all(
            [
                ObservationTypeEntity(observation_type_name=observation_type_name)
                for observation_type_name in ObservationTypeName
            ]
        )
        # capital_scheme
        session.add_all([BidStatusEntity(bid_status_name=bid_status_name) for bid_status_name in BidStatusName])
        session.add_all(
            [
                MilestoneEntity(milestone_name=milestone_name, stage_order=index)
                for index, milestone_name in enumerate(MilestoneName)
            ]
        )
        session.add_all([SchemeTypeEntity(scheme_type_name=scheme_type_name) for scheme_type_name in SchemeTypeName])
        await session.commit()
