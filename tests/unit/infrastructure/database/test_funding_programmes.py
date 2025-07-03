import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from ate_api.domain.funding_programmes import FundingProgramme, FundingProgrammeCode
from ate_api.infrastructure.database import FundingProgrammeEntity
from ate_api.infrastructure.database.funding_programmes import DatabaseFundingProgrammeRepository


class TestFundingProgrammeEntity:
    def test_from_domain(self) -> None:
        funding_programme = FundingProgramme(code=FundingProgrammeCode("ATF3"))

        funding_programme_entity = FundingProgrammeEntity.from_domain(funding_programme)

        assert (
            funding_programme_entity.funding_programme_code == "ATF3"
            and funding_programme_entity.is_under_embargo is False
        )

    def test_to_domain(self) -> None:
        funding_programme_entity = FundingProgrammeEntity(funding_programme_code="ATF3", is_under_embargo=False)

        funding_programme = funding_programme_entity.to_domain()

        assert funding_programme.code == FundingProgrammeCode("ATF3")


@pytest.mark.usefixtures("data")
@pytest.mark.asyncio(loop_scope="package")
class TestDatabaseFundingProgrammeRepository:
    async def test_add(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            funding_programmes = DatabaseFundingProgrammeRepository(session)
            await funding_programmes.add(FundingProgramme(code=FundingProgrammeCode("ATF3")))

        async with AsyncSession(engine) as session:
            (row,) = await session.scalars(select(FundingProgrammeEntity))
        assert row.funding_programme_code == "ATF3"

    async def test_get(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    FundingProgrammeEntity(funding_programme_code="ATF3", is_under_embargo=False),
                    FundingProgrammeEntity(funding_programme_code="ATF4", is_under_embargo=False),
                ]
            )

        async with AsyncSession(engine) as session:
            funding_programmes = DatabaseFundingProgrammeRepository(session)
            funding_programme = await funding_programmes.get(FundingProgrammeCode("ATF3"))

        assert funding_programme and funding_programme.code == FundingProgrammeCode("ATF3")

    async def test_get_filters_under_embargo(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add(FundingProgrammeEntity(funding_programme_code="ATF3", is_under_embargo=True))

        async with AsyncSession(engine) as session:
            funding_programmes = DatabaseFundingProgrammeRepository(session)
            funding_programme = await funding_programmes.get(FundingProgrammeCode("ATF3"))

        assert not funding_programme

    async def test_get_when_not_found(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session:
            funding_programmes = DatabaseFundingProgrammeRepository(session)
            funding_programme = await funding_programmes.get(FundingProgrammeCode("ATF3"))

        assert not funding_programme

    async def test_get_all(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    FundingProgrammeEntity(funding_programme_code="ATF3", is_under_embargo=False),
                    FundingProgrammeEntity(funding_programme_code="ATF4", is_under_embargo=False),
                ]
            )

        async with AsyncSession(engine) as session:
            funding_programmes = DatabaseFundingProgrammeRepository(session)
            funding_programme1, funding_programme2 = await funding_programmes.get_all()

        assert funding_programme1.code == FundingProgrammeCode("ATF3")
        assert funding_programme2.code == FundingProgrammeCode("ATF4")

    async def test_get_all_when_none(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session:
            funding_programmes = DatabaseFundingProgrammeRepository(session)
            all_funding_programmes = await funding_programmes.get_all()

        assert all_funding_programmes == []

    async def test_exists(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add(FundingProgrammeEntity(funding_programme_code="ATF3", is_under_embargo=False))

        async with AsyncSession(engine) as session:
            funding_programmes = DatabaseFundingProgrammeRepository(session)
            exists = await funding_programmes.exists(FundingProgrammeCode("ATF3"))

        assert exists

    async def test_exists_filters_under_embargo(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add(FundingProgrammeEntity(funding_programme_code="ATF3", is_under_embargo=True))

        async with AsyncSession(engine) as session:
            funding_programmes = DatabaseFundingProgrammeRepository(session)
            exists = await funding_programmes.exists(FundingProgrammeCode("ATF3"))

        assert not exists

    async def test_exists_when_not_found(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session:
            funding_programmes = DatabaseFundingProgrammeRepository(session)
            exists = await funding_programmes.exists(FundingProgrammeCode("ATF3"))

        assert not exists

    async def test_exists_all(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    FundingProgrammeEntity(funding_programme_code="ATF3", is_under_embargo=False),
                    FundingProgrammeEntity(funding_programme_code="ATF4", is_under_embargo=False),
                ]
            )

        async with AsyncSession(engine) as session:
            funding_programmes = DatabaseFundingProgrammeRepository(session)
            exists = await funding_programmes.exists_all([FundingProgrammeCode("ATF3"), FundingProgrammeCode("ATF4")])

        assert exists

    async def test_exists_all_filters_under_embargo(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add(FundingProgrammeEntity(funding_programme_code="ATF3", is_under_embargo=True))

        async with AsyncSession(engine) as session:
            funding_programmes = DatabaseFundingProgrammeRepository(session)
            exists = await funding_programmes.exists_all([FundingProgrammeCode("ATF3")])

        assert not exists

    async def test_exists_all_when_some_found(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add(FundingProgrammeEntity(funding_programme_code="ATF3", is_under_embargo=False))

        async with AsyncSession(engine) as session:
            funding_programmes = DatabaseFundingProgrammeRepository(session)
            exists = await funding_programmes.exists_all([FundingProgrammeCode("ATF3"), FundingProgrammeCode("ATF4")])

        assert not exists

    async def test_exists_all_when_none_found(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session:
            funding_programmes = DatabaseFundingProgrammeRepository(session)
            exists = await funding_programmes.exists_all([FundingProgrammeCode("ATF3"), FundingProgrammeCode("ATF4")])

        assert not exists
