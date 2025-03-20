import pytest

from ate_api.authorities import Authority, AuthorityModel, MemoryAuthorityRepository


class TestAuthority:
    def test_create(self) -> None:
        authority = Authority(abbreviation="LIV", full_name="Liverpool City Region Combined Authority")

        assert authority.abbreviation == "LIV" and authority.full_name == "Liverpool City Region Combined Authority"


class TestMemoryAuthorityRepository:
    @pytest.fixture(name="authorities")
    def authorities_fixture(self) -> MemoryAuthorityRepository:
        return MemoryAuthorityRepository()

    def test_add(self, authorities: MemoryAuthorityRepository) -> None:
        authorities.add(Authority(abbreviation="LIV", full_name="Liverpool City Region Combined Authority"))

        authority = authorities.get_by_abbreviation("LIV")
        assert authority.abbreviation == "LIV" and authority.full_name == "Liverpool City Region Combined Authority"

    def test_get_by_abbreviation(self, authorities: MemoryAuthorityRepository) -> None:
        authorities.add(Authority(abbreviation="LIV", full_name="Liverpool City Region Combined Authority"))

        authority = authorities.get_by_abbreviation("LIV")

        assert authority.abbreviation == "LIV" and authority.full_name == "Liverpool City Region Combined Authority"


class TestAuthorityModel:
    def test_from_domain(self) -> None:
        authority = Authority(abbreviation="LIV", full_name="Liverpool City Region Combined Authority")

        authority_model = AuthorityModel.from_domain(authority)

        assert (
            authority_model.abbreviation == "LIV"
            and authority_model.full_name == "Liverpool City Region Combined Authority"
        )
