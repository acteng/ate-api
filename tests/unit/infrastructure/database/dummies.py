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


def dummy_overview_entity() -> CapitalSchemeOverviewEntity:
    return CapitalSchemeOverviewEntity(
        bid_submitting_authority=AuthorityEntity(),
        funding_programme=FundingProgrammeEntity(),
        scheme_type=SchemeTypeEntity(scheme_type_name=SchemeTypeName.DEVELOPMENT),
        effective_date_from=datetime.min,
    )


def dummy_bid_status_entity() -> CapitalSchemeBidStatusEntity:
    return CapitalSchemeBidStatusEntity(
        bid_status=BidStatusEntity(bid_status_name=BidStatusName.NOT_FUNDED), effective_date_from=datetime.min
    )
