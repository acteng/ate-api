from pydantic import AnyUrl

from ate_api.routes.capital_schemes.overviews import CapitalSchemeOverviewModel
from ate_api.routes.capital_schemes.statuses import CapitalSchemeStatusModel, StatusModel


def build_authority_url(base_url: str) -> AnyUrl:
    return AnyUrl(f"{base_url}/authorities/dummy")


def build_capital_scheme_overview_model(
    name: str = "dummy", improvement: AnyUrl | None = None
) -> CapitalSchemeOverviewModel:
    return CapitalSchemeOverviewModel(name=name, improvement=improvement)


def build_capital_scheme_status_model(status: StatusModel = StatusModel.PIPELINE) -> CapitalSchemeStatusModel:
    return CapitalSchemeStatusModel(status=status)
