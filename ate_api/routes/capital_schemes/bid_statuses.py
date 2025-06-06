from datetime import datetime
from enum import Enum
from typing import Self

from ate_api.domain.capital_schemes.bid_statuses import BidStatus, CapitalSchemeBidStatusDetails
from ate_api.domain.dates import DateTimeRange
from ate_api.routes.base import BaseModel


class BidStatusModel(str, Enum):
    SUBMITTED = "submitted"
    FUNDED = "funded"
    NOT_FUNDED = "not funded"
    SPLIT = "split"
    DELETED = "deleted"

    @classmethod
    def from_domain(cls, bid_status: BidStatus) -> Self:
        return cls[bid_status.name]

    def to_domain(self) -> BidStatus:
        return BidStatus[self.name]


class CapitalSchemeBidStatusDetailsModel(BaseModel):
    bid_status: BidStatusModel

    @classmethod
    def from_domain(cls, bid_status_details: CapitalSchemeBidStatusDetails) -> Self:
        return cls(bid_status=BidStatusModel.from_domain(bid_status_details.bid_status))

    def to_domain(self, now: datetime) -> CapitalSchemeBidStatusDetails:
        return CapitalSchemeBidStatusDetails(effective_date=DateTimeRange(now), bid_status=self.bid_status.to_domain())
