from datetime import datetime

from pydantic import AnyUrl
from starlette.requests import Request

from ate_api.domain.capital_schemes import (
    CapitalScheme,
    CapitalSchemeAuthorityReview,
    CapitalSchemeOverview,
    CapitalSchemeType,
)
from ate_api.domain.dates import DateTimeRange
from ate_api.routes.capital_schemes import (
    CapitalSchemeAuthorityReviewModel,
    CapitalSchemeModel,
    CapitalSchemeOverviewModel,
    CapitalSchemeTypeModel,
)
from ate_api.routes.dates import DateTimeRangeModel


class TestCapitalSchemeModel:
    def test_from_domain(self, http_request: Request, base_url: str) -> None:
        capital_scheme = CapitalScheme(
            reference="ATE00001",
            overview=CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1)),
                name="Wirral Package",
                bid_submitting_authority="LIV",
                funding_programme="ATF3",
                type=CapitalSchemeType.CONSTRUCTION,
            ),
        )

        capital_scheme_model = CapitalSchemeModel.from_domain(capital_scheme, http_request)

        assert capital_scheme_model == CapitalSchemeModel(
            reference="ATE00001",
            overview=CapitalSchemeOverviewModel(
                effective_date=DateTimeRangeModel(from_=datetime(2020, 1, 1)),
                name="Wirral Package",
                bid_submitting_authority=AnyUrl(f"{base_url}/authorities/LIV"),
                funding_programme=AnyUrl(f"{base_url}/funding-programmes/ATF3"),
                type_=CapitalSchemeTypeModel.CONSTRUCTION,
            ),
            authority_review=None,
        )

    def test_from_domain_sets_authority_review(self, http_request: Request) -> None:
        capital_scheme = CapitalScheme(reference="ATE00001", overview=self._dummy_overview())
        capital_scheme.perform_authority_review(CapitalSchemeAuthorityReview(review_date=datetime(2020, 1, 1)))

        capital_scheme_model = CapitalSchemeModel.from_domain(capital_scheme, http_request)

        assert capital_scheme_model.authority_review == CapitalSchemeAuthorityReviewModel(
            review_date=datetime(2020, 1, 1)
        )

    def test_to_domain(self, http_request: Request, base_url: str) -> None:
        capital_scheme_model = CapitalSchemeModel(
            reference="ATE00001",
            overview=CapitalSchemeOverviewModel(
                effective_date=DateTimeRangeModel(from_=datetime(2020, 1, 1)),
                name="Wirral Package",
                bid_submitting_authority=AnyUrl(f"{base_url}/authorities/LIV"),
                funding_programme=AnyUrl(f"{base_url}/funding-programmes/ATF3"),
                type_=CapitalSchemeTypeModel.CONSTRUCTION,
            ),
            authority_review=None,
        )

        capital_scheme = capital_scheme_model.to_domain(http_request)

        assert (
            capital_scheme.reference == "ATE00001"
            and capital_scheme.overview
            == CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1)),
                name="Wirral Package",
                bid_submitting_authority="LIV",
                funding_programme="ATF3",
                type=CapitalSchemeType.CONSTRUCTION,
            )
            and not capital_scheme.authority_review
        )

    def test_to_domain_sets_authority_review(self, http_request: Request, base_url: str) -> None:
        capital_scheme_model = CapitalSchemeModel(
            reference="ATE00001",
            overview=CapitalSchemeOverviewModel(
                effective_date=DateTimeRangeModel(from_=datetime(2020, 1, 1)),
                name="Wirral Package",
                bid_submitting_authority=AnyUrl(f"{base_url}/authorities/LIV"),
                funding_programme=AnyUrl(f"{base_url}/funding-programmes/ATF3"),
                type_=CapitalSchemeTypeModel.CONSTRUCTION,
            ),
            authority_review=CapitalSchemeAuthorityReviewModel(review_date=datetime(2020, 2, 1)),
        )

        capital_scheme = capital_scheme_model.to_domain(http_request)

        assert capital_scheme.authority_review == CapitalSchemeAuthorityReview(review_date=datetime(2020, 2, 1))

    @staticmethod
    def _dummy_overview() -> CapitalSchemeOverview:
        return CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime.min),
            name="",
            bid_submitting_authority="dummy",
            funding_programme="dummy",
            type=CapitalSchemeType.DEVELOPMENT,
        )


class TestCapitalSchemeTypeModel:
    def test_from_domain(self) -> None:
        assert CapitalSchemeTypeModel.from_domain(CapitalSchemeType.CONSTRUCTION) == CapitalSchemeTypeModel.CONSTRUCTION

    def test_to_domain(self) -> None:
        assert CapitalSchemeTypeModel.CONSTRUCTION.to_domain() == CapitalSchemeType.CONSTRUCTION


class TestCapitalSchemeOverviewModel:
    def test_from_domain(self, http_request: Request, base_url: str) -> None:
        overview = CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1)),
            name="Wirral Package",
            bid_submitting_authority="LIV",
            funding_programme="ATF3",
            type=CapitalSchemeType.CONSTRUCTION,
        )

        overview_model = CapitalSchemeOverviewModel.from_domain(overview, http_request)

        assert overview_model == CapitalSchemeOverviewModel(
            effective_date=DateTimeRangeModel(from_=datetime(2020, 1, 1)),
            name="Wirral Package",
            bid_submitting_authority=AnyUrl(f"{base_url}/authorities/LIV"),
            funding_programme=AnyUrl(f"{base_url}/funding-programmes/ATF3"),
            type_=CapitalSchemeTypeModel.CONSTRUCTION,
        )

    def test_to_domain(self, http_request: Request, base_url: str) -> None:
        overview_model = CapitalSchemeOverviewModel(
            effective_date=DateTimeRangeModel(from_=datetime(2020, 1, 1)),
            name="Wirral Package",
            bid_submitting_authority=AnyUrl(f"{base_url}/authorities/LIV"),
            funding_programme=AnyUrl(f"{base_url}/funding-programmes/ATF3"),
            type_=CapitalSchemeTypeModel.CONSTRUCTION,
        )

        overview = overview_model.to_domain(http_request)

        assert overview == CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1)),
            name="Wirral Package",
            bid_submitting_authority="LIV",
            funding_programme="ATF3",
            type=CapitalSchemeType.CONSTRUCTION,
        )


class TestCapitalSchemeAuthorityReviewModel:
    def test_from_domain(self) -> None:
        authority_review = CapitalSchemeAuthorityReview(review_date=datetime(2020, 1, 1))

        authority_review_model = CapitalSchemeAuthorityReviewModel.from_domain(authority_review)

        assert authority_review_model == CapitalSchemeAuthorityReviewModel(review_date=datetime(2020, 1, 1))

    def test_to_domain(self) -> None:
        authority_review_model = CapitalSchemeAuthorityReviewModel(review_date=datetime(2020, 1, 1))

        authority_review = authority_review_model.to_domain()

        assert authority_review == CapitalSchemeAuthorityReview(review_date=datetime(2020, 1, 1))
