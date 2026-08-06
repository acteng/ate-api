from datetime import datetime

from ate_api.domain.authorities import Authority, AuthorityAbbreviation
from ate_api.domain.capital_schemes.bid_statuses import BidStatus, CapitalSchemeBidStatusDetails
from ate_api.domain.capital_schemes.capital_schemes import CapitalScheme, CapitalSchemeReference
from ate_api.domain.capital_schemes.overviews import CapitalSchemeOverview, CapitalSchemeType
from ate_api.domain.capital_schemes.statuses import CapitalSchemeStatus, Status
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.funding_programmes import FundingProgrammeCode
from ate_api.domain.improvements.improvements import ImprovementReference
from tests.unit.dates import dummy_datetime

_dummy_capital_scheme_type = CapitalSchemeType.DEVELOPMENT


def build_authority(abbreviation: AuthorityAbbreviation | None = None, full_name: str = "dummy") -> Authority:
    return Authority(abbreviation=abbreviation or build_authority_abbreviation(), full_name=full_name)


def build_authority_abbreviation(abbreviation: str = "dummy") -> AuthorityAbbreviation:
    return AuthorityAbbreviation(abbreviation)


def build_capital_scheme(
    reference: CapitalSchemeReference | None = None,
    overview: CapitalSchemeOverview | None = None,
    bid_status_details: CapitalSchemeBidStatusDetails | None = None,
    status: CapitalSchemeStatus | None = None,
) -> CapitalScheme:
    return CapitalScheme(
        reference=reference or build_capital_scheme_reference(),
        overview=overview or build_capital_scheme_overview(),
        bid_status_details=bid_status_details or build_capital_scheme_bid_status_details(),
        status=status or build_capital_scheme_status(),
    )


def build_capital_scheme_reference(reference: str = "dummy") -> CapitalSchemeReference:
    return CapitalSchemeReference(reference)


def build_capital_scheme_overview(
    effective_date: DateTimeRange | None = None,
    name: str = "dummy",
    bid_submitting_authority: AuthorityAbbreviation | None = None,
    funding_programme: FundingProgrammeCode | None = None,
    improvement: ImprovementReference | None = None,
    type_: CapitalSchemeType = _dummy_capital_scheme_type,
) -> CapitalSchemeOverview:
    return CapitalSchemeOverview(
        effective_date=effective_date or build_date_time_range(),
        name=name,
        bid_submitting_authority=bid_submitting_authority or build_authority_abbreviation(),
        funding_programme=funding_programme or build_funding_programme_code(),
        improvement=improvement,
        type=type_,
    )


def build_capital_scheme_bid_status_details(
    effective_date: DateTimeRange | None = None, bid_status: BidStatus = BidStatus.SUBMITTED
) -> CapitalSchemeBidStatusDetails:
    return CapitalSchemeBidStatusDetails(
        effective_date=effective_date or build_date_time_range(), bid_status=bid_status
    )


def build_capital_scheme_status(
    effective_date: DateTimeRange | None = None, status: Status = Status.PIPELINE
) -> CapitalSchemeStatus:
    return CapitalSchemeStatus(effective_date=effective_date or build_date_time_range(), status=status)


def build_funding_programme_code(code: str = "dummy") -> FundingProgrammeCode:
    return FundingProgrammeCode(code)


def build_capital_scheme_type() -> CapitalSchemeType:
    return _dummy_capital_scheme_type


def build_date_time_range(from_: datetime = dummy_datetime, to: datetime = dummy_datetime) -> DateTimeRange:
    return DateTimeRange(from_=from_, to=to)
