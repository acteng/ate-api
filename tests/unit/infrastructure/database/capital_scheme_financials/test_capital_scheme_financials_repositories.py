from datetime import UTC, datetime

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from ate_api.domain.capital_scheme_financials import CapitalSchemeFinancials, CapitalSchemeFunding, CapitalSchemeSpend
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeReference
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.funding_programmes import FundingProgrammeCode
from ate_api.domain.moneys import Money
from ate_api.infrastructure.database import (
    CapitalSchemeEntity,
    CapitalSchemeFundingEntity,
    CapitalSchemeSpendEntity,
    DataSourceName,
)
from ate_api.infrastructure.database.capital_scheme_financials.capital_scheme_financials_repositories import (
    DatabaseCapitalSchemeFinancialsRepository,
)
from tests.unit.dates import local_datetime
from tests.unit.infrastructure.database.builders import (
    EntityBuilder,
    build_data_source_entity,
    build_funding_programme_entity,
)


@pytest.mark.usefixtures("data")
@pytest.mark.asyncio(loop_scope="package")
class TestDatabaseCapitalSchemeFinancialsRepository:
    async def test_add_stores_funding(self, engine: AsyncEngine, entities: EntityBuilder) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    build_funding_programme_entity(id_=1, code="ATF3"),
                    build_data_source_entity(id_=2, name=DataSourceName.ATF3_BID),
                    entities.build_capital_scheme(reference="ATE00001"),
                ]
            )

        async with AsyncSession(engine) as session, session.begin():
            capital_scheme_financials = DatabaseCapitalSchemeFinancialsRepository(session)
            financials = CapitalSchemeFinancials(capital_scheme=CapitalSchemeReference("ATE00001"))
            financials.adjust_funding(
                CapitalSchemeFunding(
                    effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                    funding_programme=FundingProgrammeCode("ATF3"),
                    amount=Money(2_000_000),
                    data_source=DataSource.ATF3_BID,
                )
            )
            financials.adjust_funding(
                CapitalSchemeFunding(
                    effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                    funding_programme=FundingProgrammeCode("ATF3"),
                    amount=Money(1_000_000),
                    data_source=DataSource.ATF3_BID,
                )
            )
            await capital_scheme_financials.add(financials)

        async with AsyncSession(engine) as session:
            (capital_scheme_row,) = await session.scalars(select(CapitalSchemeEntity))
            funding_row1, funding_row2 = await session.scalars(select(CapitalSchemeFundingEntity))
        assert (
            funding_row1.capital_scheme_id == capital_scheme_row.capital_scheme_id
            and funding_row1.amount == 2_000_000
            and funding_row1.funding_programme_id == 1
            and funding_row1.data_source_id == 2
            and funding_row1.effective_date_from == local_datetime(2020, 1, 1)
            and not funding_row1.effective_date_to
        )
        assert (
            funding_row2.capital_scheme_id == capital_scheme_row.capital_scheme_id
            and funding_row2.amount == 1_000_000
            and funding_row2.funding_programme_id == 1
            and funding_row2.data_source_id == 2
            and funding_row2.effective_date_from == local_datetime(2020, 1, 1)
            and not funding_row2.effective_date_to
        )

    async def test_add_stores_spend(self, engine: AsyncEngine, entities: EntityBuilder) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    build_data_source_entity(id_=1, name=DataSourceName.ATF3_BID),
                    entities.build_capital_scheme(reference="ATE00001"),
                ]
            )

        async with AsyncSession(engine) as session, session.begin():
            capital_scheme_financials = DatabaseCapitalSchemeFinancialsRepository(session)
            financials = CapitalSchemeFinancials(capital_scheme=CapitalSchemeReference("ATE00001"))
            financials.change_spend(
                CapitalSchemeSpend(
                    effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                    amount=Money(1_000_000),
                    data_source=DataSource.ATF3_BID,
                )
            )
            await capital_scheme_financials.add(financials)

        async with AsyncSession(engine) as session:
            (capital_scheme_row,) = await session.scalars(select(CapitalSchemeEntity))
            (spend_row,) = await session.scalars(select(CapitalSchemeSpendEntity))
        assert (
            spend_row.capital_scheme_id == capital_scheme_row.capital_scheme_id
            and spend_row.amount == 1_000_000
            and spend_row.data_source_id == 1
            and spend_row.effective_date_from == local_datetime(2020, 1, 1)
            and not spend_row.effective_date_to
        )

    async def test_get(self, engine: AsyncEngine, entities: EntityBuilder) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add(entities.build_capital_scheme(reference="ATE00001"))

        async with AsyncSession(engine) as session:
            capital_scheme_financials = DatabaseCapitalSchemeFinancialsRepository(session)
            financials = await capital_scheme_financials.get(CapitalSchemeReference("ATE00001"))

        assert (
            financials
            and financials.capital_scheme == CapitalSchemeReference("ATE00001")
            and not financials.fundings
            and not financials.spend
        )

    async def test_get_fetches_current_fundings(self, engine: AsyncEngine, entities: EntityBuilder) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    atf3 := build_funding_programme_entity(code="ATF3"),
                    atf3_bid := build_data_source_entity(name=DataSourceName.ATF3_BID),
                    entities.build_capital_scheme(id_=1, reference="ATE00001"),
                    CapitalSchemeFundingEntity(
                        capital_scheme_id=1,
                        amount=3_000_000,
                        funding_programme=atf3,
                        data_source=atf3_bid,
                        effective_date_from=local_datetime(2020, 1, 1),
                        effective_date_to=local_datetime(2020, 2, 1),
                    ),
                    CapitalSchemeFundingEntity(
                        capital_scheme_id=1,
                        amount=2_000_000,
                        funding_programme=atf3,
                        data_source=atf3_bid,
                        effective_date_from=local_datetime(2020, 2, 1),
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_scheme_financials = DatabaseCapitalSchemeFinancialsRepository(session)
            financials = await capital_scheme_financials.get(CapitalSchemeReference("ATE00001"))

        assert financials and financials.fundings == [
            CapitalSchemeFunding(
                effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)),
                funding_programme=FundingProgrammeCode("ATF3"),
                amount=Money(2_000_000),
                data_source=DataSource.ATF3_BID,
            )
        ]

    async def test_get_fetches_current_fundings_ordered_by_effective_date_from(
        self, engine: AsyncEngine, entities: EntityBuilder
    ) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    atf3 := build_funding_programme_entity(code="ATF3"),
                    atf3_bid := build_data_source_entity(name=DataSourceName.ATF3_BID),
                    entities.build_capital_scheme(id_=1, reference="ATE00001"),
                    CapitalSchemeFundingEntity(
                        capital_scheme_id=1,
                        amount=3_000_000,
                        funding_programme=atf3,
                        data_source=atf3_bid,
                        effective_date_from=local_datetime(2020, 3, 1),
                    ),
                    CapitalSchemeFundingEntity(
                        capital_scheme_id=1,
                        amount=2_000_000,
                        funding_programme=atf3,
                        data_source=atf3_bid,
                        effective_date_from=local_datetime(2020, 2, 1),
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_scheme_financials = DatabaseCapitalSchemeFinancialsRepository(session)
            financials = await capital_scheme_financials.get(CapitalSchemeReference("ATE00001"))

        assert financials and financials.fundings == [
            CapitalSchemeFunding(
                effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)),
                funding_programme=FundingProgrammeCode("ATF3"),
                amount=Money(2_000_000),
                data_source=DataSource.ATF3_BID,
            ),
            CapitalSchemeFunding(
                effective_date=DateTimeRange(datetime(2020, 3, 1, tzinfo=UTC)),
                funding_programme=FundingProgrammeCode("ATF3"),
                amount=Money(3_000_000),
                data_source=DataSource.ATF3_BID,
            ),
        ]

    async def test_get_fetches_current_spend(self, engine: AsyncEngine, entities: EntityBuilder) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    atf3_bid := build_data_source_entity(name=DataSourceName.ATF3_BID),
                    entities.build_capital_scheme(id_=1, reference="ATE00001"),
                    CapitalSchemeSpendEntity(
                        capital_scheme_id=1,
                        amount=2_000_000,
                        data_source=atf3_bid,
                        effective_date_from=local_datetime(2020, 1, 1),
                        effective_date_to=local_datetime(2020, 2, 1),
                    ),
                    CapitalSchemeSpendEntity(
                        capital_scheme_id=1,
                        amount=1_000_000,
                        data_source=atf3_bid,
                        effective_date_from=local_datetime(2020, 2, 1),
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_scheme_financials = DatabaseCapitalSchemeFinancialsRepository(session)
            financials = await capital_scheme_financials.get(CapitalSchemeReference("ATE00001"))

        assert financials and financials.spend == CapitalSchemeSpend(
            effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)),
            amount=Money(1_000_000),
            data_source=DataSource.ATF3_BID,
        )

    async def test_get_when_not_found(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session:
            capital_scheme_financials = DatabaseCapitalSchemeFinancialsRepository(session)
            financials = await capital_scheme_financials.get(CapitalSchemeReference("ATE00001"))

        assert not financials

    async def test_update_creates_funding(self, engine: AsyncEngine, entities: EntityBuilder) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    build_funding_programme_entity(id_=2, code="ATF3"),
                    build_data_source_entity(id_=3, name=DataSourceName.ATF3_BID),
                    entities.build_capital_scheme(id_=1, reference="ATE00001"),
                ]
            )

        async with AsyncSession(engine) as session, session.begin():
            capital_scheme_financials = DatabaseCapitalSchemeFinancialsRepository(session)
            financials = await capital_scheme_financials.get(CapitalSchemeReference("ATE00001"))
            assert financials
            financials.adjust_funding(
                CapitalSchemeFunding(
                    effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)),
                    funding_programme=FundingProgrammeCode("ATF3"),
                    amount=Money(3_000_000),
                    data_source=DataSource.ATF3_BID,
                )
            )
            await capital_scheme_financials.update(financials)

        async with AsyncSession(engine) as session:
            (funding_row,) = await session.scalars(select(CapitalSchemeFundingEntity))
        assert (
            funding_row.capital_scheme_id == 1
            and funding_row.funding_programme_id == 2
            and funding_row.amount == 3_000_000
            and funding_row.data_source_id == 3
            and funding_row.effective_date_from == local_datetime(2020, 2, 1)
            and not funding_row.effective_date_to
        )

    async def test_update_preserves_current_funding(self, engine: AsyncEngine, entities: EntityBuilder) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    atf3 := build_funding_programme_entity(code="ATF3"),
                    atf3_bid := build_data_source_entity(name=DataSourceName.ATF3_BID),
                    entities.build_capital_scheme(id_=1, reference="ATE00001"),
                    CapitalSchemeFundingEntity(
                        capital_scheme_id=1,
                        funding_programme=atf3,
                        amount=3_000_000,
                        data_source=atf3_bid,
                        effective_date_from=local_datetime(2020, 1, 1),
                    ),
                ]
            )

        async with AsyncSession(engine) as session, session.begin():
            capital_scheme_financials = DatabaseCapitalSchemeFinancialsRepository(session)
            financials = await capital_scheme_financials.get(CapitalSchemeReference("ATE00001"))
            assert financials
            financials.adjust_funding(
                CapitalSchemeFunding(
                    effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)),
                    funding_programme=FundingProgrammeCode("ATF3"),
                    amount=Money(2_000_000),
                    data_source=DataSource.ATF3_BID,
                )
            )
            await capital_scheme_financials.update(financials)

        async with AsyncSession(engine) as session:
            funding_row1, _ = await session.scalars(select(CapitalSchemeFundingEntity))
        assert funding_row1.capital_scheme_id == 1 and not funding_row1.effective_date_to

    async def test_update_ignores_unchanged_funding(self, engine: AsyncEngine, entities: EntityBuilder) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    atf3 := build_funding_programme_entity(id_=2, code="ATF3"),
                    atf3_bid := build_data_source_entity(id_=3, name=DataSourceName.ATF3_BID),
                    entities.build_capital_scheme(id_=1, reference="ATE00001"),
                    CapitalSchemeFundingEntity(
                        capital_scheme_id=1,
                        funding_programme=atf3,
                        amount=3_000_000,
                        data_source=atf3_bid,
                        effective_date_from=local_datetime(2020, 1, 1),
                    ),
                ]
            )

        async with AsyncSession(engine) as session, session.begin():
            capital_scheme_financials = DatabaseCapitalSchemeFinancialsRepository(session)
            financials = await capital_scheme_financials.get(CapitalSchemeReference("ATE00001"))
            assert financials
            await capital_scheme_financials.update(financials)

        async with AsyncSession(engine) as session:
            (funding_row,) = await session.scalars(select(CapitalSchemeFundingEntity))
        assert (
            funding_row.capital_scheme_id == 1
            and funding_row.funding_programme_id == 2
            and funding_row.amount == 3_000_000
            and funding_row.data_source_id == 3
            and funding_row.effective_date_from == local_datetime(2020, 1, 1)
            and not funding_row.effective_date_to
        )

    async def test_update_creates_spend(self, engine: AsyncEngine, entities: EntityBuilder) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    build_data_source_entity(id_=2, name=DataSourceName.ATF3_BID),
                    entities.build_capital_scheme(id_=1, reference="ATE00001"),
                ]
            )

        async with AsyncSession(engine) as session, session.begin():
            capital_scheme_financials = DatabaseCapitalSchemeFinancialsRepository(session)
            financials = await capital_scheme_financials.get(CapitalSchemeReference("ATE00001"))
            assert financials
            financials.change_spend(
                CapitalSchemeSpend(
                    effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)),
                    amount=Money(2_000_000),
                    data_source=DataSource.ATF3_BID,
                )
            )
            await capital_scheme_financials.update(financials)

        async with AsyncSession(engine) as session:
            (spend_row,) = await session.scalars(select(CapitalSchemeSpendEntity))
        assert (
            spend_row.capital_scheme_id == 1
            and spend_row.amount == 2_000_000
            and spend_row.data_source_id == 2
            and spend_row.effective_date_from == local_datetime(2020, 2, 1)
            and not spend_row.effective_date_to
        )

    async def test_update_closes_current_spend(self, engine: AsyncEngine, entities: EntityBuilder) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    atf3_bid := build_data_source_entity(id_=2, name=DataSourceName.ATF3_BID),
                    entities.build_capital_scheme(id_=1, reference="ATE00001"),
                    CapitalSchemeSpendEntity(
                        capital_scheme_id=1,
                        amount=3_000_000,
                        data_source=atf3_bid,
                        effective_date_from=local_datetime(2020, 1, 1),
                    ),
                ]
            )

        async with AsyncSession(engine) as session, session.begin():
            capital_scheme_financials = DatabaseCapitalSchemeFinancialsRepository(session)
            financials = await capital_scheme_financials.get(CapitalSchemeReference("ATE00001"))
            assert financials
            financials.change_spend(
                CapitalSchemeSpend(
                    effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)),
                    amount=Money(2_000_000),
                    data_source=DataSource.ATF3_BID,
                )
            )
            await capital_scheme_financials.update(financials)

        async with AsyncSession(engine) as session:
            spend_row1, _ = await session.scalars(select(CapitalSchemeSpendEntity))
        assert spend_row1.capital_scheme_id == 1 and spend_row1.effective_date_to == local_datetime(2020, 2, 1)

    async def test_update_ignores_unchanged_spend(self, engine: AsyncEngine, entities: EntityBuilder) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    atf3_bid := build_data_source_entity(id_=2, name=DataSourceName.ATF3_BID),
                    entities.build_capital_scheme(id_=1, reference="ATE00001"),
                    CapitalSchemeSpendEntity(
                        capital_scheme_id=1,
                        amount=3_000_000,
                        data_source=atf3_bid,
                        effective_date_from=local_datetime(2020, 1, 1),
                    ),
                ]
            )

        async with AsyncSession(engine) as session, session.begin():
            capital_scheme_financials = DatabaseCapitalSchemeFinancialsRepository(session)
            financials = await capital_scheme_financials.get(CapitalSchemeReference("ATE00001"))
            assert financials
            await capital_scheme_financials.update(financials)

        async with AsyncSession(engine) as session:
            (spend_row,) = await session.scalars(select(CapitalSchemeSpendEntity))
        assert (
            spend_row.capital_scheme_id == 1
            and spend_row.amount == 3_000_000
            and spend_row.data_source_id == 2
            and spend_row.effective_date_from == local_datetime(2020, 1, 1)
            and not spend_row.effective_date_to
        )

    async def test_update_ignores_no_spend(self, engine: AsyncEngine, entities: EntityBuilder) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add(entities.build_capital_scheme(reference="ATE00001"))

        async with AsyncSession(engine) as session, session.begin():
            capital_scheme_financials = DatabaseCapitalSchemeFinancialsRepository(session)
            financials = await capital_scheme_financials.get(CapitalSchemeReference("ATE00001"))
            assert financials
            await capital_scheme_financials.update(financials)

        async with AsyncSession(engine) as session:
            spend_count = await session.scalar(select(func.count()).select_from(CapitalSchemeSpendEntity))
        assert spend_count == 0
