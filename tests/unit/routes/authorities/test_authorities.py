from ate_api.domain.authorities import Authority
from ate_api.main import app
from ate_api.routes.authorities.authorities import AuthorityModel


class TestAuthorityModel:
    def test_from_domain(self) -> None:
        authority = Authority(abbreviation="LIV", full_name="Liverpool City Region Combined Authority")

        authority_model = AuthorityModel.from_domain(authority, app)

        assert authority_model == AuthorityModel(
            abbreviation="LIV",
            full_name="Liverpool City Region Combined Authority",
            bid_submitting_capital_schemes="/authorities/LIV/capital-schemes/bid-submitting",
        )

    def test_to_domain(self) -> None:
        authority_model = AuthorityModel(abbreviation="LIV", full_name="Liverpool City Region Combined Authority")

        authority = authority_model.to_domain()

        assert authority.abbreviation == "LIV" and authority.full_name == "Liverpool City Region Combined Authority"
