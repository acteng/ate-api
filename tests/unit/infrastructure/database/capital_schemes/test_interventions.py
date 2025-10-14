from datetime import UTC, datetime
from decimal import Decimal

import pytest

from ate_api.domain.capital_schemes.outputs import CapitalSchemeOutput, OutputMeasure, OutputType
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.observation_types import ObservationType
from ate_api.infrastructure.database import (
    CapitalSchemeInterventionEntity,
    InterventionMeasureEntity,
    InterventionMeasureName,
    InterventionTypeEntity,
    InterventionTypeMeasureEntity,
    InterventionTypeName,
    ObservationTypeEntity,
    ObservationTypeName,
)


@pytest.mark.parametrize(
    "type_, type_name",
    [
        (OutputType.NEW_SEGREGATED_CYCLING_FACILITY, InterventionTypeName.NEW_SEGREGATED_CYCLING_FACILITY),
        (
            OutputType.NEW_TEMPORARY_SEGREGATED_CYCLING_FACILITY,
            InterventionTypeName.NEW_TEMPORARY_SEGREGATED_CYCLING_FACILITY,
        ),
        (OutputType.NEW_JUNCTION_TREATMENT, InterventionTypeName.NEW_JUNCTION_TREATMENT),
        (OutputType.NEW_PERMANENT_FOOTWAY, InterventionTypeName.NEW_PERMANENT_FOOTWAY),
        (OutputType.NEW_TEMPORARY_FOOTWAY, InterventionTypeName.NEW_TEMPORARY_FOOTWAY),
        (
            OutputType.NEW_SHARED_USE_WALKING_AND_CYCLING_FACILITIES,
            InterventionTypeName.NEW_SHARED_USE_WALKING_AND_CYCLING_FACILITIES,
        ),
        (
            OutputType.NEW_SHARED_USE_WALKING_WHEELING_AND_CYCLING_FACILITIES,
            InterventionTypeName.NEW_SHARED_USE_WALKING_WHEELING_AND_CYCLING_FACILITIES,
        ),
        (OutputType.IMPROVEMENTS_TO_EXISTING_ROUTE, InterventionTypeName.IMPROVEMENTS_TO_EXISTING_ROUTE),
        (OutputType.AREA_WIDE_TRAFFIC_MANAGEMENT, InterventionTypeName.AREA_WIDE_TRAFFIC_MANAGEMENT),
        (OutputType.BUS_PRIORITY_MEASURES, InterventionTypeName.BUS_PRIORITY_MEASURES),
        (OutputType.SECURE_CYCLE_PARKING, InterventionTypeName.SECURE_CYCLE_PARKING),
        (OutputType.NEW_ROAD_CROSSINGS, InterventionTypeName.NEW_ROAD_CROSSINGS),
        (
            OutputType.RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY,
            InterventionTypeName.RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY,
        ),
        (OutputType.SCHOOL_STREETS, InterventionTypeName.SCHOOL_STREETS),
        (OutputType.UPGRADES_TO_EXISTING_FACILITIES, InterventionTypeName.UPGRADES_TO_EXISTING_FACILITIES),
        (OutputType.E_SCOOTER_TRIALS, InterventionTypeName.E_SCOOTER_TRIALS),
        (OutputType.PARK_AND_CYCLE_STRIDE_FACILITIES, InterventionTypeName.PARK_AND_CYCLE_STRIDE_FACILITIES),
        (OutputType.TRAFFIC_CALMING, InterventionTypeName.TRAFFIC_CALMING),
        (OutputType.WIDENING_EXISTING_FOOTWAY, InterventionTypeName.WIDENING_EXISTING_FOOTWAY),
        (OutputType.OTHER_INTERVENTIONS, InterventionTypeName.OTHER_INTERVENTIONS),
    ],
)
class TestInterventionTypeName:
    def test_from_domain(self, type_: OutputType, type_name: InterventionTypeName) -> None:
        assert InterventionTypeName.from_domain(type_) == type_name

    def test_to_domain(self, type_: OutputType, type_name: InterventionTypeName) -> None:
        assert type_name.to_domain() == type_


@pytest.mark.parametrize(
    "measure, measure_name",
    [
        (OutputMeasure.MILES, InterventionMeasureName.MILES),
        (OutputMeasure.NUMBER_OF_JUNCTIONS, InterventionMeasureName.NUMBER_OF_JUNCTIONS),
        (OutputMeasure.SIZE_OF_AREA, InterventionMeasureName.SIZE_OF_AREA),
        (OutputMeasure.NUMBER_OF_PARKING_SPACES, InterventionMeasureName.NUMBER_OF_PARKING_SPACES),
        (OutputMeasure.NUMBER_OF_CROSSINGS, InterventionMeasureName.NUMBER_OF_CROSSINGS),
        (OutputMeasure.NUMBER_OF_SCHOOL_STREETS, InterventionMeasureName.NUMBER_OF_SCHOOL_STREETS),
        (OutputMeasure.NUMBER_OF_TRIALS, InterventionMeasureName.NUMBER_OF_TRIALS),
        (OutputMeasure.NUMBER_OF_BUS_GATES, InterventionMeasureName.NUMBER_OF_BUS_GATES),
        (OutputMeasure.NUMBER_OF_UPGRADES, InterventionMeasureName.NUMBER_OF_UPGRADES),
        (OutputMeasure.NUMBER_OF_CHILDREN_AFFECTED, InterventionMeasureName.NUMBER_OF_CHILDREN_AFFECTED),
        (OutputMeasure.NUMBER_OF_MEASURES_PLANNED, InterventionMeasureName.NUMBER_OF_MEASURES_PLANNED),
    ],
)
class TestInterventionMeasureName:
    def test_from_domain(self, measure: OutputMeasure, measure_name: InterventionMeasureName) -> None:
        assert InterventionMeasureName.from_domain(measure) == measure_name

    def test_to_domain(self, measure: OutputMeasure, measure_name: InterventionMeasureName) -> None:
        assert measure_name.to_domain() == measure


