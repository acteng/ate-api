import pytest

from ate_api.domain.authorities import Authority, AuthorityAbbreviation
from tests.unit.infrastructure.memory.authorities import MemoryAuthorityRepository


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
