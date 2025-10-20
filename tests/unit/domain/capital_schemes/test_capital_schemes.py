from datetime import UTC, date, datetime
from decimal import Decimal

from ate_api.domain.authorities import AuthorityAbbreviation
from ate_api.domain.capital_schemes.authority_reviews import CapitalSchemeAuthorityReview
from ate_api.domain.capital_schemes.bid_statuses import BidStatus, CapitalSchemeBidStatusDetails
from ate_api.domain.capital_schemes.capital_schemes import CapitalScheme, CapitalSchemeReference
from ate_api.domain.capital_schemes.milestones import CapitalSchemeMilestone, Milestone
from ate_api.domain.capital_schemes.outputs import CapitalSchemeOutput, OutputMeasure, OutputType
from ate_api.domain.capital_schemes.overviews import CapitalSchemeOverview, CapitalSchemeType
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.funding_programmes import FundingProgrammeCode
from ate_api.domain.observation_types import ObservationType
from tests.unit.domain.dummies import dummy_bid_status_details, dummy_overview


class TestCapitalSchemeReference:
    def test_create(self) -> None:
        reference = CapitalSchemeReference("ATE00001")

        assert str(reference) == "ATE00001"

    def test_equals(self) -> None:
        reference1 = CapitalSchemeReference("ATE00001")
        reference2 = CapitalSchemeReference("ATE00001")

        assert reference1 == reference2

    def test_equals_when_different_reference(self) -> None:
        reference1 = CapitalSchemeReference("ATE00001")
        reference2 = CapitalSchemeReference("ATE00002")

        assert not reference1 == reference2

    def test_equals_when_different_class(self) -> None:
        reference = CapitalSchemeReference("ATE00001")

        assert not reference == "ATE00001"

    def test_hash(self) -> None:
        reference1 = CapitalSchemeReference("ATE00001")
        reference2 = CapitalSchemeReference("ATE00001")

        assert hash(reference1) == hash(reference2)

    def test_repr(self) -> None:
        reference = CapitalSchemeReference("ATE00001")

        assert repr(reference) == "CapitalSchemeReference('ATE00001')"


class TestCapitalScheme:
    def test_create(self) -> None:
        overview = CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            name="Wirral Package",
            bid_submitting_authority=AuthorityAbbreviation("LIV"),
            funding_programme=FundingProgrammeCode("ATF3"),
            type=CapitalSchemeType.CONSTRUCTION,
        )
        bid_status_details = CapitalSchemeBidStatusDetails(
            effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)), bid_status=BidStatus.FUNDED
        )

        capital_scheme = CapitalScheme(
            reference=CapitalSchemeReference("ATE00001"), overview=overview, bid_status_details=bid_status_details
        )

        assert (
            capital_scheme.reference == CapitalSchemeReference("ATE00001")
            and capital_scheme.overview == overview
            and capital_scheme.bid_status_details == bid_status_details
            and not capital_scheme.milestones
            and not capital_scheme.authority_review
        )

    def test_milestones_is_copy(self) -> None:
        capital_scheme = CapitalScheme(
            reference=CapitalSchemeReference("ATE00001"),
            overview=dummy_overview(),
            bid_status_details=dummy_bid_status_details(),
        )
        capital_scheme.change_milestone(
            CapitalSchemeMilestone(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 2, 1),
            )
        )

        capital_scheme.milestones.clear()

        assert capital_scheme.milestones

    def test_current_milestone_selects_actual_observation_type(self) -> None:
        capital_scheme = CapitalScheme(
            reference=CapitalSchemeReference("ATE00001"),
            overview=dummy_overview(),
            bid_status_details=dummy_bid_status_details(),
        )
        capital_scheme.change_milestone(
            CapitalSchemeMilestone(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.PLANNED,
                status_date=date(2020, 2, 1),
            )
        )
        capital_scheme.change_milestone(
            CapitalSchemeMilestone(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 3, 1),
            )
        )

        assert capital_scheme.current_milestone == Milestone.DETAILED_DESIGN_COMPLETED

    def test_current_milestone_selects_latest_milestone(self) -> None:
        capital_scheme = CapitalScheme(
            reference=CapitalSchemeReference("ATE00001"),
            overview=dummy_overview(),
            bid_status_details=dummy_bid_status_details(),
        )
        capital_scheme.change_milestone(
            CapitalSchemeMilestone(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 2, 1),
            )
        )
        capital_scheme.change_milestone(
            CapitalSchemeMilestone(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 3, 1),
            )
        )

        assert capital_scheme.current_milestone == Milestone.CONSTRUCTION_STARTED

    def test_current_milestone_when_none(self) -> None:
        capital_scheme = CapitalScheme(
            reference=CapitalSchemeReference("ATE00001"),
            overview=dummy_overview(),
            bid_status_details=dummy_bid_status_details(),
        )

        assert not capital_scheme.current_milestone

    def test_change_milestone(self) -> None:
        capital_scheme = CapitalScheme(
            reference=CapitalSchemeReference("ATE00001"),
            overview=dummy_overview(),
            bid_status_details=dummy_bid_status_details(),
        )
        milestone = CapitalSchemeMilestone(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            milestone=Milestone.DETAILED_DESIGN_COMPLETED,
            observation_type=ObservationType.ACTUAL,
            status_date=date(2020, 2, 1),
        )

        capital_scheme.change_milestone(milestone)

        assert capital_scheme.milestones == [milestone]

    def test_outputs_is_copy(self) -> None:
        capital_scheme = CapitalScheme(
            reference=CapitalSchemeReference("ATE00001"),
            overview=dummy_overview(),
            bid_status_details=dummy_bid_status_details(),
        )
        capital_scheme.change_output(
            CapitalSchemeOutput(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                type=OutputType.WIDENING_EXISTING_FOOTWAY,
                value=Decimal(1.5),
                measure=OutputMeasure.MILES,
                observation_type=ObservationType.ACTUAL,
            )
        )

        capital_scheme.outputs.clear()

        assert capital_scheme.outputs

    def test_change_output(self) -> None:
        capital_scheme = CapitalScheme(
            reference=CapitalSchemeReference("ATE00001"),
            overview=dummy_overview(),
            bid_status_details=dummy_bid_status_details(),
        )
        output = CapitalSchemeOutput(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            type=OutputType.WIDENING_EXISTING_FOOTWAY,
            value=Decimal(1.5),
            measure=OutputMeasure.MILES,
            observation_type=ObservationType.ACTUAL,
        )

        capital_scheme.change_output(output)

        assert capital_scheme.outputs == [output]

    def test_perform_authority_review(self) -> None:
        capital_scheme = CapitalScheme(
            reference=CapitalSchemeReference("ATE00001"),
            overview=dummy_overview(),
            bid_status_details=dummy_bid_status_details(),
        )
        authority_review = CapitalSchemeAuthorityReview(review_date=datetime(2020, 2, 1, tzinfo=UTC))

        capital_scheme.perform_authority_review(authority_review)

        assert capital_scheme.authority_review == authority_review
