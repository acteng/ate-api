from datetime import datetime
from enum import Enum
from typing import Self

from sqlalchemy import ForeignKey, false, select
from sqlalchemy.orm import (
    Mapped,
    Session,
    contains_eager,
    joinedload,
    mapped_column,
    relationship,
)

from ate_api.domain.capital_schemes import (
    CapitalScheme,
    CapitalSchemeOverview,
    CapitalSchemeRepository,
    CapitalSchemeType,
)
from ate_api.domain.dates import DateTimeRange
from ate_api.infrastructure.database.authorities import AuthorityEntity
from ate_api.infrastructure.database.base import BaseEntity
from ate_api.infrastructure.database.dates import local_to_zoned, zoned_to_local
from ate_api.infrastructure.database.funding_programmes import FundingProgrammeEntity


class SchemeTypeName(Enum):
    DEVELOPMENT = "development"
    CONSTRUCTION = "construction"

    @classmethod
    def from_domain(cls, type_: CapitalSchemeType) -> Self:
        return cls[type_.name]

    def to_domain(self) -> CapitalSchemeType:
        return CapitalSchemeType[self.name]


class SchemeTypeEntity(BaseEntity):
    __tablename__ = "scheme_type"
    __table_args__ = {"schema": "capital_scheme"}

    scheme_type_id: Mapped[int] = mapped_column(primary_key=True)
    scheme_type_name: Mapped[SchemeTypeName] = mapped_column(unique=True)


class CapitalSchemeOverviewEntity(BaseEntity):
    __tablename__ = "capital_scheme_overview"
    __table_args__ = {"schema": "capital_scheme"}

    capital_scheme_overview_id: Mapped[int] = mapped_column(primary_key=True)
    capital_scheme_id = mapped_column(ForeignKey("capital_scheme.capital_scheme.capital_scheme_id"), nullable=False)
    scheme_name: Mapped[str]
    bid_submitting_authority_id = mapped_column(ForeignKey(AuthorityEntity.authority_id), nullable=False)
    bid_submitting_authority: Mapped[AuthorityEntity] = relationship(lazy="raise")
    funding_programme_id = mapped_column(ForeignKey(FundingProgrammeEntity.funding_programme_id), nullable=False)
    funding_programme: Mapped[FundingProgrammeEntity] = relationship(lazy="raise")
    scheme_type_id = mapped_column(ForeignKey(SchemeTypeEntity.scheme_type_id), nullable=False)
    scheme_type: Mapped[SchemeTypeEntity] = relationship(lazy="raise")
    effective_date_from: Mapped[datetime]
    effective_date_to: Mapped[datetime | None]

    @classmethod
    def from_domain(
        cls,
        overview: CapitalSchemeOverview,
        authority_ids: dict[str, int],
        funding_programme_ids: dict[str, int],
        scheme_type_ids: dict[SchemeTypeName, int],
    ) -> Self:
        return cls(
            scheme_name=overview.name,
            bid_submitting_authority_id=authority_ids[overview.bid_submitting_authority],
            funding_programme_id=funding_programme_ids[overview.funding_programme],
            scheme_type_id=scheme_type_ids[SchemeTypeName.from_domain(overview.type)],
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
            bid_submitting_authority=self.bid_submitting_authority.authority_abbreviation,
            funding_programme=self.funding_programme.funding_programme_code,
            type=self.scheme_type.scheme_type_name.to_domain(),
        )


class CapitalSchemeEntity(BaseEntity):
    __tablename__ = "capital_scheme"
    __table_args__ = {"schema": "capital_scheme"}

    capital_scheme_id: Mapped[int] = mapped_column(primary_key=True)
    scheme_reference: Mapped[str] = mapped_column(unique=True)
    capital_scheme_overviews: Mapped[list[CapitalSchemeOverviewEntity]] = relationship(lazy="raise")

    @classmethod
    def from_domain(
        cls,
        capital_scheme: CapitalScheme,
        authority_ids: dict[str, int],
        funding_programme_ids: dict[str, int],
        scheme_type_ids: dict[SchemeTypeName, int],
    ) -> Self:
        return cls(
            scheme_reference=capital_scheme.reference,
            capital_scheme_overviews=[
                CapitalSchemeOverviewEntity.from_domain(
                    capital_scheme.overview, authority_ids, funding_programme_ids, scheme_type_ids
                )
            ],
        )

    def to_domain(self) -> CapitalScheme:
        (capital_scheme_overview,) = self.capital_scheme_overviews
        return CapitalScheme(reference=self.scheme_reference, overview=capital_scheme_overview.to_domain())


