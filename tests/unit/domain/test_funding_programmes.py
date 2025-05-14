from ate_api.domain.funding_programmes import FundingProgramme


class TestFundingProgramme:
    def test_create(self) -> None:
        funding_programme = FundingProgramme(code="ATF3")

        assert funding_programme.code == "ATF3"
