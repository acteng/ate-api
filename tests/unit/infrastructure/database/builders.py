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


def build_authority_entity(full_name: str = "dummy", abbreviation: str = "dummy") -> AuthorityEntity:
    return AuthorityEntity(authority_full_name=full_name, authority_abbreviation=abbreviation)


def build_capital_scheme_overview_entity(
    name: str = "",
    bid_submitting_authority: AuthorityEntity | None = None,
    funding_programme: FundingProgrammeEntity | None = None,
    type_: SchemeTypeEntity | None = None,
    effective_date_from: datetime = datetime.min,
) -> CapitalSchemeOverviewEntity:
    return CapitalSchemeOverviewEntity(
        scheme_name=name,
        bid_submitting_authority=bid_submitting_authority or build_authority_entity(),
        funding_programme=funding_programme or build_funding_programme_entity(),
        scheme_type=type_ or build_scheme_type_entity(),
        effective_date_from=effective_date_from,
    )


def build_funding_programme_entity(code: str = "dummy", is_under_embargo: bool = False) -> FundingProgrammeEntity:
    return FundingProgrammeEntity(funding_programme_code=code, is_under_embargo=is_under_embargo)


def build_scheme_type_entity(name: SchemeTypeName = SchemeTypeName.DEVELOPMENT) -> SchemeTypeEntity:
    return SchemeTypeEntity(scheme_type_name=name)


def build_capital_scheme_bid_status_entity(
    bid_status: BidStatusEntity | None = None, effective_date_from: datetime = datetime.min
) -> CapitalSchemeBidStatusEntity:
    return CapitalSchemeBidStatusEntity(
        bid_status=bid_status or build_bid_status_entity(), effective_date_from=effective_date_from
    )


def build_bid_status_entity(name: BidStatusName = BidStatusName.SUBMITTED) -> BidStatusEntity:
    return BidStatusEntity(bid_status_name=name)
