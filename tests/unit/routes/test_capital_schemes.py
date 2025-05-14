from datetime import datetime

from pydantic import AnyUrl
from starlette.requests import Request

from ate_api.domain.capital_schemes import (
    CapitalScheme,
    CapitalSchemeAuthorityReview,
    CapitalSchemeBidStatus,
    CapitalSchemeBidStatusDetails,
    CapitalSchemeOverview,
    CapitalSchemeType,
)
from ate_api.domain.dates import DateTimeRange
from ate_api.routes.capital_schemes import (
    CapitalSchemeAuthorityReviewModel,
    CapitalSchemeBidStatusDetailsModel,
    CapitalSchemeBidStatusModel,
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
            bid_status_details=CapitalSchemeBidStatusDetails(
                effective_date=DateTimeRange(datetime(2020, 2, 1)),
                bid_status=CapitalSchemeBidStatus.FUNDED,
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
            bid_status_details=CapitalSchemeBidStatusDetailsModel(
                effective_date=DateTimeRangeModel(from_=datetime(2020, 2, 1)),
                bid_status=CapitalSchemeBidStatusModel.FUNDED,
            ),
            authority_review=None,
        )

    def test_from_domain_sets_authority_review(self, http_request: Request) -> None:
        capital_scheme = CapitalScheme(
            reference="ATE00001", overview=self._dummy_overview(), bid_status_details=self._dummy_bid_status_details()
        )
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
            bid_status_details=CapitalSchemeBidStatusDetailsModel(
                effective_date=DateTimeRangeModel(from_=datetime(2020, 2, 1)),
                bid_status=CapitalSchemeBidStatusModel.FUNDED,
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
            and capital_scheme.bid_status_details
            == CapitalSchemeBidStatusDetails(
                effective_date=DateTimeRange(datetime(2020, 2, 1)), bid_status=CapitalSchemeBidStatus.FUNDED
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
            bid_status_details=self._dummy_bid_status_details_model(),
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

    @staticmethod
    def _dummy_bid_status_details() -> CapitalSchemeBidStatusDetails:
        return CapitalSchemeBidStatusDetails(
            effective_date=DateTimeRange(datetime.min), bid_status=CapitalSchemeBidStatus.NOT_FUNDED
        )

    @staticmethod
    def _dummy_bid_status_details_model() -> CapitalSchemeBidStatusDetailsModel:
        return CapitalSchemeBidStatusDetailsModel(
            effective_date=DateTimeRangeModel(from_=datetime.min), bid_status=CapitalSchemeBidStatusModel.NOT_FUNDED
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


class TestCapitalSchemeStatusModel:
    def test_from_domain(self) -> None:
        assert (
            CapitalSchemeBidStatusModel.from_domain(CapitalSchemeBidStatus.FUNDED) == CapitalSchemeBidStatusModel.FUNDED
        )

    def test_to_domain(self) -> None:
        assert CapitalSchemeBidStatusModel.FUNDED.to_domain() == CapitalSchemeBidStatus.FUNDED


class TestCapitalSchemeBidStatusModel:
    def test_from_domain(self) -> None:
        bid_status_details = CapitalSchemeBidStatusDetails(
            effective_date=DateTimeRange(datetime(2020, 1, 1)), bid_status=CapitalSchemeBidStatus.FUNDED
        )

        bid_status_details_model = CapitalSchemeBidStatusDetailsModel.from_domain(bid_status_details)

        assert bid_status_details_model == CapitalSchemeBidStatusDetailsModel(
            effective_date=DateTimeRangeModel(from_=datetime(2020, 1, 1)), bid_status=CapitalSchemeBidStatusModel.FUNDED
        )

    def test_to_domain(self) -> None:
        bid_status_details_model = CapitalSchemeBidStatusDetailsModel(
            effective_date=DateTimeRangeModel(from_=datetime(2020, 1, 1)), bid_status=CapitalSchemeBidStatusModel.FUNDED
        )

        bid_status_details = bid_status_details_model.to_domain()

        assert bid_status_details == CapitalSchemeBidStatusDetails(
            effective_date=DateTimeRange(datetime(2020, 1, 1)), bid_status=CapitalSchemeBidStatus.FUNDED
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
