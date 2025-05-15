from enum import Enum
from typing import Self

from ate_api.domain.capital_schemes.bid_statuses import (
    CapitalSchemeBidStatus,
    CapitalSchemeBidStatusDetails,
)
from ate_api.routes.base import BaseModel
from ate_api.routes.dates import DateTimeRangeModel


class CapitalSchemeBidStatusModel(str, Enum):
    SUBMITTED = "submitted"
    FUNDED = "funded"
    NOT_FUNDED = "not funded"
    SPLIT = "split"
    DELETED = "deleted"

    @classmethod
    def from_domain(cls, bid_status: CapitalSchemeBidStatus) -> Self:
        return cls[bid_status.name]

    def to_domain(self) -> CapitalSchemeBidStatus:
        return CapitalSchemeBidStatus[self.name]


class CapitalSchemeBidStatusDetailsModel(BaseModel):
    effective_date: DateTimeRangeModel
    bid_status: CapitalSchemeBidStatusModel

    @classmethod
    def from_domain(cls, bid_status_details: CapitalSchemeBidStatusDetails) -> Self:
        return cls(
            effective_date=DateTimeRangeModel.from_domain(bid_status_details.effective_date),
            bid_status=CapitalSchemeBidStatusModel.from_domain(bid_status_details.bid_status),
        )

    def to_domain(self) -> CapitalSchemeBidStatusDetails:
        return CapitalSchemeBidStatusDetails(
            effective_date=self.effective_date.to_domain(), bid_status=self.bid_status.to_domain()
        )
