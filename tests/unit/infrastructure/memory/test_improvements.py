from datetime import UTC, datetime

import pytest

from ate_api.domain.authorities import AuthorityAbbreviation
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.improvements.improvements import Improvement, ImprovementReference
from ate_api.domain.improvements.overviews import ImprovementOverview
from tests.unit.infrastructure.memory.improvements import MemoryImprovementRepository


class TestMemoryImprovementRepository:
    @pytest.fixture(name="improvements")
    def improvements_fixture(self) -> MemoryImprovementRepository:
        return MemoryImprovementRepository()

    async def test_add(self, improvements: MemoryImprovementRepository) -> None:
        overview = ImprovementOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            name="Wirral Package",
            funding_managed_by=AuthorityAbbreviation("LIV"),
            data_source=DataSource.AUTHORITY_UPDATE,
        )

        await improvements.add(Improvement(reference=ImprovementReference("IMP00001"), overview=overview))

        improvement = await improvements.get(ImprovementReference("IMP00001"))
        assert (
            improvement
            and improvement.reference == ImprovementReference("IMP00001")
            and improvement.overview == overview
        )

    async def test_get(self, improvements: MemoryImprovementRepository) -> None:
        overview = ImprovementOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            name="Wirral Package",
            funding_managed_by=AuthorityAbbreviation("LIV"),
            data_source=DataSource.AUTHORITY_UPDATE,
        )
        await improvements.add(Improvement(reference=ImprovementReference("IMP00001"), overview=overview))

        improvement = await improvements.get(ImprovementReference("IMP00001"))

        assert (
            improvement
            and improvement.reference == ImprovementReference("IMP00001")
            and improvement.overview == overview
        )

    async def test_get_when_not_found(self, improvements: MemoryImprovementRepository) -> None:
        improvement = await improvements.get(ImprovementReference("IMP00001"))

        assert not improvement
