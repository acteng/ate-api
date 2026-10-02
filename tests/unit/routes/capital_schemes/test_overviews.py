from datetime import UTC, datetime

from fastapi import Request
from pydantic import AnyUrl

from ate_api.domain.capital_schemes.overviews import CapitalSchemeOverview
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.funding_programmes import FundingProgrammeCode
from ate_api.domain.improvements.improvements import ImprovementReference
from ate_api.routes.capital_schemes.overviews import CapitalSchemeOverviewModel
from tests.unit.domain.builders import build_capital_scheme_overview


class TestCapitalSchemeOverviewModel:
    def test_from_domain(self, http_request: Request, base_url: str) -> None:
        overview = CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            name="Wirral Package",
            funding_programme=FundingProgrammeCode("ATF3"),
            improvement=ImprovementReference("IMP00001"),
        )

        overview_model = CapitalSchemeOverviewModel.from_domain(overview, http_request)

        assert overview_model == CapitalSchemeOverviewModel(
            name="Wirral Package",
            funding_programme=AnyUrl(f"{base_url}/funding-programmes/ATF3"),
            improvement=AnyUrl(f"{base_url}/improvements/IMP00001"),
        )

    def test_from_domain_without_improvement(self, http_request: Request, base_url: str) -> None:
        overview = build_capital_scheme_overview(improvement=None)

        overview_model = CapitalSchemeOverviewModel.from_domain(overview, http_request)

        assert not overview_model.improvement

    def test_to_domain(self, http_request: Request, base_url: str) -> None:
        overview_model = CapitalSchemeOverviewModel(
            name="Wirral Package",
            funding_programme=AnyUrl(f"{base_url}/funding-programmes/ATF3"),
            improvement=AnyUrl(f"{base_url}/improvements/IMP00001"),
        )

        overview = overview_model.to_domain(datetime(2020, 1, 1, tzinfo=UTC), http_request)

        assert overview == CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            name="Wirral Package",
            funding_programme=FundingProgrammeCode("ATF3"),
            improvement=ImprovementReference("IMP00001"),
        )

    def test_to_domain_without_improvement(self, http_request: Request, base_url: str) -> None:
        overview_model = CapitalSchemeOverviewModel(
            name="Wirral Package", funding_programme=AnyUrl(f"{base_url}/funding-programmes/ATF3"), improvement=None
        )

        overview = overview_model.to_domain(datetime(2020, 1, 1, tzinfo=UTC), http_request)

        assert not overview.improvement
