from datetime import date, datetime

import pytest

from ate_api.domain.authorities import Authority, AuthorityAbbreviation
from ate_api.domain.capital_schemes.bid_statuses import BidStatus, CapitalSchemeBidStatusDetails
from ate_api.domain.capital_schemes.capital_schemes import CapitalScheme, CapitalSchemeReference
from ate_api.domain.capital_schemes.milestones import CapitalSchemeMilestone, Milestone
from ate_api.domain.capital_schemes.overviews import CapitalSchemeOverview, CapitalSchemeType
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.funding_programmes import FundingProgramme, FundingProgrammeCode
from ate_api.domain.observation_types import ObservationType
from tests.integration.memory import (
    MemoryAuthorityRepository,
    MemoryCapitalSchemeRepository,
    MemoryFundingProgrammeRepository,
)
from tests.unit.domain.dummies import dummy_bid_status_details


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


class TestMemoryAuthorityRepository:
    @pytest.fixture(name="authorities")
    def authorities_fixture(self) -> MemoryAuthorityRepository:
        return MemoryAuthorityRepository()

    def test_add(self, authorities: MemoryAuthorityRepository) -> None:
        authorities.add(
            Authority(abbreviation=AuthorityAbbreviation("LIV"), full_name="Liverpool City Region Combined Authority")
        )

        authority = authorities.get(AuthorityAbbreviation("LIV"))
        assert (
            authority
            and authority.abbreviation == AuthorityAbbreviation("LIV")
            and authority.full_name == "Liverpool City Region Combined Authority"
        )

    def test_get(self, authorities: MemoryAuthorityRepository) -> None:
        authorities.add(
            Authority(abbreviation=AuthorityAbbreviation("LIV"), full_name="Liverpool City Region Combined Authority")
        )

        authority = authorities.get(AuthorityAbbreviation("LIV"))

        assert (
            authority
            and authority.abbreviation == AuthorityAbbreviation("LIV")
            and authority.full_name == "Liverpool City Region Combined Authority"
        )

    def test_get_when_not_found(self, authorities: MemoryAuthorityRepository) -> None:
        authority = authorities.get(AuthorityAbbreviation("LIV"))

        assert not authority


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

        references = capital_schemes.get_references_by_bid_submitting_authority(
            AuthorityAbbreviation("LIV"), current_milestone=Milestone.DETAILED_DESIGN_COMPLETED
        )

        assert references == [CapitalSchemeReference("ATE00001")]

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
