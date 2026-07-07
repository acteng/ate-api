from datetime import UTC, datetime

from fastapi import Request
from pydantic import AnyUrl

from ate_api.domain.authorities import AuthorityAbbreviation
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.improvements.overviews import ImprovementOverview
from ate_api.routes.data_sources import DataSourceModel
from ate_api.routes.improvements.overviews import ImprovementOverviewModel


class TestImprovementOverviewModel:
    def test_from_domain(self, http_request: Request, base_url: str) -> None:
        overview = ImprovementOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            name="Wirral Package",
            funding_managed_by=AuthorityAbbreviation("LIV"),
            data_source=DataSource.AUTHORITY_UPDATE,
        )

        overview_model = ImprovementOverviewModel.from_domain(overview, http_request)

        assert overview_model == ImprovementOverviewModel(
            name="Wirral Package",
            funding_managed_by=AnyUrl(f"{base_url}/authorities/LIV"),
            source=DataSourceModel.AUTHORITY_UPDATE,
        )

    def test_from_domain_sets_description(self, http_request: Request, base_url: str) -> None:
        overview = ImprovementOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            name="Wirral Package",
            description='Improvement for the "Wirral Package" capital scheme created as part of funding devolution.',
            funding_managed_by=AuthorityAbbreviation("LIV"),
            data_source=DataSource.AUTHORITY_UPDATE,
        )

        overview_model = ImprovementOverviewModel.from_domain(overview, http_request)

        assert (
            overview_model.description
            == 'Improvement for the "Wirral Package" capital scheme created as part of funding devolution.'
        )

    def test_to_domain(self, http_request: Request, base_url: str) -> None:
        overview_model = ImprovementOverviewModel(
            name="Wirral Package",
            funding_managed_by=AnyUrl(f"{base_url}/authorities/LIV"),
            source=DataSourceModel.AUTHORITY_UPDATE,
        )

        overview = overview_model.to_domain(datetime(2020, 1, 1, tzinfo=UTC), http_request)

        assert overview == ImprovementOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            name="Wirral Package",
            funding_managed_by=AuthorityAbbreviation("LIV"),
            data_source=DataSource.AUTHORITY_UPDATE,
        )

    def test_to_domain_sets_description(self, http_request: Request, base_url: str) -> None:
        overview_model = ImprovementOverviewModel(
            name="Wirral Package",
            description='Improvement for the "Wirral Package" capital scheme created as part of funding devolution.',
            funding_managed_by=AnyUrl(f"{base_url}/authorities/LIV"),
            source=DataSourceModel.AUTHORITY_UPDATE,
        )

        overview = overview_model.to_domain(datetime(2020, 1, 1, tzinfo=UTC), http_request)

        assert (
            overview.description
            == 'Improvement for the "Wirral Package" capital scheme created as part of funding devolution.'
        )
