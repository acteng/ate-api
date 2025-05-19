from datetime import datetime

from ate_api.domain.authorities import AuthorityAbbreviation
from ate_api.domain.capital_schemes.authority_reviews import CapitalSchemeAuthorityReview
from ate_api.domain.capital_schemes.bid_statuses import CapitalSchemeBidStatus, CapitalSchemeBidStatusDetails
from ate_api.domain.capital_schemes.capital_schemes import CapitalScheme, CapitalSchemeReference
from ate_api.domain.capital_schemes.overviews import CapitalSchemeOverview, CapitalSchemeType
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.funding_programmes import FundingProgrammeCode
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


class TestCapitalScheme:
    def test_create(self) -> None:
        overview = CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1)),
            name="Wirral Package",
            bid_submitting_authority=AuthorityAbbreviation("LIV"),
            funding_programme=FundingProgrammeCode("ATF3"),
            type=CapitalSchemeType.CONSTRUCTION,
        )
        bid_status_details = CapitalSchemeBidStatusDetails(
            effective_date=DateTimeRange(datetime(2020, 2, 1)), bid_status=CapitalSchemeBidStatus.FUNDED
        )

        capital_scheme = CapitalScheme(
            reference=CapitalSchemeReference("ATE00001"), overview=overview, bid_status_details=bid_status_details
        )

        assert (
            capital_scheme.reference == CapitalSchemeReference("ATE00001")
            and capital_scheme.overview == overview
            and capital_scheme.bid_status_details == bid_status_details
            and not capital_scheme.authority_review
        )

    def test_perform_authority_review(self) -> None:
        capital_scheme = CapitalScheme(
            reference=CapitalSchemeReference("ATE00001"),
            overview=dummy_overview(),
            bid_status_details=dummy_bid_status_details(),
        )
        authority_review = CapitalSchemeAuthorityReview(review_date=datetime(2020, 2, 1))

        capital_scheme.perform_authority_review(authority_review)

        assert capital_scheme.authority_review == authority_review
