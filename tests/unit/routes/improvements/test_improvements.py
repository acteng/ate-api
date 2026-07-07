from datetime import UTC, datetime

from fastapi import Request
from pydantic import AnyUrl

from ate_api.domain.authorities import AuthorityAbbreviation
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.improvements.improvements import Improvement, ImprovementReference
from ate_api.domain.improvements.overviews import ImprovementOverview
from ate_api.routes.data_sources import DataSourceModel
from ate_api.routes.improvements.improvements import ImprovementModel
from ate_api.routes.improvements.overviews import ImprovementOverviewModel


class TestImprovementModel:
    def test_from_domain(self, http_request: Request, base_url: str) -> None:
        improvement = Improvement(
            reference=ImprovementReference("IMP00001"),
            overview=ImprovementOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                name="Wirral Package",
                funding_managed_by=AuthorityAbbreviation("LIV"),
                data_source=DataSource.AUTHORITY_UPDATE,
            ),
        )

        improvement_model = ImprovementModel.from_domain(improvement, http_request)

        assert improvement_model == ImprovementModel(
            id=AnyUrl(f"{base_url}/improvements/IMP00001"),
            reference="IMP00001",
            overview=ImprovementOverviewModel(
                name="Wirral Package",
                funding_managed_by=AnyUrl(f"{base_url}/authorities/LIV"),
                source=DataSourceModel.AUTHORITY_UPDATE,
            ),
        )

    def test_to_domain(self, http_request: Request, base_url: str) -> None:
        improvement_model = ImprovementModel(
            reference="IMP00001",
            overview=ImprovementOverviewModel(
                name="Wirral Package",
                funding_managed_by=AnyUrl(f"{base_url}/authorities/LIV"),
                source=DataSourceModel.AUTHORITY_UPDATE,
            ),
        )

        improvement = improvement_model.to_domain(datetime(2020, 1, 1, tzinfo=UTC), http_request)

        assert improvement.reference == ImprovementReference("IMP00001")
        assert improvement.overview == ImprovementOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            name="Wirral Package",
            funding_managed_by=AuthorityAbbreviation("LIV"),
            data_source=DataSource.AUTHORITY_UPDATE,
        )
