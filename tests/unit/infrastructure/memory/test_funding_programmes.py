import pytest

from ate_api.domain.funding_programmes import FundingProgramme, FundingProgrammeCode
from tests.unit.infrastructure.memory.funding_programmes import MemoryFundingProgrammeRepository


class TestMemoryFundingProgrammeRepository:
    @pytest.fixture(name="funding_programmes")
    def funding_programmes_fixture(self) -> MemoryFundingProgrammeRepository:
        return MemoryFundingProgrammeRepository()

    async def test_add(self, funding_programmes: MemoryFundingProgrammeRepository) -> None:
        await funding_programmes.add(
            FundingProgramme(code=FundingProgrammeCode("ATF3"), is_eligible_for_authority_update=True)
        )

        funding_programme = await funding_programmes.get(FundingProgrammeCode("ATF3"))
        assert (
            funding_programme
            and funding_programme.code == FundingProgrammeCode("ATF3")
            and funding_programme.is_eligible_for_authority_update
        )

    async def test_get(self, funding_programmes: MemoryFundingProgrammeRepository) -> None:
        await funding_programmes.add(
            FundingProgramme(code=FundingProgrammeCode("ATF3"), is_eligible_for_authority_update=True)
        )

        funding_programme = await funding_programmes.get(FundingProgrammeCode("ATF3"))

        assert (
            funding_programme
            and funding_programme.code == FundingProgrammeCode("ATF3")
            and funding_programme.is_eligible_for_authority_update
        )

    async def test_get_when_not_found(self, funding_programmes: MemoryFundingProgrammeRepository) -> None:
        funding_programme = await funding_programmes.get(FundingProgrammeCode("ATF3"))

        assert not funding_programme

    async def test_get_all(self, funding_programmes: MemoryFundingProgrammeRepository) -> None:
        funding_programme1 = FundingProgramme(code=FundingProgrammeCode("ATF3"), is_eligible_for_authority_update=True)
        await funding_programmes.add(funding_programme1)
        funding_programme2 = FundingProgramme(code=FundingProgrammeCode("ATF4"), is_eligible_for_authority_update=True)
        await funding_programmes.add(funding_programme2)

        all_funding_programmes = await funding_programmes.get_all()

        assert all_funding_programmes == [funding_programme1, funding_programme2]

    async def test_get_all_orders_by_code(self, funding_programmes: MemoryFundingProgrammeRepository) -> None:
        funding_programme1 = FundingProgramme(code=FundingProgrammeCode("ATF3"))
        funding_programme2 = FundingProgramme(code=FundingProgrammeCode("ATF4"))
        await funding_programmes.add(funding_programme2)
        await funding_programmes.add(funding_programme1)

        all_funding_programmes = await funding_programmes.get_all()

        assert all_funding_programmes == [funding_programme1, funding_programme2]

    async def test_get_all_when_none(self, funding_programmes: MemoryFundingProgrammeRepository) -> None:
        all_funding_programmes = await funding_programmes.get_all()

        assert all_funding_programmes == []

    async def test_exists(self, funding_programmes: MemoryFundingProgrammeRepository) -> None:
        await funding_programmes.add(FundingProgramme(code=FundingProgrammeCode("ATF3")))

        exists = await funding_programmes.exists(FundingProgrammeCode("ATF3"))

        assert exists

    async def test_exists_when_not_found(self, funding_programmes: MemoryFundingProgrammeRepository) -> None:
        exists = await funding_programmes.exists(FundingProgrammeCode("ATF3"))

        assert not exists

    async def test_exists_all(self, funding_programmes: MemoryFundingProgrammeRepository) -> None:
        await funding_programmes.add(FundingProgramme(code=FundingProgrammeCode("ATF3")))
        await funding_programmes.add(FundingProgramme(code=FundingProgrammeCode("ATF4")))

        exists = await funding_programmes.exists_all([FundingProgrammeCode("ATF3"), FundingProgrammeCode("ATF4")])

        assert exists

    async def test_exists_all_when_some_found(self, funding_programmes: MemoryFundingProgrammeRepository) -> None:
        await funding_programmes.add(FundingProgramme(code=FundingProgrammeCode("ATF3")))

        exists = await funding_programmes.exists_all([FundingProgrammeCode("ATF3"), FundingProgrammeCode("ATF4")])

        assert not exists

    async def test_exists_all_when_none_found(self, funding_programmes: MemoryFundingProgrammeRepository) -> None:
        exists = await funding_programmes.exists_all([FundingProgrammeCode("ATF3"), FundingProgrammeCode("ATF4")])

        assert not exists
