from datetime import datetime

import pytest

from ate_api.domain.authorities import Authority
from ate_api.domain.capital_schemes import CapitalScheme, CapitalSchemeOverview
from ate_api.domain.dates import DateTimeRange
from tests.integration.memory import (
    MemoryAuthorityRepository,
    MemoryCapitalSchemeRepository,
)


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

    def test_clear(self, authorities: MemoryAuthorityRepository) -> None:
        authorities.add(Authority(abbreviation="LIV", full_name="Liverpool City Region Combined Authority"))

        authorities.clear()

        assert not authorities.get("LIV")

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
        capital_schemes.add(CapitalScheme(reference="ATE00001"))

        capital_scheme = capital_schemes.get("ATE00001")
        assert capital_scheme and capital_scheme.reference == "ATE00001"

    def test_clear(self, capital_schemes: MemoryCapitalSchemeRepository) -> None:
        capital_schemes.add(CapitalScheme(reference="ATE00001"))

        capital_schemes.clear()

        assert not capital_schemes.get("ATE00001")

    def test_get(self, capital_schemes: MemoryCapitalSchemeRepository) -> None:
        capital_schemes.add(CapitalScheme(reference="ATE00001"))

        capital_scheme = capital_schemes.get("ATE00001")

        assert capital_scheme and capital_scheme.reference == "ATE00001"

    def test_get_when_not_found(self, capital_schemes: MemoryCapitalSchemeRepository) -> None:
        capital_scheme = capital_schemes.get("ATE00001")

        assert not capital_scheme

    def test_get_references_by_bid_submitting_authority(self, capital_schemes: MemoryCapitalSchemeRepository) -> None:
        capital_scheme1 = CapitalScheme(reference="ATE00001")
        capital_scheme1.update_overview(
            CapitalSchemeOverview(effective_date=DateTimeRange(datetime(2020, 1, 1)), bid_submitting_authority="LIV")
        )
        capital_schemes.add(capital_scheme1)
        capital_scheme2 = CapitalScheme(reference="ATE00002")
        capital_scheme2.update_overview(
            CapitalSchemeOverview(effective_date=DateTimeRange(datetime(2020, 1, 1)), bid_submitting_authority="LIV")
        )
        capital_schemes.add(capital_scheme2)
        capital_scheme3 = CapitalScheme(reference="ATE00003")
        capital_scheme3.update_overview(
            CapitalSchemeOverview(effective_date=DateTimeRange(datetime(2020, 1, 1)), bid_submitting_authority="WYO")
        )
        capital_schemes.add(capital_scheme3)

        references = capital_schemes.get_references_by_bid_submitting_authority("LIV")

        assert references == ["ATE00001", "ATE00002"]

    def test_get_references_by_bid_submitting_authority_uses_current_overview(
        self, capital_schemes: MemoryCapitalSchemeRepository
    ) -> None:
        capital_scheme = CapitalScheme(reference="ATE00001")
        capital_scheme.update_overview(
            CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1), datetime(2020, 2, 1)), bid_submitting_authority="LIV"
            )
        )
        capital_scheme.update_overview(
            CapitalSchemeOverview(effective_date=DateTimeRange(datetime(2020, 2, 1)), bid_submitting_authority="WYO")
        )
        capital_schemes.add(capital_scheme)

        references = capital_schemes.get_references_by_bid_submitting_authority("LIV")

        assert not references

    def test_get_references_by_bid_submitting_authority_orders_by_reference(
        self, capital_schemes: MemoryCapitalSchemeRepository
    ) -> None:
        capital_scheme2 = CapitalScheme(reference="ATE00002")
        capital_scheme2.update_overview(
            CapitalSchemeOverview(effective_date=DateTimeRange(datetime(2020, 1, 1)), bid_submitting_authority="LIV")
        )
        capital_schemes.add(capital_scheme2)
        capital_scheme1 = CapitalScheme(reference="ATE00001")
        capital_scheme1.update_overview(
            CapitalSchemeOverview(effective_date=DateTimeRange(datetime(2020, 1, 1)), bid_submitting_authority="LIV")
        )
        capital_schemes.add(capital_scheme1)

        references = capital_schemes.get_references_by_bid_submitting_authority("LIV")

        assert references == ["ATE00001", "ATE00002"]
