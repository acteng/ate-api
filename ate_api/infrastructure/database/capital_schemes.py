from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, delete, select
from sqlalchemy.orm import (
    Mapped,
    Session,
    joinedload,
    mapped_column,
    relationship,
)

from ate_api.domain.capital_schemes import CapitalScheme, CapitalSchemeRepository
from ate_api.domain.dates import DateTimeRange
from ate_api.infrastructure.database.authorities import AuthorityEntity
from ate_api.infrastructure.database.base import BaseEntity
from ate_api.infrastructure.database.dates import local_to_zoned, zoned_to_local


class CapitalSchemeEntity(BaseEntity):
    __tablename__ = "capital_scheme"
    __table_args__ = {"schema": "capital_scheme"}

    capital_scheme_id: Mapped[int] = mapped_column(primary_key=True)
    scheme_reference: Mapped[str] = mapped_column(unique=True)


class CapitalSchemeOverviewEntity(BaseEntity):
    __tablename__ = "capital_scheme_overview"
    __table_args__ = {"schema": "capital_scheme"}

    capital_scheme_overview_id: Mapped[int] = mapped_column(primary_key=True)
    capital_scheme_id = mapped_column(ForeignKey(CapitalSchemeEntity.capital_scheme_id), nullable=False)
    capital_scheme: Mapped[CapitalSchemeEntity] = relationship(lazy="raise")
    bid_submitting_authority_id = mapped_column(ForeignKey(AuthorityEntity.authority_id), nullable=False)
    bid_submitting_authority: Mapped[AuthorityEntity] = relationship(lazy="raise")
    effective_date_from: Mapped[datetime]
    effective_date_to: Mapped[datetime | None]

    @classmethod
    def from_domain(cls, capital_scheme: CapitalScheme, authority_ids: dict[str, int]) -> CapitalSchemeOverviewEntity:
        return cls(
            capital_scheme=CapitalSchemeEntity(scheme_reference=capital_scheme.reference),
            bid_submitting_authority_id=authority_ids[capital_scheme.bid_submitting_authority],
            effective_date_from=zoned_to_local(capital_scheme.effective_date.from_),
            effective_date_to=(
                zoned_to_local(capital_scheme.effective_date.to) if capital_scheme.effective_date.to else None
            ),
        )

    def to_domain(self) -> CapitalScheme:
        return CapitalScheme(
            reference=self.capital_scheme.scheme_reference,
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
        self._session.add(CapitalSchemeOverviewEntity.from_domain(capital_scheme, authority_ids))

    def clear(self) -> None:
        self._session.execute(delete(CapitalSchemeOverviewEntity))
        self._session.execute(delete(CapitalSchemeEntity))

    def get(self, reference: str) -> CapitalScheme | None:
        result = self._session.scalars(
            select(CapitalSchemeOverviewEntity)
            .options(
                joinedload(CapitalSchemeOverviewEntity.capital_scheme),
                joinedload(CapitalSchemeOverviewEntity.bid_submitting_authority),
            )
            .join(CapitalSchemeEntity)
            .where(CapitalSchemeEntity.scheme_reference == reference)
            .where(CapitalSchemeOverviewEntity.effective_date_to.is_(None))
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
        authority_abbreviations = [capital_scheme.bid_submitting_authority]
        rows = self._session.execute(
            select(AuthorityEntity.authority_abbreviation, AuthorityEntity.authority_id).where(
                AuthorityEntity.authority_abbreviation.in_(authority_abbreviations)
            )
        )
        return {row.authority_abbreviation: row.authority_id for row in rows}
