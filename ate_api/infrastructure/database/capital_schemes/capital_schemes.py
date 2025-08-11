from typing import Self

from sqlalchemy import ColumnElement, Select, and_, false, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, aliased, contains_eager, joinedload, mapped_column, relationship
from sqlalchemy.orm.attributes import InstrumentedAttribute, set_committed_value

from ate_api.domain.authorities import AuthorityAbbreviation
from ate_api.domain.capital_schemes.bid_statuses import BidStatus
from ate_api.domain.capital_schemes.capital_schemes import (
    CapitalScheme,
    CapitalSchemeReference,
    CapitalSchemeRepository,
)
from ate_api.domain.capital_schemes.milestones import Milestone
from ate_api.domain.capital_schemes.overviews import CapitalSchemeType
from ate_api.domain.funding_programmes import FundingProgrammeCode
from ate_api.domain.observation_types import ObservationType
from ate_api.infrastructure.database.authorities import AuthorityEntity
from ate_api.infrastructure.database.base import BaseEntity
from ate_api.infrastructure.database.capital_schemes.authority_reviews import CapitalSchemeAuthorityReviewEntity
from ate_api.infrastructure.database.capital_schemes.bid_statuses import (
    BidStatusEntity,
    BidStatusName,
    CapitalSchemeBidStatusEntity,
)
from ate_api.infrastructure.database.capital_schemes.milestones import (
    CapitalSchemeMilestoneEntity,
    MilestoneEntity,
    MilestoneName,
)
from ate_api.infrastructure.database.capital_schemes.overviews import (
    CapitalSchemeOverviewEntity,
    SchemeTypeEntity,
    SchemeTypeName,
)
from ate_api.infrastructure.database.funding_programmes import FundingProgrammeEntity
from ate_api.infrastructure.database.observation_types import ObservationTypeEntity, ObservationTypeName


class CapitalSchemeEntity(BaseEntity):
    __tablename__ = "capital_scheme"
    __table_args__ = {"schema": "capital_scheme"}

    capital_scheme_id: Mapped[int] = mapped_column(primary_key=True)
    scheme_reference: Mapped[str] = mapped_column(unique=True)
    capital_scheme_overviews: Mapped[list[CapitalSchemeOverviewEntity]] = relationship(lazy="raise")
    capital_scheme_bid_statuses: Mapped[list[CapitalSchemeBidStatusEntity]] = relationship(lazy="raise")
    capital_scheme_milestones: Mapped[list[CapitalSchemeMilestoneEntity]] = relationship(lazy="raise")
    capital_scheme_authority_reviews: Mapped[list[CapitalSchemeAuthorityReviewEntity]] = relationship(lazy="raise")

    @classmethod
    def from_domain(
        cls,
        capital_scheme: CapitalScheme,
        authority_ids: dict[AuthorityAbbreviation, int],
        funding_programme_ids: dict[FundingProgrammeCode, int],
        scheme_type_ids: dict[CapitalSchemeType, int],
        bid_status_ids: dict[BidStatus, int],
        milestone_ids: dict[Milestone, int],
        observation_type_ids: dict[ObservationType, int],
    ) -> Self:
        return cls(
            scheme_reference=str(capital_scheme.reference),
            capital_scheme_overviews=[
                CapitalSchemeOverviewEntity.from_domain(
                    capital_scheme.overview, authority_ids, funding_programme_ids, scheme_type_ids
                )
            ],
            capital_scheme_bid_statuses=[
                CapitalSchemeBidStatusEntity.from_domain(capital_scheme.bid_status_details, bid_status_ids)
            ],
            capital_scheme_milestones=[
                CapitalSchemeMilestoneEntity.from_domain(milestone, milestone_ids, observation_type_ids)
                for milestone in capital_scheme.milestones
            ],
            capital_scheme_authority_reviews=(
                [CapitalSchemeAuthorityReviewEntity.from_domain(capital_scheme.authority_review)]
                if capital_scheme.authority_review
                else []
            ),
        )

    def to_domain(self) -> CapitalScheme:
        (capital_scheme_overview,) = self.capital_scheme_overviews
        (capital_scheme_bid_status,) = self.capital_scheme_bid_statuses
        capital_scheme = CapitalScheme(
            reference=CapitalSchemeReference(self.scheme_reference),
            overview=capital_scheme_overview.to_domain(),
            bid_status_details=capital_scheme_bid_status.to_domain(),
        )

        for capital_scheme_milestone in self.capital_scheme_milestones:
            capital_scheme.change_milestone(capital_scheme_milestone.to_domain())

        if self.capital_scheme_authority_reviews:
            (capital_scheme_authority_review,) = self.capital_scheme_authority_reviews
            capital_scheme.perform_authority_review(capital_scheme_authority_review.to_domain())

        return capital_scheme