class DatabaseCapitalSchemeRepository(CapitalSchemeRepository):
    def __init__(self, session: Session):
        self._session = session

    def add(self, capital_scheme: CapitalScheme) -> None:
        authority_ids = self._get_authority_ids(capital_scheme)
        funding_programme_ids = self._get_funding_programme_ids(capital_scheme)
        scheme_type_ids = self._get_scheme_type_ids(capital_scheme)
        self._session.add(
            CapitalSchemeEntity.from_domain(capital_scheme, authority_ids, funding_programme_ids, scheme_type_ids)
        )

    def get(self, reference: str) -> CapitalScheme | None:
        result = self._session.scalars(
            select(CapitalSchemeEntity)
            .options(
                contains_eager(CapitalSchemeEntity.capital_scheme_overviews),
                joinedload(
                    CapitalSchemeEntity.capital_scheme_overviews, CapitalSchemeOverviewEntity.bid_submitting_authority
                ),
                contains_eager(
                    CapitalSchemeEntity.capital_scheme_overviews, CapitalSchemeOverviewEntity.funding_programme
                ),
                joinedload(CapitalSchemeEntity.capital_scheme_overviews, CapitalSchemeOverviewEntity.scheme_type),
            )
            .join(
                CapitalSchemeEntity.capital_scheme_overviews.and_(
                    CapitalSchemeOverviewEntity.effective_date_to.is_(None)
                )
            )
            .join(
                CapitalSchemeOverviewEntity.funding_programme.and_(FundingProgrammeEntity.is_under_embargo == false())
            )
            .where(CapitalSchemeEntity.scheme_reference == reference)
        )
        row = result.unique().one_or_none()
        return row.to_domain() if row else None

    def get_references_by_bid_submitting_authority(self, authority_abbreviation: str) -> list[str]:
        result = self._session.scalars(
            select(CapitalSchemeEntity.scheme_reference)
            .join(CapitalSchemeOverviewEntity)
            .join(
                AuthorityEntity, AuthorityEntity.authority_id == CapitalSchemeOverviewEntity.bid_submitting_authority_id
            )
            .join(FundingProgrammeEntity)
            .where(CapitalSchemeOverviewEntity.effective_date_to.is_(None))
            .where(AuthorityEntity.authority_abbreviation == authority_abbreviation)
            .where(FundingProgrammeEntity.is_under_embargo == false())
            .order_by(CapitalSchemeEntity.scheme_reference)
        )
        return list(result.all())

    def _get_authority_ids(self, capital_scheme: CapitalScheme) -> dict[str, int]:
        authority_abbreviations = [capital_scheme.overview.bid_submitting_authority]
        rows = self._session.execute(
            select(AuthorityEntity.authority_abbreviation, AuthorityEntity.authority_id).where(
                AuthorityEntity.authority_abbreviation.in_(authority_abbreviations)
            )
        )
        return {row.authority_abbreviation: row.authority_id for row in rows}

    def _get_funding_programme_ids(self, capital_scheme: CapitalScheme) -> dict[str, int]:
        funding_programme_codes = [capital_scheme.overview.funding_programme]
        rows = self._session.execute(
            select(FundingProgrammeEntity.funding_programme_code, FundingProgrammeEntity.funding_programme_id).where(
                FundingProgrammeEntity.funding_programme_code.in_(funding_programme_codes)
            )
        )
        return {row.funding_programme_code: row.funding_programme_id for row in rows}

    def _get_scheme_type_ids(self, capital_scheme: CapitalScheme) -> dict[SchemeTypeName, int]:
        scheme_type_names = [SchemeTypeName.from_domain(capital_scheme.overview.type)]
        rows = self._session.execute(
            select(SchemeTypeEntity.scheme_type_name, SchemeTypeEntity.scheme_type_id).where(
                SchemeTypeEntity.scheme_type_name.in_(scheme_type_names)
            )
        )
        return {row.scheme_type_name: row.scheme_type_id for row in rows}
