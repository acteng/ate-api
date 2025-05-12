from datetime import datetime

from pydantic import AnyUrl
from starlette.requests import Request

from ate_api.domain.capital_schemes import CapitalScheme, CapitalSchemeType
from ate_api.domain.dates import DateTimeRange
from ate_api.routes.capital_schemes import (
    CapitalSchemeModel,
    CapitalSchemeOverviewModel,
    CapitalSchemeTypeModel,
)
from ate_api.routes.dates import DateTimeRangeModel


class TestCapitalSchemeModel:
    def test_from_domain(self, http_request: Request, base_url: str) -> None:
        capital_scheme = CapitalScheme(
            reference="ATE00001",
            effective_date=DateTimeRange(datetime(2020, 1, 1)),
            name="Wirral Package",
            bid_submitting_authority="LIV",
            funding_programme="ATF3",
            type_=CapitalSchemeType.CONSTRUCTION,
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
        )

        capital_scheme = capital_scheme_model.to_domain(http_request)

        assert (
            capital_scheme.reference == "ATE00001"
            and capital_scheme.effective_date == DateTimeRange(datetime(2020, 1, 1))
            and capital_scheme.name == "Wirral Package"
            and capital_scheme.bid_submitting_authority == "LIV"
            and capital_scheme.funding_programme == "ATF3"
            and capital_scheme.type == CapitalSchemeType.CONSTRUCTION
        )


class TestCapitalSchemeTypeModel:
    def test_from_domain(self) -> None:
        assert CapitalSchemeTypeModel.from_domain(CapitalSchemeType.CONSTRUCTION) == CapitalSchemeTypeModel.CONSTRUCTION

    def test_to_domain(self) -> None:
        assert CapitalSchemeTypeModel.CONSTRUCTION.to_domain() == CapitalSchemeType.CONSTRUCTION


class TestCapitalSchemeOverviewModel:
    def test_from_domain(self, http_request: Request, base_url: str) -> None:
        capital_scheme = CapitalScheme(
            reference="ATE00001",
            effective_date=DateTimeRange(datetime(2020, 1, 1)),
            name="Wirral Package",
            bid_submitting_authority="LIV",
            funding_programme="ATF3",
            type_=CapitalSchemeType.CONSTRUCTION,
        )

        overview_model = CapitalSchemeOverviewModel.from_domain(capital_scheme, http_request)

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

        capital_scheme = overview_model.to_domain("ATE00001", http_request)

        assert (
            capital_scheme.reference == "ATE00001"
            and capital_scheme.effective_date == DateTimeRange(datetime(2020, 1, 1))
            and capital_scheme.name == "Wirral Package"
            and capital_scheme.bid_submitting_authority == "LIV"
            and capital_scheme.funding_programme == "ATF3"
            and capital_scheme.type == CapitalSchemeType.CONSTRUCTION
        )
