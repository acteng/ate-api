import pytest

from ate_api.domain.data_sources import DataSource
from ate_api.infrastructure.database import DataSourceName


@pytest.mark.parametrize(
    "source, source_name",
    [
        (DataSource.PULSE_5, DataSourceName.PULSE_5),
        (DataSource.PULSE_6, DataSourceName.PULSE_6),
        (DataSource.ATF4_BID, DataSourceName.ATF4_BID),
        (DataSource.ATF3_BID, DataSourceName.ATF3_BID),
        (DataSource.INSPECTORATE_REQUEST, DataSourceName.INSPECTORATE_REQUEST),
        (DataSource.REGIONAL_TEAM_REQUEST, DataSourceName.REGIONAL_TEAM_REQUEST),
        (DataSource.INVESTMENT_TEAM_REQUEST, DataSourceName.INVESTMENT_TEAM_REQUEST),
        (DataSource.ATE_PUBLISHED_DATA, DataSourceName.ATE_PUBLISHED_DATA),
        (DataSource.CHANGE_CONTROL, DataSourceName.CHANGE_CONTROL),
        (DataSource.ATF4E_BID, DataSourceName.ATF4E_BID),
        (DataSource.ATF4E_MODERATION, DataSourceName.ATF4E_MODERATION),
        (DataSource.PULSE_2023_24_Q2, DataSourceName.PULSE_2023_24_Q2),
        (DataSource.PULSE_2023_24_Q3, DataSourceName.PULSE_2023_24_Q3),
        (DataSource.PULSE_2023_24_Q4, DataSourceName.PULSE_2023_24_Q4),
        (DataSource.INITIAL_SCHEME_LIST, DataSourceName.INITIAL_SCHEME_LIST),
        (DataSource.AUTHORITY_UPDATE, DataSourceName.AUTHORITY_UPDATE),
        (DataSource.UNKNOWN, DataSourceName.UNKNOWN),
        (DataSource.PULSE_2023_24_Q2_DATA_CLEANSE, DataSourceName.PULSE_2023_24_Q2_DATA_CLEANSE),
        (DataSource.PULSE_2023_24_Q3_DATA_CLEANSE, DataSourceName.PULSE_2023_24_Q3_DATA_CLEANSE),
        (DataSource.LUF_SCHEME_LIST, DataSourceName.LUF_SCHEME_LIST),
        (DataSource.LUF_QUARTERLY_UPDATE, DataSourceName.LUF_QUARTERLY_UPDATE),
        (DataSource.CRSTS_SCHEME_LIST, DataSourceName.CRSTS_SCHEME_LIST),
        (DataSource.CRSTS_QUARTERLY_UPDATE, DataSourceName.CRSTS_QUARTERLY_UPDATE),
        (DataSource.MRN_SCHEME_LIST, DataSourceName.MRN_SCHEME_LIST),
        (DataSource.MRN_QUARTERLY_UPDATE, DataSourceName.MRN_QUARTERLY_UPDATE),
        (DataSource.CATF_SCHEME_SUBMISSION, DataSourceName.CATF_SCHEME_SUBMISSION),
        (DataSource.IST_SCHEME_LIST, DataSourceName.IST_SCHEME_LIST),
    ],
)
class TestDataSourceName:
    def test_from_domain(self, source: DataSource, source_name: DataSourceName) -> None:
        assert DataSourceName.from_domain(source) == source_name

    def test_to_domain(self, source: DataSource, source_name: DataSourceName) -> None:
        assert source_name.to_domain() == source
