from ate_api.domain import Authority
from ate_api.routes import AuthorityModel


class TestAuthorityModel:
    def test_from_domain(self) -> None:
        authority = Authority(abbreviation="LIV", full_name="Liverpool City Region Combined Authority")

        authority_model = AuthorityModel.from_domain(authority)

        assert (
            authority_model.abbreviation == "LIV"
            and authority_model.full_name == "Liverpool City Region Combined Authority"
        )

    def test_to_domain(self) -> None:
        authority_model = AuthorityModel(abbreviation="LIV", full_name="Liverpool City Region Combined Authority")

        authority = authority_model.to_domain()

        assert authority.abbreviation == "LIV" and authority.full_name == "Liverpool City Region Combined Authority"
