from sqlalchemy import ColumnElement, Select, and_, false, func, or_, select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, contains_eager, joinedload
from sqlalchemy.orm.attributes import InstrumentedAttribute, set_committed_value

from ate_api.domain.authorities import AuthorityAbbreviation
from ate_api.domain.capital_scheme_milestones import Milestone
from ate_api.domain.capital_schemes.bid_statuses import BidStatus
from ate_api.domain.capital_schemes.capital_scheme_repositories import CapitalSchemeRepository
from ate_api.domain.capital_schemes.capital_schemes import CapitalScheme, CapitalSchemeReference
from ate_api.domain.capital_schemes.outputs import OutputMeasure, OutputType
from ate_api.domain.capital_schemes.overviews import CapitalSchemeType
from ate_api.domain.data_sources import DataSource
from ate_api.domain.funding_programmes import FundingProgrammeCode
from ate_api.domain.observation_types import ObservationType
from ate_api.infrastructure.database import DataSourceEntity, DataSourceName
from ate_api.infrastructure.database.authorities import AuthorityEntity
from ate_api.infrastructure.database.capital_scheme_milestones import (
    CapitalSchemeMilestoneEntity,
    MilestoneEntity,
    MilestoneName,
)
from ate_api.infrastructure.database.capital_schemes.authority_reviews import CapitalSchemeAuthorityReviewEntity
from ate_api.infrastructure.database.capital_schemes.bid_statuses import (
    BidStatusEntity,
    BidStatusName,
    CapitalSchemeBidStatusEntity,
)
from ate_api.infrastructure.database.capital_schemes.capital_schemes import CapitalSchemeEntity
from ate_api.infrastructure.database.capital_schemes.interventions import (
    CapitalSchemeInterventionEntity,
    InterventionMeasureEntity,
    InterventionMeasureName,
    InterventionTypeEntity,
    InterventionTypeMeasureEntity,
    InterventionTypeName,
)
from ate_api.infrastructure.database.capital_schemes.overviews import (
    CapitalSchemeOverviewEntity,
    SchemeTypeEntity,
    SchemeTypeName,
)
from ate_api.infrastructure.database.funding_programmes import FundingProgrammeEntity
from ate_api.infrastructure.database.observation_types import ObservationTypeEntity, ObservationTypeName


