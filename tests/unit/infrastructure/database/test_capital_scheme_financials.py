from datetime import UTC, datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from ate_api.domain.capital_scheme_financials import CapitalSchemeFinancial, CapitalSchemeFinancials
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeReference
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.financial_types import FinancialType
from ate_api.domain.moneys import Money
from ate_api.infrastructure.database import (
    CapitalSchemeEntity,
    CapitalSchemeFinancialEntity,
    DataSourceEntity,
    DataSourceName,
    FinancialTypeEntity,
    FinancialTypeName,
)
from ate_api.infrastructure.database.capital_scheme_financials import DatabaseCapitalSchemeFinancialsRepository
from tests.unit.infrastructure.database.builders import (
    build_capital_scheme_overview_entity,
    build_data_source_entity,
    build_financial_type_entity,
    build_funding_programme_entity,
)


class TestCapitalSchemeFinancialEntity:
    def test_from_domain(self) -> None:
        financial = CapitalSchemeFinancial(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC), datetime(2020, 2, 1, tzinfo=UTC)),
            type=FinancialType.FUNDING_ALLOCATION,
            amount=Money(2_000_000),
            data_source=DataSource.ATF4_BID,
            surrogate_id=1,
        )

        financial_entity = CapitalSchemeFinancialEntity.from_domain(
            financial, 2, {FinancialType.FUNDING_ALLOCATION: 3}, {DataSource.ATF4_BID: 4}
        )

        assert (
            financial_entity.capital_scheme_financial_id == 1
            and financial_entity.capital_scheme_id == 2
            and financial_entity.financial_type_id == 3
            and financial_entity.amount == 2_000_000
            and financial_entity.effective_date_from == datetime(2020, 1, 1)
            and financial_entity.effective_date_to == datetime(2020, 2, 1)
            and financial_entity.data_source_id == 4
        )

    def test_from_domain_when_current(self) -> None:
        financial = CapitalSchemeFinancial(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            type=FinancialType.FUNDING_ALLOCATION,
            amount=Money(2_000_000),
            data_source=DataSource.ATF4_BID,
        )

        financial_entity = CapitalSchemeFinancialEntity.from_domain(
            financial, 0, {FinancialType.FUNDING_ALLOCATION: 0}, {DataSource.ATF4_BID: 0}
        )

        assert not financial_entity.effective_date_to

    def test_from_domain_converts_dates_to_local_europe_london(self) -> None:
        financial = CapitalSchemeFinancial(
            effective_date=DateTimeRange(datetime(2020, 6, 1, 12, tzinfo=UTC), datetime(2020, 7, 1, 12, tzinfo=UTC)),
            type=FinancialType.FUNDING_ALLOCATION,
            amount=Money(2_000_000),
            data_source=DataSource.ATF4_BID,
        )

        financial_entity = CapitalSchemeFinancialEntity.from_domain(
            financial, 0, {FinancialType.FUNDING_ALLOCATION: 0}, {DataSource.ATF4_BID: 0}
        )

        assert financial_entity.effective_date_from == datetime(2020, 6, 1, 13)
        assert financial_entity.effective_date_to == datetime(2020, 7, 1, 13)

    def test_to_domain(self) -> None:
        financial_entity = CapitalSchemeFinancialEntity(
            capital_scheme_financial_id=1,
            financial_type=FinancialTypeEntity(financial_type_name=FinancialTypeName.FUNDING_ALLOCATION),
            amount=2_000_000,
            effective_date_from=datetime(2020, 1, 1),
            effective_date_to=datetime(2020, 2, 1),
            data_source=DataSourceEntity(data_source_name=DataSourceName.ATF4_BID),
        )

        financial = financial_entity.to_domain()

        assert financial == CapitalSchemeFinancial(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC), datetime(2020, 2, 1, tzinfo=UTC)),
            type=FinancialType.FUNDING_ALLOCATION,
            amount=Money(2_000_000),
            data_source=DataSource.ATF4_BID,
        )
        assert financial.surrogate_id == 1

    def test_to_domain_when_current(self) -> None:
        financial_entity = CapitalSchemeFinancialEntity(
            financial_type=FinancialTypeEntity(financial_type_name=FinancialTypeName.FUNDING_ALLOCATION),
            amount=2_000_000,
            effective_date_from=datetime(2020, 1, 1),
            data_source=DataSourceEntity(data_source_name=DataSourceName.ATF4_BID),
        )

        financial = financial_entity.to_domain()

        assert not financial.effective_date.to

    def test_to_domain_converts_dates_from_local_europe_london(self) -> None:
        financial_entity = CapitalSchemeFinancialEntity(
            financial_type=FinancialTypeEntity(financial_type_name=FinancialTypeName.FUNDING_ALLOCATION),
            amount=2_000_000,
            effective_date_from=datetime(2020, 6, 1, 13),
            effective_date_to=datetime(2020, 7, 1, 13),
            data_source=DataSourceEntity(data_source_name=DataSourceName.ATF4_BID),
        )

        financial = financial_entity.to_domain()

        assert financial.effective_date == DateTimeRange(
            datetime(2020, 6, 1, 12, tzinfo=UTC), datetime(2020, 7, 1, 12, tzinfo=UTC)
        )


