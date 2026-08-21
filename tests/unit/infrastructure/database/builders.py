from datetime import datetime

from ate_api.infrastructure.database import (
    AuthorityEntity,
    CapitalSchemeAuthorityReviewEntity,
    CapitalSchemeEntity,
    CapitalSchemeInterventionEntity,
    CapitalSchemeOverviewEntity,
    CapitalSchemeSchemeStatusEntity,
    DataSourceEntity,
    DataSourceName,
    FinancialTypeEntity,
    FinancialTypeName,
    FundingProgrammeEntity,
    ImprovementEntity,
    ImprovementOverviewEntity,
    InterventionMeasureEntity,
    InterventionMeasureName,
    InterventionTypeEntity,
    InterventionTypeMeasureEntity,
    InterventionTypeName,
    MilestoneEntity,
    MilestoneName,
    ObservationTypeEntity,
    ObservationTypeName,
    SchemeStatusEntity,
    SchemeStatusName,
    SchemeTypeEntity,
    SchemeTypeName,
)
from tests.unit.dates import dummy_local_datetime


class EntityBuilder:
    """
    Factory for database entities to be used by tests.

    Built entities use shared reference data to avoid duplicate inserts.
    """

    def __init__(self) -> None:
        self._dummy_funding_programme = build_funding_programme_entity()
        self._dummy_scheme_type = build_scheme_type_entity()
        self._dummy_scheme_status = build_scheme_status_entity()

    def build_capital_scheme(
        self,
        id_: int | None = None,
        reference: str = "dummy",
        overviews: list[CapitalSchemeOverviewEntity] | None = None,
        scheme_statuses: list[CapitalSchemeSchemeStatusEntity] | None = None,
        interventions: list[CapitalSchemeInterventionEntity] | None = None,
        authority_reviews: list[CapitalSchemeAuthorityReviewEntity] | None = None,
    ) -> CapitalSchemeEntity:
        return CapitalSchemeEntity(
            capital_scheme_id=id_,
            scheme_reference=reference,
            capital_scheme_overviews=overviews if overviews is not None else [self.build_capital_scheme_overview()],
            capital_scheme_scheme_statuses=(
                scheme_statuses if scheme_statuses is not None else [self.build_capital_scheme_scheme_status_entity()]
            ),
            capital_scheme_interventions=interventions or [],
            capital_scheme_authority_reviews=authority_reviews or [],
        )

    def build_capital_scheme_overview(
        self,
        name: str = "dummy",
        bid_submitting_authority: AuthorityEntity | None = None,
        funding_programme: FundingProgrammeEntity | None = None,
        improvement: ImprovementEntity | None = None,
        type_: SchemeTypeEntity | None = None,
        effective_date_from: datetime = dummy_local_datetime,
    ) -> CapitalSchemeOverviewEntity:
        return CapitalSchemeOverviewEntity(
            scheme_name=name,
            bid_submitting_authority=bid_submitting_authority or build_authority_entity(),
            funding_programme=funding_programme or self._dummy_funding_programme,
            improvement=improvement,
            scheme_type=type_ or self._dummy_scheme_type,
            effective_date_from=effective_date_from,
        )

    def build_capital_scheme_scheme_status_entity(
        self, scheme_status: SchemeStatusEntity | None = None, effective_date_from: datetime = dummy_local_datetime
    ) -> CapitalSchemeSchemeStatusEntity:
        return CapitalSchemeSchemeStatusEntity(
            scheme_status=scheme_status or self._dummy_scheme_status, effective_date_from=effective_date_from
        )


def build_authority_entity(
    id_: int | None = None, full_name: str = "dummy", abbreviation: str = "dummy"
) -> AuthorityEntity:
    return AuthorityEntity(authority_id=id_, authority_full_name=full_name, authority_abbreviation=abbreviation)


def build_improvement_overview_entity(
    name: str = "dummy",
    description: str = "dummy",
    funding_managed_by: AuthorityEntity | None = None,
    data_source: DataSourceEntity | None = None,
    effective_date_from: datetime = dummy_local_datetime,
    is_deleted: bool = False,
) -> ImprovementOverviewEntity:
    return ImprovementOverviewEntity(
        improvement_name=name,
        improvement_description=description,
        funding_managed_by=funding_managed_by or build_authority_entity(),
        data_source=data_source or build_data_source_entity(),
        effective_date_from=effective_date_from,
        is_deleted=is_deleted,
    )


def build_scheme_type_entity(
    id_: int | None = None, name: SchemeTypeName = SchemeTypeName.DEVELOPMENT
) -> SchemeTypeEntity:
    return SchemeTypeEntity(scheme_type_id=id_, scheme_type_name=name)


def build_scheme_status_entity(
    id_: int | None = None, name: SchemeStatusName = SchemeStatusName.PIPELINE
) -> SchemeStatusEntity:
    return SchemeStatusEntity(scheme_status_id=id_, scheme_status_name=name)


def build_financial_type_entity(
    id_: int | None = None, name: FinancialTypeName = FinancialTypeName.EXPECTED_COST
) -> FinancialTypeEntity:
    return FinancialTypeEntity(financial_type_id=id_, financial_type_name=name)


def build_data_source_entity(id_: int | None = None, name: DataSourceName = DataSourceName.PULSE_5) -> DataSourceEntity:
    return DataSourceEntity(data_source_id=id_, data_source_name=name)


def build_milestone_entity(
    id_: int | None = None,
    name: MilestoneName = MilestoneName.PUBLIC_CONSULTATION_COMPLETED,
    milestone_order: int = 0,
) -> MilestoneEntity:
    return MilestoneEntity(milestone_id=id_, milestone_name=name, milestone_order=milestone_order)


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
    is_eligible_for_authority_update: bool = False,
) -> FundingProgrammeEntity:
    return FundingProgrammeEntity(
        funding_programme_id=id_,
        funding_programme_code=code,
        is_eligible_for_authority_update=is_eligible_for_authority_update,
    )
