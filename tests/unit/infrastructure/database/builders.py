from datetime import datetime

from ate_api.infrastructure.database import (
    AuthorityEntity,
    BidStatusEntity,
    BidStatusName,
    CapitalSchemeBidStatusEntity,
    CapitalSchemeOverviewEntity,
    FinancialTypeEntity,
    FinancialTypeName,
    FundingProgrammeEntity,
    InterventionMeasureEntity,
    InterventionMeasureName,
    InterventionTypeEntity,
    InterventionTypeMeasureEntity,
    InterventionTypeName,
    MilestoneEntity,
    MilestoneName,
    ObservationTypeEntity,
    ObservationTypeName,
    SchemeTypeEntity,
    SchemeTypeName,
)


def build_authority_entity(
    id_: int | None = None, full_name: str = "dummy", abbreviation: str = "dummy"
) -> AuthorityEntity:
    return AuthorityEntity(authority_id=id_, authority_full_name=full_name, authority_abbreviation=abbreviation)


def build_capital_scheme_overview_entity(
    name: str = "dummy",
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


def build_scheme_type_entity(
    id_: int | None = None, name: SchemeTypeName = SchemeTypeName.DEVELOPMENT
) -> SchemeTypeEntity:
    return SchemeTypeEntity(scheme_type_id=id_, scheme_type_name=name)


def build_capital_scheme_bid_status_entity(
    bid_status: BidStatusEntity | None = None, effective_date_from: datetime = datetime.min
) -> CapitalSchemeBidStatusEntity:
    return CapitalSchemeBidStatusEntity(
        bid_status=bid_status or build_bid_status_entity(), effective_date_from=effective_date_from
    )


def build_bid_status_entity(id_: int | None = None, name: BidStatusName = BidStatusName.SUBMITTED) -> BidStatusEntity:
    return BidStatusEntity(bid_status_id=id_, bid_status_name=name)


def build_financial_type_entity(
    id_: int | None = None, name: FinancialTypeName = FinancialTypeName.EXPECTED_COST
) -> FinancialTypeEntity:
    return FinancialTypeEntity(financial_type_id=id_, financial_type_name=name)


def build_milestone_entity(
    id_: int | None = None,
    name: MilestoneName = MilestoneName.PUBLIC_CONSULTATION_COMPLETED,
    stage_order: int = 0,
    is_active: bool = False,
    is_complete: bool = False,
) -> MilestoneEntity:
    return MilestoneEntity(
        milestone_id=id_, milestone_name=name, stage_order=stage_order, is_active=is_active, is_complete=is_complete
    )


def build_intervention_type_measure_entity(
    id_: int | None = None,
    type_: InterventionTypeEntity | None = None,
    measure: InterventionMeasureEntity | None = None,
) -> InterventionTypeMeasureEntity:
    return InterventionTypeMeasureEntity(
        intervention_type_measure_id=id_,
        intervention_type=type_ or build_intervention_type_entity(),
        intervention_measure=measure or build_intervention_measure_entity(),
    )


def build_intervention_type_entity(
    id_: int | None = None, name: InterventionTypeName = InterventionTypeName.NEW_SEGREGATED_CYCLING_FACILITY
) -> InterventionTypeEntity:
    return InterventionTypeEntity(intervention_type_id=id_, intervention_type_name=name)


def build_intervention_measure_entity(
    id_: int | None = None, name: InterventionMeasureName = InterventionMeasureName.MILES
) -> InterventionMeasureEntity:
    return InterventionMeasureEntity(intervention_measure_id=id_, intervention_measure_name=name)


def build_observation_type_entity(
    id_: int | None = None, name: ObservationTypeName = ObservationTypeName.PLANNED
) -> ObservationTypeEntity:
    return ObservationTypeEntity(observation_type_id=id_, observation_type_name=name)


def build_funding_programme_entity(
    id_: int | None = None,
    code: str = "dummy",
    is_under_embargo: bool = False,
    is_eligible_for_authority_update: bool = False,
) -> FundingProgrammeEntity:
    return FundingProgrammeEntity(
        funding_programme_id=id_,
        funding_programme_code=code,
        is_under_embargo=is_under_embargo,
        is_eligible_for_authority_update=is_eligible_for_authority_update,
    )
