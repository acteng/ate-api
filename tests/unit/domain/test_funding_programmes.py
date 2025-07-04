from ate_api.domain.funding_programmes import FundingProgramme, FundingProgrammeCode


class TestFundingProgrammeCode:
    def test_create(self) -> None:
        code = FundingProgrammeCode("ATF3")

        assert str(code) == "ATF3"

    def test_equals(self) -> None:
        code1 = FundingProgrammeCode("ATF3")
        code2 = FundingProgrammeCode("ATF3")

        assert code1 == code2

    def test_equals_when_different_code(self) -> None:
        code1 = FundingProgrammeCode("ATF3")
        code2 = FundingProgrammeCode("ATF4")

        assert not code1 == code2

    def test_equals_when_different_class(self) -> None:
        code = FundingProgrammeCode("ATF3")

        assert not code == "ATF3"

    def test_hash(self) -> None:
        code1 = FundingProgrammeCode("ATF3")
        code2 = FundingProgrammeCode("ATF3")

        assert hash(code1) == hash(code2)

    def test_repr(self) -> None:
        code = FundingProgrammeCode("ATF3")

        assert repr(code) == "FundingProgrammeCode('ATF3')"


class TestFundingProgramme:
    def test_create(self) -> None:
        funding_programme = FundingProgramme(code=FundingProgrammeCode("ATF3"), is_eligible_for_authority_update=True)

        assert (
            funding_programme.code == FundingProgrammeCode("ATF3")
            and funding_programme.is_eligible_for_authority_update
        )

    def test_create_with_defaults(self) -> None:
        funding_programme = FundingProgramme(code=FundingProgrammeCode("ATF3"))

        assert not funding_programme.is_eligible_for_authority_update
