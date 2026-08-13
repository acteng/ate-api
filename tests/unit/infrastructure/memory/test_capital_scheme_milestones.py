from datetime import UTC, date, datetime

import pytest

from ate_api.domain.capital_scheme_milestones import CapitalSchemeMilestone, CapitalSchemeMilestones, Milestone
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeReference
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.observation_types import ObservationType
from tests.unit.infrastructure.memory.capital_scheme_milestones import MemoryCapitalSchemeMilestonesRepository


class TestMemoryCapitalSchemeMilestonesRepository:
    @pytest.fixture(name="capital_scheme_milestones")
    def capital_scheme_milestones_fixture(self) -> MemoryCapitalSchemeMilestonesRepository:
        return MemoryCapitalSchemeMilestonesRepository()

    async def test_add(self, capital_scheme_milestones: MemoryCapitalSchemeMilestonesRepository) -> None:
        milestones = CapitalSchemeMilestones(capital_scheme=CapitalSchemeReference("ATE00001"))
        milestone1 = CapitalSchemeMilestone(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 2, 1),
            data_source=DataSource.ATF4_BID,
        )
        milestones.change_milestone(milestone1)
        milestone2 = CapitalSchemeMilestone(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            milestone=Milestone.CONSTRUCTION_STARTED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 3, 1),
            data_source=DataSource.ATF4_BID,
        )
        milestones.change_milestone(milestone2)

        await capital_scheme_milestones.add(milestones)

        actual_milestones = await capital_scheme_milestones.get(CapitalSchemeReference("ATE00001"))
        assert (
            actual_milestones
            and actual_milestones.capital_scheme == CapitalSchemeReference("ATE00001")
            and actual_milestones.milestones == [milestone1, milestone2]
        )

    async def test_get(self, capital_scheme_milestones: MemoryCapitalSchemeMilestonesRepository) -> None:
        milestones = CapitalSchemeMilestones(capital_scheme=CapitalSchemeReference("ATE00001"))
        milestone1 = CapitalSchemeMilestone(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 2, 1),
            data_source=DataSource.ATF4_BID,
        )
        milestones.change_milestone(milestone1)
        milestone2 = CapitalSchemeMilestone(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            milestone=Milestone.CONSTRUCTION_STARTED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 3, 1),
            data_source=DataSource.ATF4_BID,
        )
        milestones.change_milestone(milestone2)
        await capital_scheme_milestones.add(milestones)

        actual_milestones = await capital_scheme_milestones.get(CapitalSchemeReference("ATE00001"))

        assert (
            actual_milestones
            and actual_milestones.capital_scheme == CapitalSchemeReference("ATE00001")
            and actual_milestones.milestones == [milestone1, milestone2]
        )

    async def test_get_when_not_found(self, capital_scheme_milestones: MemoryCapitalSchemeMilestonesRepository) -> None:
        milestones = await capital_scheme_milestones.get(CapitalSchemeReference("ATE00001"))

        assert not milestones

    async def test_update(self, capital_scheme_milestones: MemoryCapitalSchemeMilestonesRepository) -> None:
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
        await capital_scheme_milestones.add(milestones)
        milestone2 = CapitalSchemeMilestone(
            effective_date=DateTimeRange(datetime(2021, 1, 1, tzinfo=UTC)),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2021, 2, 1),
            data_source=DataSource.ATF4_BID,
        )
        milestones.change_milestone(milestone2)

        await capital_scheme_milestones.update(milestones)

        actual_milestones = await capital_scheme_milestones.get(CapitalSchemeReference("ATE00001"))
        assert actual_milestones and actual_milestones.capital_scheme == CapitalSchemeReference("ATE00001")
        actual_milestone1, actual_milestone2 = actual_milestones.milestones
        assert actual_milestone1.effective_date.to == datetime(2021, 1, 1, tzinfo=UTC)
        assert actual_milestone2 == milestone2
