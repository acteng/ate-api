from datetime import datetime

from pydantic import AnyUrl

from ate_api.routes.capital_schemes.bid_statuses import CapitalSchemeBidStatusDetailsModel, CapitalSchemeBidStatusModel
from ate_api.routes.capital_schemes.overviews import CapitalSchemeOverviewModel, CapitalSchemeTypeModel
from ate_api.routes.dates import DateTimeRangeModel


def dummy_overview_model(base_url: str) -> CapitalSchemeOverviewModel:
    return CapitalSchemeOverviewModel(
        name="",
        bid_submitting_authority=AnyUrl(f"{base_url}/authorities/dummy"),
        funding_programme=AnyUrl(f"{base_url}/funding-programmes/dummy"),
        type_=CapitalSchemeTypeModel.DEVELOPMENT,
        effective_date=DateTimeRangeModel(from_=datetime.min),
    )


def dummy_bid_status_details_model() -> CapitalSchemeBidStatusDetailsModel:
    return CapitalSchemeBidStatusDetailsModel(bid_status=CapitalSchemeBidStatusModel.NOT_FUNDED)
