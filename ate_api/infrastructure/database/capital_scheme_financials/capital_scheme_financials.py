from collections.abc import Mapping
from datetime import datetime
from typing import Self

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ate_api.domain.capital_scheme_financials import CapitalSchemeFunding, CapitalSchemeSpend
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.funding_programmes import FundingProgrammeCode
from ate_api.domain.moneys import Money
from ate_api.infrastructure.database.base import BaseEntity
from ate_api.infrastructure.database.data_sources import DataSourceEntity
from ate_api.infrastructure.database.dates import local_to_zoned, zoned_to_local
from ate_api.infrastructure.database.funding_programmes import FundingProgrammeEntity


class CapitalSchemeFundingEntity(BaseEntity):
    __tablename__ = "capital_scheme_funding"
    __table_args__: Mapping[str, str] = {"schema": "capital_scheme"}

    capital_scheme_funding_id: Mapped[int] = mapped_column(primary_key=True)
    capital_scheme_id = mapped_column(ForeignKey("capital_scheme.capital_scheme.capital_scheme_id"), nullable=False)
    amount: Mapped[int]
    funding_programme_id = mapped_column(ForeignKey(FundingProgrammeEntity.funding_programme_id), nullable=False)
    funding_programme: Mapped[FundingProgrammeEntity] = relationship(lazy="raise")
    data_source_id = mapped_column(ForeignKey(DataSourceEntity.data_source_id), nullable=False)
    data_source: Mapped[DataSourceEntity] = relationship(lazy="raise")
    effective_date_from: Mapped[datetime]
    effective_date_to: Mapped[datetime | None]

    @classmethod
    def from_domain(
        cls,
        funding: CapitalSchemeFunding,
        capital_scheme_id: int,
        funding_programme_ids: dict[FundingProgrammeCode, int],
        data_source_ids: dict[DataSource, int],
    ) -> Self:
        return cls(
            capital_scheme_funding_id=funding.surrogate_id,
            capital_scheme_id=capital_scheme_id,
            amount=funding.amount.amount,
            funding_programme_id=funding_programme_ids[funding.funding_programme],
            data_source_id=data_source_ids[funding.data_source],
            effective_date_from=zoned_to_local(funding.effective_date.from_),
            effective_date_to=zoned_to_local(funding.effective_date.to) if funding.effective_date.to else None,
        )

    def to_domain(self) -> CapitalSchemeFunding:
        return CapitalSchemeFunding(
            effective_date=DateTimeRange(
                local_to_zoned(self.effective_date_from),
                local_to_zoned(self.effective_date_to) if self.effective_date_to else None,
            ),
            funding_programme=FundingProgrammeCode(self.funding_programme.funding_programme_code),
            amount=Money(self.amount),
            data_source=self.data_source.data_source_name.to_domain(),
            surrogate_id=self.capital_scheme_funding_id,
        )


class CapitalSchemeSpendEntity(BaseEntity):
    __tablename__ = "capital_scheme_spend"
    __table_args__: Mapping[str, str] = {"schema": "capital_scheme"}

    capital_scheme_spend_id: Mapped[int] = mapped_column(primary_key=True)
    capital_scheme_id = mapped_column(ForeignKey("capital_scheme.capital_scheme.capital_scheme_id"), nullable=False)
    amount: Mapped[int]
    data_source_id = mapped_column(ForeignKey(DataSourceEntity.data_source_id), nullable=False)
    data_source: Mapped[DataSourceEntity] = relationship(lazy="raise")
    effective_date_from: Mapped[datetime]
    effective_date_to: Mapped[datetime | None]

    @classmethod
    def from_domain(
        cls, spend: CapitalSchemeSpend, capital_scheme_id: int, data_source_ids: dict[DataSource, int]
    ) -> Self:
        return cls(
            capital_scheme_spend_id=spend.surrogate_id,
            capital_scheme_id=capital_scheme_id,
            amount=spend.amount.amount,
            data_source_id=data_source_ids[spend.data_source],
            effective_date_from=zoned_to_local(spend.effective_date.from_),
            effective_date_to=zoned_to_local(spend.effective_date.to) if spend.effective_date.to else None,
        )

    def to_domain(self) -> CapitalSchemeSpend:
        return CapitalSchemeSpend(
            effective_date=DateTimeRange(
                local_to_zoned(self.effective_date_from),
                local_to_zoned(self.effective_date_to) if self.effective_date_to else None,
            ),
            amount=Money(self.amount),
            data_source=self.data_source.data_source_name.to_domain(),
            surrogate_id=self.capital_scheme_spend_id,
        )
