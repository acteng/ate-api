from ate_api.domain.capital_schemes.bid_statuses import CapitalSchemeBidStatusDetails
from ate_api.domain.capital_schemes.capital_schemes import CapitalScheme, CapitalSchemeReference
from ate_api.domain.capital_schemes.overviews import CapitalSchemeOverview
from tests.unit.domain.dummies import dummy_bid_status_details, dummy_overview


def build_capital_scheme(
    reference: CapitalSchemeReference | None = None,
    overview: CapitalSchemeOverview | None = None,
    bid_status_details: CapitalSchemeBidStatusDetails | None = None,
) -> CapitalScheme:
    return CapitalScheme(
        reference=reference or build_capital_scheme_reference(),
        overview=overview or dummy_overview(),
        bid_status_details=bid_status_details or dummy_bid_status_details(),
    )


def build_capital_scheme_reference(reference: str = "dummy") -> CapitalSchemeReference:
    return CapitalSchemeReference(reference)
