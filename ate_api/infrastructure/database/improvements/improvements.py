from collections.abc import Mapping
from typing import Self

from sqlalchemy import false, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, contains_eager, joinedload, mapped_column, relationship

from ate_api.domain.authorities import AuthorityAbbreviation
from ate_api.domain.data_sources import DataSource
from ate_api.domain.improvements.improvements import Improvement, ImprovementReference, ImprovementRepository
from ate_api.infrastructure.database.authorities import AuthorityEntity
from ate_api.infrastructure.database.base import BaseEntity
from ate_api.infrastructure.database.data_sources import DataSourceEntity, DataSourceName
from ate_api.infrastructure.database.improvements.overviews import ImprovementOverviewEntity


class ImprovementEntity(BaseEntity):
    __tablename__ = "improvement"
    __table_args__: Mapping[str, str] = {"schema": "improvement"}

    improvement_id: Mapped[int] = mapped_column(primary_key=True)
    improvement_reference: Mapped[str] = mapped_column(unique=True)
    improvement_overviews: Mapped[list[ImprovementOverviewEntity]] = relationship(lazy="raise")

    @classmethod
    def from_domain(
        cls,
        improvement: Improvement,
        authority_ids: dict[AuthorityAbbreviation, int],
        data_source_ids: dict[DataSource, int],
    ) -> Self:
        return cls(
            improvement_reference=str(improvement.reference),
            improvement_overviews=[
                ImprovementOverviewEntity.from_domain(improvement.overview, authority_ids, data_source_ids)
            ],
        )

    def to_domain(self) -> Improvement:
        (improvement_overview,) = self.improvement_overviews

        return Improvement(
            reference=ImprovementReference(self.improvement_reference),
            overview=improvement_overview.to_domain(),
        )


class DatabaseImprovementRepository(ImprovementRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, improvement: Improvement) -> None:
        authority_ids = await self._get_authority_ids(improvement)
        data_source_ids = await self._get_data_source_ids(improvement)

        self._session.add(ImprovementEntity.from_domain(improvement, authority_ids, data_source_ids))

    async def get(self, reference: ImprovementReference) -> Improvement | None:
        statement = select(ImprovementEntity).where(ImprovementEntity.improvement_reference == str(reference))

        # fetch current overview
        statement = statement.options(
            contains_eager(ImprovementEntity.improvement_overviews),
            joinedload(ImprovementEntity.improvement_overviews, ImprovementOverviewEntity.funding_managed_by),
            joinedload(ImprovementEntity.improvement_overviews, ImprovementOverviewEntity.data_source),
        ).join(
            ImprovementEntity.improvement_overviews.and_(ImprovementOverviewEntity.effective_date_to.is_(None)).and_(
                ImprovementOverviewEntity.is_deleted == false()
            )
        )

        result = await self._session.scalars(statement)
        row = result.unique().one_or_none()

        if not row:
            return None

        return row.to_domain()

    async def _get_authority_ids(self, improvement: Improvement) -> dict[AuthorityAbbreviation, int]:
        authority_abbreviation = str(improvement.overview.funding_managed_by)
        rows = await self._session.execute(
            select(AuthorityEntity.authority_abbreviation, AuthorityEntity.authority_id).where(
                AuthorityEntity.authority_abbreviation == authority_abbreviation
            )
        )
        return {AuthorityAbbreviation(row.authority_abbreviation): row.authority_id for row in rows}

    async def _get_data_source_ids(self, improvement: Improvement) -> dict[DataSource, int]:
        data_source_name = DataSourceName.from_domain(improvement.overview.data_source)
        rows = await self._session.execute(
            select(DataSourceEntity.data_source_name, DataSourceEntity.data_source_id).where(
                DataSourceEntity.data_source_name == data_source_name
            )
        )
        return {row.data_source_name.to_domain(): row.data_source_id for row in rows}
