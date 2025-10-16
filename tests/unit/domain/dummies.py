from datetime import UTC, datetime

from ate_api.domain.authorities import AuthorityAbbreviation
from ate_api.domain.capital_schemes.bid_statuses import BidStatus, CapitalSchemeBidStatusDetails
from ate_api.domain.capital_schemes.overviews import CapitalSchemeOverview, CapitalSchemeType
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.funding_programmes import FundingProgrammeCode


def dummy_overview() -> CapitalSchemeOverview:
    return CapitalSchemeOverview(
        effective_date=dummy_date_time_range(),
        name="",
        bid_submitting_authority=AuthorityAbbreviation("dummy"),
        funding_programme=FundingProgrammeCode("dummy"),
        type=CapitalSchemeType.DEVELOPMENT,
    )


def dummy_bid_status_details() -> CapitalSchemeBidStatusDetails:
    return CapitalSchemeBidStatusDetails(effective_date=dummy_date_time_range(), bid_status=BidStatus.SUBMITTED)


def dummy_date_time_range() -> DateTimeRange:
    return DateTimeRange(datetime.fromtimestamp(0, UTC))
