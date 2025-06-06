from enum import Enum
from typing import Self

from ate_api.domain.observation_types import ObservationType


class ObservationTypeModel(str, Enum):
    PLANNED = "planned"
    ACTUAL = "actual"

    @classmethod
    def from_domain(cls, observation_type: ObservationType) -> Self:
        return cls[observation_type.name]

    def to_domain(self) -> ObservationType:
        return ObservationType[self.name]
