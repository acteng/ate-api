import pytest

from ate_api.domain.funding_programmes import FundingProgramme, FundingProgrammeCode
from tests.unit.infrastructure.memory.funding_programmes import MemoryFundingProgrammeRepository


class TestMemoryFundingProgrammeRepository:
    @pytest.fixture(name="funding_programmes")
    def funding_programmes_fixture(self) -> MemoryFundingProgrammeRepository:
        return MemoryFundingProgrammeRepository()

    def test_add(self, funding_programmes: MemoryFundingProgrammeRepository) -> None:
        funding_programmes.add(FundingProgramme(code=FundingProgrammeCode("ATF3")))

        funding_programme = funding_programmes.get(FundingProgrammeCode("ATF3"))
        assert funding_programme and funding_programme.code == FundingProgrammeCode("ATF3")

    def test_get(self, funding_programmes: MemoryFundingProgrammeRepository) -> None:
        funding_programmes.add(FundingProgramme(code=FundingProgrammeCode("ATF3")))

        funding_programme = funding_programmes.get(FundingProgrammeCode("ATF3"))

        assert funding_programme and funding_programme.code == FundingProgrammeCode("ATF3")

    def test_get_when_not_found(self, funding_programmes: MemoryFundingProgrammeRepository) -> None:
        funding_programme = funding_programmes.get(FundingProgrammeCode("ATF3"))

        assert not funding_programme
