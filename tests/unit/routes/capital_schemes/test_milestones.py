from datetime import UTC, date, datetime

import pytest

from ate_api.domain.capital_schemes.milestones import CapitalSchemeMilestone, Milestone
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.observation_types import ObservationType
from ate_api.routes.capital_schemes.milestones import CapitalSchemeMilestoneModel, MilestoneModel
from ate_api.routes.data_sources import DataSourceModel
from ate_api.routes.observation_types import ObservationTypeModel


@pytest.mark.parametrize(
    "milestone, milestone_model",
    [
        (Milestone.PUBLIC_CONSULTATION_COMPLETED, MilestoneModel.PUBLIC_CONSULTATION_COMPLETED),
        (Milestone.FEASIBILITY_DESIGN_STARTED, MilestoneModel.FEASIBILITY_DESIGN_STARTED),
        (Milestone.FEASIBILITY_DESIGN_COMPLETED, MilestoneModel.FEASIBILITY_DESIGN_COMPLETED),
        (Milestone.PRELIMINARY_DESIGN_COMPLETED, MilestoneModel.PRELIMINARY_DESIGN_COMPLETED),
        (Milestone.OUTLINE_DESIGN_COMPLETED, MilestoneModel.OUTLINE_DESIGN_COMPLETED),
        (Milestone.DETAILED_DESIGN_COMPLETED, MilestoneModel.DETAILED_DESIGN_COMPLETED),
        (Milestone.CONSTRUCTION_STARTED, MilestoneModel.CONSTRUCTION_STARTED),
        (Milestone.CONSTRUCTION_COMPLETED, MilestoneModel.CONSTRUCTION_COMPLETED),
        (Milestone.FUNDING_COMPLETED, MilestoneModel.FUNDING_COMPLETED),
        (Milestone.NOT_PROGRESSED, MilestoneModel.NOT_PROGRESSED),
        (Milestone.SUPERSEDED, MilestoneModel.SUPERSEDED),
        (Milestone.REMOVED, MilestoneModel.REMOVED),
    ],
)
class TestMilestoneModel:
    def test_from_domain(self, milestone: Milestone, milestone_model: MilestoneModel) -> None:
        assert MilestoneModel.from_domain(milestone) == milestone_model

    def test_to_domain(self, milestone: Milestone, milestone_model: MilestoneModel) -> None:
        assert milestone_model.to_domain() == milestone


class TestCapitalSchemeMilestoneModel:
    def test_from_domain(self) -> None:
        milestone = CapitalSchemeMilestone(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 2, 1),
            data_source=DataSource.ATF4_BID,
        )

        milestone_model = CapitalSchemeMilestoneModel.from_domain(milestone)

        assert milestone_model == CapitalSchemeMilestoneModel(
            milestone=MilestoneModel.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationTypeModel.ACTUAL,
            status_date=date(2020, 2, 1),
            source=DataSourceModel.ATF4_BID,
        )

    def test_to_domain(self) -> None:
        milestone_model = CapitalSchemeMilestoneModel(
            milestone=MilestoneModel.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationTypeModel.ACTUAL,
            status_date=date(2020, 2, 1),
            source=DataSourceModel.ATF4_BID,
        )

        milestone = milestone_model.to_domain(datetime(2020, 1, 1, tzinfo=UTC))

        assert milestone == CapitalSchemeMilestone(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 2, 1),
            data_source=DataSource.ATF4_BID,
        )
