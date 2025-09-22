from datetime import datetime, timezone
from decimal import Decimal

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


class TestInterventionTypeName:
    def test_from_domain(self) -> None:
        assert (
            InterventionTypeName.from_domain(OutputType.WIDENING_EXISTING_FOOTWAY)
            == InterventionTypeName.WIDENING_EXISTING_FOOTWAY
        )

    def test_to_domain(self) -> None:
        assert InterventionTypeName.WIDENING_EXISTING_FOOTWAY.to_domain() == OutputType.WIDENING_EXISTING_FOOTWAY


class TestInterventionMeasureName:
    def test_from_domain(self) -> None:
        assert InterventionMeasureName.from_domain(OutputMeasure.MILES) == InterventionMeasureName.MILES

    def test_to_domain(self) -> None:
        assert InterventionMeasureName.MILES.to_domain() == OutputMeasure.MILES


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
            effective_date=DateTimeRange(
                datetime(2020, 6, 1, 12, tzinfo=timezone.utc), datetime(2020, 7, 1, 12, tzinfo=timezone.utc)
            ),
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
            effective_date=DateTimeRange(
                datetime(2020, 1, 1, tzinfo=timezone.utc), datetime(2020, 2, 1, tzinfo=timezone.utc)
            ),
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
            datetime(2020, 6, 1, 12, tzinfo=timezone.utc), datetime(2020, 7, 1, 12, tzinfo=timezone.utc)
        )
