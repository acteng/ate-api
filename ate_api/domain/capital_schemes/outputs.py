from dataclasses import dataclass
from decimal import Decimal
from enum import Enum, auto

from ate_api.domain.dates import DateTimeRange
from ate_api.domain.observation_types import ObservationType


class OutputType(Enum):
    NEW_SEGREGATED_CYCLING_FACILITY = auto()
    NEW_TEMPORARY_SEGREGATED_CYCLING_FACILITY = auto()
    NEW_JUNCTION_TREATMENT = auto()
    NEW_PERMANENT_FOOTWAY = auto()
    NEW_TEMPORARY_FOOTWAY = auto()
    NEW_SHARED_USE_WALKING_AND_CYCLING_FACILITIES = auto()
    NEW_SHARED_USE_WALKING_WHEELING_AND_CYCLING_FACILITIES = auto()
    IMPROVEMENTS_TO_EXISTING_ROUTE = auto()
    AREA_WIDE_TRAFFIC_MANAGEMENT = auto()
    BUS_PRIORITY_MEASURES = auto()
    SECURE_CYCLE_PARKING = auto()
    NEW_ROAD_CROSSINGS = auto()
    RESTRICTION_OR_REDUCTION_OF_CAR_PARKING_AVAILABILITY = auto()
    SCHOOL_STREETS = auto()
    UPGRADES_TO_EXISTING_FACILITIES = auto()
    E_SCOOTER_TRIALS = auto()
    PARK_AND_CYCLE_STRIDE_FACILITIES = auto()
    TRAFFIC_CALMING = auto()
    WIDENING_EXISTING_FOOTWAY = auto()
    OTHER_INTERVENTIONS = auto()


class OutputMeasure(Enum):
    MILES = auto()
    NUMBER_OF_JUNCTIONS = auto()
    SIZE_OF_AREA = auto()
    NUMBER_OF_PARKING_SPACES = auto()
    NUMBER_OF_CROSSINGS = auto()
    NUMBER_OF_SCHOOL_STREETS = auto()
    NUMBER_OF_TRIALS = auto()
    NUMBER_OF_BUS_GATES = auto()
    NUMBER_OF_UPGRADES = auto()
    NUMBER_OF_CHILDREN_AFFECTED = auto()
    NUMBER_OF_MEASURES_PLANNED = auto()


@dataclass(frozen=True)
class CapitalSchemeOutput:
    effective_date: DateTimeRange
    type: OutputType
    value: Decimal
    measure: OutputMeasure
    observation_type: ObservationType
