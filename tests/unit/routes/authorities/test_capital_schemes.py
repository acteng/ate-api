from datetime import UTC, datetime

from fastapi import Request
from pydantic import AnyUrl

from ate_api.domain.capital_schemes.authority_reviews import CapitalSchemeAuthorityReview
from ate_api.domain.capital_schemes.capital_scheme_repositories import CapitalSchemeItem, CapitalSchemeItemOverview
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeReference
from ate_api.domain.data_sources import DataSource
from ate_api.domain.funding_programmes import FundingProgrammeCode
from ate_api.routes.authorities.capital_schemes import CapitalSchemeItemModel, CapitalSchemeItemOverviewModel
from ate_api.routes.capital_schemes.authority_reviews import CapitalSchemeAuthorityReviewModel
from ate_api.routes.data_sources import DataSourceModel


class TestCapitalSchemeItemOverviewModel:
    def test_from_domain(self, http_request: Request, base_url: str) -> None:
        overview = CapitalSchemeItemOverview(name="Wirral Package", funding_programme=FundingProgrammeCode("ATF3"))

        overview_model = CapitalSchemeItemOverviewModel.from_domain(overview, http_request)

        assert overview_model == CapitalSchemeItemOverviewModel(
            name="Wirral Package", funding_programme=AnyUrl(f"{base_url}/funding-programmes/ATF3")
        )


class TestCapitalSchemeItemModel:
    def test_from_domain(self, http_request: Request, base_url: str) -> None:
        capital_scheme_item = CapitalSchemeItem(
            reference=CapitalSchemeReference("ATE00001"),
            overview=CapitalSchemeItemOverview(name="Wirral Package", funding_programme=FundingProgrammeCode("ATF3")),
            authority_review=None,
        )

        capital_scheme_item_model = CapitalSchemeItemModel.from_domain(capital_scheme_item, http_request)

        assert capital_scheme_item_model == CapitalSchemeItemModel(
            id=AnyUrl(f"{base_url}/capital-schemes/ATE00001"),
            reference="ATE00001",
            overview=CapitalSchemeItemOverviewModel(
                name="Wirral Package", funding_programme=AnyUrl(f"{base_url}/funding-programmes/ATF3")
            ),
            authority_review=None,
        )

    def test_from_domain_sets_authority_review(self, http_request: Request, base_url: str) -> None:
        capital_scheme_item = CapitalSchemeItem(
            reference=CapitalSchemeReference("ATE00001"),
            overview=CapitalSchemeItemOverview(name="Wirral Package", funding_programme=FundingProgrammeCode("ATF3")),
            authority_review=CapitalSchemeAuthorityReview(
                review_date=datetime(2020, 2, 1, tzinfo=UTC), data_source=DataSource.AUTHORITY_UPDATE
            ),
        )

        capital_scheme_item_model = CapitalSchemeItemModel.from_domain(capital_scheme_item, http_request)

        assert capital_scheme_item_model.authority_review == CapitalSchemeAuthorityReviewModel(
            review_date=datetime(2020, 2, 1, tzinfo=UTC), source=DataSourceModel.AUTHORITY_UPDATE
        )
