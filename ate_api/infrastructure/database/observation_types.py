from enum import Enum
from typing import Self

from sqlalchemy.orm import Mapped, mapped_column

from ate_api.domain.observation_types import ObservationType
from ate_api.infrastructure.database.base import BaseEntity


class ObservationTypeName(Enum):
    PLANNED = "planned"
    ACTUAL = "actual"

    @classmethod
    def from_domain(cls, observation_type: ObservationType) -> Self:
        return cls[observation_type.name]

    def to_domain(self) -> ObservationType:
        return ObservationType[self.name]


class ObservationTypeEntity(BaseEntity):
    __tablename__ = "observation_type"
    __table_args__ = {"schema": "common"}

    observation_type_id: Mapped[int] = mapped_column(primary_key=True)
    observation_type_name: Mapped[ObservationTypeName] = mapped_column(unique=True)
