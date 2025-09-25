from datetime import datetime

import pytest
from fastapi import Request
from pydantic import AnyUrl

from ate_api.domain.authorities import AuthorityAbbreviation
from ate_api.domain.capital_schemes.overviews import CapitalSchemeOverview, CapitalSchemeType
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.funding_programmes import FundingProgrammeCode
from ate_api.routes.capital_schemes.overviews import CapitalSchemeOverviewModel, CapitalSchemeTypeModel


@pytest.mark.parametrize(
    "type_, type_model",
    [
        (CapitalSchemeType.DEVELOPMENT, CapitalSchemeTypeModel.DEVELOPMENT),
        (CapitalSchemeType.CONSTRUCTION, CapitalSchemeTypeModel.CONSTRUCTION),
    ],
)
class TestCapitalSchemeTypeModel:
    def test_from_domain(self, type_: CapitalSchemeType, type_model: CapitalSchemeTypeModel) -> None:
        assert CapitalSchemeTypeModel.from_domain(type_) == type_model

    def test_to_domain(self, type_: CapitalSchemeType, type_model: CapitalSchemeTypeModel) -> None:
        assert type_model.to_domain() == type_


class TestCapitalSchemeOverviewModel:
    def test_from_domain(self, http_request: Request, base_url: str) -> None:
        overview = CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1)),
            name="Wirral Package",
            bid_submitting_authority=AuthorityAbbreviation("LIV"),
            funding_programme=FundingProgrammeCode("ATF3"),
            type=CapitalSchemeType.CONSTRUCTION,
        )

        overview_model = CapitalSchemeOverviewModel.from_domain(overview, http_request)

        assert overview_model == CapitalSchemeOverviewModel(
            name="Wirral Package",
            bid_submitting_authority=AnyUrl(f"{base_url}/authorities/LIV"),
            funding_programme=AnyUrl(f"{base_url}/funding-programmes/ATF3"),
            type_=CapitalSchemeTypeModel.CONSTRUCTION,
        )

    def test_to_domain(self, http_request: Request, base_url: str) -> None:
        overview_model = CapitalSchemeOverviewModel(
            name="Wirral Package",
            bid_submitting_authority=AnyUrl(f"{base_url}/authorities/LIV"),
            funding_programme=AnyUrl(f"{base_url}/funding-programmes/ATF3"),
            type_=CapitalSchemeTypeModel.CONSTRUCTION,
        )

        overview = overview_model.to_domain(datetime(2020, 1, 1), http_request)

        assert overview == CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1)),
            name="Wirral Package",
            bid_submitting_authority=AuthorityAbbreviation("LIV"),
            funding_programme=FundingProgrammeCode("ATF3"),
            type=CapitalSchemeType.CONSTRUCTION,
        )
