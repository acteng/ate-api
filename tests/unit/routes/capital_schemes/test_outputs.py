from datetime import datetime
from decimal import Decimal

import pytest

from ate_api.domain.capital_schemes.outputs import CapitalSchemeOutput, OutputMeasure, OutputType
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.observation_types import ObservationType
from ate_api.routes.capital_schemes.outputs import CapitalSchemeOutputModel, OutputMeasureModel, OutputTypeModel
from ate_api.routes.observation_types import ObservationTypeModel


@pytest.mark.parametrize(
    "type_, type_model",
    [
        (OutputType.NEW_SEGREGATED_CYCLING_FACILITY, OutputTypeModel.NEW_SEGREGATED_CYCLING_FACILITY),
        (
            OutputType.NEW_TEMPORARY_SEGREGATED_CYCLING_FACILITY,
            OutputTypeModel.NEW_TEMPORARY_SEGREGATED_CYCLING_FACILITY,
        ),
        (OutputType.NEW_JUNCTION_TREATMENT, OutputTypeModel.NEW_JUNCTION_TREATMENT),
        (OutputType.NEW_PERMANENT_FOOTWAY, OutputTypeModel.NEW_PERMANENT_FOOTWAY),
        (OutputType.NEW_TEMPORARY_FOOTWAY, OutputTypeModel.NEW_TEMPORARY_FOOTWAY),
        (
            OutputType.NEW_SHARED_USE_WALKING_AND_CYCLING_FACILITIES,
            OutputTypeModel.NEW_SHARED_USE_WALKING_AND_CYCLING_FACILITIES,
        ),
        (
            OutputType.NEW_SHARED_USE_WALKING_WHEELING_AND_CYCLING_FACILITIES,
            OutputTypeModel.NEW_SHARED_USE_WALKING_WHEELING_AND_CYCLING_FACILITIES,
        ),
        (OutputType.IMPROVEMENTS_TO_EXISTING_ROUTE, OutputTypeModel.IMPROVEMENTS_TO_EXISTING_ROUTE),
        (OutputType.AREA_WIDE_TRAFFIC_MANAGEMENT, OutputTypeModel.AREA_WIDE_TRAFFIC_MANAGEMENT),
        (OutputType.BUS_PRIORITY_MEASURES, OutputTypeModel.BUS_PRIORITY_MEASURES),
        (OutputType.SECURE_CYCLE_PARKING, OutputTypeModel.SECURE_CYCLE_PARKING),
        (OutputType.NEW_ROAD_CROSSINGS, OutputTypeModel.NEW_ROAD_CROSSINGS),
        (
            OutputType.RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY,
            OutputTypeModel.RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY,
        ),
        (OutputType.SCHOOL_STREETS, OutputTypeModel.SCHOOL_STREETS),
        (OutputType.UPGRADES_TO_EXISTING_FACILITIES, OutputTypeModel.UPGRADES_TO_EXISTING_FACILITIES),
        (OutputType.E_SCOOTER_TRIALS, OutputTypeModel.E_SCOOTER_TRIALS),
        (OutputType.PARK_AND_CYCLE_STRIDE_FACILITIES, OutputTypeModel.PARK_AND_CYCLE_STRIDE_FACILITIES),
        (OutputType.TRAFFIC_CALMING, OutputTypeModel.TRAFFIC_CALMING),
        (OutputType.WIDENING_EXISTING_FOOTWAY, OutputTypeModel.WIDENING_EXISTING_FOOTWAY),
        (OutputType.OTHER_INTERVENTIONS, OutputTypeModel.OTHER_INTERVENTIONS),
    ],
)
class TestOutputTypeModel:
    def test_from_domain(self, type_: OutputType, type_model: OutputTypeModel) -> None:
        assert OutputTypeModel.from_domain(type_) == type_model

    def test_to_domain(self, type_: OutputType, type_model: OutputTypeModel) -> None:
        assert type_model.to_domain() == type_


@pytest.mark.parametrize(
    "measure, measure_model",
    [
        (OutputMeasure.MILES, OutputMeasureModel.MILES),
        (OutputMeasure.NUMBER_OF_JUNCTIONS, OutputMeasureModel.NUMBER_OF_JUNCTIONS),
        (OutputMeasure.SIZE_OF_AREA, OutputMeasureModel.SIZE_OF_AREA),
        (OutputMeasure.NUMBER_OF_PARKING_SPACES, OutputMeasureModel.NUMBER_OF_PARKING_SPACES),
        (OutputMeasure.NUMBER_OF_CROSSINGS, OutputMeasureModel.NUMBER_OF_CROSSINGS),
        (OutputMeasure.NUMBER_OF_SCHOOL_STREETS, OutputMeasureModel.NUMBER_OF_SCHOOL_STREETS),
        (OutputMeasure.NUMBER_OF_TRIALS, OutputMeasureModel.NUMBER_OF_TRIALS),
        (OutputMeasure.NUMBER_OF_BUS_GATES, OutputMeasureModel.NUMBER_OF_BUS_GATES),
        (OutputMeasure.NUMBER_OF_UPGRADES, OutputMeasureModel.NUMBER_OF_UPGRADES),
        (OutputMeasure.NUMBER_OF_CHILDREN_AFFECTED, OutputMeasureModel.NUMBER_OF_CHILDREN_AFFECTED),
        (OutputMeasure.NUMBER_OF_MEASURES_PLANNED, OutputMeasureModel.NUMBER_OF_MEASURES_PLANNED),
    ],
)
class TestOutputMeasureModel:
    def test_from_domain(self, measure: OutputMeasure, measure_model: OutputMeasureModel) -> None:
        assert OutputMeasureModel.from_domain(measure) == measure_model

    def test_to_domain(self, measure: OutputMeasure, measure_model: OutputMeasureModel) -> None:
        assert measure_model.to_domain() == measure


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