class DatabaseCapitalSchemeRepository(CapitalSchemeRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, capital_scheme: CapitalScheme) -> None:
        authority_ids = await self._get_authority_ids(capital_scheme)
        funding_programme_ids = await self._get_funding_programme_ids(capital_scheme)
        scheme_type_ids = await self._get_scheme_type_ids(capital_scheme)
        bid_status_ids = await self._get_bid_status_ids(capital_scheme)
        intervention_type_measure_ids = await self._get_intervention_type_measure_ids(capital_scheme)
        observation_type_ids = await self._get_observation_type_ids(capital_scheme)
        data_source_ids = await self._get_data_source_ids(capital_scheme)

        self._session.add(
            CapitalSchemeEntity.from_domain(
                capital_scheme,
                authority_ids,
                funding_programme_ids,
                scheme_type_ids,
                bid_status_ids,
                intervention_type_measure_ids,
                observation_type_ids,
                data_source_ids,
            )
        )

    async def get(self, reference: CapitalSchemeReference) -> CapitalScheme | None:
        statement = select(CapitalSchemeEntity).where(CapitalSchemeEntity.scheme_reference == str(reference))

        # fetch current overview
        statement = (
            statement.options(
                contains_eager(CapitalSchemeEntity.capital_scheme_overviews),
                joinedload(
                    CapitalSchemeEntity.capital_scheme_overviews, CapitalSchemeOverviewEntity.bid_submitting_authority
                ),
                contains_eager(
                    CapitalSchemeEntity.capital_scheme_overviews, CapitalSchemeOverviewEntity.funding_programme
                ),
                joinedload(CapitalSchemeEntity.capital_scheme_overviews, CapitalSchemeOverviewEntity.scheme_type),
            )
            .join(
                CapitalSchemeEntity.capital_scheme_overviews.and_(
                    CapitalSchemeOverviewEntity.effective_date_to.is_(None)
                )
            )
            .join(FundingProgrammeEntity)
            .where(FundingProgrammeEntity.is_under_embargo == false())
        )

        # fetch current bid status
        statement = statement.options(
            contains_eager(CapitalSchemeEntity.capital_scheme_bid_statuses),
            joinedload(CapitalSchemeEntity.capital_scheme_bid_statuses, CapitalSchemeBidStatusEntity.bid_status),
        ).join(
            CapitalSchemeEntity.capital_scheme_bid_statuses.and_(
                CapitalSchemeBidStatusEntity.effective_date_to.is_(None)
            )
        )

        # fetch latest authority review
        ranked_capital_scheme_authority_reviews = self._select_ranked_capital_scheme_authority_reviews().cte()
        ranked_capital_scheme_authority_reviews_alias = aliased(
            CapitalSchemeAuthorityReviewEntity, ranked_capital_scheme_authority_reviews
        )
        statement = statement.options(
            contains_eager(
                CapitalSchemeEntity.capital_scheme_authority_reviews.of_type(
                    ranked_capital_scheme_authority_reviews_alias
                )
            ),
            joinedload(
                CapitalSchemeEntity.capital_scheme_authority_reviews, CapitalSchemeAuthorityReviewEntity.data_source
            ),
        ).outerjoin(
            ranked_capital_scheme_authority_reviews_alias,
            and_(
                CapitalSchemeEntity.capital_scheme_id
                == ranked_capital_scheme_authority_reviews_alias.capital_scheme_id,
                ranked_capital_scheme_authority_reviews.c.rank == 1,
            ),
        )

        result = await self._session.scalars(statement)
        row = result.unique().one_or_none()

        if not row:
            return None

        # fetch current interventions
        capital_scheme_interventions = (
            await self._session.scalars(self._select_current_capital_scheme_interventions(row.capital_scheme_id))
        ).all()
        set_committed_value(row, "capital_scheme_interventions", capital_scheme_interventions)

        return row.to_domain()

    async def get_references_by_bid_submitting_authority(
        self,
        authority_abbreviation: AuthorityAbbreviation,
        funding_programme_codes: list[FundingProgrammeCode] | None = None,
        bid_status: BidStatus | None = None,
        current_milestones: list[Milestone | None] | None = None,
    ) -> list[CapitalSchemeReference]:
        statement = (
            select(CapitalSchemeEntity.scheme_reference)
            .join(
                CapitalSchemeEntity.capital_scheme_overviews.and_(
                    CapitalSchemeOverviewEntity.effective_date_to.is_(None)
                )
            )
            .join(
                CapitalSchemeEntity.capital_scheme_bid_statuses.and_(
                    CapitalSchemeBidStatusEntity.effective_date_to.is_(None)
                )
            )
            .join(
                AuthorityEntity, AuthorityEntity.authority_id == CapitalSchemeOverviewEntity.bid_submitting_authority_id
            )
            .join(FundingProgrammeEntity)
            .where(AuthorityEntity.authority_abbreviation == str(authority_abbreviation))
            .where(FundingProgrammeEntity.is_under_embargo == false())
            .order_by(CapitalSchemeEntity.scheme_reference)
        )

        if funding_programme_codes:
            statement = statement.where(
                FundingProgrammeEntity.funding_programme_code.in_(str(code) for code in funding_programme_codes)
            )

        if bid_status:
            statement = statement.join(BidStatusEntity).where(
                BidStatusEntity.bid_status_name == BidStatusName.from_domain(bid_status)
            )

        if current_milestones:
            ranked_actual_capital_scheme_milestones = self._select_ranked_actual_capital_scheme_milestones().cte()
            ranked_actual_capital_scheme_milestones_alias = aliased(
                CapitalSchemeMilestoneEntity, ranked_actual_capital_scheme_milestones
            )
            statement = (
                statement.outerjoin(
                    ranked_actual_capital_scheme_milestones_alias,
                    and_(
                        CapitalSchemeEntity.capital_scheme_id
                        == ranked_actual_capital_scheme_milestones_alias.capital_scheme_id,
                        ranked_actual_capital_scheme_milestones.c.rank == 1,
                    ),
                )
                .outerjoin(MilestoneEntity)
                .where(
                    self._optional_in(
                        MilestoneEntity.milestone_name,
                        [
                            None if milestone is None else MilestoneName.from_domain(milestone)
                            for milestone in current_milestones
                        ],
                    )
                )
            )

        result = await self._session.scalars(statement)
        return [CapitalSchemeReference(reference) for reference in result.all()]

    async def update(self, capital_scheme: CapitalScheme) -> None:
        capital_scheme_id = await self._get_capital_scheme_id(capital_scheme)
        data_source_ids = await self._get_data_source_ids(capital_scheme)

        if capital_scheme.authority_review:
            await self._session.merge(
                CapitalSchemeAuthorityReviewEntity.from_domain(
                    capital_scheme.authority_review, capital_scheme_id, data_source_ids
                )
            )

    @staticmethod
    def _optional_in[T](attribute: InstrumentedAttribute[T], values: list[T | None]) -> ColumnElement[bool]:
        in_values = [value for value in values if value is not None]
        return or_(
            attribute.in_(in_values) if in_values else false(),
            attribute.is_(None) if None in values else false(),
        )

    async def _get_capital_scheme_id(self, capital_scheme: CapitalScheme) -> int:
        capital_scheme_reference = str(capital_scheme.reference)
        rows = await self._session.scalars(
            select(CapitalSchemeEntity.capital_scheme_id).where(
                CapitalSchemeEntity.scheme_reference == capital_scheme_reference
            )
        )
        return rows.one()

    async def _get_authority_ids(self, capital_scheme: CapitalScheme) -> dict[AuthorityAbbreviation, int]:
        authority_abbreviation = str(capital_scheme.overview.bid_submitting_authority)
        rows = await self._session.execute(
            select(AuthorityEntity.authority_abbreviation, AuthorityEntity.authority_id).where(
                AuthorityEntity.authority_abbreviation == authority_abbreviation
            )
        )
        return {AuthorityAbbreviation(row.authority_abbreviation): row.authority_id for row in rows}

    async def _get_funding_programme_ids(self, capital_scheme: CapitalScheme) -> dict[FundingProgrammeCode, int]:
        funding_programme_code = str(capital_scheme.overview.funding_programme)
        rows = await self._session.execute(
            select(FundingProgrammeEntity.funding_programme_code, FundingProgrammeEntity.funding_programme_id).where(
                FundingProgrammeEntity.funding_programme_code == funding_programme_code
            )
        )
        return {FundingProgrammeCode(row.funding_programme_code): row.funding_programme_id for row in rows}

    async def _get_scheme_type_ids(self, capital_scheme: CapitalScheme) -> dict[CapitalSchemeType, int]:
        scheme_type_name = SchemeTypeName.from_domain(capital_scheme.overview.type)
        rows = await self._session.execute(
            select(SchemeTypeEntity.scheme_type_name, SchemeTypeEntity.scheme_type_id).where(
                SchemeTypeEntity.scheme_type_name == scheme_type_name
            )
        )
        return {row.scheme_type_name.to_domain(): row.scheme_type_id for row in rows}

    async def _get_bid_status_ids(self, capital_scheme: CapitalScheme) -> dict[BidStatus, int]:
        bid_status_name = BidStatusName.from_domain(capital_scheme.bid_status_details.bid_status)
        rows = await self._session.execute(
            select(BidStatusEntity.bid_status_name, BidStatusEntity.bid_status_id).where(
                BidStatusEntity.bid_status_name == bid_status_name
            )
        )
        return {row.bid_status_name.to_domain(): row.bid_status_id for row in rows}

    async def _get_intervention_type_measure_ids(
        self, capital_scheme: CapitalScheme
    ) -> dict[tuple[OutputType, OutputMeasure], int]:
        intervention_type_measure_names = {
            (InterventionTypeName.from_domain(output.type), InterventionMeasureName.from_domain(output.measure))
            for output in capital_scheme.outputs
        }
        rows = await self._session.execute(
            select(
                InterventionTypeEntity.intervention_type_name,
                InterventionMeasureEntity.intervention_measure_name,
                InterventionTypeMeasureEntity.intervention_type_measure_id,
            )
            .join(InterventionTypeEntity)
            .join(InterventionMeasureEntity)
            .where(
                tuple_(
                    InterventionTypeEntity.intervention_type_name, InterventionMeasureEntity.intervention_measure_name
                ).in_(intervention_type_measure_names)
            )
        )
        return {
            (
                row.intervention_type_name.to_domain(),
                row.intervention_measure_name.to_domain(),
            ): row.intervention_type_measure_id
            for row in rows
        }

    async def _get_observation_type_ids(self, capital_scheme: CapitalScheme) -> dict[ObservationType, int]:
        observation_type_names = {
            ObservationTypeName.from_domain(output.observation_type) for output in capital_scheme.outputs
        }
        rows = await self._session.execute(
            select(ObservationTypeEntity.observation_type_name, ObservationTypeEntity.observation_type_id).where(
                ObservationTypeEntity.observation_type_name.in_(observation_type_names)
            )
        )
        return {row.observation_type_name.to_domain(): row.observation_type_id for row in rows}

    async def _get_data_source_ids(self, capital_scheme: CapitalScheme) -> dict[DataSource, int]:
        if not capital_scheme.authority_review:
            return {}

        data_source_name = DataSourceName.from_domain(capital_scheme.authority_review.data_source)
        rows = await self._session.execute(
            select(DataSourceEntity.data_source_name, DataSourceEntity.data_source_id).where(
                DataSourceEntity.data_source_name == data_source_name
            )
        )
        return {row.data_source_name.to_domain(): row.data_source_id for row in rows}

    @staticmethod
    def _select_current_capital_scheme_interventions(
        capital_scheme_id: int,
    ) -> Select[tuple[CapitalSchemeInterventionEntity]]:
        return (
            select(CapitalSchemeInterventionEntity)
            .options(
                contains_eager(CapitalSchemeInterventionEntity.intervention_type_measure),
                contains_eager(
                    CapitalSchemeInterventionEntity.intervention_type_measure,
                    InterventionTypeMeasureEntity.intervention_type,
                ),
                contains_eager(
                    CapitalSchemeInterventionEntity.intervention_type_measure,
                    InterventionTypeMeasureEntity.intervention_measure,
                ),
                contains_eager(CapitalSchemeInterventionEntity.observation_type),
            )
            .join(InterventionTypeMeasureEntity)
            .join(InterventionTypeEntity)
            .join(InterventionMeasureEntity)
            .join(ObservationTypeEntity)
            .where(CapitalSchemeInterventionEntity.capital_scheme_id == capital_scheme_id)
            .where(CapitalSchemeInterventionEntity.effective_date_to.is_(None))
            .order_by(InterventionTypeEntity.intervention_type_id)
            .order_by(InterventionMeasureEntity.intervention_measure_id)
        )

    @staticmethod
    def _select_ranked_capital_scheme_authority_reviews() -> Select[tuple[CapitalSchemeAuthorityReviewEntity, int]]:
        return select(
            CapitalSchemeAuthorityReviewEntity,
            func.rank()
            .over(
                partition_by=CapitalSchemeAuthorityReviewEntity.capital_scheme_id,
                order_by=CapitalSchemeAuthorityReviewEntity.review_date.desc(),
            )
            .label("rank"),
        )

    @staticmethod
    def _select_ranked_actual_capital_scheme_milestones() -> Select[tuple[CapitalSchemeMilestoneEntity, int]]:
        return (
            select(
                CapitalSchemeMilestoneEntity,
                func.rank()
                .over(
                    partition_by=CapitalSchemeMilestoneEntity.capital_scheme_id,
                    order_by=MilestoneEntity.stage_order.desc(),
                )
                .label("rank"),
            )
            .join(MilestoneEntity)
            .join(ObservationTypeEntity)
            .where(CapitalSchemeMilestoneEntity.effective_date_to.is_(None))
            .where(ObservationTypeEntity.observation_type_name == ObservationTypeName.ACTUAL)
        )
