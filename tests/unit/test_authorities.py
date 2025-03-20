from ate_api.authorities import Authority, AuthorityModel


class TestAuthority:
    def test_create(self) -> None:
        authority = Authority(abbreviation="LIV", full_name="Liverpool City Region Combined Authority")

        assert authority.abbreviation == "LIV" and authority.full_name == "Liverpool City Region Combined Authority"


class TestAuthorityModel:
    def test_from_domain(self) -> None:
        authority = Authority(abbreviation="LIV", full_name="Liverpool City Region Combined Authority")

        authority_model = AuthorityModel.from_domain(authority)

        assert (
            authority_model.abbreviation == "LIV"
            and authority_model.full_name == "Liverpool City Region Combined Authority"
        )
