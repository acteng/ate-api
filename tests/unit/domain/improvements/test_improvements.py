from datetime import UTC, datetime

from ate_api.domain.authorities import AuthorityAbbreviation
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.improvements.improvements import Improvement, ImprovementReference
from ate_api.domain.improvements.overviews import ImprovementOverview


class TestImprovementReference:
    def test_create(self) -> None:
        reference = ImprovementReference("IMP00001")

        assert str(reference) == "IMP00001"

    def test_equals(self) -> None:
        reference1 = ImprovementReference("IMP00001")
        reference2 = ImprovementReference("IMP00001")

        equal = reference1 == reference2

        assert equal

    def test_equals_when_different_reference(self) -> None:
        reference1 = ImprovementReference("IMP00001")
        reference2 = ImprovementReference("IMP00002")

        equal = reference1 == reference2

        assert not equal

    def test_equals_when_different_class(self) -> None:
        reference = ImprovementReference("IMP00001")

        equal = reference == "IMP00001"

        assert not equal

    def test_hash(self) -> None:
        reference1 = ImprovementReference("IMP00001")
        reference2 = ImprovementReference("IMP00001")

        assert hash(reference1) == hash(reference2)

    def test_repr(self) -> None:
        reference = ImprovementReference("IMP00001")

        assert repr(reference) == "ImprovementReference('IMP00001')"


class TestImprovement:
    def test_create(self) -> None:
        overview = ImprovementOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            name="Wirral Package",
            funding_managed_by=AuthorityAbbreviation("LIV"),
            data_source=DataSource.AUTHORITY_UPDATE,
        )

        improvement = Improvement(reference=ImprovementReference("IMP00001"), overview=overview)

        assert improvement.reference == ImprovementReference("IMP00001") and improvement.overview == overview
