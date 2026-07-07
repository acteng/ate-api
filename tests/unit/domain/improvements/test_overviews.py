from datetime import UTC, datetime

from ate_api.domain.authorities import AuthorityAbbreviation
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.improvements.overviews import ImprovementOverview


class TestImprovementOverview:
    def test_create(self) -> None:
        overview = ImprovementOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            name="Wirral Package",
            funding_managed_by=AuthorityAbbreviation("LIV"),
            data_source=DataSource.AUTHORITY_UPDATE,
        )

        assert (
            overview.effective_date == DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC))
            and overview.name == "Wirral Package"
            and overview.description is None
            and overview.funding_managed_by == AuthorityAbbreviation("LIV")
            and overview.data_source == DataSource.AUTHORITY_UPDATE
        )

    def test_create_with_description(self) -> None:
        overview = ImprovementOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            name="Wirral Package",
            description='Improvement for the "Wirral Package" capital scheme created as part of funding devolution.',
            funding_managed_by=AuthorityAbbreviation("LIV"),
            data_source=DataSource.AUTHORITY_UPDATE,
        )

        assert (
            overview.description
            == 'Improvement for the "Wirral Package" capital scheme created as part of funding devolution.'
        )
