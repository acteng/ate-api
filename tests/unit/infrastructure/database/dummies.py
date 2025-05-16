from datetime import datetime

from ate_api.infrastructure.database import (
    AuthorityEntity,
    BidStatusEntity,
    BidStatusName,
    CapitalSchemeBidStatusEntity,
    CapitalSchemeOverviewEntity,
    FundingProgrammeEntity,
    SchemeTypeEntity,
    SchemeTypeName,
)


def dummy_authority_entity() -> AuthorityEntity:
    return AuthorityEntity(authority_full_name="dummy", authority_abbreviation="dummy")


def dummy_capital_scheme_overview_entity() -> CapitalSchemeOverviewEntity:
    return CapitalSchemeOverviewEntity(
        scheme_name="",
        bid_submitting_authority=dummy_authority_entity(),
        funding_programme=dummy_funding_programme_entity(),
        scheme_type=dummy_scheme_type_entity(),
        effective_date_from=datetime.min,
    )


def dummy_funding_programme_entity() -> FundingProgrammeEntity:
    return FundingProgrammeEntity(funding_programme_code="dummy", is_under_embargo=False)


def dummy_scheme_type_entity() -> SchemeTypeEntity:
    return SchemeTypeEntity(scheme_type_name=SchemeTypeName.DEVELOPMENT)


def dummy_capital_scheme_bid_status_entity() -> CapitalSchemeBidStatusEntity:
    return CapitalSchemeBidStatusEntity(bid_status=dummy_bid_status_entity(), effective_date_from=datetime.min)


def dummy_bid_status_entity() -> BidStatusEntity:
    return BidStatusEntity(bid_status_name=BidStatusName.SUBMITTED)
