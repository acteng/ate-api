from datetime import datetime
from enum import Enum
from typing import Self

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ate_api.domain.capital_schemes.bid_statuses import CapitalSchemeBidStatus, CapitalSchemeBidStatusDetails
from ate_api.domain.dates import DateTimeRange
from ate_api.infrastructure.database.base import BaseEntity
from ate_api.infrastructure.database.dates import local_to_zoned, zoned_to_local


class BidStatusName(Enum):
    SUBMITTED = "submitted"
    FUNDED = "funded"
    NOT_FUNDED = "not funded"
    SPLIT = "split"
    DELETED = "deleted"

    @classmethod
    def from_domain(cls, status: CapitalSchemeBidStatus) -> Self:
        return cls[status.name]

    def to_domain(self) -> CapitalSchemeBidStatus:
        return CapitalSchemeBidStatus[self.name]


class BidStatusEntity(BaseEntity):
    __tablename__ = "bid_status"
    __table_args__ = {"schema": "capital_scheme"}

    bid_status_id: Mapped[int] = mapped_column(primary_key=True)
    bid_status_name: Mapped[BidStatusName] = mapped_column(unique=True)


class CapitalSchemeBidStatusEntity(BaseEntity):
    __tablename__ = "capital_scheme_bid_status"
    __table_args__ = {"schema": "capital_scheme"}

    capital_scheme_bid_status_id: Mapped[int] = mapped_column(primary_key=True)
    capital_scheme_id = mapped_column(ForeignKey("capital_scheme.capital_scheme.capital_scheme_id"), nullable=False)
    bid_status_id = mapped_column(ForeignKey(BidStatusEntity.bid_status_id), nullable=False)
    bid_status: Mapped[BidStatusEntity] = relationship(lazy="raise")
    effective_date_from: Mapped[datetime]
    effective_date_to: Mapped[datetime | None]

    @classmethod
    def from_domain(
        cls, bid_status_details: CapitalSchemeBidStatusDetails, bid_status_ids: dict[CapitalSchemeBidStatus, int]
    ) -> Self:
        return cls(
            bid_status_id=bid_status_ids[bid_status_details.bid_status],
            effective_date_from=zoned_to_local(bid_status_details.effective_date.from_),
            effective_date_to=(
                zoned_to_local(bid_status_details.effective_date.to) if bid_status_details.effective_date.to else None
            ),
        )

    def to_domain(self) -> CapitalSchemeBidStatusDetails:
        return CapitalSchemeBidStatusDetails(
            effective_date=DateTimeRange(
                local_to_zoned(self.effective_date_from),
                local_to_zoned(self.effective_date_to) if self.effective_date_to else None,
            ),
            bid_status=self.bid_status.bid_status_name.to_domain(),
        )
