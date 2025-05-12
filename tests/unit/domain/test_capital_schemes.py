from datetime import datetime

from ate_api.domain.capital_schemes import (
    CapitalScheme,
    CapitalSchemeOverview,
    CapitalSchemeType,
)
from ate_api.domain.dates import DateTimeRange


class TestCapitalSchemeOverview:
    pass


class TestCapitalScheme:
    def test_create(self) -> None:
        overview = CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1)),
            name="Wirral Package",
            bid_submitting_authority="LIV",
            funding_programme="ATF3",
            type=CapitalSchemeType.CONSTRUCTION,
        )

        capital_scheme = CapitalScheme(reference="ATE00001", overview=overview)

        assert capital_scheme.reference == "ATE00001" and capital_scheme.overview == overview
