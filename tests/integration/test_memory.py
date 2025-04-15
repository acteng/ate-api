import pytest

from ate_api.domain import Authority
from tests.integration.memory import MemoryAuthorityRepository


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
