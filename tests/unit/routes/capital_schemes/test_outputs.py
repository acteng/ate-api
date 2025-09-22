from datetime import datetime
from decimal import Decimal

from ate_api.domain.capital_schemes.outputs import CapitalSchemeOutput, OutputMeasure, OutputType
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.observation_types import ObservationType
from ate_api.routes.capital_schemes.outputs import CapitalSchemeOutputModel, OutputMeasureModel, OutputTypeModel
from ate_api.routes.observation_types import ObservationTypeModel


class TestOutputTypeModel:
    def test_from_domain(self) -> None:
        assert (
            OutputTypeModel.from_domain(OutputType.WIDENING_EXISTING_FOOTWAY)
            == OutputTypeModel.WIDENING_EXISTING_FOOTWAY
        )

    def test_to_domain(self) -> None:
        assert OutputTypeModel.WIDENING_EXISTING_FOOTWAY.to_domain() == OutputType.WIDENING_EXISTING_FOOTWAY


class TestOutputMeasureModel:
    def test_from_domain(self) -> None:
        assert OutputMeasureModel.from_domain(OutputMeasure.MILES) == OutputMeasureModel.MILES

    def test_to_domain(self) -> None:
        assert OutputMeasureModel.MILES.to_domain() == OutputMeasure.MILES


class TestCapitalSchemeOutputModel:
    def test_from_domain(self) -> None:
        output = CapitalSchemeOutput(
            effective_date=DateTimeRange(datetime(2020, 1, 1)),
            type=OutputType.WIDENING_EXISTING_FOOTWAY,
            measure=OutputMeasure.MILES,
            observation_type=ObservationType.ACTUAL,
            value=Decimal(1.5),
        )

        output_model = CapitalSchemeOutputModel.from_domain(output)

        assert output_model == CapitalSchemeOutputModel(
            type=OutputTypeModel.WIDENING_EXISTING_FOOTWAY,
            measure=OutputMeasureModel.MILES,
            observation_type=ObservationTypeModel.ACTUAL,
            value=Decimal(1.5),
        )

    def test_to_domain(self) -> None:
        output_model = CapitalSchemeOutputModel(
            type=OutputTypeModel.WIDENING_EXISTING_FOOTWAY,
            measure=OutputMeasureModel.MILES,
            observation_type=ObservationTypeModel.ACTUAL,
            value=Decimal(1.5),
        )

        output = output_model.to_domain(datetime(2020, 1, 1))

        assert output == CapitalSchemeOutput(
            effective_date=DateTimeRange(datetime(2020, 1, 1)),
            type=OutputType.WIDENING_EXISTING_FOOTWAY,
            measure=OutputMeasure.MILES,
            observation_type=ObservationType.ACTUAL,
            value=Decimal(1.5),
        )
