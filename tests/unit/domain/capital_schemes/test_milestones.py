import pytest

from ate_api.domain.capital_schemes.milestones import Milestone


class TestMilestone:
    @pytest.mark.parametrize(
        "milestone, expected_is_active",
        [
            (Milestone.PUBLIC_CONSULTATION_COMPLETED, True),
            (Milestone.FEASIBILITY_DESIGN_STARTED, True),
            (Milestone.FEASIBILITY_DESIGN_COMPLETED, True),
            (Milestone.PRELIMINARY_DESIGN_COMPLETED, True),
            (Milestone.OUTLINE_DESIGN_COMPLETED, True),
            (Milestone.DETAILED_DESIGN_COMPLETED, True),
            (Milestone.CONSTRUCTION_STARTED, True),
            (Milestone.CONSTRUCTION_COMPLETED, True),
            (Milestone.FUNDING_COMPLETED, True),
            (Milestone.NOT_PROGRESSED, False),
            (Milestone.SUPERSEDED, False),
            (Milestone.REMOVED, False),
        ],
    )
    def test_is_active(self, milestone: Milestone, expected_is_active: bool) -> None:
        assert milestone.is_active == expected_is_active

    @pytest.mark.parametrize(
        "milestone, expected_is_complete",
        [
            (Milestone.PUBLIC_CONSULTATION_COMPLETED, False),
            (Milestone.FEASIBILITY_DESIGN_STARTED, False),
            (Milestone.FEASIBILITY_DESIGN_COMPLETED, False),
            (Milestone.PRELIMINARY_DESIGN_COMPLETED, False),
            (Milestone.OUTLINE_DESIGN_COMPLETED, False),
            (Milestone.DETAILED_DESIGN_COMPLETED, False),
            (Milestone.CONSTRUCTION_STARTED, False),
            (Milestone.CONSTRUCTION_COMPLETED, False),
            (Milestone.FUNDING_COMPLETED, True),
            (Milestone.NOT_PROGRESSED, False),
            (Milestone.SUPERSEDED, False),
            (Milestone.REMOVED, False),
        ],
    )
    def test_is_complete(self, milestone: Milestone, expected_is_complete: bool) -> None:
        assert milestone.is_complete == expected_is_complete