@pytest.mark.usefixtures("data")
@pytest.mark.asyncio(loop_scope="package")
class TestDatabaseCapitalSchemeFinancialsRepository:
    async def test_add_stores_financials(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    build_financial_type_entity(id_=1, name=FinancialTypeName.FUNDING_ALLOCATION),
                    build_financial_type_entity(id_=2, name=FinancialTypeName.SPEND_TO_DATE),
                    build_data_source_entity(id_=3, name=DataSourceName.ATF4_BID),
                    CapitalSchemeEntity(scheme_reference="ATE00001"),
                ]
            )

        async with AsyncSession(engine) as session, session.begin():
            capital_scheme_financials = DatabaseCapitalSchemeFinancialsRepository(session)
            financials = CapitalSchemeFinancials(capital_scheme=CapitalSchemeReference("ATE00001"))
            financials.adjust_financial(
                CapitalSchemeFinancial(
                    effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                    type=FinancialType.FUNDING_ALLOCATION,
                    amount=Money(2_000_000),
                    data_source=DataSource.ATF4_BID,
                )
            )
            financials.adjust_financial(
                CapitalSchemeFinancial(
                    effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                    type=FinancialType.SPEND_TO_DATE,
                    amount=Money(1_000_000),
                    data_source=DataSource.ATF4_BID,
                )
            )
            await capital_scheme_financials.add(financials)

        async with AsyncSession(engine) as session:
            (capital_scheme_row,) = await session.scalars(select(CapitalSchemeEntity))
            financial_row1, financial_row2 = await session.scalars(select(CapitalSchemeFinancialEntity))
        assert (
            financial_row1.capital_scheme_id == capital_scheme_row.capital_scheme_id
            and financial_row1.financial_type_id == 1
            and financial_row1.amount == 2_000_000
            and financial_row1.effective_date_from == datetime(2020, 1, 1)
            and not financial_row1.effective_date_to
            and financial_row1.data_source_id == 3
        )
        assert (
            financial_row2.capital_scheme_id == capital_scheme_row.capital_scheme_id
            and financial_row2.financial_type_id == 2
            and financial_row2.amount == 1_000_000
            and financial_row2.effective_date_from == datetime(2020, 1, 1)
            and not financial_row2.effective_date_to
            and financial_row2.data_source_id == 3
        )

    async def test_get(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add(
                CapitalSchemeEntity(
                    capital_scheme_id=1,
                    scheme_reference="ATE00001",
                    capital_scheme_overviews=[build_capital_scheme_overview_entity()],
                )
            )

        async with AsyncSession(engine) as session:
            capital_scheme_financials = DatabaseCapitalSchemeFinancialsRepository(session)
            financials = await capital_scheme_financials.get(CapitalSchemeReference("ATE00001"))

        assert (
            financials and financials.capital_scheme == CapitalSchemeReference("ATE00001") and not financials.financials
        )

    async def test_get_fetches_current_financials(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    funding_allocation := build_financial_type_entity(name=FinancialTypeName.FUNDING_ALLOCATION),
                    spend_to_date := build_financial_type_entity(name=FinancialTypeName.SPEND_TO_DATE),
                    atf4_bid := build_data_source_entity(name=DataSourceName.ATF4_BID),
                    CapitalSchemeEntity(
                        capital_scheme_id=1,
                        scheme_reference="ATE00001",
                        capital_scheme_overviews=[build_capital_scheme_overview_entity()],
                    ),
                    CapitalSchemeFinancialEntity(
                        capital_scheme_id=1,
                        financial_type=funding_allocation,
                        amount=3_000_000,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=datetime(2020, 2, 1),
                        data_source=atf4_bid,
                    ),
                    CapitalSchemeFinancialEntity(
                        capital_scheme_id=1,
                        financial_type=funding_allocation,
                        amount=2_000_000,
                        effective_date_from=datetime(2020, 2, 1),
                        data_source=atf4_bid,
                    ),
                    CapitalSchemeFinancialEntity(
                        capital_scheme_id=1,
                        financial_type=spend_to_date,
                        amount=1_000_000,
                        effective_date_from=datetime(2020, 2, 1),
                        data_source=atf4_bid,
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_scheme_financials = DatabaseCapitalSchemeFinancialsRepository(session)
            financials = await capital_scheme_financials.get(CapitalSchemeReference("ATE00001"))

        assert financials and financials.financials == [
            CapitalSchemeFinancial(
                effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Money(2_000_000),
                data_source=DataSource.ATF4_BID,
            ),
            CapitalSchemeFinancial(
                effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)),
                type=FinancialType.SPEND_TO_DATE,
                amount=Money(1_000_000),
                data_source=DataSource.ATF4_BID,
            ),
        ]

    async def test_get_fetches_current_financials_ordered_by_financial_type_then_effective_date_from(
        self, engine: AsyncEngine
    ) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    funding_allocation := build_financial_type_entity(name=FinancialTypeName.FUNDING_ALLOCATION),
                    spend_to_date := build_financial_type_entity(name=FinancialTypeName.SPEND_TO_DATE),
                    atf4_bid := build_data_source_entity(name=DataSourceName.ATF4_BID),
                    CapitalSchemeEntity(
                        capital_scheme_id=1,
                        scheme_reference="ATE00001",
                        capital_scheme_overviews=[build_capital_scheme_overview_entity()],
                    ),
                    CapitalSchemeFinancialEntity(
                        capital_scheme_id=1,
                        financial_type=spend_to_date,
                        amount=1_000_000,
                        effective_date_from=datetime(2020, 2, 1),
                        data_source=atf4_bid,
                    ),
                    CapitalSchemeFinancialEntity(
                        capital_scheme_id=1,
                        financial_type=funding_allocation,
                        amount=3_000_000,
                        effective_date_from=datetime(2020, 3, 1),
                        data_source=atf4_bid,
                    ),
                    CapitalSchemeFinancialEntity(
                        capital_scheme_id=1,
                        financial_type=funding_allocation,
                        amount=2_000_000,
                        effective_date_from=datetime(2020, 2, 1),
                        data_source=atf4_bid,
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_scheme_financials = DatabaseCapitalSchemeFinancialsRepository(session)
            financials = await capital_scheme_financials.get(CapitalSchemeReference("ATE00001"))

        assert financials and financials.financials == [
            CapitalSchemeFinancial(
                effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Money(2_000_000),
                data_source=DataSource.ATF4_BID,
            ),
            CapitalSchemeFinancial(
                effective_date=DateTimeRange(datetime(2020, 3, 1, tzinfo=UTC)),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Money(3_000_000),
                data_source=DataSource.ATF4_BID,
            ),
            CapitalSchemeFinancial(
                effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)),
                type=FinancialType.SPEND_TO_DATE,
                amount=Money(1_000_000),
                data_source=DataSource.ATF4_BID,
            ),
        ]

    async def test_get_filters_under_embargo(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    atf3 := build_funding_programme_entity(code="ATF3", is_under_embargo=True),
                    funding_allocation := build_financial_type_entity(name=FinancialTypeName.FUNDING_ALLOCATION),
                    atf4_bid := build_data_source_entity(name=DataSourceName.ATF4_BID),
                    CapitalSchemeEntity(
                        capital_scheme_id=1,
                        scheme_reference="ATE00001",
                        capital_scheme_overviews=[build_capital_scheme_overview_entity(funding_programme=atf3)],
                    ),
                    CapitalSchemeFinancialEntity(
                        capital_scheme_id=1,
                        financial_type=funding_allocation,
                        amount=3_000_000,
                        effective_date_from=datetime(2020, 1, 1),
                        data_source=atf4_bid,
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_scheme_financials = DatabaseCapitalSchemeFinancialsRepository(session)
            financials = await capital_scheme_financials.get(CapitalSchemeReference("ATE00001"))

        assert not financials

    async def test_get_when_not_found(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session:
            capital_scheme_financials = DatabaseCapitalSchemeFinancialsRepository(session)
            financials = await capital_scheme_financials.get(CapitalSchemeReference("ATE00001"))

        assert not financials

    async def test_update(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    funding_allocation := build_financial_type_entity(id_=2, name=FinancialTypeName.FUNDING_ALLOCATION),
                    atf4_bid := build_data_source_entity(id_=3, name=DataSourceName.ATF4_BID),
                    CapitalSchemeEntity(
                        capital_scheme_id=1,
                        scheme_reference="ATE00001",
                        capital_scheme_overviews=[build_capital_scheme_overview_entity()],
                    ),
                    CapitalSchemeFinancialEntity(
                        capital_scheme_id=1,
                        financial_type=funding_allocation,
                        amount=3_000_000,
                        effective_date_from=datetime(2020, 1, 1),
                        data_source=atf4_bid,
                    ),
                ]
            )

        async with AsyncSession(engine) as session, session.begin():
            capital_scheme_financials = DatabaseCapitalSchemeFinancialsRepository(session)
            financials = await capital_scheme_financials.get(CapitalSchemeReference("ATE00001"))
            assert financials
            financials.change_financial(
                CapitalSchemeFinancial(
                    effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)),
                    type=FinancialType.FUNDING_ALLOCATION,
                    amount=Money(2_000_000),
                    data_source=DataSource.ATF4_BID,
                )
            )
            await capital_scheme_financials.update(financials)

        async with AsyncSession(engine) as session:
            (capital_scheme_row,) = await session.scalars(select(CapitalSchemeEntity))
            financial_row1, financial_row2 = await session.scalars(select(CapitalSchemeFinancialEntity))
        assert (
            financial_row1.capital_scheme_id == capital_scheme_row.capital_scheme_id
            and financial_row1.effective_date_to == datetime(2020, 2, 1)
        )
        assert (
            financial_row2.capital_scheme_id == capital_scheme_row.capital_scheme_id
            and financial_row2.financial_type_id == 2
            and financial_row2.amount == 2_000_000
            and financial_row2.effective_date_from == datetime(2020, 2, 1)
            and not financial_row2.effective_date_to
            and financial_row2.data_source_id == 3
        )
