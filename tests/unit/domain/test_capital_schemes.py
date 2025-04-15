from datetime import datetime

from ate_api.domain.capital_schemes import CapitalScheme, CapitalSchemeOverview
from ate_api.domain.dates import DateTimeRange


class TestCapitalScheme:
    def test_create(self) -> None:
        capital_scheme = CapitalScheme(reference="ATE00001")

        assert capital_scheme.reference == "ATE00001" and capital_scheme.overviews == []

    def test_overview(self) -> None:
        capital_scheme = CapitalScheme(reference="ATE00001")
        capital_scheme.update_overview(
            CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1), datetime(2020, 2, 1)), bid_submitting_authority="WYO"
            )
        )
        overview = CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 2, 1)), bid_submitting_authority="LIV"
        )
        capital_scheme.update_overview(overview)

        assert capital_scheme.overview == overview

    def test_overviews(self) -> None:
        capital_scheme = CapitalScheme(reference="ATE00001")
        overview1 = CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1), datetime(2020, 2, 1)), bid_submitting_authority="WYO"
        )
        capital_scheme.update_overview(overview1)
        overview2 = CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 2, 1)), bid_submitting_authority="LIV"
        )
        capital_scheme.update_overview(overview2)

        assert capital_scheme.overviews == [overview1, overview2]

    def test_overviews_is_copy(self) -> None:
        capital_scheme = CapitalScheme(reference="ATE00001")
        capital_scheme.update_overview(
            CapitalSchemeOverview(effective_date=DateTimeRange(datetime(2020, 2, 1)), bid_submitting_authority="LIV")
        )

        capital_scheme.overviews.clear()

        assert capital_scheme.overviews

    def test_update_overview(self) -> None:
        capital_scheme = CapitalScheme(reference="ATE00001")
        overview = CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1)), bid_submitting_authority="LIV"
        )

        capital_scheme.update_overview(overview)

        assert capital_scheme.overviews == [overview]


class TestCapitalSchemeOverview:
    def test_create(self) -> None:
        overview = CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1)), bid_submitting_authority="LIV"
        )

        assert (
            overview.effective_date == DateTimeRange(datetime(2020, 1, 1))
            and overview.bid_submitting_authority == "LIV"
        )
