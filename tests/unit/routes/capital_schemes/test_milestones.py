from datetime import date, datetime

from ate_api.domain.capital_schemes.milestones import CapitalSchemeMilestone, Milestone
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.observation_types import ObservationType
from ate_api.routes.capital_schemes.milestones import CapitalSchemeMilestoneModel, MilestoneModel
from ate_api.routes.observation_types import ObservationTypeModel


class TestMilestoneModel:
    def test_from_domain(self) -> None:
        assert (
            MilestoneModel.from_domain(Milestone.DETAILED_DESIGN_COMPLETED) == MilestoneModel.DETAILED_DESIGN_COMPLETED
        )

    def test_to_domain(self) -> None:
        assert MilestoneModel.DETAILED_DESIGN_COMPLETED.to_domain() == Milestone.DETAILED_DESIGN_COMPLETED


class TestCapitalSchemeMilestoneModel:
    def test_from_domain(self) -> None:
        milestone = CapitalSchemeMilestone(
            effective_date=DateTimeRange(datetime(2020, 1, 1)),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 2, 1),
        )

        milestone_model = CapitalSchemeMilestoneModel.from_domain(milestone)

        assert milestone_model == CapitalSchemeMilestoneModel(
            milestone=MilestoneModel.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationTypeModel.ACTUAL,
            status_date=date(2020, 2, 1),
        )

    def test_to_domain(self) -> None:
        milestone_model = CapitalSchemeMilestoneModel(
            milestone=MilestoneModel.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationTypeModel.ACTUAL,
            status_date=date(2020, 2, 1),
        )

        milestone = milestone_model.to_domain(datetime(2020, 1, 1))

        assert milestone == CapitalSchemeMilestone(
            effective_date=DateTimeRange(datetime(2020, 1, 1)),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 2, 1),
        )
