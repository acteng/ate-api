from datetime import UTC, date, datetime

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
from tests.unit.infrastructure.database.builders import build_milestone_entity


@pytest.mark.parametrize(
    "milestone, milestone_name",
    [
        (Milestone.PUBLIC_CONSULTATION_COMPLETED, MilestoneName.PUBLIC_CONSULTATION_COMPLETED),
        (Milestone.FEASIBILITY_DESIGN_STARTED, MilestoneName.FEASIBILITY_DESIGN_STARTED),
        (Milestone.FEASIBILITY_DESIGN_COMPLETED, MilestoneName.FEASIBILITY_DESIGN_COMPLETED),
        (Milestone.PRELIMINARY_DESIGN_COMPLETED, MilestoneName.PRELIMINARY_DESIGN_COMPLETED),
        (Milestone.OUTLINE_DESIGN_COMPLETED, MilestoneName.OUTLINE_DESIGN_COMPLETED),
        (Milestone.DETAILED_DESIGN_COMPLETED, MilestoneName.DETAILED_DESIGN_COMPLETED),
        (Milestone.CONSTRUCTION_STARTED, MilestoneName.CONSTRUCTION_STARTED),
        (Milestone.CONSTRUCTION_COMPLETED, MilestoneName.CONSTRUCTION_COMPLETED),
        (Milestone.FUNDING_COMPLETED, MilestoneName.FUNDING_COMPLETED),
        (Milestone.NOT_PROGRESSED, MilestoneName.NOT_PROGRESSED),
        (Milestone.SUPERSEDED, MilestoneName.SUPERSEDED),
        (Milestone.REMOVED, MilestoneName.REMOVED),
    ],
)
class TestMilestoneName:
    def test_from_domain(self, milestone: Milestone, milestone_name: MilestoneName) -> None:
        assert MilestoneName.from_domain(milestone) == milestone_name

    def test_to_domain(self, milestone: Milestone, milestone_name: MilestoneName) -> None:
        assert milestone_name.to_domain() == milestone


class TestCapitalSchemeMilestoneEntity:
    def test_from_domain(self) -> None:
        milestone = CapitalSchemeMilestone(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC), datetime(2020, 2, 1, tzinfo=UTC)),
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
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
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
            effective_date=DateTimeRange(datetime(2020, 6, 1, 12, tzinfo=UTC), datetime(2020, 7, 1, 12, tzinfo=UTC)),
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
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC), datetime(2020, 2, 1, tzinfo=UTC)),
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
            datetime(2020, 6, 1, 12, tzinfo=UTC), datetime(2020, 7, 1, 12, tzinfo=UTC)
        )


@pytest.mark.usefixtures("data")
@pytest.mark.asyncio(loop_scope="package")
class TestDatabaseMilestoneRepository:
    async def test_get_all(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    build_milestone_entity(name=MilestoneName.DETAILED_DESIGN_COMPLETED),
                    build_milestone_entity(name=MilestoneName.CONSTRUCTION_STARTED),
                ]
            )

        async with AsyncSession(engine) as session:
            milestones = DatabaseMilestoneRepository(session)
            all_milestones = await milestones.get_all()

        assert all_milestones == [Milestone.DETAILED_DESIGN_COMPLETED, Milestone.CONSTRUCTION_STARTED]

    @pytest.mark.parametrize(
        "is_active, expected_milestone",
        [(True, Milestone.DETAILED_DESIGN_COMPLETED), (False, Milestone.CONSTRUCTION_STARTED)],
    )
    async def test_get_all_filters_by_is_active(
        self, engine: AsyncEngine, is_active: bool, expected_milestone: Milestone
    ) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    build_milestone_entity(name=MilestoneName.DETAILED_DESIGN_COMPLETED, is_active=True),
                    build_milestone_entity(name=MilestoneName.CONSTRUCTION_STARTED, is_active=False),
                ]
            )

        async with AsyncSession(engine) as session:
            milestones = DatabaseMilestoneRepository(session)
            all_milestones = await milestones.get_all(is_active=is_active)

        assert all_milestones == [expected_milestone]

    @pytest.mark.parametrize(
        "is_complete, expected_milestone",
        [(True, Milestone.DETAILED_DESIGN_COMPLETED), (False, Milestone.CONSTRUCTION_STARTED)],
    )
    async def test_get_all_filters_by_is_complete(
        self, engine: AsyncEngine, is_complete: bool, expected_milestone: Milestone
    ) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    build_milestone_entity(name=MilestoneName.DETAILED_DESIGN_COMPLETED, is_complete=True),
                    build_milestone_entity(name=MilestoneName.CONSTRUCTION_STARTED, is_complete=False),
                ]
            )

        async with AsyncSession(engine) as session:
            milestones = DatabaseMilestoneRepository(session)
            all_milestones = await milestones.get_all(is_complete=is_complete)

        assert all_milestones == [expected_milestone]

    async def test_get_all_orders_by_stage_order(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    build_milestone_entity(name=MilestoneName.CONSTRUCTION_STARTED, stage_order=2),
                    build_milestone_entity(name=MilestoneName.DETAILED_DESIGN_COMPLETED, stage_order=1),
                ]
            )

        async with AsyncSession(engine) as session:
            milestones = DatabaseMilestoneRepository(session)
            all_milestones = await milestones.get_all()

        assert all_milestones == [Milestone.DETAILED_DESIGN_COMPLETED, Milestone.CONSTRUCTION_STARTED]
