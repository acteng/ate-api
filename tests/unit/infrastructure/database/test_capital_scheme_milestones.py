from datetime import UTC, date, datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from ate_api.domain.capital_scheme_milestones import CapitalSchemeMilestone, CapitalSchemeMilestones, Milestone
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeReference
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.observation_types import ObservationType
from ate_api.infrastructure.database import (
    CapitalSchemeEntity,
    CapitalSchemeMilestoneEntity,
    DataSourceEntity,
    DataSourceName,
    MilestoneEntity,
    MilestoneName,
    ObservationTypeEntity,
    ObservationTypeName,
)
from ate_api.infrastructure.database.capital_scheme_milestones import (
    DatabaseCapitalSchemeMilestonesRepository,
    DatabaseMilestoneRepository,
)
from tests.unit.infrastructure.database.builders import (
    build_data_source_entity,
    build_milestone_entity,
    build_observation_type_entity,
)


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
            data_source=DataSource.ATF4_BID,
            surrogate_id=1,
        )

        milestone_entity = CapitalSchemeMilestoneEntity.from_domain(
            milestone,
            2,
            {Milestone.DETAILED_DESIGN_COMPLETED: 3},
            {ObservationType.ACTUAL: 4},
            {DataSource.ATF4_BID: 5},
        )

        assert (
            milestone_entity.capital_scheme_milestone_id == 1
            and milestone_entity.capital_scheme_id == 2
            and milestone_entity.milestone_id == 3
            and milestone_entity.status_date == date(2020, 3, 1)
            and milestone_entity.observation_type_id == 4
            and milestone_entity.data_source_id == 5
            and milestone_entity.effective_date_from == datetime(2020, 1, 1)
            and milestone_entity.effective_date_to == datetime(2020, 2, 1)
        )

    def test_from_domain_when_current(self) -> None:
        milestone = CapitalSchemeMilestone(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 3, 1),
            data_source=DataSource.ATF4_BID,
        )

        milestone_entity = CapitalSchemeMilestoneEntity.from_domain(
            milestone,
            0,
            {Milestone.DETAILED_DESIGN_COMPLETED: 0},
            {ObservationType.ACTUAL: 0},
            {DataSource.ATF4_BID: 0},
        )

        assert not milestone_entity.effective_date_to

    def test_from_domain_converts_dates_to_local_europe_london(self) -> None:
        milestone = CapitalSchemeMilestone(
            effective_date=DateTimeRange(datetime(2020, 6, 1, 12, tzinfo=UTC), datetime(2020, 7, 1, 12, tzinfo=UTC)),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 3, 1),
            data_source=DataSource.ATF4_BID,
        )

        milestone_entity = CapitalSchemeMilestoneEntity.from_domain(
            milestone,
            0,
            {Milestone.DETAILED_DESIGN_COMPLETED: 0},
            {ObservationType.ACTUAL: 0},
            {DataSource.ATF4_BID: 0},
        )

        assert milestone_entity.effective_date_from == datetime(2020, 6, 1, 13)
        assert milestone_entity.effective_date_to == datetime(2020, 7, 1, 13)

    def test_to_domain(self) -> None:
        milestone_entity = CapitalSchemeMilestoneEntity(
            capital_scheme_milestone_id=1,
            milestone=MilestoneEntity(milestone_name=MilestoneName.DETAILED_DESIGN_COMPLETED),
            observation_type=ObservationTypeEntity(observation_type_name=ObservationTypeName.ACTUAL),
            status_date=date(2020, 3, 1),
            data_source=DataSourceEntity(data_source_name=DataSourceName.ATF4_BID),
            effective_date_from=datetime(2020, 1, 1),
            effective_date_to=datetime(2020, 2, 1),
        )

        milestone = milestone_entity.to_domain()

        assert milestone == CapitalSchemeMilestone(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC), datetime(2020, 2, 1, tzinfo=UTC)),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 3, 1),
            data_source=DataSource.ATF4_BID,
        )
        assert milestone.surrogate_id == 1

    def test_to_domain_when_current(self) -> None:
        milestone_entity = CapitalSchemeMilestoneEntity(
            milestone=MilestoneEntity(milestone_name=MilestoneName.DETAILED_DESIGN_COMPLETED),
            observation_type=ObservationTypeEntity(observation_type_name=ObservationTypeName.ACTUAL),
            status_date=date(2020, 3, 1),
            effective_date_from=datetime(2020, 1, 1),
            data_source=DataSourceEntity(data_source_name=DataSourceName.ATF4_BID),
        )

        milestone = milestone_entity.to_domain()

        assert not milestone.effective_date.to

    def test_to_domain_converts_dates_from_local_europe_london(self) -> None:
        milestone_entity = CapitalSchemeMilestoneEntity(
            milestone=MilestoneEntity(milestone_name=MilestoneName.DETAILED_DESIGN_COMPLETED),
            observation_type=ObservationTypeEntity(observation_type_name=ObservationTypeName.ACTUAL),
            status_date=date(2020, 3, 1),
            data_source=DataSourceEntity(data_source_name=DataSourceName.ATF4_BID),
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


@pytest.mark.usefixtures("data")
@pytest.mark.asyncio(loop_scope="package")
class TestDatabaseCapitalSchemeMilestonesRepository:
    async def test_add_stores_milestones(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    build_milestone_entity(id_=1, name=MilestoneName.DETAILED_DESIGN_COMPLETED),
                    build_milestone_entity(id_=2, name=MilestoneName.CONSTRUCTION_STARTED),
                    build_observation_type_entity(id_=1, name=ObservationTypeName.ACTUAL),
                    build_data_source_entity(id_=1, name=DataSourceName.ATF4_BID),
                    CapitalSchemeEntity(scheme_reference="ATE00001"),
                ]
            )

        async with AsyncSession(engine) as session, session.begin():
            capital_scheme_milestones = DatabaseCapitalSchemeMilestonesRepository(session)
            milestones = CapitalSchemeMilestones(capital_scheme=CapitalSchemeReference("ATE00001"))
            milestones.change_milestone(
                CapitalSchemeMilestone(
                    effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                    milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                    observation_type=ObservationType.ACTUAL,
                    status_date=date(2020, 2, 1),
                    data_source=DataSource.ATF4_BID,
                )
            )
            milestones.change_milestone(
                CapitalSchemeMilestone(
                    effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                    milestone=Milestone.CONSTRUCTION_STARTED,
                    observation_type=ObservationType.ACTUAL,
                    status_date=date(2020, 3, 1),
                    data_source=DataSource.ATF4_BID,
                )
            )
            await capital_scheme_milestones.add(milestones)

        async with AsyncSession(engine) as session:
            (capital_scheme_row,) = await session.scalars(select(CapitalSchemeEntity))
            milestone_row1, milestone_row2 = await session.scalars(select(CapitalSchemeMilestoneEntity))
        assert (
            milestone_row1.capital_scheme_id == capital_scheme_row.capital_scheme_id
            and milestone_row1.milestone_id == 1
            and milestone_row1.status_date == date(2020, 2, 1)
            and milestone_row1.observation_type_id == 1
            and milestone_row1.data_source_id == 1
            and milestone_row1.effective_date_from == datetime(2020, 1, 1)
            and not milestone_row1.effective_date_to
        )
        assert (
            milestone_row2.capital_scheme_id == capital_scheme_row.capital_scheme_id
            and milestone_row2.milestone_id == 2
            and milestone_row2.status_date == date(2020, 3, 1)
            and milestone_row2.observation_type_id == 1
            and milestone_row2.data_source_id == 1
            and milestone_row2.effective_date_from == datetime(2020, 1, 1)
            and not milestone_row2.effective_date_to
        )

    async def test_get(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add(CapitalSchemeEntity(capital_scheme_id=1, scheme_reference="ATE00001"))

        async with AsyncSession(engine) as session:
            capital_scheme_milestones = DatabaseCapitalSchemeMilestonesRepository(session)
            milestones = await capital_scheme_milestones.get(CapitalSchemeReference("ATE00001"))

        assert (
            milestones and milestones.capital_scheme == CapitalSchemeReference("ATE00001") and not milestones.milestones
        )

    async def test_get_fetches_current_milestones(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    detailed_design_completed := build_milestone_entity(name=MilestoneName.DETAILED_DESIGN_COMPLETED),
                    construction_started := build_milestone_entity(name=MilestoneName.CONSTRUCTION_STARTED),
                    actual := build_observation_type_entity(name=ObservationTypeName.ACTUAL),
                    atf4_bid := build_data_source_entity(name=DataSourceName.ATF4_BID),
                    CapitalSchemeEntity(capital_scheme_id=1, scheme_reference="ATE00001"),
                    CapitalSchemeMilestoneEntity(
                        capital_scheme_id=1,
                        milestone=detailed_design_completed,
                        observation_type=actual,
                        status_date=date(2020, 3, 1),
                        data_source=atf4_bid,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=datetime(2020, 2, 1),
                    ),
                    CapitalSchemeMilestoneEntity(
                        capital_scheme_id=1,
                        milestone=detailed_design_completed,
                        observation_type=actual,
                        status_date=date(2020, 4, 1),
                        data_source=atf4_bid,
                        effective_date_from=datetime(2020, 2, 1),
                    ),
                    CapitalSchemeMilestoneEntity(
                        capital_scheme_id=1,
                        milestone=construction_started,
                        observation_type=actual,
                        status_date=date(2020, 5, 1),
                        data_source=atf4_bid,
                        effective_date_from=datetime(2020, 2, 1),
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_scheme_milestones = DatabaseCapitalSchemeMilestonesRepository(session)
            milestones = await capital_scheme_milestones.get(CapitalSchemeReference("ATE00001"))

        assert milestones and milestones.milestones == [
            CapitalSchemeMilestone(
                effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 4, 1),
                data_source=DataSource.ATF4_BID,
            ),
            CapitalSchemeMilestone(
                effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)),
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 5, 1),
                data_source=DataSource.ATF4_BID,
            ),
        ]

    async def test_get_fetches_current_milestones_ordered_by_milestone_stage_order_then_observation_type(
        self, engine: AsyncEngine
    ) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    detailed_design_completed := build_milestone_entity(
                        name=MilestoneName.DETAILED_DESIGN_COMPLETED, stage_order=1
                    ),
                    construction_started := build_milestone_entity(
                        name=MilestoneName.CONSTRUCTION_STARTED, stage_order=2
                    ),
                    planned := build_observation_type_entity(name=ObservationTypeName.PLANNED),
                    actual := build_observation_type_entity(name=ObservationTypeName.ACTUAL),
                    atf4_bid := build_data_source_entity(name=DataSourceName.ATF4_BID),
                    CapitalSchemeEntity(capital_scheme_id=1, scheme_reference="ATE00001"),
                    CapitalSchemeMilestoneEntity(
                        capital_scheme_id=1,
                        milestone=construction_started,
                        observation_type=actual,
                        status_date=date(2020, 4, 1),
                        data_source=atf4_bid,
                        effective_date_from=datetime(2020, 1, 1),
                    ),
                    CapitalSchemeMilestoneEntity(
                        capital_scheme_id=1,
                        milestone=detailed_design_completed,
                        observation_type=actual,
                        status_date=date(2020, 3, 1),
                        data_source=atf4_bid,
                        effective_date_from=datetime(2020, 1, 1),
                    ),
                    CapitalSchemeMilestoneEntity(
                        capital_scheme_id=1,
                        milestone=detailed_design_completed,
                        observation_type=planned,
                        status_date=date(2020, 2, 1),
                        data_source=atf4_bid,
                        effective_date_from=datetime(2020, 1, 1),
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_scheme_milestones = DatabaseCapitalSchemeMilestonesRepository(session)
            milestones = await capital_scheme_milestones.get(CapitalSchemeReference("ATE00001"))

        assert milestones and milestones.milestones == [
            CapitalSchemeMilestone(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.PLANNED,
                status_date=date(2020, 2, 1),
                data_source=DataSource.ATF4_BID,
            ),
            CapitalSchemeMilestone(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 3, 1),
                data_source=DataSource.ATF4_BID,
            ),
            CapitalSchemeMilestone(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 4, 1),
                data_source=DataSource.ATF4_BID,
            ),
        ]

    async def test_get_when_not_found(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session:
            capital_scheme_milestones = DatabaseCapitalSchemeMilestonesRepository(session)
            milestones = await capital_scheme_milestones.get(CapitalSchemeReference("ATE00001"))

        assert not milestones

    async def test_update(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    detailed_design_completed := build_milestone_entity(
                        id_=2, name=MilestoneName.DETAILED_DESIGN_COMPLETED
                    ),
                    actual := build_observation_type_entity(id_=3, name=ObservationTypeName.ACTUAL),
                    atf4_bid := build_data_source_entity(id_=4, name=DataSourceName.ATF4_BID),
                    CapitalSchemeEntity(capital_scheme_id=1, scheme_reference="ATE00001"),
                    CapitalSchemeMilestoneEntity(
                        capital_scheme_id=1,
                        milestone=detailed_design_completed,
                        observation_type=actual,
                        status_date=date(2020, 2, 1),
                        data_source=atf4_bid,
                        effective_date_from=datetime(2020, 1, 1),
                    ),
                ]
            )

        async with AsyncSession(engine) as session, session.begin():
            capital_scheme_milestones = DatabaseCapitalSchemeMilestonesRepository(session)
            milestones = await capital_scheme_milestones.get(CapitalSchemeReference("ATE00001"))
            assert milestones
            milestones.change_milestone(
                CapitalSchemeMilestone(
                    effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)),
                    milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                    observation_type=ObservationType.ACTUAL,
                    status_date=date(2020, 3, 1),
                    data_source=DataSource.ATF4_BID,
                )
            )
            await capital_scheme_milestones.update(milestones)

        async with AsyncSession(engine) as session:
            (capital_scheme_row,) = await session.scalars(select(CapitalSchemeEntity))
            milestone_row1, milestone_row2 = await session.scalars(select(CapitalSchemeMilestoneEntity))
        assert (
            milestone_row1.capital_scheme_id == capital_scheme_row.capital_scheme_id
            and milestone_row1.effective_date_to == datetime(2020, 2, 1)
        )
        assert (
            milestone_row2.capital_scheme_id == capital_scheme_row.capital_scheme_id
            and milestone_row2.milestone_id == 2
            and milestone_row2.status_date == date(2020, 3, 1)
            and milestone_row2.observation_type_id == 3
            and milestone_row2.data_source_id == 4
            and milestone_row2.effective_date_from == datetime(2020, 2, 1)
            and not milestone_row2.effective_date_to
        )
