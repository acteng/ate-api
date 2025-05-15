from datetime import datetime

from pydantic import AnyUrl
from starlette.requests import Request

from ate_api.domain.capital_schemes.overviews import CapitalSchemeOverview, CapitalSchemeType
from ate_api.domain.dates import DateTimeRange
from ate_api.routes.capital_schemes.overviews import CapitalSchemeOverviewModel, CapitalSchemeTypeModel
from ate_api.routes.dates import DateTimeRangeModel


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
