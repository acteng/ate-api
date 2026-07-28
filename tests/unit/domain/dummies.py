from datetime import UTC, datetime

from ate_api.domain.capital_schemes.bid_statuses import BidStatus, CapitalSchemeBidStatusDetails
from ate_api.domain.dates import DateTimeRange


def dummy_bid_status_details() -> CapitalSchemeBidStatusDetails:
    return CapitalSchemeBidStatusDetails(effective_date=dummy_date_time_range(), bid_status=BidStatus.SUBMITTED)


def dummy_date_time_range() -> DateTimeRange:
    return DateTimeRange(datetime.fromtimestamp(0, UTC))
