from datetime import UTC, date, datetime

import pytest

from ate_api.domain.authorities import AuthorityAbbreviation
from ate_api.domain.capital_scheme_milestones import (
    CapitalSchemeMilestone,
    CapitalSchemeMilestones,
    CapitalSchemeMilestonesRepository,
    Milestone,
)
from ate_api.domain.capital_schemes.authority_reviews import CapitalSchemeAuthorityReview
from ate_api.domain.capital_schemes.bid_statuses import BidStatus, CapitalSchemeBidStatusDetails
from ate_api.domain.capital_schemes.capital_scheme_repositories import CapitalSchemeItem
from ate_api.domain.capital_schemes.capital_schemes import CapitalScheme, CapitalSchemeReference
from ate_api.domain.capital_schemes.overviews import CapitalSchemeOverview, CapitalSchemeType
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.funding_programmes import FundingProgrammeCode
from ate_api.domain.observation_types import ObservationType
from tests.unit.domain.dummies import dummy_bid_status_details, dummy_overview
from tests.unit.infrastructure.memory.capital_scheme_milestones import MemoryCapitalSchemeMilestonesRepository
from tests.unit.infrastructure.memory.capital_schemes import MemoryCapitalSchemeRepository


class TestMemoryCapitalSchemeRepository:
    @pytest.fixture(name="capital_scheme_milestones")
    def capital_scheme_milestones_fixture(self) -> CapitalSchemeMilestonesRepository:
        return MemoryCapitalSchemeMilestonesRepository()

    @pytest.fixture(name="capital_schemes")
    def capital_schemes_fixture(
        self, capital_scheme_milestones: MemoryCapitalSchemeMilestonesRepository
    ) -> MemoryCapitalSchemeRepository:
        return MemoryCapitalSchemeRepository(capital_scheme_milestones)

    async def test_add(self, capital_schemes: MemoryCapitalSchemeRepository) -> None:
        overview = CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            name="Wirral Package",
            bid_submitting_authority=AuthorityAbbreviation("LIV"),
            funding_programme=FundingProgrammeCode("ATF3"),
            type=CapitalSchemeType.CONSTRUCTION,
        )
        bid_status_details = CapitalSchemeBidStatusDetails(
            effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)), bid_status=BidStatus.FUNDED
        )

        await capital_schemes.add(
            CapitalScheme(
                reference=CapitalSchemeReference("ATE00001"), overview=overview, bid_status_details=bid_status_details
            )
        )

        capital_scheme = await capital_schemes.get(CapitalSchemeReference("ATE00001"))
        assert (
            capital_scheme
            and capital_scheme.reference == CapitalSchemeReference("ATE00001")
            and capital_scheme.overview == overview
            and capital_scheme.bid_status_details == bid_status_details
        )

    async def test_get(self, capital_schemes: MemoryCapitalSchemeRepository) -> None:
        overview = CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            name="Wirral Package",
            bid_submitting_authority=AuthorityAbbreviation("LIV"),
            funding_programme=FundingProgrammeCode("ATF3"),
            type=CapitalSchemeType.CONSTRUCTION,
        )
        bid_status_details = CapitalSchemeBidStatusDetails(
            effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)), bid_status=BidStatus.FUNDED
        )
        await capital_schemes.add(
            CapitalScheme(
                reference=CapitalSchemeReference("ATE00001"), overview=overview, bid_status_details=bid_status_details
            )
        )

        capital_scheme = await capital_schemes.get(CapitalSchemeReference("ATE00001"))

        assert (
            capital_scheme
            and capital_scheme.reference == CapitalSchemeReference("ATE00001")
            and capital_scheme.overview == overview
            and capital_scheme.bid_status_details == bid_status_details
        )

    async def test_get_when_not_found(self, capital_schemes: MemoryCapitalSchemeRepository) -> None:
        capital_scheme = await capital_schemes.get(CapitalSchemeReference("ATE00001"))

        assert not capital_scheme

    async def test_get_items_by_bid_submitting_authority(self, capital_schemes: MemoryCapitalSchemeRepository) -> None:
        await capital_schemes.add(
            CapitalScheme(
                reference=CapitalSchemeReference("ATE00001"),
                overview=CapitalSchemeOverview(
                    effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                    name="Wirral Package",
                    bid_submitting_authority=AuthorityAbbreviation("LIV"),
                    funding_programme=FundingProgrammeCode("ATF3"),
                    type=CapitalSchemeType.CONSTRUCTION,
                ),
                bid_status_details=dummy_bid_status_details(),
            )
        )
        await capital_schemes.add(
            CapitalScheme(
                reference=CapitalSchemeReference("ATE00002"),
                overview=CapitalSchemeOverview(
                    effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                    name="School Streets",
                    bid_submitting_authority=AuthorityAbbreviation("LIV"),
                    funding_programme=FundingProgrammeCode("ATF3"),
                    type=CapitalSchemeType.CONSTRUCTION,
                ),
                bid_status_details=dummy_bid_status_details(),
            )
        )
        await capital_schemes.add(
            CapitalScheme(
                reference=CapitalSchemeReference("ATE00003"),
                overview=CapitalSchemeOverview(
                    effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                    name="Hospital Fields Road",
                    bid_submitting_authority=AuthorityAbbreviation("WYO"),
                    funding_programme=FundingProgrammeCode("ATF3"),
                    type=CapitalSchemeType.CONSTRUCTION,
                ),
                bid_status_details=dummy_bid_status_details(),
            )
        )

        capital_scheme_items = await capital_schemes.get_items_by_bid_submitting_authority(AuthorityAbbreviation("LIV"))

        assert capital_scheme_items == [
            CapitalSchemeItem(reference=CapitalSchemeReference("ATE00001"), name="Wirral Package"),
            CapitalSchemeItem(reference=CapitalSchemeReference("ATE00002"), name="School Streets"),
        ]

    async def test_get_items_by_bid_submitting_authority_filters_by_funding_programme(
        self, capital_schemes: MemoryCapitalSchemeRepository
    ) -> None:
        await capital_schemes.add(
            CapitalScheme(
                reference=CapitalSchemeReference("ATE00001"),
                overview=CapitalSchemeOverview(
                    effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                    name="Wirral Package",
                    bid_submitting_authority=AuthorityAbbreviation("LIV"),
                    funding_programme=FundingProgrammeCode("ATF3"),
                    type=CapitalSchemeType.CONSTRUCTION,
                ),
                bid_status_details=dummy_bid_status_details(),
            )
        )
        await capital_schemes.add(
            CapitalScheme(
                reference=CapitalSchemeReference("ATE00002"),
                overview=CapitalSchemeOverview(
                    effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                    name="School Streets",
                    bid_submitting_authority=AuthorityAbbreviation("LIV"),
                    funding_programme=FundingProgrammeCode("ATF4"),
                    type=CapitalSchemeType.CONSTRUCTION,
                ),
                bid_status_details=dummy_bid_status_details(),
            )
        )
        await capital_schemes.add(
            CapitalScheme(
                reference=CapitalSchemeReference("ATE00003"),
                overview=CapitalSchemeOverview(
                    effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                    name="Hospital Fields Road",
                    bid_submitting_authority=AuthorityAbbreviation("LIV"),
                    funding_programme=FundingProgrammeCode("ATF5"),
                    type=CapitalSchemeType.CONSTRUCTION,
                ),
                bid_status_details=dummy_bid_status_details(),
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

    async def test_get_items_by_bid_submitting_authority_filters_by_bid_status(
        self, capital_schemes: MemoryCapitalSchemeRepository
    ) -> None:
        await capital_schemes.add(
            CapitalScheme(
                reference=CapitalSchemeReference("ATE00001"),
                overview=CapitalSchemeOverview(
                    effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                    name="Wirral Package",
                    bid_submitting_authority=AuthorityAbbreviation("LIV"),
                    funding_programme=FundingProgrammeCode("ATF3"),
                    type=CapitalSchemeType.CONSTRUCTION,
                ),
                bid_status_details=CapitalSchemeBidStatusDetails(
                    effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)), bid_status=BidStatus.FUNDED
                ),
            )
        )
        await capital_schemes.add(
            CapitalScheme(
                reference=CapitalSchemeReference("ATE00002"),
                overview=CapitalSchemeOverview(
                    effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                    name="School Streets",
                    bid_submitting_authority=AuthorityAbbreviation("LIV"),
                    funding_programme=FundingProgrammeCode("ATF3"),
                    type=CapitalSchemeType.CONSTRUCTION,
                ),
                bid_status_details=CapitalSchemeBidStatusDetails(
                    effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)), bid_status=BidStatus.NOT_FUNDED
                ),
            )
        )

        capital_scheme_items = await capital_schemes.get_items_by_bid_submitting_authority(
            AuthorityAbbreviation("LIV"), bid_status=BidStatus.FUNDED
        )

        assert [capital_scheme_item.reference for capital_scheme_item in capital_scheme_items] == [
            CapitalSchemeReference("ATE00001")
        ]

    async def test_get_items_by_bid_submitting_authority_filters_by_current_milestone(
        self,
        capital_schemes: MemoryCapitalSchemeRepository,
        capital_scheme_milestones: MemoryCapitalSchemeMilestonesRepository,
    ) -> None:
        await capital_schemes.add(
            CapitalScheme(
                reference=CapitalSchemeReference("ATE00001"),
                overview=CapitalSchemeOverview(
                    effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                    name="Wirral Package",
                    bid_submitting_authority=AuthorityAbbreviation("LIV"),
                    funding_programme=FundingProgrammeCode("ATF3"),
                    type=CapitalSchemeType.CONSTRUCTION,
                ),
                bid_status_details=dummy_bid_status_details(),
            )
        )
        milestones1 = CapitalSchemeMilestones(capital_scheme=CapitalSchemeReference("ATE00001"))
        milestones1.change_milestone(
            CapitalSchemeMilestone(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 2, 1),
                data_source=DataSource.ATF4_BID,
            )
        )
        await capital_scheme_milestones.add(milestones1)
        await capital_schemes.add(
            CapitalScheme(
                reference=CapitalSchemeReference("ATE00002"),
                overview=CapitalSchemeOverview(
                    effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                    name="School Streets",
                    bid_submitting_authority=AuthorityAbbreviation("LIV"),
                    funding_programme=FundingProgrammeCode("ATF3"),
                    type=CapitalSchemeType.CONSTRUCTION,
                ),
                bid_status_details=dummy_bid_status_details(),
            )
        )
        milestones2 = CapitalSchemeMilestones(capital_scheme=CapitalSchemeReference("ATE00002"))
        milestones2.change_milestone(
            CapitalSchemeMilestone(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 3, 1),
                data_source=DataSource.ATF4_BID,
            )
        )
        await capital_scheme_milestones.add(milestones2)
        await capital_schemes.add(
            CapitalScheme(
                reference=CapitalSchemeReference("ATE00003"),
                overview=CapitalSchemeOverview(
                    effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                    name="Hospital Fields Road",
                    bid_submitting_authority=AuthorityAbbreviation("LIV"),
                    funding_programme=FundingProgrammeCode("ATF3"),
                    type=CapitalSchemeType.CONSTRUCTION,
                ),
                bid_status_details=dummy_bid_status_details(),
            )
        )
        milestones3 = CapitalSchemeMilestones(capital_scheme=CapitalSchemeReference("ATE00003"))
        milestones3.change_milestone(
            CapitalSchemeMilestone(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                milestone=Milestone.CONSTRUCTION_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 4, 1),
                data_source=DataSource.ATF4_BID,
            )
        )
        await capital_scheme_milestones.add(milestones3)

        capital_scheme_items = await capital_schemes.get_items_by_bid_submitting_authority(
            AuthorityAbbreviation("LIV"),
            current_milestones=[Milestone.DETAILED_DESIGN_COMPLETED, Milestone.CONSTRUCTION_STARTED],
        )

        assert [capital_scheme_item.reference for capital_scheme_item in capital_scheme_items] == [
            CapitalSchemeReference("ATE00001"),
            CapitalSchemeReference("ATE00002"),
        ]

    async def test_get_items_by_bid_submitting_authority_filters_by_no_current_milestone(
        self,
        capital_schemes: MemoryCapitalSchemeRepository,
        capital_scheme_milestones: MemoryCapitalSchemeMilestonesRepository,
    ) -> None:
        await capital_schemes.add(
            CapitalScheme(
                reference=CapitalSchemeReference("ATE00001"),
                overview=CapitalSchemeOverview(
                    effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                    name="Wirral Package",
                    bid_submitting_authority=AuthorityAbbreviation("LIV"),
                    funding_programme=FundingProgrammeCode("ATF3"),
                    type=CapitalSchemeType.CONSTRUCTION,
                ),
                bid_status_details=dummy_bid_status_details(),
            )
        )
        await capital_scheme_milestones.add(CapitalSchemeMilestones(capital_scheme=CapitalSchemeReference("ATE00001")))
        await capital_schemes.add(
            CapitalScheme(
                reference=CapitalSchemeReference("ATE00002"),
                overview=CapitalSchemeOverview(
                    effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                    name="School Streets",
                    bid_submitting_authority=AuthorityAbbreviation("LIV"),
                    funding_programme=FundingProgrammeCode("ATF3"),
                    type=CapitalSchemeType.CONSTRUCTION,
                ),
                bid_status_details=dummy_bid_status_details(),
            )
        )
        milestones2 = CapitalSchemeMilestones(capital_scheme=CapitalSchemeReference("ATE00002"))
        milestones2.change_milestone(
            CapitalSchemeMilestone(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 3, 1),
                data_source=DataSource.ATF4_BID,
            )
        )
        await capital_scheme_milestones.add(milestones2)

        capital_scheme_items = await capital_schemes.get_items_by_bid_submitting_authority(
            AuthorityAbbreviation("LIV"), current_milestones=[None]
        )

        assert [capital_scheme_item.reference for capital_scheme_item in capital_scheme_items] == [
            CapitalSchemeReference("ATE00001")
        ]

    async def test_get_items_by_bid_submitting_authority_orders_by_reference(
        self, capital_schemes: MemoryCapitalSchemeRepository
    ) -> None:
        await capital_schemes.add(
            CapitalScheme(
                reference=CapitalSchemeReference("ATE00002"),
                overview=CapitalSchemeOverview(
                    effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                    name="Wirral Package",
                    bid_submitting_authority=AuthorityAbbreviation("LIV"),
                    funding_programme=FundingProgrammeCode("ATF3"),
                    type=CapitalSchemeType.CONSTRUCTION,
                ),
                bid_status_details=dummy_bid_status_details(),
            )
        )
        await capital_schemes.add(
            CapitalScheme(
                reference=CapitalSchemeReference("ATE00001"),
                overview=CapitalSchemeOverview(
                    effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                    name="Wirral Package",
                    bid_submitting_authority=AuthorityAbbreviation("LIV"),
                    funding_programme=FundingProgrammeCode("ATF3"),
                    type=CapitalSchemeType.CONSTRUCTION,
                ),
                bid_status_details=dummy_bid_status_details(),
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

    async def test_update_updates_authority_review(self, capital_schemes: MemoryCapitalSchemeRepository) -> None:
        capital_scheme = CapitalScheme(
            reference=CapitalSchemeReference("ATE00001"),
            overview=dummy_overview(),
            bid_status_details=dummy_bid_status_details(),
        )
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
