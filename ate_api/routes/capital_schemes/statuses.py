from datetime import datetime
from enum import Enum
from typing import Self

from ate_api.domain.capital_schemes.statuses import CapitalSchemeStatus, Status
from ate_api.domain.dates import DateTimeRange
from ate_api.routes.base import BaseModel


class StatusModel(str, Enum):
    PIPELINE = "pipeline"
    ACTIVE = "active"
    PAUSED = "paused"
    CONCLUDED = "concluded"
    DELETED = "deleted"

    @classmethod
    def from_domain(cls, status: Status) -> Self:
        return cls[status.name]

    def to_domain(self) -> Status:
        return Status[self.name]


class CapitalSchemeStatusModel(BaseModel):
    status: StatusModel

    @classmethod
    def from_domain(cls, status: CapitalSchemeStatus) -> Self:
        return cls(status=StatusModel.from_domain(status.status))

    def to_domain(self, now: datetime) -> CapitalSchemeStatus:
        return CapitalSchemeStatus(effective_date=DateTimeRange(now), status=self.status.to_domain())
