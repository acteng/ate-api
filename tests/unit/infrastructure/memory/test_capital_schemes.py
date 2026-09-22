from datetime import UTC, datetime

import pytest

from ate_api.domain.authorities import AuthorityAbbreviation
from ate_api.domain.capital_schemes.authority_reviews import CapitalSchemeAuthorityReview
from ate_api.domain.capital_schemes.capital_scheme_repositories import CapitalSchemeItem
from ate_api.domain.capital_schemes.capital_schemes import CapitalScheme, CapitalSchemeReference
from ate_api.domain.capital_schemes.overviews import CapitalSchemeOverview, CapitalSchemeType
from ate_api.domain.capital_schemes.statuses import CapitalSchemeStatus, Status
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.funding_programmes import FundingProgrammeCode
from ate_api.domain.improvements.improvements import Improvement, ImprovementReference, ImprovementRepository
from tests.unit.domain.builders import build_capital_scheme, build_capital_scheme_overview, build_improvement_overview
from tests.unit.infrastructure.memory.capital_schemes import MemoryCapitalSchemeRepository
from tests.unit.infrastructure.memory.improvements import MemoryImprovementRepository


class TestMemoryCapitalSchemeRepository:
    @pytest.fixture(name="improvements")
    def improvements_fixture(self) -> ImprovementRepository:
        return MemoryImprovementRepository()

    @pytest.fixture(name="capital_schemes")
    def capital_schemes_fixture(self, improvements: ImprovementRepository) -> MemoryCapitalSchemeRepository:
        return MemoryCapitalSchemeRepository(improvements)

    async def test_add(self, capital_schemes: MemoryCapitalSchemeRepository) -> None:
        overview = CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            name="Wirral Package",
            bid_submitting_authority=AuthorityAbbreviation("LIV"),
            funding_programme=FundingProgrammeCode("ATF3"),
            improvement=ImprovementReference("IMP00001"),
            type=CapitalSchemeType.CONSTRUCTION,
        )
        status = CapitalSchemeStatus(
            effective_date=DateTimeRange(datetime(2020, 3, 1, tzinfo=UTC)), status=Status.ACTIVE
        )

        await capital_schemes.add(
            CapitalScheme(reference=CapitalSchemeReference("ATE00001"), overview=overview, status=status)
        )

        capital_scheme = await capital_schemes.get(CapitalSchemeReference("ATE00001"))
        assert (
            capital_scheme
            and capital_scheme.reference == CapitalSchemeReference("ATE00001")
            and capital_scheme.overview == overview
            and capital_scheme.status == status
        )

    async def test_get(self, capital_schemes: MemoryCapitalSchemeRepository) -> None:
        overview = CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            name="Wirral Package",
            bid_submitting_authority=AuthorityAbbreviation("LIV"),
            funding_programme=FundingProgrammeCode("ATF3"),
            improvement=ImprovementReference("IMP00001"),
            type=CapitalSchemeType.CONSTRUCTION,
        )
        status = CapitalSchemeStatus(
            effective_date=DateTimeRange(datetime(2020, 3, 1, tzinfo=UTC)), status=Status.ACTIVE
        )
        await capital_schemes.add(
            CapitalScheme(reference=CapitalSchemeReference("ATE00001"), overview=overview, status=status)
        )

        capital_scheme = await capital_schemes.get(CapitalSchemeReference("ATE00001"))

        assert (
            capital_scheme
            and capital_scheme.reference == CapitalSchemeReference("ATE00001")
            and capital_scheme.overview == overview
            and capital_scheme.status == status
        )

    async def test_get_when_not_found(self, capital_schemes: MemoryCapitalSchemeRepository) -> None:
        capital_scheme = await capital_schemes.get(CapitalSchemeReference("ATE00001"))

        assert not capital_scheme

    async def test_get_items_by_bid_submitting_authority(self, capital_schemes: MemoryCapitalSchemeRepository) -> None:
        overview1 = CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            name="Wirral Package",
            bid_submitting_authority=AuthorityAbbreviation("LIV"),
            funding_programme=FundingProgrammeCode("ATF3"),
            improvement=ImprovementReference("IMP00001"),
            type=CapitalSchemeType.CONSTRUCTION,
        )
        status1 = CapitalSchemeStatus(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)), status=Status.ACTIVE
        )
        await capital_schemes.add(
            build_capital_scheme(reference=CapitalSchemeReference("ATE00001"), overview=overview1, status=status1)
        )
        overview2 = CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            name="School Streets",
            bid_submitting_authority=AuthorityAbbreviation("LIV"),
            funding_programme=FundingProgrammeCode("ATF3"),
            improvement=ImprovementReference("IMP00001"),
            type=CapitalSchemeType.CONSTRUCTION,
        )
        status2 = CapitalSchemeStatus(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)), status=Status.ACTIVE
        )
        await capital_schemes.add(
            build_capital_scheme(reference=CapitalSchemeReference("ATE00002"), overview=overview2, status=status2)
        )
        await capital_schemes.add(
            build_capital_scheme(
                reference=CapitalSchemeReference("ATE00003"),
                overview=CapitalSchemeOverview(
                    effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                    name="Hospital Fields Road",
                    bid_submitting_authority=AuthorityAbbreviation("WYO"),
                    funding_programme=FundingProgrammeCode("ATF3"),
                    improvement=ImprovementReference("IMP00002"),
                    type=CapitalSchemeType.CONSTRUCTION,
                ),
                status=CapitalSchemeStatus(
                    effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)), status=Status.ACTIVE
                ),
            )
        )

        capital_scheme_items = await capital_schemes.get_items_by_bid_submitting_authority(AuthorityAbbreviation("LIV"))

        assert capital_scheme_items == [
            CapitalSchemeItem(
                reference=CapitalSchemeReference("ATE00001"), overview=overview1, status=status1, authority_review=None
            ),
            CapitalSchemeItem(
                reference=CapitalSchemeReference("ATE00002"), overview=overview2, status=status2, authority_review=None
            ),
        ]

    async def test_get_items_by_bid_submitting_authority_fetches_authority_review(
        self, capital_schemes: MemoryCapitalSchemeRepository
    ) -> None:
        authority_review = CapitalSchemeAuthorityReview(
            review_date=datetime(2020, 2, 1, tzinfo=UTC), data_source=DataSource.AUTHORITY_UPDATE
        )
        capital_scheme = build_capital_scheme(
            reference=CapitalSchemeReference("ATE00001"),
            overview=build_capital_scheme_overview(bid_submitting_authority=AuthorityAbbreviation("LIV")),
        )
        capital_scheme.perform_authority_review(authority_review)
        await capital_schemes.add(capital_scheme)

        capital_scheme_items = await capital_schemes.get_items_by_bid_submitting_authority(AuthorityAbbreviation("LIV"))

        assert [capital_scheme_item.authority_review for capital_scheme_item in capital_scheme_items] == [
            authority_review
        ]

    async def test_get_items_by_bid_submitting_authority_filters_by_funding_programme(
        self, capital_schemes: MemoryCapitalSchemeRepository
    ) -> None:
        await capital_schemes.add(
            build_capital_scheme(
                reference=CapitalSchemeReference("ATE00001"),
                overview=build_capital_scheme_overview(
                    bid_submitting_authority=AuthorityAbbreviation("LIV"),
                    funding_programme=FundingProgrammeCode("ATF3"),
                ),
            )
        )
        await capital_schemes.add(
            build_capital_scheme(
                reference=CapitalSchemeReference("ATE00002"),
                overview=build_capital_scheme_overview(
                    bid_submitting_authority=AuthorityAbbreviation("LIV"),
                    funding_programme=FundingProgrammeCode("ATF4"),
                ),
            )
        )
        await capital_schemes.add(
            build_capital_scheme(
                reference=CapitalSchemeReference("ATE00003"),
                overview=build_capital_scheme_overview(
                    bid_submitting_authority=AuthorityAbbreviation("LIV"),
                    funding_programme=FundingProgrammeCode("ATF5"),
                ),
            )
        )

        capital_scheme_items = await capital_schemes.get_items_by_bid_submitting_authority(
            AuthorityAbbreviation("LIV"),
            funding_programme_codes=[FundingProgrammeCode("ATF3"), FundingProgrammeCode("ATF4")],
        )

        assert [capital_scheme_item.reference for capital_scheme_item in capital_scheme_items] == [
            CapitalSchemeReference("ATE00001"),
            CapitalSchemeReference("ATE00002"),
        ]

    async def test_get_items_by_bid_submitting_authority_filters_by_status(
        self, capital_schemes: MemoryCapitalSchemeRepository
    ) -> None:
        await capital_schemes.add(
            build_capital_scheme(
                reference=CapitalSchemeReference("ATE00001"),
                overview=build_capital_scheme_overview(bid_submitting_authority=AuthorityAbbreviation("LIV")),
                status=CapitalSchemeStatus(
                    effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)), status=Status.ACTIVE
                ),
            )
        )
        await capital_schemes.add(
            build_capital_scheme(
                reference=CapitalSchemeReference("ATE00002"),
                overview=build_capital_scheme_overview(bid_submitting_authority=AuthorityAbbreviation("LIV")),
                status=CapitalSchemeStatus(
                    effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)), status=Status.PIPELINE
                ),
            )
        )

        capital_scheme_items = await capital_schemes.get_items_by_bid_submitting_authority(
            AuthorityAbbreviation("LIV"), status=Status.ACTIVE
        )

        assert [capital_scheme_item.reference for capital_scheme_item in capital_scheme_items] == [
            CapitalSchemeReference("ATE00001")
        ]

    async def test_get_items_by_bid_submitting_authority_orders_by_reference(
        self, capital_schemes: MemoryCapitalSchemeRepository
    ) -> None:
        await capital_schemes.add(
            build_capital_scheme(
                reference=CapitalSchemeReference("ATE00002"),
                overview=build_capital_scheme_overview(bid_submitting_authority=AuthorityAbbreviation("LIV")),
            )
        )
        await capital_schemes.add(
            build_capital_scheme(
                reference=CapitalSchemeReference("ATE00001"),
                overview=build_capital_scheme_overview(bid_submitting_authority=AuthorityAbbreviation("LIV")),
            )
        )

        capital_scheme_items = await capital_schemes.get_items_by_bid_submitting_authority(AuthorityAbbreviation("LIV"))

        assert [capital_scheme_item.reference for capital_scheme_item in capital_scheme_items] == [
            CapitalSchemeReference("ATE00001"),
            CapitalSchemeReference("ATE00002"),
        ]

    async def test_get_items_by_bid_submitting_authority_when_none(
        self, capital_schemes: MemoryCapitalSchemeRepository
    ) -> None:
        capital_scheme_items = await capital_schemes.get_items_by_bid_submitting_authority(AuthorityAbbreviation("LIV"))

        assert not capital_scheme_items

    async def test_get_items_by_funding_managed_by(
        self, capital_schemes: MemoryCapitalSchemeRepository, improvements: MemoryImprovementRepository
    ) -> None:
        await improvements.add(
            Improvement(
                reference=ImprovementReference("IMP00001"),
                overview=build_improvement_overview(funding_managed_by=AuthorityAbbreviation("LIV")),
            )
        )
        overview1 = CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            name="Wirral Package",
            bid_submitting_authority=AuthorityAbbreviation("LIV"),
            funding_programme=FundingProgrammeCode("ATF3"),
            improvement=ImprovementReference("IMP00001"),
            type=CapitalSchemeType.CONSTRUCTION,
        )
        status1 = CapitalSchemeStatus(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)), status=Status.ACTIVE
        )
        await capital_schemes.add(
            build_capital_scheme(reference=CapitalSchemeReference("ATE00001"), overview=overview1, status=status1)
        )
        overview2 = CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            name="School Streets",
            bid_submitting_authority=AuthorityAbbreviation("LIV"),
            funding_programme=FundingProgrammeCode("ATF3"),
            improvement=ImprovementReference("IMP00001"),
            type=CapitalSchemeType.CONSTRUCTION,
        )
        status2 = CapitalSchemeStatus(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)), status=Status.ACTIVE
        )
        await capital_schemes.add(
            build_capital_scheme(reference=CapitalSchemeReference("ATE00002"), overview=overview2, status=status2)
        )
        await improvements.add(
            Improvement(
                reference=ImprovementReference("IMP00002"),
                overview=build_improvement_overview(funding_managed_by=AuthorityAbbreviation("WYO")),
            )
        )
        await capital_schemes.add(
            build_capital_scheme(
                reference=CapitalSchemeReference("ATE00003"),
                overview=CapitalSchemeOverview(
                    effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                    name="Hospital Fields Road",
                    bid_submitting_authority=AuthorityAbbreviation("WYO"),
                    funding_programme=FundingProgrammeCode("ATF3"),
                    improvement=ImprovementReference("IMP00002"),
                    type=CapitalSchemeType.CONSTRUCTION,
                ),
                status=CapitalSchemeStatus(
                    effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)), status=Status.ACTIVE
                ),
            )
        )

        capital_scheme_items = await capital_schemes.get_items_by_funding_managed_by(AuthorityAbbreviation("LIV"))

        assert capital_scheme_items == [
            CapitalSchemeItem(
                reference=CapitalSchemeReference("ATE00001"), overview=overview1, status=status1, authority_review=None
            ),
            CapitalSchemeItem(
                reference=CapitalSchemeReference("ATE00002"), overview=overview2, status=status2, authority_review=None
            ),
        ]

    async def test_get_items_by_funding_managed_by_fetches_authority_review(
        self,
        capital_schemes: MemoryCapitalSchemeRepository,
        improvements: ImprovementRepository,
    ) -> None:
        await improvements.add(
            Improvement(
                reference=ImprovementReference("IMP00001"),
                overview=build_improvement_overview(funding_managed_by=AuthorityAbbreviation("LIV")),
            )
        )
        authority_review = CapitalSchemeAuthorityReview(
            review_date=datetime(2020, 2, 1, tzinfo=UTC), data_source=DataSource.AUTHORITY_UPDATE
        )
        capital_scheme = build_capital_scheme(
            reference=CapitalSchemeReference("ATE00001"),
            overview=build_capital_scheme_overview(improvement=ImprovementReference("IMP00001")),
        )
        capital_scheme.perform_authority_review(authority_review)
        await capital_schemes.add(capital_scheme)

        capital_scheme_items = await capital_schemes.get_items_by_funding_managed_by(AuthorityAbbreviation("LIV"))

        assert [capital_scheme_item.authority_review for capital_scheme_item in capital_scheme_items] == [
            authority_review
        ]

    async def test_get_items_by_funding_managed_by_filters_by_funding_programme(
        self, capital_schemes: MemoryCapitalSchemeRepository, improvements: MemoryImprovementRepository
    ) -> None:
        await improvements.add(
            Improvement(
                reference=ImprovementReference("IMP00001"),
                overview=build_improvement_overview(funding_managed_by=AuthorityAbbreviation("LIV")),
            )
        )
        await capital_schemes.add(
            build_capital_scheme(
                reference=CapitalSchemeReference("ATE00001"),
                overview=build_capital_scheme_overview(
                    funding_programme=FundingProgrammeCode("ATF3"),
                    improvement=ImprovementReference("IMP00001"),
                ),
            )
        )
        await capital_schemes.add(
            build_capital_scheme(
                reference=CapitalSchemeReference("ATE00002"),
                overview=build_capital_scheme_overview(
                    funding_programme=FundingProgrammeCode("ATF4"),
                    improvement=ImprovementReference("IMP00001"),
                ),
            )
        )
        await capital_schemes.add(
            build_capital_scheme(
                reference=CapitalSchemeReference("ATE00003"),
                overview=build_capital_scheme_overview(
                    funding_programme=FundingProgrammeCode("ATF5"),
                    improvement=ImprovementReference("IMP00001"),
                ),
            )
        )

        capital_scheme_items = await capital_schemes.get_items_by_funding_managed_by(
            AuthorityAbbreviation("LIV"),
            funding_programme_codes=[FundingProgrammeCode("ATF3"), FundingProgrammeCode("ATF4")],
        )

        assert [capital_scheme_item.reference for capital_scheme_item in capital_scheme_items] == [
            CapitalSchemeReference("ATE00001"),
            CapitalSchemeReference("ATE00002"),
        ]

    async def test_get_items_by_funding_managed_by_filters_by_status(
        self, improvements: ImprovementRepository, capital_schemes: MemoryCapitalSchemeRepository
    ) -> None:
        await improvements.add(
            Improvement(
                reference=ImprovementReference("IMP00001"),
                overview=build_improvement_overview(funding_managed_by=AuthorityAbbreviation("LIV")),
            )
        )
        await capital_schemes.add(
            build_capital_scheme(
                reference=CapitalSchemeReference("ATE00001"),
                overview=build_capital_scheme_overview(improvement=ImprovementReference("IMP00001")),
                status=CapitalSchemeStatus(
                    effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)), status=Status.ACTIVE
                ),
            )
        )
        await capital_schemes.add(
            build_capital_scheme(
                reference=CapitalSchemeReference("ATE00002"),
                overview=build_capital_scheme_overview(improvement=ImprovementReference("IMP00001")),
                status=CapitalSchemeStatus(
                    effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)), status=Status.PIPELINE
                ),
            )
        )

        capital_scheme_items = await capital_schemes.get_items_by_funding_managed_by(
            AuthorityAbbreviation("LIV"), status=Status.ACTIVE
        )

        assert [capital_scheme_item.reference for capital_scheme_item in capital_scheme_items] == [
            CapitalSchemeReference("ATE00001")
        ]

    async def test_get_items_by_funding_managed_by_orders_by_reference(
        self, capital_schemes: MemoryCapitalSchemeRepository, improvements: ImprovementRepository
    ) -> None:
        await improvements.add(
            Improvement(
                reference=ImprovementReference("IMP00001"),
                overview=build_improvement_overview(funding_managed_by=AuthorityAbbreviation("LIV")),
            )
        )
        await capital_schemes.add(
            build_capital_scheme(
                reference=CapitalSchemeReference("ATE00002"),
                overview=build_capital_scheme_overview(improvement=ImprovementReference("IMP00001")),
            )
        )
        await capital_schemes.add(
            build_capital_scheme(
                reference=CapitalSchemeReference("ATE00001"),
                overview=build_capital_scheme_overview(improvement=ImprovementReference("IMP00001")),
            )
        )

        capital_scheme_items = await capital_schemes.get_items_by_funding_managed_by(AuthorityAbbreviation("LIV"))

        assert [capital_scheme_item.reference for capital_scheme_item in capital_scheme_items] == [
            CapitalSchemeReference("ATE00001"),
            CapitalSchemeReference("ATE00002"),
        ]

    async def test_get_items_by_funding_managed_by_when_none(
        self, capital_schemes: MemoryCapitalSchemeRepository
    ) -> None:
        capital_scheme_items = await capital_schemes.get_items_by_funding_managed_by(AuthorityAbbreviation("LIV"))

        assert not capital_scheme_items

    async def test_update_updates_authority_review(self, capital_schemes: MemoryCapitalSchemeRepository) -> None:
        capital_scheme = build_capital_scheme(reference=CapitalSchemeReference("ATE00001"))
        capital_scheme.perform_authority_review(
            CapitalSchemeAuthorityReview(
                review_date=datetime(2020, 2, 1, tzinfo=UTC), data_source=DataSource.AUTHORITY_UPDATE
            )
        )
        await capital_schemes.add(capital_scheme)
        authority_review2 = CapitalSchemeAuthorityReview(
            review_date=datetime(2020, 3, 1, tzinfo=UTC), data_source=DataSource.AUTHORITY_UPDATE
        )
        capital_scheme.perform_authority_review(authority_review2)

        await capital_schemes.update(capital_scheme)

        actual_capital_scheme = await capital_schemes.get(CapitalSchemeReference("ATE00001"))
        assert actual_capital_scheme and actual_capital_scheme.authority_review == authority_review2
