from functools import lru_cache
from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.sql.ddl import CreateSchema

from ate_api.domain.capital_schemes.bid_statuses import BidStatus
from ate_api.domain.capital_schemes.milestones import Milestone
from ate_api.domain.capital_schemes.outputs import OutputMeasure, OutputType
from ate_api.domain.capital_schemes.overviews import CapitalSchemeType
from ate_api.domain.financial_types import FinancialType
from ate_api.domain.observation_types import ObservationType
from ate_api.infrastructure.database import (
    BaseEntity,
    BidStatusEntity,
    BidStatusName,
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
                FinancialTypeEntity(financial_type_name=FinancialTypeName.from_domain(financial_type))
                for financial_type in FinancialType
            ]
        )
        session.add_all(
            [
                ObservationTypeEntity(observation_type_name=ObservationTypeName.from_domain(observation_type))
                for observation_type in ObservationType
            ]
        )
        # capital_scheme
        session.add_all(
            [BidStatusEntity(bid_status_name=BidStatusName.from_domain(bid_status)) for bid_status in BidStatus]
        )
        intervention_measures = {
            measure: InterventionMeasureEntity(intervention_measure_name=InterventionMeasureName.from_domain(measure))
            for measure in OutputMeasure
        }
        session.add_all(intervention_measures.values())
        intervention_types = {
            type_: InterventionTypeEntity(intervention_type_name=InterventionTypeName.from_domain(type_))
            for type_ in OutputType
        }
        session.add_all(intervention_types.values())
        session.add_all(
            [
                InterventionTypeMeasureEntity(
                    intervention_type=intervention_types[type_], intervention_measure=intervention_measures[measure]
                )
                for (type_, measure) in _get_output_type_measures()
            ]
        )
        session.add_all(
            [
                MilestoneEntity(
                    milestone_name=MilestoneName.from_domain(milestone),
                    stage_order=index,
                    is_active=milestone.is_active,
                    is_complete=milestone.is_complete,
                )
                for index, milestone in enumerate(Milestone)
            ]
        )
        session.add_all(
            [SchemeTypeEntity(scheme_type_name=SchemeTypeName.from_domain(type_)) for type_ in CapitalSchemeType]
        )
        await session.commit()


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
