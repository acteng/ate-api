from pydantic import AnyUrl

from ate_api.routes.capital_schemes.overviews import CapitalSchemeOverviewModel, CapitalSchemeTypeModel


def build_authority_url(base_url: str) -> AnyUrl:
    return AnyUrl(f"{base_url}/authorities/dummy")


def build_capital_scheme_overview_model(
    base_url: str,
    name: str = "dummy",
    bid_submitting_authority: AnyUrl | None = None,
    funding_programme: AnyUrl | None = None,
    improvement: AnyUrl | None = None,
    type_: CapitalSchemeTypeModel = CapitalSchemeTypeModel.DEVELOPMENT,
) -> CapitalSchemeOverviewModel:
    return CapitalSchemeOverviewModel(
        name=name,
        bid_submitting_authority=bid_submitting_authority or build_authority_url(base_url),
        funding_programme=funding_programme or build_funding_programme_url(base_url),
        improvement=improvement,
        type=type_,
    )


def build_funding_programme_url(base_url: str) -> AnyUrl:
    return AnyUrl(f"{base_url}/funding-programmes/dummy")
