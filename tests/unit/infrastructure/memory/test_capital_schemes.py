from datetime import date, datetime

import pytest

from ate_api.domain.authorities import AuthorityAbbreviation
from ate_api.domain.capital_schemes.bid_statuses import BidStatus, CapitalSchemeBidStatusDetails
from ate_api.domain.capital_schemes.capital_schemes import CapitalScheme, CapitalSchemeReference
from ate_api.domain.capital_schemes.milestones import CapitalSchemeMilestone, Milestone
from ate_api.domain.capital_schemes.overviews import CapitalSchemeOverview, CapitalSchemeType
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.funding_programmes import FundingProgrammeCode
from ate_api.domain.observation_types import ObservationType
from tests.unit.domain.dummies import dummy_bid_status_details
from tests.unit.infrastructure.memory.capital_schemes import MemoryCapitalSchemeRepository


class TestMemoryCapitalSchemeRepository:
    @pytest.fixture(name="capital_schemes")
    def capital_schemes_fixture(self) -> MemoryCapitalSchemeRepository:
        return MemoryCapitalSchemeRepository()

    def test_add(self, capital_schemes: MemoryCapitalSchemeRepository) -> None:
        overview = CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1)),
            name="Wirral Package",
            bid_submitting_authority=AuthorityAbbreviation("LIV"),
            funding_programme=FundingProgrammeCode("ATF3"),
            type=CapitalSchemeType.CONSTRUCTION,
        )
        bid_status_details = CapitalSchemeBidStatusDetails(
            effective_date=DateTimeRange(datetime(2020, 2, 1)),
            bid_status=BidStatus.FUNDED,
        )

        capital_schemes.add(
            CapitalScheme(
                reference=CapitalSchemeReference("ATE00001"), overview=overview, bid_status_details=bid_status_details
            )
        )

        capital_scheme = capital_schemes.get(CapitalSchemeReference("ATE00001"))
        assert (
            capital_scheme
            and capital_scheme.reference == CapitalSchemeReference("ATE00001")
            and capital_scheme.overview == overview
            and capital_scheme.bid_status_details == bid_status_details
        )

    def test_get(self, capital_schemes: MemoryCapitalSchemeRepository) -> None:
        overview = CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1)),
            name="Wirral Package",
            bid_submitting_authority=AuthorityAbbreviation("LIV"),
            funding_programme=FundingProgrammeCode("ATF3"),
            type=CapitalSchemeType.CONSTRUCTION,
        )
        bid_status_details = CapitalSchemeBidStatusDetails(
            effective_date=DateTimeRange(datetime(2020, 2, 1)),
            bid_status=BidStatus.FUNDED,
        )

        capital_schemes.add(
            CapitalScheme(
                reference=CapitalSchemeReference("ATE00001"), overview=overview, bid_status_details=bid_status_details
            )
        )

        capital_scheme = capital_schemes.get(CapitalSchemeReference("ATE00001"))

        assert (
            capital_scheme
            and capital_scheme.reference == CapitalSchemeReference("ATE00001")
            and capital_scheme.overview == overview
            and capital_scheme.bid_status_details == bid_status_details
        )

    def test_get_when_not_found(self, capital_schemes: MemoryCapitalSchemeRepository) -> None:
        capital_scheme = capital_schemes.get(CapitalSchemeReference("ATE00001"))

        assert not capital_scheme

    def test_get_references_by_bid_submitting_authority(self, capital_schemes: MemoryCapitalSchemeRepository) -> None:
        capital_schemes.add(
            CapitalScheme(
                reference=CapitalSchemeReference("ATE00001"),
                overview=CapitalSchemeOverview(
                    effective_date=DateTimeRange(datetime(2020, 1, 1)),
                    name="Wirral Package",
                    bid_submitting_authority=AuthorityAbbreviation("LIV"),
                    funding_programme=FundingProgrammeCode("ATF3"),
                    type=CapitalSchemeType.CONSTRUCTION,
                ),
                bid_status_details=dummy_bid_status_details(),
            )
        )
        capital_schemes.add(
            CapitalScheme(
                reference=CapitalSchemeReference("ATE00002"),
                overview=CapitalSchemeOverview(
                    effective_date=DateTimeRange(datetime(2020, 1, 1)),
                    name="School Streets",
                    bid_submitting_authority=AuthorityAbbreviation("LIV"),
                    funding_programme=FundingProgrammeCode("ATF3"),
                    type=CapitalSchemeType.CONSTRUCTION,
                ),
                bid_status_details=dummy_bid_status_details(),
            )
        )
        capital_schemes.add(
            CapitalScheme(
                reference=CapitalSchemeReference("ATE00003"),
                overview=CapitalSchemeOverview(
                    effective_date=DateTimeRange(datetime(2020, 1, 1)),
                    name="Hospital Fields Road",
                    bid_submitting_authority=AuthorityAbbreviation("WYO"),
                    funding_programme=FundingProgrammeCode("ATF3"),
                    type=CapitalSchemeType.CONSTRUCTION,
                ),
                bid_status_details=dummy_bid_status_details(),
            )
        )

        references = capital_schemes.get_references_by_bid_submitting_authority(AuthorityAbbreviation("LIV"))

        assert references == [CapitalSchemeReference("ATE00001"), CapitalSchemeReference("ATE00002")]

    def test_get_references_by_bid_submitting_authority_filters_by_bid_status(
        self, capital_schemes: MemoryCapitalSchemeRepository
    ) -> None:
        capital_schemes.add(
            CapitalScheme(
                reference=CapitalSchemeReference("ATE00001"),
                overview=CapitalSchemeOverview(
                    effective_date=DateTimeRange(datetime(2020, 1, 1)),
                    name="Wirral Package",
                    bid_submitting_authority=AuthorityAbbreviation("LIV"),
                    funding_programme=FundingProgrammeCode("ATF3"),
                    type=CapitalSchemeType.CONSTRUCTION,
                ),
                bid_status_details=CapitalSchemeBidStatusDetails(
                    effective_date=DateTimeRange(datetime(2020, 1, 1)),
                    bid_status=BidStatus.FUNDED,
                ),
            )
        )
        capital_schemes.add(
            CapitalScheme(
                reference=CapitalSchemeReference("ATE00002"),
                overview=CapitalSchemeOverview(
                    effective_date=DateTimeRange(datetime(2020, 1, 1)),
                    name="School Streets",
                    bid_submitting_authority=AuthorityAbbreviation("LIV"),
                    funding_programme=FundingProgrammeCode("ATF3"),
                    type=CapitalSchemeType.CONSTRUCTION,
                ),
                bid_status_details=CapitalSchemeBidStatusDetails(
                    effective_date=DateTimeRange(datetime(2020, 1, 1)),
                    bid_status=BidStatus.NOT_FUNDED,
                ),
            )
        )

        references = capital_schemes.get_references_by_bid_submitting_authority(
            AuthorityAbbreviation("LIV"), bid_status=BidStatus.FUNDED
        )

        assert references == [CapitalSchemeReference("ATE00001")]

    def test_get_references_by_bid_submitting_authority_filters_by_current_milestone(
        self, capital_schemes: MemoryCapitalSchemeRepository
    ) -> None:
        capital_scheme1 = CapitalScheme(
            reference=CapitalSchemeReference("ATE00001"),
            overview=CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1)),
                name="Wirral Package",
                bid_submitting_authority=AuthorityAbbreviation("LIV"),
                funding_programme=FundingProgrammeCode("ATF3"),
                type=CapitalSchemeType.CONSTRUCTION,
            ),
            bid_status_details=dummy_bid_status_details(),
        )
        capital_scheme1.change_milestone(
            CapitalSchemeMilestone(
                effective_date=DateTimeRange(datetime(2020, 1, 1)),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 2, 1),
            )
        )
        capital_schemes.add(capital_scheme1)
        capital_scheme2 = CapitalScheme(
            reference=CapitalSchemeReference("ATE00002"),
            overview=CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1)),
                name="School Streets",
                bid_submitting_authority=AuthorityAbbreviation("LIV"),
                funding_programme=FundingProgrammeCode("ATF3"),
                type=CapitalSchemeType.CONSTRUCTION,
            ),
            bid_status_details=dummy_bid_status_details(),
        )
        capital_scheme2.change_milestone(
            CapitalSchemeMilestone(
                effective_date=DateTimeRange(datetime(2020, 1, 1)),
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 3, 1),
            )
        )
        capital_schemes.add(capital_scheme2)
        capital_scheme3 = CapitalScheme(
            reference=CapitalSchemeReference("ATE00003"),
            overview=CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1)),
                name="Hospital Fields Road",
                bid_submitting_authority=AuthorityAbbreviation("LIV"),
                funding_programme=FundingProgrammeCode("ATF3"),
                type=CapitalSchemeType.CONSTRUCTION,
            ),
            bid_status_details=dummy_bid_status_details(),
        )
        capital_scheme3.change_milestone(
            CapitalSchemeMilestone(
                effective_date=DateTimeRange(datetime(2020, 1, 1)),
                milestone=Milestone.CONSTRUCTION_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 4, 1),
            )
        )
        capital_schemes.add(capital_scheme3)

        references = capital_schemes.get_references_by_bid_submitting_authority(
            AuthorityAbbreviation("LIV"),
            current_milestones=[Milestone.DETAILED_DESIGN_COMPLETED, Milestone.CONSTRUCTION_STARTED],
        )

        assert references == [CapitalSchemeReference("ATE00001"), CapitalSchemeReference("ATE00002")]

    def test_get_references_by_bid_submitting_authority_orders_by_reference(
        self, capital_schemes: MemoryCapitalSchemeRepository
    ) -> None:
        capital_schemes.add(
            CapitalScheme(
                reference=CapitalSchemeReference("ATE00002"),
                overview=CapitalSchemeOverview(
                    effective_date=DateTimeRange(datetime(2020, 1, 1)),
                    name="Wirral Package",
                    bid_submitting_authority=AuthorityAbbreviation("LIV"),
                    funding_programme=FundingProgrammeCode("ATF3"),
                    type=CapitalSchemeType.CONSTRUCTION,
                ),
                bid_status_details=dummy_bid_status_details(),
            )
        )
        capital_schemes.add(
            CapitalScheme(
                reference=CapitalSchemeReference("ATE00001"),
                overview=CapitalSchemeOverview(
                    effective_date=DateTimeRange(datetime(2020, 1, 1)),
                    name="Wirral Package",
                    bid_submitting_authority=AuthorityAbbreviation("LIV"),
                    funding_programme=FundingProgrammeCode("ATF3"),
                    type=CapitalSchemeType.CONSTRUCTION,
                ),
                bid_status_details=dummy_bid_status_details(),
            )
        )

        references = capital_schemes.get_references_by_bid_submitting_authority(AuthorityAbbreviation("LIV"))

        assert references == [CapitalSchemeReference("ATE00001"), CapitalSchemeReference("ATE00002")]

    def test_get_references_by_bid_submitting_authority_when_none(
        self, capital_schemes: MemoryCapitalSchemeRepository
    ) -> None:
        references = capital_schemes.get_references_by_bid_submitting_authority(AuthorityAbbreviation("LIV"))

        assert not references