class DatabaseCapitalSchemeRepository(CapitalSchemeRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, capital_scheme: CapitalScheme) -> None:
        authority_ids = await self._get_authority_ids(capital_scheme)
        funding_programme_ids = await self._get_funding_programme_ids(capital_scheme)
        scheme_type_ids = await self._get_scheme_type_ids(capital_scheme)
        bid_status_ids = await self._get_bid_status_ids(capital_scheme)
        milestone_ids = await self._get_milestone_ids(capital_scheme)
        observation_type_ids = await self._get_observation_type_ids(capital_scheme)

        self._session.add(
            CapitalSchemeEntity.from_domain(
                capital_scheme,
                authority_ids,
                funding_programme_ids,
                scheme_type_ids,
                bid_status_ids,
                milestone_ids,
                observation_type_ids,
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
            )
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

        # fetch current milestones
        capital_scheme_milestones = (
            await self._session.scalars(self._select_current_capital_scheme_milestones(row.capital_scheme_id))
        ).all()
        set_committed_value(row, "capital_scheme_milestones", capital_scheme_milestones)

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

    @staticmethod
    def _optional_in[T](attribute: InstrumentedAttribute[T], values: list[T | None]) -> ColumnElement[bool]:
        in_values = [value for value in values if value is not None]
        return or_(
            attribute.in_(in_values) if in_values else false(),
            attribute.is_(None) if None in values else false(),
        )

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

    async def _get_milestone_ids(self, capital_scheme: CapitalScheme) -> dict[Milestone, int]:
        milestone_names = {MilestoneName.from_domain(milestone.milestone) for milestone in capital_scheme.milestones}
        rows = await self._session.execute(
            select(MilestoneEntity.milestone_name, MilestoneEntity.milestone_id).where(
                MilestoneEntity.milestone_name.in_(milestone_names)
            )
        )
        return {row.milestone_name.to_domain(): row.milestone_id for row in rows}

    async def _get_observation_type_ids(self, capital_scheme: CapitalScheme) -> dict[ObservationType, int]:
        observation_type_names = {
            ObservationTypeName.from_domain(milestone.observation_type) for milestone in capital_scheme.milestones
        }
        rows = await self._session.execute(
            select(ObservationTypeEntity.observation_type_name, ObservationTypeEntity.observation_type_id).where(
                ObservationTypeEntity.observation_type_name.in_(observation_type_names)
            )
        )
        return {row.observation_type_name.to_domain(): row.observation_type_id for row in rows}

    @staticmethod
    def _select_current_capital_scheme_milestones(
        capital_scheme_id: int,
    ) -> Select[tuple[CapitalSchemeMilestoneEntity]]:
        return (
            select(CapitalSchemeMilestoneEntity)
            .options(
                contains_eager(CapitalSchemeMilestoneEntity.milestone),
                contains_eager(CapitalSchemeMilestoneEntity.observation_type),
            )
            .join(MilestoneEntity)
            .join(ObservationTypeEntity)
            .where(CapitalSchemeMilestoneEntity.capital_scheme_id == capital_scheme_id)
            .where(CapitalSchemeMilestoneEntity.effective_date_to.is_(None))
            .order_by(MilestoneEntity.stage_order)
            .order_by(ObservationTypeEntity.observation_type_id)
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
