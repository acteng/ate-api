from datetime import datetime
from typing import Self

from sqlalchemy import ForeignKey, and_, false, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, contains_eager, joinedload, mapped_column, relationship

from ate_api.domain.capital_scheme_financials import (
    CapitalSchemeFinancial,
    CapitalSchemeFinancials,
    CapitalSchemeFinancialsRepository,
)
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeReference
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.financial_types import FinancialType
from ate_api.domain.moneys import Money
from ate_api.infrastructure.database.base import BaseEntity
from ate_api.infrastructure.database.capital_schemes.capital_schemes import CapitalSchemeEntity
from ate_api.infrastructure.database.capital_schemes.overviews import CapitalSchemeOverviewEntity
from ate_api.infrastructure.database.data_sources import DataSourceEntity, DataSourceName
from ate_api.infrastructure.database.dates import local_to_zoned, zoned_to_local
from ate_api.infrastructure.database.financial_types import FinancialTypeEntity, FinancialTypeName
from ate_api.infrastructure.database.funding_programmes import FundingProgrammeEntity


class CapitalSchemeFinancialEntity(BaseEntity):
    __tablename__ = "capital_scheme_financial"
    __table_args__ = {"schema": "capital_scheme"}

    capital_scheme_financial_id: Mapped[int] = mapped_column(primary_key=True)
    capital_scheme_id = mapped_column(ForeignKey(CapitalSchemeEntity.capital_scheme_id), nullable=False)
    financial_type_id = mapped_column(ForeignKey(FinancialTypeEntity.financial_type_id), nullable=False)
    financial_type: Mapped[FinancialTypeEntity] = relationship(lazy="raise")
    amount: Mapped[int]
    effective_date_from: Mapped[datetime]
    effective_date_to: Mapped[datetime | None]
    data_source_id = mapped_column(ForeignKey(DataSourceEntity.data_source_id), nullable=False)
    data_source: Mapped[DataSourceEntity] = relationship(lazy="raise")

    @classmethod
    def from_domain(
        cls,
        financial: CapitalSchemeFinancial,
        capital_scheme_id: int,
        financial_type_ids: dict[FinancialType, int],
        data_source_ids: dict[DataSource, int],
    ) -> Self:
        return cls(
            capital_scheme_financial_id=financial.surrogate_id,
            capital_scheme_id=capital_scheme_id,
            financial_type_id=financial_type_ids[financial.type],
            amount=financial.amount.amount,
            effective_date_from=zoned_to_local(financial.effective_date.from_),
            effective_date_to=zoned_to_local(financial.effective_date.to) if financial.effective_date.to else None,
            data_source_id=data_source_ids[financial.data_source],
        )

    def to_domain(self) -> CapitalSchemeFinancial:
        return CapitalSchemeFinancial(
            effective_date=DateTimeRange(
                local_to_zoned(self.effective_date_from),
                local_to_zoned(self.effective_date_to) if self.effective_date_to else None,
            ),
            type=self.financial_type.financial_type_name.to_domain(),
            amount=Money(self.amount),
            data_source=self.data_source.data_source_name.to_domain(),
            surrogate_id=self.capital_scheme_financial_id,
        )


class DatabaseCapitalSchemeFinancialsRepository(CapitalSchemeFinancialsRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, financials: CapitalSchemeFinancials) -> None:
        capital_scheme_id = await self._get_capital_scheme_id(financials)
        financial_type_ids = await self._get_financial_type_ids(financials)
        data_source_ids = await self._get_data_source_ids(financials)

        self._session.add_all(
            CapitalSchemeFinancialEntity.from_domain(financial, capital_scheme_id, financial_type_ids, data_source_ids)
            for financial in financials.financials
        )

    async def get(self, capital_scheme: CapitalSchemeReference) -> CapitalSchemeFinancials | None:
        result = await self._session.execute(
            select(CapitalSchemeEntity, CapitalSchemeFinancialEntity)
            .options(
                contains_eager(CapitalSchemeFinancialEntity.financial_type),
                joinedload(CapitalSchemeFinancialEntity.data_source),
            )
            .join(
                CapitalSchemeEntity.capital_scheme_overviews.and_(
                    CapitalSchemeOverviewEntity.effective_date_to.is_(None)
                )
            )
            .join(FundingProgrammeEntity)
            .outerjoin(
                CapitalSchemeFinancialEntity,
                and_(
                    CapitalSchemeEntity.capital_scheme_id == CapitalSchemeFinancialEntity.capital_scheme_id,
                    CapitalSchemeFinancialEntity.effective_date_to.is_(None),
                ),
            )
            .outerjoin(FinancialTypeEntity)
            .where(CapitalSchemeEntity.scheme_reference == str(capital_scheme))
            .where(FundingProgrammeEntity.is_under_embargo == false())
            .order_by(FinancialTypeEntity.financial_type_id)
            .order_by(CapitalSchemeFinancialEntity.effective_date_from)
        )
        rows = result.all()

        if not rows:
            return None

        financial_rows = [row.CapitalSchemeFinancialEntity for row in rows if row.CapitalSchemeFinancialEntity]

        financials = CapitalSchemeFinancials(capital_scheme=capital_scheme)
        for financial_row in financial_rows:
            financials.adjust_financial(financial_row.to_domain())
        return financials

    async def update(self, financials: CapitalSchemeFinancials) -> None:
        capital_scheme_id = await self._get_capital_scheme_id(financials)
        financial_type_ids = await self._get_financial_type_ids(financials)
        data_source_ids = await self._get_data_source_ids(financials)

        for financial in financials.financials:
            await self._session.merge(
                CapitalSchemeFinancialEntity.from_domain(
                    financial, capital_scheme_id, financial_type_ids, data_source_ids
                )
            )

    async def _get_capital_scheme_id(self, financials: CapitalSchemeFinancials) -> int:
        capital_scheme_reference = str(financials.capital_scheme)
        rows = await self._session.scalars(
            select(CapitalSchemeEntity.capital_scheme_id).where(
                CapitalSchemeEntity.scheme_reference == capital_scheme_reference
            )
        )
        return rows.one()

    async def _get_financial_type_ids(self, financials: CapitalSchemeFinancials) -> dict[FinancialType, int]:
        financial_type_names = {FinancialTypeName.from_domain(financial.type) for financial in financials.financials}
        rows = await self._session.execute(
            select(FinancialTypeEntity.financial_type_name, FinancialTypeEntity.financial_type_id).where(
                FinancialTypeEntity.financial_type_name.in_(financial_type_names)
            )
        )
        return {row.financial_type_name.to_domain(): row.financial_type_id for row in rows}

    async def _get_data_source_ids(self, financials: CapitalSchemeFinancials) -> dict[DataSource, int]:
        data_source_names = {DataSourceName.from_domain(financial.data_source) for financial in financials.financials}
        rows = await self._session.execute(
            select(DataSourceEntity.data_source_name, DataSourceEntity.data_source_id).where(
                DataSourceEntity.data_source_name.in_(data_source_names)
            )
        )
        return {row.data_source_name.to_domain(): row.data_source_id for row in rows}
