from datetime import datetime

from ate_api.domain.capital_schemes import (
    CapitalScheme,
    CapitalSchemeAuthorityReview,
    CapitalSchemeOverview,
    CapitalSchemeType,
)
from ate_api.domain.dates import DateTimeRange


class TestCapitalSchemeOverview:
    pass


class TestCapitalScheme:
    def test_create(self) -> None:
        overview = CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1)),
            name="Wirral Package",
            bid_submitting_authority="LIV",
            funding_programme="ATF3",
            type=CapitalSchemeType.CONSTRUCTION,
        )

        capital_scheme = CapitalScheme(reference="ATE00001", overview=overview)

        assert (
            capital_scheme.reference == "ATE00001"
            and capital_scheme.overview == overview
            and not capital_scheme.authority_review
        )

    def test_perform_authority_review(self) -> None:
        capital_scheme = CapitalScheme(reference="ATE00001", overview=self._dummy_overview())
        authority_review = CapitalSchemeAuthorityReview(review_date=datetime(2020, 2, 1))

        capital_scheme.perform_authority_review(authority_review)

        assert capital_scheme.authority_review == authority_review

    @staticmethod
    def _dummy_overview() -> CapitalSchemeOverview:
        return CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime.min),
            name="",
            bid_submitting_authority="",
            funding_programme="",
            type=CapitalSchemeType.DEVELOPMENT,
        )
