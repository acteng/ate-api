from collections.abc import Mapping
from datetime import datetime
from typing import Self

from sqlalchemy import ForeignKey, and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, contains_eager, joinedload, mapped_column, relationship

from ate_api.domain.capital_scheme_financials import (
    CapitalSchemeFinancials,
    CapitalSchemeFinancialsRepository,
    CapitalSchemeFunding,
    CapitalSchemeSpend,
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


class CapitalSchemeFinancialEntity(BaseEntity):
    __tablename__ = "capital_scheme_financial"
    __table_args__: Mapping[str, str] = {"schema": "capital_scheme"}

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
    def from_funding_domain(
        cls,
        funding: CapitalSchemeFunding,
        capital_scheme_id: int,
        financial_type_ids: dict[FinancialType, int],
        data_source_ids: dict[DataSource, int],
    ) -> Self:
        return cls(
            capital_scheme_id=capital_scheme_id,
            financial_type_id=financial_type_ids[FinancialType.FUNDING_ALLOCATION],
            amount=funding.amount.amount,
            effective_date_from=zoned_to_local(funding.effective_date.from_),
            effective_date_to=zoned_to_local(funding.effective_date.to) if funding.effective_date.to else None,
            data_source_id=data_source_ids[funding.data_source],
        )

    @classmethod
    def from_spend_domain(
        cls,
        spend: CapitalSchemeSpend,
        capital_scheme_id: int,
        financial_type_ids: dict[FinancialType, int],
        data_source_ids: dict[DataSource, int],
    ) -> Self:
        return cls(
            capital_scheme_financial_id=spend.surrogate_id,
            capital_scheme_id=capital_scheme_id,
            financial_type_id=financial_type_ids[FinancialType.SPEND_TO_DATE],
            amount=spend.amount.amount,
            effective_date_from=zoned_to_local(spend.effective_date.from_),
            effective_date_to=zoned_to_local(spend.effective_date.to) if spend.effective_date.to else None,
            data_source_id=data_source_ids[spend.data_source],
        )

    def to_funding_domain(self) -> CapitalSchemeFunding:
        financial_type = self.financial_type.financial_type_name.to_domain()
        if financial_type != FinancialType.FUNDING_ALLOCATION:
            raise ValueError(f"Invalid financial type: {financial_type}")

        return CapitalSchemeFunding(
            effective_date=DateTimeRange(
                local_to_zoned(self.effective_date_from),
                local_to_zoned(self.effective_date_to) if self.effective_date_to else None,
            ),
            amount=Money(self.amount),
            data_source=self.data_source.data_source_name.to_domain(),
        )

    def to_spend_domain(self) -> CapitalSchemeSpend:
        financial_type = self.financial_type.financial_type_name.to_domain()
        if financial_type != FinancialType.SPEND_TO_DATE:
            raise ValueError(f"Invalid financial type: {financial_type}")

        return CapitalSchemeSpend(
            effective_date=DateTimeRange(
                local_to_zoned(self.effective_date_from),
                local_to_zoned(self.effective_date_to) if self.effective_date_to else None,
            ),
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
            CapitalSchemeFinancialEntity.from_funding_domain(
                funding, capital_scheme_id, financial_type_ids, data_source_ids
            )
            for funding in financials.fundings
        )
        if financials.spend:
            self._session.add(
                CapitalSchemeFinancialEntity.from_spend_domain(
                    financials.spend, capital_scheme_id, financial_type_ids, data_source_ids
                )
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
            .outerjoin(
                CapitalSchemeFinancialEntity,
                and_(
                    CapitalSchemeEntity.capital_scheme_id == CapitalSchemeFinancialEntity.capital_scheme_id,
                    CapitalSchemeFinancialEntity.effective_date_to.is_(None),
                ),
            )
            .outerjoin(FinancialTypeEntity)
            .where(CapitalSchemeEntity.scheme_reference == str(capital_scheme))
            .order_by(FinancialTypeEntity.financial_type_id)
            .order_by(CapitalSchemeFinancialEntity.effective_date_from)
        )
        rows = result.all()

        if not rows:
            return None

        financials = CapitalSchemeFinancials(capital_scheme=capital_scheme)
        for row in rows:
            if row.CapitalSchemeFinancialEntity:
                match row.CapitalSchemeFinancialEntity.financial_type.financial_type_name:
                    case FinancialTypeName.FUNDING_ALLOCATION:
                        financials.adjust_funding(row.CapitalSchemeFinancialEntity.to_funding_domain())
                    case FinancialTypeName.SPEND_TO_DATE:
                        financials.change_spend(row.CapitalSchemeFinancialEntity.to_spend_domain())
        return financials

    async def update(self, financials: CapitalSchemeFinancials) -> None:
        capital_scheme_id = await self._get_capital_scheme_id(financials)
        financial_type_ids = await self._get_financial_type_ids(financials)
        data_source_ids = await self._get_data_source_ids(financials)

        if financials.spend:
            financial_entity = CapitalSchemeFinancialEntity.from_spend_domain(
                financials.spend, capital_scheme_id, financial_type_ids, data_source_ids
            )

            if financial_entity.capital_scheme_financial_id is None:
                await self._close_financial(
                    financial_entity.capital_scheme_id,
                    financial_entity.financial_type_id,
                    financial_entity.effective_date_from,
                )

            await self._session.merge(financial_entity)

    async def _get_capital_scheme_id(self, financials: CapitalSchemeFinancials) -> int:
        capital_scheme_reference = str(financials.capital_scheme)
        rows = await self._session.scalars(
            select(CapitalSchemeEntity.capital_scheme_id).where(
                CapitalSchemeEntity.scheme_reference == capital_scheme_reference
            )
        )
        return rows.one()

    async def _get_financial_type_ids(self, financials: CapitalSchemeFinancials) -> dict[FinancialType, int]:
        financial_type_names = set()
        if financials.fundings:
            financial_type_names.add(FinancialTypeName.from_domain(FinancialType.FUNDING_ALLOCATION))
        if financials.spend:
            financial_type_names.add(FinancialTypeName.from_domain(FinancialType.SPEND_TO_DATE))
        rows = await self._session.execute(
            select(FinancialTypeEntity.financial_type_name, FinancialTypeEntity.financial_type_id).where(
                FinancialTypeEntity.financial_type_name.in_(financial_type_names)
            )
        )
        return {row.financial_type_name.to_domain(): row.financial_type_id for row in rows}

    async def _get_data_source_ids(self, financials: CapitalSchemeFinancials) -> dict[DataSource, int]:
        data_source_names = {DataSourceName.from_domain(financial.data_source) for financial in financials.fundings}
        if financials.spend:
            data_source_names.add(DataSourceName.from_domain(financials.spend.data_source))
        rows = await self._session.execute(
            select(DataSourceEntity.data_source_name, DataSourceEntity.data_source_id).where(
                DataSourceEntity.data_source_name.in_(data_source_names)
            )
        )
        return {row.data_source_name.to_domain(): row.data_source_id for row in rows}

    async def _close_financial(
        self, capital_scheme_id: int, financial_type_id: int, effective_date_to: datetime
    ) -> None:
        await self._session.execute(
            update(CapitalSchemeFinancialEntity)
            .where(CapitalSchemeFinancialEntity.capital_scheme_id == capital_scheme_id)
            .where(CapitalSchemeFinancialEntity.financial_type_id == financial_type_id)
            .where(CapitalSchemeFinancialEntity.effective_date_to.is_(None))
            .values(effective_date_to=effective_date_to)
        )
