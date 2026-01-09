from datetime import UTC, date, datetime

import pytest

from ate_api.domain.capital_scheme_milestones import CapitalSchemeMilestone, CapitalSchemeMilestones, Milestone
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeReference
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.observation_types import ObservationType


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


class TestCapitalSchemeMilestone:
    @pytest.mark.parametrize(
        "effective_date_to, expected_is_open",
        [pytest.param(None, True, id="open"), pytest.param(datetime(2020, 2, 1, tzinfo=UTC), False, id="closed")],
    )
    def test_is_open(self, effective_date_to: datetime | None, expected_is_open: bool) -> None:
        milestone = CapitalSchemeMilestone(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC), effective_date_to),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 2, 1),
            data_source=DataSource.ATF4_BID,
        )

        assert milestone.is_open == expected_is_open

    def test_close(self) -> None:
        open_milestone = CapitalSchemeMilestone(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 2, 1),
            data_source=DataSource.ATF4_BID,
            surrogate_id=1,
        )

        closed_milestone = open_milestone.close(datetime(2020, 2, 1, tzinfo=UTC))

        assert closed_milestone == CapitalSchemeMilestone(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC), datetime(2020, 2, 1, tzinfo=UTC)),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 2, 1),
            data_source=DataSource.ATF4_BID,
        )
        assert closed_milestone.surrogate_id == 1

    def test_cannot_close_when_closed(self) -> None:
        closed_milestone = CapitalSchemeMilestone(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC), datetime(2020, 2, 1, tzinfo=UTC)),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 2, 1),
            data_source=DataSource.ATF4_BID,
        )

        with pytest.raises(ValueError, match="Capital scheme milestone is already closed"):
            closed_milestone.close(datetime(2020, 2, 1, tzinfo=UTC))


class TestCapitalSchemeMilestones:
    def test_create(self) -> None:
        milestones = CapitalSchemeMilestones(capital_scheme=CapitalSchemeReference("ATE00001"))

        assert milestones.capital_scheme == CapitalSchemeReference("ATE00001") and not milestones.milestones

    def test_milestones_is_copy(self) -> None:
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

        milestones.milestones.clear()

        assert milestones.milestones

    def test_current_milestone_selects_actual_observation_type(self) -> None:
        milestones = CapitalSchemeMilestones(capital_scheme=CapitalSchemeReference("ATE00001"))
        milestones.change_milestone(
            CapitalSchemeMilestone(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.PLANNED,
                status_date=date(2020, 2, 1),
                data_source=DataSource.ATF4_BID,
            )
        )
        milestones.change_milestone(
            CapitalSchemeMilestone(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 3, 1),
                data_source=DataSource.ATF4_BID,
            )
        )

        assert milestones.current_milestone == Milestone.DETAILED_DESIGN_COMPLETED

    def test_current_milestone_selects_latest_milestone(self) -> None:
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

        assert milestones.current_milestone == Milestone.CONSTRUCTION_STARTED

    def test_current_milestone_when_none(self) -> None:
        milestones = CapitalSchemeMilestones(capital_scheme=CapitalSchemeReference("ATE00001"))

        assert not milestones.current_milestone

    def test_change_milestone_adds_milestone(self) -> None:
        milestones = CapitalSchemeMilestones(capital_scheme=CapitalSchemeReference("ATE00001"))
        milestone = CapitalSchemeMilestone(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 2, 1),
            data_source=DataSource.ATF4_BID,
        )

        milestones.change_milestone(milestone)

        assert milestones.milestones == [milestone]

    def test_change_milestone_closes_matching_current_milestone(self) -> None:
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
                effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 2, 1),
                data_source=DataSource.ATF4_BID,
            )
        )

        assert milestones.milestones[0].effective_date.to == datetime(2020, 2, 1, tzinfo=UTC)

    def test_change_milestone_preserves_matching_historic_milestone(self) -> None:
        milestones = CapitalSchemeMilestones(capital_scheme=CapitalSchemeReference("ATE00001"))
        milestone1 = CapitalSchemeMilestone(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC), datetime(2020, 2, 1, tzinfo=UTC)),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 2, 1),
            data_source=DataSource.ATF4_BID,
        )
        milestones.change_milestone(milestone1)

        milestones.change_milestone(
            CapitalSchemeMilestone(
                effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 3, 1),
                data_source=DataSource.ATF4_BID,
            )
        )

        assert milestones.milestones[0] == milestone1

    def test_change_milestone_preserves_other_current_milestones(self) -> None:
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
            observation_type=ObservationType.PLANNED,
            status_date=date(2020, 3, 1),
            data_source=DataSource.ATF4_BID,
        )
        milestones.change_milestone(milestone2)

        milestones.change_milestone(
            CapitalSchemeMilestone(
                effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)),
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 4, 1),
                data_source=DataSource.ATF4_BID,
            )
        )

        actual_milestone1, actual_milestone2, _ = milestones.milestones
        assert actual_milestone1 == milestone1 and actual_milestone2 == milestone2
