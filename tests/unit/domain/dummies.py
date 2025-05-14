from datetime import datetime

from ate_api.domain.capital_schemes.capital_schemes import (
    CapitalSchemeBidStatus,
    CapitalSchemeBidStatusDetails,
    CapitalSchemeOverview,
    CapitalSchemeType,
)
from ate_api.domain.dates import DateTimeRange


def dummy_overview() -> CapitalSchemeOverview:
    return CapitalSchemeOverview(
        effective_date=dummy_date_time_range(),
        name="",
        bid_submitting_authority="dummy",
        funding_programme="dummy",
        type=CapitalSchemeType.DEVELOPMENT,
    )


def dummy_bid_status_details() -> CapitalSchemeBidStatusDetails:
    return CapitalSchemeBidStatusDetails(
        effective_date=dummy_date_time_range(), bid_status=CapitalSchemeBidStatus.NOT_FUNDED
    )


def dummy_date_time_range() -> DateTimeRange:
    return DateTimeRange(datetime.fromtimestamp(0))
