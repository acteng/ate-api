from datetime import datetime

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ate_api.domain.capital_scheme_financials import (
    CapitalSchemeFinancials,
    CapitalSchemeFinancialsRepository,
)
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeReference
from ate_api.domain.data_sources import DataSource
from ate_api.domain.funding_programmes import FundingProgrammeCode
from ate_api.infrastructure.database.capital_scheme_financials.capital_scheme_financials import (
    CapitalSchemeFundingEntity,
    CapitalSchemeSpendEntity,
)
from ate_api.infrastructure.database.capital_schemes.capital_schemes import CapitalSchemeEntity
from ate_api.infrastructure.database.capital_schemes.overviews import CapitalSchemeOverviewEntity
from ate_api.infrastructure.database.data_sources import DataSourceEntity, DataSourceName
from ate_api.infrastructure.database.funding_programmes import FundingProgrammeEntity


class DatabaseCapitalSchemeFinancialsRepository(CapitalSchemeFinancialsRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, financials: CapitalSchemeFinancials) -> None:
        capital_scheme_id = await self._get_capital_scheme_id(financials)
        funding_programme_ids = await self._get_funding_programme_ids(financials)
        data_source_ids = await self._get_data_source_ids(financials)

        self._session.add_all(
            CapitalSchemeFundingEntity.from_domain(funding, capital_scheme_id, funding_programme_ids, data_source_ids)
            for funding in financials.fundings
        )
        if financials.spend:
            self._session.add(
                CapitalSchemeSpendEntity.from_domain(financials.spend, capital_scheme_id, data_source_ids)
            )

    async def get(self, capital_scheme: CapitalSchemeReference) -> CapitalSchemeFinancials | None:
        result = await self._session.execute(
            select(CapitalSchemeEntity, CapitalSchemeFundingEntity, CapitalSchemeSpendEntity)
            .options(
                joinedload(CapitalSchemeFundingEntity.funding_programme),
                joinedload(CapitalSchemeFundingEntity.data_source),
                joinedload(CapitalSchemeSpendEntity.data_source),
            )
            .join(
                CapitalSchemeEntity.capital_scheme_overviews.and_(
                    CapitalSchemeOverviewEntity.effective_date_to.is_(None)
                )
            )
            .outerjoin(
                CapitalSchemeFundingEntity,
                and_(
                    CapitalSchemeEntity.capital_scheme_id == CapitalSchemeFundingEntity.capital_scheme_id,
                    CapitalSchemeFundingEntity.effective_date_to.is_(None),
                ),
            )
            .outerjoin(
                CapitalSchemeSpendEntity,
                and_(
                    CapitalSchemeEntity.capital_scheme_id == CapitalSchemeSpendEntity.capital_scheme_id,
                    CapitalSchemeSpendEntity.effective_date_to.is_(None),
                ),
            )
            .where(CapitalSchemeEntity.scheme_reference == str(capital_scheme))
            .order_by(CapitalSchemeFundingEntity.effective_date_from)
        )
        rows = result.all()

        if not rows:
            return None

        financials = CapitalSchemeFinancials(capital_scheme=capital_scheme)
        for row in rows:
            if row.CapitalSchemeFundingEntity:
                financials.adjust_funding(row.CapitalSchemeFundingEntity.to_domain())
            if row.CapitalSchemeSpendEntity:
                financials.change_spend(row.CapitalSchemeSpendEntity.to_domain())
        return financials

    async def update(self, financials: CapitalSchemeFinancials) -> None:
        capital_scheme_id = await self._get_capital_scheme_id(financials)
        funding_programme_ids = await self._get_funding_programme_ids(financials)
        data_source_ids = await self._get_data_source_ids(financials)

        for funding in financials.fundings:
            await self._session.merge(
                CapitalSchemeFundingEntity.from_domain(
                    funding, capital_scheme_id, funding_programme_ids, data_source_ids
                )
            )

        if financials.spend:
            spend_entity = CapitalSchemeSpendEntity.from_domain(financials.spend, capital_scheme_id, data_source_ids)

            if spend_entity.capital_scheme_spend_id is None:
                await self._close_current_spend(spend_entity.capital_scheme_id, spend_entity.effective_date_from)

            await self._session.merge(spend_entity)

    async def _get_capital_scheme_id(self, financials: CapitalSchemeFinancials) -> int:
        capital_scheme_reference = str(financials.capital_scheme)
        rows = await self._session.scalars(
            select(CapitalSchemeEntity.capital_scheme_id).where(
                CapitalSchemeEntity.scheme_reference == capital_scheme_reference
            )
        )
        return rows.one()

    async def _get_funding_programme_ids(self, financials: CapitalSchemeFinancials) -> dict[FundingProgrammeCode, int]:
        funding_programme_codes = {str(funding.funding_programme) for funding in financials.fundings}
        rows = await self._session.execute(
            select(FundingProgrammeEntity.funding_programme_code, FundingProgrammeEntity.funding_programme_id).where(
                FundingProgrammeEntity.funding_programme_code.in_(funding_programme_codes)
            )
        )
        return {FundingProgrammeCode(row.funding_programme_code): row.funding_programme_id for row in rows}

    async def _get_data_source_ids(self, financials: CapitalSchemeFinancials) -> dict[DataSource, int]:
        data_source_names = {DataSourceName.from_domain(funding.data_source) for funding in financials.fundings}
        if financials.spend:
            data_source_names.add(DataSourceName.from_domain(financials.spend.data_source))
        rows = await self._session.execute(
            select(DataSourceEntity.data_source_name, DataSourceEntity.data_source_id).where(
                DataSourceEntity.data_source_name.in_(data_source_names)
            )
        )
        return {row.data_source_name.to_domain(): row.data_source_id for row in rows}

    async def _close_current_spend(self, capital_scheme_id: int, effective_date_to: datetime) -> None:
        spends = await self._session.scalars(
            select(CapitalSchemeSpendEntity)
            .where(CapitalSchemeSpendEntity.capital_scheme_id == capital_scheme_id)
            .where(CapitalSchemeSpendEntity.effective_date_to.is_(None))
        )
        spend = spends.one_or_none()
        if spend:
            spend.effective_date_to = effective_date_to
