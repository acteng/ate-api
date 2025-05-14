from datetime import datetime

from ate_api.domain.capital_schemes import (
    CapitalScheme,
    CapitalSchemeAuthorityReview,
    CapitalSchemeBidStatus,
    CapitalSchemeBidStatusDetails,
    CapitalSchemeOverview,
    CapitalSchemeType,
)
from ate_api.domain.dates import DateTimeRange
from tests.unit.domain.dummies import dummy_bid_status_details, dummy_overview


class TestCapitalScheme:
    def test_create(self) -> None:
        overview = CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1)),
            name="Wirral Package",
            bid_submitting_authority="LIV",
            funding_programme="ATF3",
            type=CapitalSchemeType.CONSTRUCTION,
        )
        bid_status_details = CapitalSchemeBidStatusDetails(
            effective_date=DateTimeRange(datetime(2020, 2, 1)), bid_status=CapitalSchemeBidStatus.FUNDED
        )

        capital_scheme = CapitalScheme(reference="ATE00001", overview=overview, bid_status_details=bid_status_details)

        assert (
            capital_scheme.reference == "ATE00001"
            and capital_scheme.overview == overview
            and capital_scheme.bid_status_details == bid_status_details
            and not capital_scheme.authority_review
        )

    def test_perform_authority_review(self) -> None:
        capital_scheme = CapitalScheme(
            reference="ATE00001", overview=dummy_overview(), bid_status_details=dummy_bid_status_details()
        )
        authority_review = CapitalSchemeAuthorityReview(review_date=datetime(2020, 2, 1))

        capital_scheme.perform_authority_review(authority_review)

        assert capital_scheme.authority_review == authority_review
