from collections.abc import Mapping
from datetime import datetime
from typing import Self

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ate_api.domain.authorities import AuthorityAbbreviation
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.improvements.overviews import ImprovementOverview
from ate_api.infrastructure.database.authorities import AuthorityEntity
from ate_api.infrastructure.database.base import BaseEntity
from ate_api.infrastructure.database.data_sources import DataSourceEntity
from ate_api.infrastructure.database.dates import local_to_zoned, zoned_to_local


class ImprovementOverviewEntity(BaseEntity):
    __tablename__ = "improvement_overview"
    __table_args__: Mapping[str, str] = {"schema": "improvement"}

    improvement_overview_id: Mapped[int] = mapped_column(primary_key=True)
    improvement_id = mapped_column(ForeignKey("improvement.improvement.improvement_id"), nullable=False)
    improvement_name: Mapped[str]
    improvement_description: Mapped[str | None]
    funding_managed_by_id = mapped_column(ForeignKey(AuthorityEntity.authority_id), nullable=False)
    funding_managed_by: Mapped[AuthorityEntity] = relationship(lazy="raise")
    data_source_id = mapped_column(ForeignKey(DataSourceEntity.data_source_id), nullable=False)
    data_source: Mapped[DataSourceEntity] = relationship(lazy="raise")
    effective_date_from: Mapped[datetime]
    effective_date_to: Mapped[datetime | None]
    is_deleted: Mapped[bool]

    @classmethod
    def from_domain(
        cls,
        overview: ImprovementOverview,
        authority_ids: dict[AuthorityAbbreviation, int],
        data_source_ids: dict[DataSource, int],
    ) -> Self:
        return cls(
            improvement_name=overview.name,
            improvement_description=overview.description,
            funding_managed_by_id=authority_ids[overview.funding_managed_by],
            data_source_id=data_source_ids[overview.data_source],
            effective_date_from=zoned_to_local(overview.effective_date.from_),
            effective_date_to=zoned_to_local(overview.effective_date.to) if overview.effective_date.to else None,
            is_deleted=False,
        )

    def to_domain(self) -> ImprovementOverview:
        if self.is_deleted:
            raise ValueError("Improvement overview is deleted")

        return ImprovementOverview(
            effective_date=DateTimeRange(
                local_to_zoned(self.effective_date_from),
                local_to_zoned(self.effective_date_to) if self.effective_date_to else None,
            ),
            name=self.improvement_name,
            description=self.improvement_description,
            funding_managed_by=AuthorityAbbreviation(self.funding_managed_by.authority_abbreviation),
            data_source=self.data_source.data_source_name.to_domain(),
        )
