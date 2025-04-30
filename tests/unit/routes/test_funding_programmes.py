from ate_api.domain.funding_programmes import FundingProgramme
from ate_api.routes.funding_programmes import FundingProgrammeModel


class TestFundingProgrammeModel:
    def test_from_domain(self) -> None:
        funding_programme = FundingProgramme(code="ATF3")

        funding_programme_model = FundingProgrammeModel.from_domain(funding_programme)

        assert funding_programme_model.code == "ATF3"

    def test_to_domain(self) -> None:
        funding_programme_model = FundingProgrammeModel(code="ATF3")

        funding_programme = funding_programme_model.to_domain()

        assert funding_programme.code == "ATF3"
