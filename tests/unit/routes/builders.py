from pydantic import AnyUrl

from ate_api.routes.capital_schemes.bid_statuses import BidStatusModel, CapitalSchemeBidStatusDetailsModel
from ate_api.routes.capital_schemes.overviews import CapitalSchemeOverviewModel, CapitalSchemeTypeModel
from ate_api.routes.capital_schemes.statuses import CapitalSchemeStatusModel, StatusModel


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


def build_capital_scheme_bid_status_details_model(
    bid_status: BidStatusModel = BidStatusModel.SUBMITTED,
) -> CapitalSchemeBidStatusDetailsModel:
    return CapitalSchemeBidStatusDetailsModel(bid_status=bid_status)


def build_capital_scheme_status_model(status: StatusModel = StatusModel.PIPELINE) -> CapitalSchemeStatusModel:
    return CapitalSchemeStatusModel(status=status)


def build_funding_programme_url(base_url: str) -> AnyUrl:
    return AnyUrl(f"{base_url}/funding-programmes/dummy")
