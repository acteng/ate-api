import pytest

from ate_api.routes.funding_programmes import FundingProgrammeModel


class TestFundingProgrammeModel:
    def test_link_to_identifier(self) -> None:
        assert FundingProgrammeModel.link_to_identifier("/funding-programmes/ATF3") == "ATF3"

    def test_link_to_identifier_when_invalid(self) -> None:
        with pytest.raises(ValueError, match="Invalid funding programme link: not a link"):
            FundingProgrammeModel.link_to_identifier("not a link")

    def test_to_domain(self) -> None:
        funding_programme_model = FundingProgrammeModel(code="ATF3")

        funding_programme = funding_programme_model.to_domain()

        assert funding_programme.code == "ATF3"
