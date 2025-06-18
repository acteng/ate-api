from ate_api.domain.authorities import Authority, AuthorityAbbreviation


class TestAuthorityAbbreviation:
    def test_create(self) -> None:
        abbreviation = AuthorityAbbreviation("LIV")

        assert str(abbreviation) == "LIV"

    def test_equals(self) -> None:
        abbreviation1 = AuthorityAbbreviation("LIV")
        abbreviation2 = AuthorityAbbreviation("LIV")

        assert abbreviation1 == abbreviation2

    def test_equals_when_different_abbreviation(self) -> None:
        abbreviation1 = AuthorityAbbreviation("LIV")
        abbreviation2 = AuthorityAbbreviation("WYO")

        assert not abbreviation1 == abbreviation2

    def test_equals_when_different_class(self) -> None:
        abbreviation = AuthorityAbbreviation("LIV")

        assert not abbreviation == "LIV"

    def test_hash(self) -> None:
        abbreviation1 = AuthorityAbbreviation("LIV")
        abbreviation2 = AuthorityAbbreviation("LIV")

        assert hash(abbreviation1) == hash(abbreviation2)

    def test_repr(self) -> None:
        abbreviation = AuthorityAbbreviation("LIV")

        assert repr(abbreviation) == "AuthorityAbbreviation('LIV')"


class TestAuthority:
    def test_create(self) -> None:
        authority = Authority(
            abbreviation=AuthorityAbbreviation("LIV"), full_name="Liverpool City Region Combined Authority"
        )

        assert (
            authority.abbreviation == AuthorityAbbreviation("LIV")
            and authority.full_name == "Liverpool City Region Combined Authority"
        )
