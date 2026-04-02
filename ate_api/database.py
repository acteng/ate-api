from functools import lru_cache
from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.sql.ddl import CreateSchema

from ate_api.domain.capital_scheme_milestones import Milestone
from ate_api.domain.capital_schemes.bid_statuses import BidStatus
from ate_api.domain.capital_schemes.outputs import OutputMeasure, OutputType
from ate_api.domain.capital_schemes.overviews import CapitalSchemeType
from ate_api.domain.data_sources import DataSource
from ate_api.domain.financial_types import FinancialType
from ate_api.domain.observation_types import ObservationType
from ate_api.infrastructure.database import (
    BaseEntity,
    BidStatusEntity,
    BidStatusName,
    DataSourceEntity,
    DataSourceName,
    FinancialTypeEntity,
    FinancialTypeName,
    InterventionMeasureEntity,
    InterventionMeasureName,
    InterventionTypeEntity,
    InterventionTypeMeasureEntity,
    InterventionTypeName,
    MilestoneEntity,
    MilestoneName,
    ObservationTypeEntity,
    ObservationTypeName,
    SchemeTypeEntity,
    SchemeTypeName,
)
from ate_api.infrastructure.database.unit_of_work import DatabaseUnitOfWork
from ate_api.settings import Settings, get_settings
from ate_api.unit_of_work import UnitOfWork


@lru_cache
def get_engine(settings: Annotated[Settings, Depends(get_settings)]) -> AsyncEngine:
    return create_async_engine(settings.database_url, pool_pre_ping=True)


async def get_session(engine: Annotated[AsyncEngine, Depends(get_engine)]) -> AsyncGenerator[AsyncSession]:
    async with AsyncSession(engine) as session:
        yield session


def get_unit_of_work(session: Annotated[AsyncSession, Depends(get_session)]) -> UnitOfWork:
    return DatabaseUnitOfWork(session)


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
        session.add_all(_create_data_sources())
        session.add_all(_create_financial_types())
        session.add_all(_create_observation_types())
        # capital_scheme
        session.add_all(_create_bid_statuses())
        intervention_types = _create_intervention_types()
        session.add_all(intervention_types.values())
        intervention_measures = _create_intervention_measures()
        session.add_all(intervention_measures.values())
        session.add_all(_create_intervention_type_measures(intervention_types, intervention_measures))
        session.add_all(_create_milestones())
        session.add_all(_create_scheme_types())
        await session.commit()


def _create_data_sources() -> list[DataSourceEntity]:
    return [DataSourceEntity(data_source_name=DataSourceName.from_domain(data_source)) for data_source in DataSource]


def _create_financial_types() -> list[FinancialTypeEntity]:
    return [
        FinancialTypeEntity(financial_type_name=FinancialTypeName.from_domain(financial_type))
        for financial_type in FinancialType
    ]


def _create_observation_types() -> list[ObservationTypeEntity]:
    return [
        ObservationTypeEntity(observation_type_name=ObservationTypeName.from_domain(observation_type))
        for observation_type in ObservationType
    ]


def _create_bid_statuses() -> list[BidStatusEntity]:
    return [BidStatusEntity(bid_status_name=BidStatusName.from_domain(bid_status)) for bid_status in BidStatus]


def _create_intervention_measures() -> dict[OutputMeasure, InterventionMeasureEntity]:
    return {
        measure: InterventionMeasureEntity(intervention_measure_name=InterventionMeasureName.from_domain(measure))
        for measure in OutputMeasure
    }


def _create_intervention_types() -> dict[OutputType, InterventionTypeEntity]:
    return {
        type_: InterventionTypeEntity(intervention_type_name=InterventionTypeName.from_domain(type_))
        for type_ in OutputType
    }


def _create_intervention_type_measures(
    intervention_types: dict[OutputType, InterventionTypeEntity],
    intervention_measures: dict[OutputMeasure, InterventionMeasureEntity],
) -> list[InterventionTypeMeasureEntity]:
    return [
        InterventionTypeMeasureEntity(
            intervention_type=intervention_types[type_], intervention_measure=intervention_measures[measure]
        )
        for (type_, measure) in _get_output_type_measures()
    ]


