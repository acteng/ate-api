from ate_api.domain import Authority


class TestAuthority:
    def test_create(self) -> None:
        authority = Authority(abbreviation="LIV", full_name="Liverpool City Region Combined Authority")

        assert authority.abbreviation == "LIV" and authority.full_name == "Liverpool City Region Combined Authority"
