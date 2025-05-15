from datetime import datetime
from enum import Enum
from typing import Self

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ate_api.domain.capital_schemes.overviews import (
    CapitalSchemeOverview,
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