def _get_output_type_measures() -> list[tuple[OutputType, OutputMeasure]]:
    return [
        (OutputType.WIDENING_EXISTING_FOOTWAY, OutputMeasure.MILES),
        (OutputType.RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY, OutputMeasure.MILES),
        (OutputType.BUS_PRIORITY_MEASURES, OutputMeasure.MILES),
        (OutputType.IMPROVEMENTS_TO_EXISTING_ROUTE, OutputMeasure.MILES),
        (OutputType.NEW_SHARED_USE_WALKING_WHEELING_AND_CYCLING_FACILITIES, OutputMeasure.MILES),
        (OutputType.NEW_SHARED_USE_WALKING_AND_CYCLING_FACILITIES, OutputMeasure.MILES),
        (OutputType.NEW_TEMPORARY_FOOTWAY, OutputMeasure.MILES),
        (OutputType.NEW_PERMANENT_FOOTWAY, OutputMeasure.MILES),
        (OutputType.NEW_TEMPORARY_SEGREGATED_CYCLING_FACILITY, OutputMeasure.MILES),
        (OutputType.NEW_SEGREGATED_CYCLING_FACILITY, OutputMeasure.MILES),
        (OutputType.IMPROVEMENTS_TO_EXISTING_ROUTE, OutputMeasure.NUMBER_OF_JUNCTIONS),
        (OutputType.NEW_PERMANENT_FOOTWAY, OutputMeasure.NUMBER_OF_JUNCTIONS),
        (OutputType.NEW_JUNCTION_TREATMENT, OutputMeasure.NUMBER_OF_JUNCTIONS),
        (OutputType.NEW_TEMPORARY_SEGREGATED_CYCLING_FACILITY, OutputMeasure.NUMBER_OF_JUNCTIONS),
        (OutputType.NEW_SEGREGATED_CYCLING_FACILITY, OutputMeasure.NUMBER_OF_JUNCTIONS),
        (OutputType.AREA_WIDE_TRAFFIC_MANAGEMENT, OutputMeasure.SIZE_OF_AREA),
        (OutputType.PARK_AND_CYCLE_STRIDE_FACILITIES, OutputMeasure.NUMBER_OF_PARKING_SPACES),
        (OutputType.RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY, OutputMeasure.NUMBER_OF_PARKING_SPACES),
        (OutputType.SECURE_CYCLE_PARKING, OutputMeasure.NUMBER_OF_PARKING_SPACES),
        (OutputType.NEW_ROAD_CROSSINGS, OutputMeasure.NUMBER_OF_CROSSINGS),
        (OutputType.SCHOOL_STREETS, OutputMeasure.NUMBER_OF_SCHOOL_STREETS),
        (OutputType.E_SCOOTER_TRIALS, OutputMeasure.NUMBER_OF_TRIALS),
        (OutputType.BUS_PRIORITY_MEASURES, OutputMeasure.NUMBER_OF_BUS_GATES),
        (OutputType.UPGRADES_TO_EXISTING_FACILITIES, OutputMeasure.NUMBER_OF_UPGRADES),
        (OutputType.SCHOOL_STREETS, OutputMeasure.NUMBER_OF_CHILDREN_AFFECTED),
        (OutputType.OTHER_INTERVENTIONS, OutputMeasure.NUMBER_OF_MEASURES_PLANNED),
        (OutputType.TRAFFIC_CALMING, OutputMeasure.NUMBER_OF_MEASURES_PLANNED),
    ]


def _create_milestones() -> list[MilestoneEntity]:
    return [
        MilestoneEntity(
            milestone_name=MilestoneName.from_domain(milestone),
            stage_order=index,
            is_active=milestone.is_active,
            is_complete=milestone.is_complete,
        )
        for index, milestone in enumerate(Milestone)
    ]


def _create_scheme_types() -> list[SchemeTypeEntity]:
    return [SchemeTypeEntity(scheme_type_name=SchemeTypeName.from_domain(type_)) for type_ in CapitalSchemeType]
