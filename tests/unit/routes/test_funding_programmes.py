from fastapi import Request
from pydantic import AnyUrl

from ate_api.domain.funding_programmes import FundingProgramme, FundingProgrammeCode
from ate_api.routes.funding_programmes import FundingProgrammeModel


class TestFundingProgrammeModel:
    def test_from_domain(self, http_request: Request, base_url: str) -> None:
        funding_programme = FundingProgramme(code=FundingProgrammeCode("ATF3"), is_eligible_for_authority_update=True)

        funding_programme_model = FundingProgrammeModel.from_domain(funding_programme, http_request)

        assert (
            funding_programme_model.id == AnyUrl(f"{base_url}/funding-programmes/ATF3")
            and funding_programme_model.code == "ATF3"
            and funding_programme_model.eligible_for_authority_update
        )

    def test_to_domain(self) -> None:
        funding_programme_model = FundingProgrammeModel(code="ATF3", eligible_for_authority_update=True)

        funding_programme = funding_programme_model.to_domain()

        assert (
            funding_programme.code == FundingProgrammeCode("ATF3")
            and funding_programme.is_eligible_for_authority_update
        )
