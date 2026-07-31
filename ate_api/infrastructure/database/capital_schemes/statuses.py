from collections.abc import Mapping
from datetime import datetime
from enum import Enum
from typing import Self

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ate_api.domain.capital_schemes.statuses import CapitalSchemeStatus, Status
from ate_api.domain.dates import DateTimeRange
from ate_api.infrastructure.database import BaseEntity
from ate_api.infrastructure.database.dates import local_to_zoned, zoned_to_local


class SchemeStatusName(Enum):
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


class SchemeStatusEntity(BaseEntity):
    __tablename__ = "scheme_status"
    __table_args__: Mapping[str, str] = {"schema": "capital_scheme"}

    scheme_status_id: Mapped[int] = mapped_column(primary_key=True)
    scheme_status_name: Mapped[SchemeStatusName] = mapped_column(unique=True)


class CapitalSchemeSchemeStatusEntity(BaseEntity):
    __tablename__ = "capital_scheme_scheme_status"
    __table_args__: Mapping[str, str] = {"schema": "capital_scheme"}

    capital_scheme_scheme_status_id: Mapped[int] = mapped_column(primary_key=True)
    capital_scheme_id = mapped_column(ForeignKey("capital_scheme.capital_scheme.capital_scheme_id"), nullable=False)
    scheme_status_id = mapped_column(ForeignKey(SchemeStatusEntity.scheme_status_id), nullable=False)
    scheme_status: Mapped[SchemeStatusEntity] = relationship(lazy="raise")
    effective_date_from: Mapped[datetime]
    effective_date_to: Mapped[datetime | None]

    @classmethod
    def from_domain(cls, status: CapitalSchemeStatus, scheme_status_ids: dict[Status, int]) -> Self:
        return cls(
            scheme_status_id=scheme_status_ids[status.status],
            effective_date_from=zoned_to_local(status.effective_date.from_),
            effective_date_to=zoned_to_local(status.effective_date.to) if status.effective_date.to else None,
        )

    def to_domain(self) -> CapitalSchemeStatus:
        return CapitalSchemeStatus(
            effective_date=DateTimeRange(
                local_to_zoned(self.effective_date_from),
                local_to_zoned(self.effective_date_to) if self.effective_date_to else None,
            ),
            status=self.scheme_status.scheme_status_name.to_domain(),
        )
