from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Self

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ate_api.domain.capital_schemes.outputs import CapitalSchemeOutput, OutputMeasure, OutputType
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.observation_types import ObservationType
from ate_api.infrastructure.database.base import BaseEntity
from ate_api.infrastructure.database.dates import local_to_zoned, zoned_to_local
from ate_api.infrastructure.database.observation_types import ObservationTypeEntity


class InterventionTypeName(Enum):
    NEW_SEGREGATED_CYCLING_FACILITY = "new segregated cycling facility"
    NEW_TEMPORARY_SEGREGATED_CYCLING_FACILITY = "new temporary segregated cycling facility"
    NEW_JUNCTION_TREATMENT = "new junction treatment"
    NEW_PERMANENT_FOOTWAY = "new permanent footway"
    NEW_TEMPORARY_FOOTWAY = "new temporary footway"
    NEW_SHARED_USE_WALKING_AND_CYCLING_FACILITIES = "new shared use (walking and cycling) facilities"
    NEW_SHARED_USE_WALKING_WHEELING_AND_CYCLING_FACILITIES = "new shared use (walking, wheeling & cycling) facilities"
    IMPROVEMENTS_TO_EXISTING_ROUTE = "improvements to make an existing walking/cycle route safer"
    AREA_WIDE_TRAFFIC_MANAGEMENT = "area-wide traffic management (including by TROs (both permanent and experimental))"
    BUS_PRIORITY_MEASURES = "bus priority measures that also enable active travel (for example, bus gates)"
    SECURE_CYCLE_PARKING = "provision of secure cycle parking facilities"
    NEW_ROAD_CROSSINGS = "new road crossings"
    RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY = "restriction or reduction of car parking availability"
    SCHOOL_STREETS = "school streets"
    UPGRADES_TO_EXISTING_FACILITIES = "upgrades to existing facilities (e.g. surfacing, signage, signals)"
    E_SCOOTER_TRIALS = "e-scooter trials"
    PARK_AND_CYCLE_STRIDE_FACILITIES = "park and cycle/stride facilities"
    TRAFFIC_CALMING = "traffic calming (e.g. lane closures, reducing speed limits)"
    WIDENING_EXISTING_FOOTWAY = "widening existing footway"
    OTHER_INTERVENTIONS = "other interventions"

    @classmethod
    def from_domain(cls, type_: OutputType) -> Self:
        return cls[type_.name]

    def to_domain(self) -> OutputType:
        return OutputType[self.name]


class InterventionTypeEntity(BaseEntity):
    __tablename__ = "intervention_type"
    __table_args__ = {"schema": "capital_scheme"}

    intervention_type_id: Mapped[int] = mapped_column(primary_key=True)
    intervention_type_name: Mapped[InterventionTypeName] = mapped_column(unique=True)


class InterventionMeasureName(Enum):
    MILES = "miles"
    NUMBER_OF_JUNCTIONS = "number of junctions"
    SIZE_OF_AREA = "size of area"
    NUMBER_OF_PARKING_SPACES = "number of parking spaces"
    NUMBER_OF_CROSSINGS = "number of crossings"
    NUMBER_OF_SCHOOL_STREETS = "number of school streets"
    NUMBER_OF_TRIALS = "number of trials"
    NUMBER_OF_BUS_GATES = "number of bus gates"
    NUMBER_OF_UPGRADES = "number of upgrades"
    NUMBER_OF_CHILDREN_AFFECTED = "number of children affected"
    NUMBER_OF_MEASURES_PLANNED = "number of measures planned"

    @classmethod
    def from_domain(cls, measure: OutputMeasure) -> Self:
        return cls[measure.name]

    def to_domain(self) -> OutputMeasure:
        return OutputMeasure[self.name]


class InterventionMeasureEntity(BaseEntity):
    __tablename__ = "intervention_measure"
    __table_args__ = {"schema": "capital_scheme"}

    intervention_measure_id: Mapped[int] = mapped_column(primary_key=True)
    intervention_measure_name: Mapped[InterventionMeasureName] = mapped_column(unique=True)


class InterventionTypeMeasureEntity(BaseEntity):
    __tablename__ = "intervention_type_measure"
    __table_args__ = {"schema": "capital_scheme"}

    intervention_type_measure_id: Mapped[int] = mapped_column(primary_key=True)
    intervention_type_id = mapped_column(ForeignKey(InterventionTypeEntity.intervention_type_id), nullable=False)
    intervention_type: Mapped[InterventionTypeEntity] = relationship(lazy="raise")
    intervention_measure_id = mapped_column(
        ForeignKey(InterventionMeasureEntity.intervention_measure_id), nullable=False
    )
    intervention_measure: Mapped[InterventionMeasureEntity] = relationship(lazy="raise")


class CapitalSchemeInterventionEntity(BaseEntity):
    __tablename__ = "capital_scheme_intervention"
    __table_args__ = {"schema": "capital_scheme"}

    capital_scheme_intervention_id: Mapped[int] = mapped_column(primary_key=True)
    capital_scheme_id = mapped_column(ForeignKey("capital_scheme.capital_scheme.capital_scheme_id"), nullable=False)
    intervention_type_measure_id = mapped_column(
        ForeignKey(InterventionTypeMeasureEntity.intervention_type_measure_id), nullable=False
    )
    intervention_type_measure: Mapped[InterventionTypeMeasureEntity] = relationship(lazy="raise")
    intervention_value: Mapped[Decimal] = mapped_column(Numeric(precision=15, scale=6))
    observation_type_id = mapped_column(ForeignKey(ObservationTypeEntity.observation_type_id), nullable=False)
    observation_type: Mapped[ObservationTypeEntity] = relationship(lazy="raise")
    effective_date_from: Mapped[datetime]
    effective_date_to: Mapped[datetime | None]

    @classmethod
    def from_domain(
        cls,
        output: CapitalSchemeOutput,
        intervention_type_measure_ids: dict[tuple[OutputType, OutputMeasure], int],
        observation_type_ids: dict[ObservationType, int],
    ) -> Self:
        return cls(
            intervention_type_measure_id=intervention_type_measure_ids[(output.type, output.measure)],
            intervention_value=output.value,
            observation_type_id=observation_type_ids[output.observation_type],
            effective_date_from=zoned_to_local(output.effective_date.from_),
            effective_date_to=zoned_to_local(output.effective_date.to) if output.effective_date.to else None,
        )

    def to_domain(self) -> CapitalSchemeOutput:
        return CapitalSchemeOutput(
            effective_date=DateTimeRange(
                local_to_zoned(self.effective_date_from),
                local_to_zoned(self.effective_date_to) if self.effective_date_to else None,
            ),
            type=self.intervention_type_measure.intervention_type.intervention_type_name.to_domain(),
            measure=self.intervention_type_measure.intervention_measure.intervention_measure_name.to_domain(),
            observation_type=self.observation_type.observation_type_name.to_domain(),
            value=self.intervention_value,
        )
