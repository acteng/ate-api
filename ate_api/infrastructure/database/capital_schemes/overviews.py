from collections.abc import Mapping
from datetime import datetime
from typing import Self

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ate_api.domain.capital_schemes.overviews import CapitalSchemeOverview
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.improvements.improvements import ImprovementReference
from ate_api.infrastructure.database.base import BaseEntity
from ate_api.infrastructure.database.dates import local_to_zoned, zoned_to_local
from ate_api.infrastructure.database.improvements.improvements import ImprovementEntity


class CapitalSchemeOverviewEntity(BaseEntity):
    __tablename__ = "capital_scheme_overview"
    __table_args__: Mapping[str, str] = {"schema": "capital_scheme"}

    capital_scheme_overview_id: Mapped[int] = mapped_column(primary_key=True)
    capital_scheme_id = mapped_column(ForeignKey("capital_scheme.capital_scheme.capital_scheme_id"), nullable=False)
    scheme_name: Mapped[str]
    improvement_id = mapped_column(ForeignKey(ImprovementEntity.improvement_id))
    improvement: Mapped[ImprovementEntity | None] = relationship(lazy="raise")
    effective_date_from: Mapped[datetime]
    effective_date_to: Mapped[datetime | None]

    @classmethod
    def from_domain(cls, overview: CapitalSchemeOverview, improvement_ids: dict[ImprovementReference, int]) -> Self:
        return cls(
            scheme_name=overview.name,
            improvement_id=improvement_ids[overview.improvement] if overview.improvement else None,
            effective_date_from=zoned_to_local(overview.effective_date.from_),
            effective_date_to=zoned_to_local(overview.effective_date.to) if overview.effective_date.to else None,
        )

    def to_domain(self) -> CapitalSchemeOverview:
        return CapitalSchemeOverview(
            effective_date=DateTimeRange(
                local_to_zoned(self.effective_date_from),
                local_to_zoned(self.effective_date_to) if self.effective_date_to else None,
            ),
            name=self.scheme_name,
            improvement=ImprovementReference(self.improvement.improvement_reference) if self.improvement else None,
        )
