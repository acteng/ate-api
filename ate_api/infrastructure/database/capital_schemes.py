from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, delete, select
from sqlalchemy.orm import (
    Mapped,
    Session,
    joinedload,
    mapped_column,
    relationship,
    selectinload,
)

from ate_api.domain.capital_schemes import (
    CapitalScheme,
    CapitalSchemeOverview,
    CapitalSchemeRepository,
)
from ate_api.domain.dates import DateTimeRange
from ate_api.infrastructure.database.authorities import AuthorityEntity
from ate_api.infrastructure.database.base import BaseEntity
from ate_api.infrastructure.database.dates import local_to_zoned, zoned_to_local


class CapitalSchemeEntity(BaseEntity):
    __tablename__ = "capital_scheme"
    __table_args__ = {"schema": "capital_scheme"}

    capital_scheme_id: Mapped[int] = mapped_column(primary_key=True)
    scheme_reference: Mapped[str] = mapped_column(unique=True)
    capital_scheme_overviews: Mapped[list[CapitalSchemeOverviewEntity]] = relationship()

    @classmethod
    def from_domain(cls, capital_scheme: CapitalScheme, authority_ids: dict[str, int]) -> CapitalSchemeEntity:
        return cls(
            scheme_reference=capital_scheme.reference,
            capital_scheme_overviews=[
                CapitalSchemeOverviewEntity.from_domain(overview, authority_ids)
                for overview in capital_scheme.overviews
            ],
        )

    def to_domain(self) -> CapitalScheme:
        capital_scheme = CapitalScheme(reference=self.scheme_reference)

        for overview in self.capital_scheme_overviews:
            capital_scheme.update_overview(overview.to_domain())

        return capital_scheme


class CapitalSchemeOverviewEntity(BaseEntity):
    __tablename__ = "capital_scheme_overview"
    __table_args__ = {"schema": "capital_scheme"}

    capital_scheme_overview_id: Mapped[int] = mapped_column(primary_key=True)
    capital_scheme_id = mapped_column(ForeignKey(CapitalSchemeEntity.capital_scheme_id), nullable=False)
    bid_submitting_authority_id = mapped_column(ForeignKey(AuthorityEntity.authority_id), nullable=False)
    bid_submitting_authority: Mapped[AuthorityEntity] = relationship()
    effective_date_from: Mapped[datetime]
    effective_date_to: Mapped[datetime | None]

    @classmethod
    def from_domain(cls, overview: CapitalSchemeOverview, authority_ids: dict[str, int]) -> CapitalSchemeOverviewEntity:
        return cls(
            bid_submitting_authority_id=authority_ids[overview.bid_submitting_authority],
            effective_date_from=zoned_to_local(overview.effective_date.from_),
            effective_date_to=zoned_to_local(overview.effective_date.to) if overview.effective_date.to else None,
        )

    def to_domain(self) -> CapitalSchemeOverview:
        return CapitalSchemeOverview(
            effective_date=DateTimeRange(
                local_to_zoned(self.effective_date_from),
                local_to_zoned(self.effective_date_to) if self.effective_date_to else None,
            ),
            bid_submitting_authority=self.bid_submitting_authority.authority_abbreviation,
        )


class DatabaseCapitalSchemeRepository(CapitalSchemeRepository):
    def __init__(self, session: Session):
        self._session = session

    def add(self, capital_scheme: CapitalScheme) -> None:
        authority_ids = self._get_authority_ids(capital_scheme)
        self._session.add(CapitalSchemeEntity.from_domain(capital_scheme, authority_ids))

    def clear(self) -> None:
        self._session.execute(delete(CapitalSchemeOverviewEntity))
        self._session.execute(delete(CapitalSchemeEntity))

    def get(self, reference: str) -> CapitalScheme | None:
        result = self._session.scalars(
            select(CapitalSchemeEntity)
            .options(
                selectinload(CapitalSchemeEntity.capital_scheme_overviews),
                joinedload(
                    CapitalSchemeEntity.capital_scheme_overviews,
                    CapitalSchemeOverviewEntity.bid_submitting_authority,
                ),
            )
            .where(CapitalSchemeEntity.scheme_reference == reference)
        )
        row = result.one_or_none()
        return row.to_domain() if row else None

    def get_references_by_bid_submitting_authority(self, authority_abbreviation: str) -> list[str]:
        result = self._session.scalars(
            select(CapitalSchemeEntity.scheme_reference)
            .join(CapitalSchemeOverviewEntity)
            .join(
                AuthorityEntity, AuthorityEntity.authority_id == CapitalSchemeOverviewEntity.bid_submitting_authority_id
            )
            .where(CapitalSchemeOverviewEntity.effective_date_to.is_(None))
            .where(AuthorityEntity.authority_abbreviation == authority_abbreviation)
            .order_by(CapitalSchemeEntity.scheme_reference)
        )
        return list(result.all())

    def _get_authority_ids(self, capital_scheme: CapitalScheme) -> dict[str, int]:
        authority_abbreviations = [overview.bid_submitting_authority for overview in capital_scheme.overviews]
        rows = self._session.execute(
            select(AuthorityEntity.authority_abbreviation, AuthorityEntity.authority_id).where(
                AuthorityEntity.authority_abbreviation.in_(authority_abbreviations)
            )
        )
        return {row.authority_abbreviation: row.authority_id for row in rows}
