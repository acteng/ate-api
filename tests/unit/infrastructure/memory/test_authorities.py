import pytest

from ate_api.domain import Authority
from ate_api.infrastructure.memory import MemoryAuthorityRepository


class TestMemoryAuthorityRepository:
    @pytest.fixture(name="authorities")
    def authorities_fixture(self) -> MemoryAuthorityRepository:
        return MemoryAuthorityRepository()

    def test_add(self, authorities: MemoryAuthorityRepository) -> None:
        authorities.add(Authority(abbreviation="LIV", full_name="Liverpool City Region Combined Authority"))

        authority = authorities.get_by_abbreviation("LIV")
        assert (
            authority
            and authority.abbreviation == "LIV"
            and authority.full_name == "Liverpool City Region Combined Authority"
        )

    def test_clear(self, authorities: MemoryAuthorityRepository) -> None:
        authorities.add(Authority(abbreviation="LIV", full_name="Liverpool City Region Combined Authority"))

        authorities.clear()

        assert not authorities.get_by_abbreviation("LIV")

    def test_get_by_abbreviation(self, authorities: MemoryAuthorityRepository) -> None:
        authorities.add(Authority(abbreviation="LIV", full_name="Liverpool City Region Combined Authority"))

        authority = authorities.get_by_abbreviation("LIV")

        assert (
            authority
            and authority.abbreviation == "LIV"
            and authority.full_name == "Liverpool City Region Combined Authority"
        )

    def test_get_by_abbreviation_when_not_found(self, authorities: MemoryAuthorityRepository) -> None:
        authority = authorities.get_by_abbreviation("LIV")

        assert not authority
