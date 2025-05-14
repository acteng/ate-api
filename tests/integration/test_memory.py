from datetime import datetime

import pytest

from ate_api.domain.authorities import Authority
from ate_api.domain.capital_schemes.capital_schemes import (
    CapitalScheme,
    CapitalSchemeBidStatus,
    CapitalSchemeBidStatusDetails,
    CapitalSchemeOverview,
    CapitalSchemeType,
)
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.funding_programmes import FundingProgramme
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
        funding_programmes.add(FundingProgramme(code="ATF3"))

        funding_programme = funding_programmes.get("ATF3")
        assert funding_programme and funding_programme.code == "ATF3"

    def test_get(self, funding_programmes: MemoryFundingProgrammeRepository) -> None:
        funding_programmes.add(FundingProgramme(code="ATF3"))

        funding_programme = funding_programmes.get("ATF3")

        assert funding_programme and funding_programme.code == "ATF3"

    def test_get_when_not_found(self, funding_programmes: MemoryFundingProgrammeRepository) -> None:
        funding_programme = funding_programmes.get("ATF3")

        assert not funding_programme


class TestMemoryAuthorityRepository:
    @pytest.fixture(name="authorities")
    def authorities_fixture(self) -> MemoryAuthorityRepository:
        return MemoryAuthorityRepository()

    def test_add(self, authorities: MemoryAuthorityRepository) -> None:
        authorities.add(Authority(abbreviation="LIV", full_name="Liverpool City Region Combined Authority"))

        authority = authorities.get("LIV")
        assert (
            authority
            and authority.abbreviation == "LIV"
            and authority.full_name == "Liverpool City Region Combined Authority"
        )

    def test_get(self, authorities: MemoryAuthorityRepository) -> None:
        authorities.add(Authority(abbreviation="LIV", full_name="Liverpool City Region Combined Authority"))

        authority = authorities.get("LIV")

        assert (
            authority
            and authority.abbreviation == "LIV"
            and authority.full_name == "Liverpool City Region Combined Authority"
        )

    def test_get_when_not_found(self, authorities: MemoryAuthorityRepository) -> None:
        authority = authorities.get("LIV")

        assert not authority


class TestMemoryCapitalSchemeRepository:
    @pytest.fixture(name="capital_schemes")
    def capital_schemes_fixture(self) -> MemoryCapitalSchemeRepository:
        return MemoryCapitalSchemeRepository()

    def test_add(self, capital_schemes: MemoryCapitalSchemeRepository) -> None:
        overview = CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1)),
            name="Wirral Package",
            bid_submitting_authority="LIV",
            funding_programme="ATF3",
            type=CapitalSchemeType.CONSTRUCTION,
        )
        bid_status_details = CapitalSchemeBidStatusDetails(
            effective_date=DateTimeRange(datetime(2020, 2, 1)),
            bid_status=CapitalSchemeBidStatus.FUNDED,
        )

        capital_schemes.add(
            CapitalScheme(reference="ATE00001", overview=overview, bid_status_details=bid_status_details)
        )

        capital_scheme = capital_schemes.get("ATE00001")
        assert (
            capital_scheme
            and capital_scheme.reference == "ATE00001"
            and capital_scheme.overview == overview
            and capital_scheme.bid_status_details == bid_status_details
        )

    def test_get(self, capital_schemes: MemoryCapitalSchemeRepository) -> None:
        overview = CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1)),
            name="Wirral Package",
            bid_submitting_authority="LIV",
            funding_programme="ATF3",
            type=CapitalSchemeType.CONSTRUCTION,
        )
        bid_status_details = CapitalSchemeBidStatusDetails(
            effective_date=DateTimeRange(datetime(2020, 2, 1)),
            bid_status=CapitalSchemeBidStatus.FUNDED,
        )

        capital_schemes.add(
            CapitalScheme(reference="ATE00001", overview=overview, bid_status_details=bid_status_details)
        )

        capital_scheme = capital_schemes.get("ATE00001")

        assert (
            capital_scheme
            and capital_scheme.reference == "ATE00001"
            and capital_scheme.overview == overview
            and capital_scheme.bid_status_details == bid_status_details
        )

    def test_get_when_not_found(self, capital_schemes: MemoryCapitalSchemeRepository) -> None:
        capital_scheme = capital_schemes.get("ATE00001")

        assert not capital_scheme

    def test_get_references_by_bid_submitting_authority(self, capital_schemes: MemoryCapitalSchemeRepository) -> None:
        capital_schemes.add(
            CapitalScheme(
                reference="ATE00001",
                overview=CapitalSchemeOverview(
                    effective_date=DateTimeRange(datetime(2020, 1, 1)),
                    name="Wirral Package",
                    bid_submitting_authority="LIV",
                    funding_programme="ATF3",
                    type=CapitalSchemeType.CONSTRUCTION,
                ),
                bid_status_details=dummy_bid_status_details(),
            )
        )
        capital_schemes.add(
            CapitalScheme(
                reference="ATE00002",
                overview=CapitalSchemeOverview(
                    effective_date=DateTimeRange(datetime(2020, 1, 1)),
                    name="School Streets",
                    bid_submitting_authority="LIV",
                    funding_programme="ATF3",
                    type=CapitalSchemeType.CONSTRUCTION,
                ),
                bid_status_details=dummy_bid_status_details(),
            )
        )
        capital_schemes.add(
            CapitalScheme(
                reference="ATE00003",
                overview=CapitalSchemeOverview(
                    effective_date=DateTimeRange(datetime(2020, 1, 1)),
                    name="Hospital Fields Road",
                    bid_submitting_authority="WYO",
                    funding_programme="ATF3",
                    type=CapitalSchemeType.CONSTRUCTION,
                ),
                bid_status_details=dummy_bid_status_details(),
            )
        )

        references = capital_schemes.get_references_by_bid_submitting_authority("LIV")

        assert references == ["ATE00001", "ATE00002"]

    def test_get_references_by_bid_submitting_authority_orders_by_reference(
        self, capital_schemes: MemoryCapitalSchemeRepository
    ) -> None:
        capital_schemes.add(
            CapitalScheme(
                reference="ATE00002",
                overview=CapitalSchemeOverview(
                    effective_date=DateTimeRange(datetime(2020, 1, 1)),
                    name="Wirral Package",
                    bid_submitting_authority="LIV",
                    funding_programme="ATF3",
                    type=CapitalSchemeType.CONSTRUCTION,
                ),
                bid_status_details=dummy_bid_status_details(),
            )
        )
        capital_schemes.add(
            CapitalScheme(
                reference="ATE00001",
                overview=CapitalSchemeOverview(
                    effective_date=DateTimeRange(datetime(2020, 1, 1)),
                    name="Wirral Package",
                    bid_submitting_authority="LIV",
                    funding_programme="ATF3",
                    type=CapitalSchemeType.CONSTRUCTION,
                ),
                bid_status_details=dummy_bid_status_details(),
            )
        )

        references = capital_schemes.get_references_by_bid_submitting_authority("LIV")

        assert references == ["ATE00001", "ATE00002"]
