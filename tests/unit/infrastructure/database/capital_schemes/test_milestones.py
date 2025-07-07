from datetime import date, datetime, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from ate_api.domain.capital_schemes.milestones import CapitalSchemeMilestone, Milestone
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.observation_types import ObservationType
from ate_api.infrastructure.database import (
    CapitalSchemeMilestoneEntity,
    MilestoneEntity,
    MilestoneName,
    ObservationTypeEntity,
    ObservationTypeName,
)
from ate_api.infrastructure.database.capital_schemes.milestones import DatabaseMilestoneRepository


class TestMilestoneName:
    def test_from_domain(self) -> None:
        assert MilestoneName.from_domain(Milestone.DETAILED_DESIGN_COMPLETED) == MilestoneName.DETAILED_DESIGN_COMPLETED

    def test_to_domain(self) -> None:
        assert MilestoneName.DETAILED_DESIGN_COMPLETED.to_domain() == Milestone.DETAILED_DESIGN_COMPLETED


class TestCapitalSchemeMilestoneEntity:
    def test_from_domain(self) -> None:
        milestone = CapitalSchemeMilestone(
            effective_date=DateTimeRange(datetime(2020, 1, 1), datetime(2020, 2, 1)),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 3, 1),
        )

        milestone_entity = CapitalSchemeMilestoneEntity.from_domain(
            milestone, {Milestone.DETAILED_DESIGN_COMPLETED: 1}, {ObservationType.ACTUAL: 2}
        )

        assert (
            milestone_entity.milestone_id == 1
            and milestone_entity.status_date == date(2020, 3, 1)
            and milestone_entity.observation_type_id == 2
            and milestone_entity.effective_date_from == datetime(2020, 1, 1)
            and milestone_entity.effective_date_to == datetime(2020, 2, 1)
        )

    def test_from_domain_when_current(self) -> None:
        milestone = CapitalSchemeMilestone(
            effective_date=DateTimeRange(datetime(2020, 1, 1)),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 3, 1),
        )

        milestone_entity = CapitalSchemeMilestoneEntity.from_domain(
            milestone, {Milestone.DETAILED_DESIGN_COMPLETED: 0}, {ObservationType.ACTUAL: 0}
        )

        assert not milestone_entity.effective_date_to

    def test_from_domain_converts_dates_to_local_europe_london(self) -> None:
        milestone = CapitalSchemeMilestone(
            effective_date=DateTimeRange(
                datetime(2020, 6, 1, 12, tzinfo=timezone.utc), datetime(2020, 7, 1, 12, tzinfo=timezone.utc)
            ),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 3, 1),
        )

        milestone_entity = CapitalSchemeMilestoneEntity.from_domain(
            milestone, {Milestone.DETAILED_DESIGN_COMPLETED: 0}, {ObservationType.ACTUAL: 0}
        )

        assert milestone_entity.effective_date_from == datetime(2020, 6, 1, 13)
        assert milestone_entity.effective_date_to == datetime(2020, 7, 1, 13)

    def test_to_domain(self) -> None:
        milestone_entity = CapitalSchemeMilestoneEntity(
            milestone=MilestoneEntity(milestone_name=MilestoneName.DETAILED_DESIGN_COMPLETED),
            observation_type=ObservationTypeEntity(observation_type_name=ObservationTypeName.ACTUAL),
            status_date=date(2020, 3, 1),
            effective_date_from=datetime(2020, 1, 1),
            effective_date_to=datetime(2020, 2, 1),
        )

        milestone = milestone_entity.to_domain()

        assert milestone == CapitalSchemeMilestone(
            effective_date=DateTimeRange(
                datetime(2020, 1, 1, tzinfo=timezone.utc), datetime(2020, 2, 1, tzinfo=timezone.utc)
            ),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 3, 1),
        )

    def test_to_domain_when_current(self) -> None:
        milestone_entity = CapitalSchemeMilestoneEntity(
            milestone=MilestoneEntity(milestone_name=MilestoneName.DETAILED_DESIGN_COMPLETED),
            observation_type=ObservationTypeEntity(observation_type_name=ObservationTypeName.ACTUAL),
            status_date=date(2020, 3, 1),
            effective_date_from=datetime(2020, 1, 1),
        )

        milestone = milestone_entity.to_domain()

        assert not milestone.effective_date.to

    def test_to_domain_converts_dates_from_local_europe_london(self) -> None:
        milestone_entity = CapitalSchemeMilestoneEntity(
            milestone=MilestoneEntity(milestone_name=MilestoneName.DETAILED_DESIGN_COMPLETED),
            observation_type=ObservationTypeEntity(observation_type_name=ObservationTypeName.ACTUAL),
            status_date=date(2020, 3, 1),
            effective_date_from=datetime(2020, 6, 1, 13),
            effective_date_to=datetime(2020, 7, 1, 13),
        )

        milestone = milestone_entity.to_domain()

        assert milestone.effective_date == DateTimeRange(
            datetime(2020, 6, 1, 12, tzinfo=timezone.utc), datetime(2020, 7, 1, 12, tzinfo=timezone.utc)
        )


@pytest.mark.usefixtures("data")
@pytest.mark.asyncio(loop_scope="package")
class TestDatabaseMilestoneRepository:
    async def test_get_all(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    MilestoneEntity(milestone_name=MilestoneName.DETAILED_DESIGN_COMPLETED, stage_order=1),
                    MilestoneEntity(milestone_name=MilestoneName.CONSTRUCTION_STARTED, stage_order=2),
                ]
            )

        async with AsyncSession(engine) as session:
            milestones = DatabaseMilestoneRepository(session)
            all_milestones = await milestones.get_all()

        assert all_milestones == [Milestone.DETAILED_DESIGN_COMPLETED, Milestone.CONSTRUCTION_STARTED]

    async def test_get_all_orders_by_stage_order(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    MilestoneEntity(milestone_name=MilestoneName.CONSTRUCTION_STARTED, stage_order=2),
                    MilestoneEntity(milestone_name=MilestoneName.DETAILED_DESIGN_COMPLETED, stage_order=1),
                ]
            )

        async with AsyncSession(engine) as session:
            milestones = DatabaseMilestoneRepository(session)
            all_milestones = await milestones.get_all()

        assert all_milestones == [Milestone.DETAILED_DESIGN_COMPLETED, Milestone.CONSTRUCTION_STARTED]
