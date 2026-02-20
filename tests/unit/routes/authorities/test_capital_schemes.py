from fastapi import Request
from pydantic import AnyUrl

from ate_api.domain.capital_schemes.capital_scheme_repositories import CapitalSchemeItem
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeReference
from ate_api.routes.authorities.capital_schemes import CapitalSchemeItemModel


class TestCapitalSchemeItemModel:
    def test_from_domain(self, http_request: Request, base_url: str) -> None:
        capital_scheme_item = CapitalSchemeItem(reference=CapitalSchemeReference("ATE00001"), name="Wirral Package")

        capital_scheme_item_model = CapitalSchemeItemModel.from_domain(capital_scheme_item, http_request)

        assert capital_scheme_item_model == CapitalSchemeItemModel(
            id=AnyUrl(f"{base_url}/capital-schemes/ATE00001"), reference="ATE00001", name="Wirral Package"
        )
