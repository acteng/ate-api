from datetime import datetime

from ate_api.domain.capital_schemes import CapitalScheme
from ate_api.domain.dates import DateTimeRange


class TestCapitalScheme:
    def test_create(self) -> None:
        capital_scheme = CapitalScheme(
            reference="ATE00001",
            effective_date=DateTimeRange(datetime(2020, 1, 1)),
            name="Wirral Package",
            bid_submitting_authority="LIV",
        )

        assert (
            capital_scheme.reference == "ATE00001"
            and capital_scheme.effective_date == DateTimeRange(datetime(2020, 1, 1))
            and capital_scheme.name == "Wirral Package"
            and capital_scheme.bid_submitting_authority == "LIV"
        )
