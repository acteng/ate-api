from datetime import datetime

from ate_api.domain.capital_schemes import CapitalScheme
from ate_api.domain.dates import DateTimeRange
from ate_api.main import app
from ate_api.routes.capital_schemes import (
    CapitalSchemeModel,
    CapitalSchemeOverviewModel,
)
from ate_api.routes.dates import DateTimeRangeModel


class TestCapitalSchemeModel:
    def test_link_from_identifier(self) -> None:
        assert CapitalSchemeModel.link_from_identifier("ATE00001", app) == "/capital-schemes/ATE00001"

    def test_from_domain(self) -> None:
        capital_scheme = CapitalScheme(
            reference="ATE00001",
            effective_date=DateTimeRange(datetime(2020, 1, 1)),
            name="Wirral Package",
            bid_submitting_authority="LIV",
        )

        capital_scheme_model = CapitalSchemeModel.from_domain(capital_scheme, app)

        assert capital_scheme_model == CapitalSchemeModel(
            reference="ATE00001",
            overview=CapitalSchemeOverviewModel(
                effective_date=DateTimeRangeModel(from_=datetime(2020, 1, 1)),
                name="Wirral Package",
                bid_submitting_authority="/authorities/LIV",
            ),
        )

    def test_to_domain(self) -> None:
        capital_scheme_model = CapitalSchemeModel(
            reference="ATE00001",
            overview=CapitalSchemeOverviewModel(
                effective_date=DateTimeRangeModel(from_=datetime(2020, 1, 1)),
                name="Wirral Package",
                bid_submitting_authority="/authorities/LIV",
            ),
        )

        capital_scheme = capital_scheme_model.to_domain()

        assert (
            capital_scheme.reference == "ATE00001"
            and capital_scheme.effective_date == DateTimeRange(datetime(2020, 1, 1))
            and capital_scheme.name == "Wirral Package"
            and capital_scheme.bid_submitting_authority == "LIV"
        )


class TestCapitalSchemeOverviewModel:
    def test_from_domain(self) -> None:
        capital_scheme = CapitalScheme(
            reference="ATE00001",
            effective_date=DateTimeRange(datetime(2020, 1, 1)),
            name="Wirral Package",
            bid_submitting_authority="LIV",
        )

        overview_model = CapitalSchemeOverviewModel.from_domain(capital_scheme, app)

        assert overview_model == CapitalSchemeOverviewModel(
            effective_date=DateTimeRangeModel(from_=datetime(2020, 1, 1)),
            name="Wirral Package",
            bid_submitting_authority="/authorities/LIV",
        )

    def test_to_domain(self) -> None:
        overview_model = CapitalSchemeOverviewModel(
            effective_date=DateTimeRangeModel(from_=datetime(2020, 1, 1)),
            name="Wirral Package",
            bid_submitting_authority="/authorities/LIV",
        )

        capital_scheme = overview_model.to_domain("ATE00001")

        assert (
            capital_scheme.reference == "ATE00001"
            and capital_scheme.effective_date == DateTimeRange(datetime(2020, 1, 1))
            and capital_scheme.name == "Wirral Package"
            and capital_scheme.bid_submitting_authority == "LIV"
        )