class TestCapitalSchemeInterventionEntity:
    def test_from_domain(self) -> None:
        output = CapitalSchemeOutput(
            effective_date=DateTimeRange(datetime(2020, 1, 1), datetime(2020, 2, 1)),
            type=OutputType.WIDENING_EXISTING_FOOTWAY,
            measure=OutputMeasure.MILES,
            observation_type=ObservationType.ACTUAL,
            value=Decimal(1.5),
        )

        intervention_entity = CapitalSchemeInterventionEntity.from_domain(
            output, {(OutputType.WIDENING_EXISTING_FOOTWAY, OutputMeasure.MILES): 1}, {ObservationType.ACTUAL: 2}
        )

        assert (
            intervention_entity.intervention_type_measure_id == 1
            and intervention_entity.intervention_value == Decimal(1.5)
            and intervention_entity.observation_type_id == 2
            and intervention_entity.effective_date_from == datetime(2020, 1, 1)
            and intervention_entity.effective_date_to == datetime(2020, 2, 1)
        )

    def test_from_domain_when_current(self) -> None:
        output = CapitalSchemeOutput(
            effective_date=DateTimeRange(datetime(2020, 1, 1)),
            type=OutputType.WIDENING_EXISTING_FOOTWAY,
            measure=OutputMeasure.MILES,
            observation_type=ObservationType.ACTUAL,
            value=Decimal(1.5),
        )

        intervention_entity = CapitalSchemeInterventionEntity.from_domain(
            output, {(OutputType.WIDENING_EXISTING_FOOTWAY, OutputMeasure.MILES): 0}, {ObservationType.ACTUAL: 0}
        )

        assert not intervention_entity.effective_date_to

    def test_from_domain_converts_dates_to_local_europe_london(self) -> None:
        output = CapitalSchemeOutput(
            effective_date=DateTimeRange(datetime(2020, 6, 1, 12, tzinfo=UTC), datetime(2020, 7, 1, 12, tzinfo=UTC)),
            type=OutputType.WIDENING_EXISTING_FOOTWAY,
            measure=OutputMeasure.MILES,
            observation_type=ObservationType.ACTUAL,
            value=Decimal(1.5),
        )

        intervention_entity = CapitalSchemeInterventionEntity.from_domain(
            output, {(OutputType.WIDENING_EXISTING_FOOTWAY, OutputMeasure.MILES): 0}, {ObservationType.ACTUAL: 0}
        )

        assert intervention_entity.effective_date_from == datetime(2020, 6, 1, 13)
        assert intervention_entity.effective_date_to == datetime(2020, 7, 1, 13)

    def test_to_domain(self) -> None:
        intervention_entity = CapitalSchemeInterventionEntity(
            intervention_type_measure=InterventionTypeMeasureEntity(
                intervention_type=InterventionTypeEntity(
                    intervention_type_name=InterventionTypeName.WIDENING_EXISTING_FOOTWAY
                ),
                intervention_measure=InterventionMeasureEntity(intervention_measure_name=InterventionMeasureName.MILES),
            ),
            intervention_value=Decimal("1.500000"),
            observation_type=ObservationTypeEntity(observation_type_name=ObservationTypeName.ACTUAL),
            effective_date_from=datetime(2020, 1, 1),
            effective_date_to=datetime(2020, 2, 1),
        )

        output = intervention_entity.to_domain()

        assert output == CapitalSchemeOutput(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC), datetime(2020, 2, 1, tzinfo=UTC)),
            type=OutputType.WIDENING_EXISTING_FOOTWAY,
            measure=OutputMeasure.MILES,
            observation_type=ObservationType.ACTUAL,
            value=Decimal(1.5),
        )

    def test_to_domain_when_current(self) -> None:
        intervention_entity = CapitalSchemeInterventionEntity(
            intervention_type_measure=InterventionTypeMeasureEntity(
                intervention_type=InterventionTypeEntity(
                    intervention_type_name=InterventionTypeName.WIDENING_EXISTING_FOOTWAY
                ),
                intervention_measure=InterventionMeasureEntity(intervention_measure_name=InterventionMeasureName.MILES),
            ),
            intervention_value=Decimal("1.500000"),
            observation_type=ObservationTypeEntity(observation_type_name=ObservationTypeName.ACTUAL),
            effective_date_from=datetime(2020, 1, 1),
        )

        output = intervention_entity.to_domain()

        assert not output.effective_date.to

    def test_to_domain_converts_dates_from_local_europe_london(self) -> None:
        intervention_entity = CapitalSchemeInterventionEntity(
            intervention_type_measure=InterventionTypeMeasureEntity(
                intervention_type=InterventionTypeEntity(
                    intervention_type_name=InterventionTypeName.WIDENING_EXISTING_FOOTWAY
                ),
                intervention_measure=InterventionMeasureEntity(intervention_measure_name=InterventionMeasureName.MILES),
            ),
            intervention_value=Decimal("1.500000"),
            observation_type=ObservationTypeEntity(observation_type_name=ObservationTypeName.ACTUAL),
            effective_date_from=datetime(2020, 6, 1, 13),
            effective_date_to=datetime(2020, 7, 1, 13),
        )

        output = intervention_entity.to_domain()

        assert output.effective_date == DateTimeRange(
            datetime(2020, 6, 1, 12, tzinfo=UTC), datetime(2020, 7, 1, 12, tzinfo=UTC)
        )
