from datetime import datetime
from enum import Enum
from typing import Self

from sqlalchemy import ForeignKey, Select, and_, false, func, select
from sqlalchemy.orm import (
    Mapped,
    Session,
    aliased,
    contains_eager,
    joinedload,
    mapped_column,
    relationship,
)

from ate_api.domain.capital_schemes.capital_schemes import (
    CapitalScheme,
    CapitalSchemeAuthorityReview,
    CapitalSchemeBidStatus,
    CapitalSchemeBidStatusDetails,
    CapitalSchemeRepository,
)
from ate_api.domain.capital_schemes.overviews import (
    CapitalSchemeOverview,
    CapitalSchemeType,
)
from ate_api.domain.dates import DateTimeRange
from ate_api.infrastructure.database.authorities import AuthorityEntity
from ate_api.infrastructure.database.base import BaseEntity
from ate_api.infrastructure.database.dates import local_to_zoned, zoned_to_local
from ate_api.infrastructure.database.funding_programmes import FundingProgrammeEntity


class SchemeTypeName(Enum):
    DEVELOPMENT = "development"
    CONSTRUCTION = "construction"

    @classmethod
    def from_domain(cls, type_: CapitalSchemeType) -> Self:
        return cls[type_.name]

    def to_domain(self) -> CapitalSchemeType:
        return CapitalSchemeType[self.name]


class SchemeTypeEntity(BaseEntity):
    __tablename__ = "scheme_type"
    __table_args__ = {"schema": "capital_scheme"}

    scheme_type_id: Mapped[int] = mapped_column(primary_key=True)
    scheme_type_name: Mapped[SchemeTypeName] = mapped_column(unique=True)


class CapitalSchemeOverviewEntity(BaseEntity):
    __tablename__ = "capital_scheme_overview"
    __table_args__ = {"schema": "capital_scheme"}

    capital_scheme_overview_id: Mapped[int] = mapped_column(primary_key=True)
    capital_scheme_id = mapped_column(ForeignKey("capital_scheme.capital_scheme.capital_scheme_id"), nullable=False)
    scheme_name: Mapped[str]
    bid_submitting_authority_id = mapped_column(ForeignKey(AuthorityEntity.authority_id), nullable=False)
    bid_submitting_authority: Mapped[AuthorityEntity] = relationship(lazy="raise")
    funding_programme_id = mapped_column(ForeignKey(FundingProgrammeEntity.funding_programme_id), nullable=False)
    funding_programme: Mapped[FundingProgrammeEntity] = relationship(lazy="raise")
    scheme_type_id = mapped_column(ForeignKey(SchemeTypeEntity.scheme_type_id), nullable=False)
    scheme_type: Mapped[SchemeTypeEntity] = relationship(lazy="raise")
    effective_date_from: Mapped[datetime]
    effective_date_to: Mapped[datetime | None]

    @classmethod
    def from_domain(
        cls,
        overview: CapitalSchemeOverview,
        authority_ids: dict[str, int],
        funding_programme_ids: dict[str, int],
        scheme_type_ids: dict[SchemeTypeName, int],
    ) -> Self:
        return cls(
            scheme_name=overview.name,
            bid_submitting_authority_id=authority_ids[overview.bid_submitting_authority],
            funding_programme_id=funding_programme_ids[overview.funding_programme],
            scheme_type_id=scheme_type_ids[SchemeTypeName.from_domain(overview.type)],
            effective_date_from=zoned_to_local(overview.effective_date.from_),
            effective_date_to=zoned_to_local(overview.effective_date.to) if overview.effective_date.to else None,
        )

    def to_domain(self) -> CapitalSchemeOverview:
        return CapitalSchemeOverview(
            effective_date=DateTimeRange(
                local_to_zoned(self.effective_date_from),
                local_to_zoned(self.effective_date_to) if self.effective_date_to else None,
            ),
            name=self.scheme_name,
            bid_submitting_authority=self.bid_submitting_authority.authority_abbreviation,
            funding_programme=self.funding_programme.funding_programme_code,
            type=self.scheme_type.scheme_type_name.to_domain(),
        )


class BidStatusName(Enum):
    SUBMITTED = "submitted"
    FUNDED = "funded"
    NOT_FUNDED = "not funded"
    SPLIT = "split"
    DELETED = "deleted"

    @classmethod
    def from_domain(cls, status: CapitalSchemeBidStatus) -> Self:
        return cls[status.name]

    def to_domain(self) -> CapitalSchemeBidStatus:
        return CapitalSchemeBidStatus[self.name]


class BidStatusEntity(BaseEntity):
    __tablename__ = "bid_status"
    __table_args__ = {"schema": "capital_scheme"}

    bid_status_id: Mapped[int] = mapped_column(primary_key=True)
    bid_status_name: Mapped[BidStatusName] = mapped_column(unique=True)


class CapitalSchemeBidStatusEntity(BaseEntity):
    __tablename__ = "capital_scheme_bid_status"
    __table_args__ = {"schema": "capital_scheme"}

    capital_scheme_bid_status_id: Mapped[int] = mapped_column(primary_key=True)
    capital_scheme_id = mapped_column(ForeignKey("capital_scheme.capital_scheme.capital_scheme_id"), nullable=False)
    bid_status_id = mapped_column(ForeignKey(BidStatusEntity.bid_status_id), nullable=False)
    bid_status: Mapped[BidStatusEntity] = relationship(lazy="raise")
    effective_date_from: Mapped[datetime]
    effective_date_to: Mapped[datetime | None]

    @classmethod
    def from_domain(
        cls, bid_status_details: CapitalSchemeBidStatusDetails, bid_status_ids: dict[BidStatusName, int]
    ) -> Self:
        return cls(
            bid_status_id=bid_status_ids[BidStatusName.from_domain(bid_status_details.bid_status)],
            effective_date_from=zoned_to_local(bid_status_details.effective_date.from_),
            effective_date_to=(
                zoned_to_local(bid_status_details.effective_date.to) if bid_status_details.effective_date.to else None
            ),
        )

    def to_domain(self) -> CapitalSchemeBidStatusDetails:
        return CapitalSchemeBidStatusDetails(
            effective_date=DateTimeRange(
                local_to_zoned(self.effective_date_from),
                local_to_zoned(self.effective_date_to) if self.effective_date_to else None,
            ),
            bid_status=self.bid_status.bid_status_name.to_domain(),
        )


class CapitalSchemeAuthorityReviewEntity(BaseEntity):
    __tablename__ = "capital_scheme_authority_review"
    __table_args__ = {"schema": "capital_scheme"}

    capital_scheme_authority_review_id: Mapped[int] = mapped_column(primary_key=True)
    capital_scheme_id = mapped_column(ForeignKey("capital_scheme.capital_scheme.capital_scheme_id"), nullable=False)
    review_date: Mapped[datetime]

    @classmethod
    def from_domain(cls, authority_review: CapitalSchemeAuthorityReview) -> Self:
        return cls(review_date=zoned_to_local(authority_review.review_date))

    def to_domain(self) -> CapitalSchemeAuthorityReview:
        return CapitalSchemeAuthorityReview(review_date=local_to_zoned(self.review_date))


class CapitalSchemeEntity(BaseEntity):
    __tablename__ = "capital_scheme"
    __table_args__ = {"schema": "capital_scheme"}

    capital_scheme_id: Mapped[int] = mapped_column(primary_key=True)
    scheme_reference: Mapped[str] = mapped_column(unique=True)
    capital_scheme_overviews: Mapped[list[CapitalSchemeOverviewEntity]] = relationship(lazy="raise")
    capital_scheme_bid_statuses: Mapped[list[CapitalSchemeBidStatusEntity]] = relationship(lazy="raise")
    capital_scheme_authority_reviews: Mapped[list[CapitalSchemeAuthorityReviewEntity]] = relationship(lazy="raise")

    @classmethod
    def from_domain(
        cls,
        capital_scheme: CapitalScheme,
        authority_ids: dict[str, int],
        funding_programme_ids: dict[str, int],
        scheme_type_ids: dict[SchemeTypeName, int],
        bid_status_ids: dict[BidStatusName, int],
    ) -> Self:
        return cls(
            scheme_reference=capital_scheme.reference,
            capital_scheme_overviews=[
                CapitalSchemeOverviewEntity.from_domain(
                    capital_scheme.overview, authority_ids, funding_programme_ids, scheme_type_ids
                )
            ],
            capital_scheme_bid_statuses=[
                CapitalSchemeBidStatusEntity.from_domain(capital_scheme.bid_status_details, bid_status_ids)
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
            reference=self.scheme_reference,
            overview=capital_scheme_overview.to_domain(),
            bid_status_details=capital_scheme_bid_status.to_domain(),
        )

        if self.capital_scheme_authority_reviews:
            (capital_scheme_authority_review,) = self.capital_scheme_authority_reviews
            capital_scheme.perform_authority_review(capital_scheme_authority_review.to_domain())

        return capital_scheme


class DatabaseCapitalSchemeRepository(CapitalSchemeRepository):
    def __init__(self, session: Session):
        self._session = session

    def add(self, capital_scheme: CapitalScheme) -> None:
        authority_ids = self._get_authority_ids(capital_scheme)
        funding_programme_ids = self._get_funding_programme_ids(capital_scheme)
        scheme_type_ids = self._get_scheme_type_ids(capital_scheme)
        bid_status_ids = self._get_bid_status_ids(capital_scheme)
        self._session.add(
            CapitalSchemeEntity.from_domain(
                capital_scheme, authority_ids, funding_programme_ids, scheme_type_ids, bid_status_ids
            )
        )

    def get(self, reference: str) -> CapitalScheme | None:
        ranked_capital_scheme_authority_reviews = self._select_ranked_capital_scheme_authority_reviews().cte()
        ranked_capital_scheme_authority_reviews_alias = aliased(
            CapitalSchemeAuthorityReviewEntity, ranked_capital_scheme_authority_reviews
        )

        result = self._session.scalars(
            select(CapitalSchemeEntity)
            .options(
                contains_eager(CapitalSchemeEntity.capital_scheme_overviews),
                joinedload(
                    CapitalSchemeEntity.capital_scheme_overviews, CapitalSchemeOverviewEntity.bid_submitting_authority
                ),
                contains_eager(
                    CapitalSchemeEntity.capital_scheme_overviews, CapitalSchemeOverviewEntity.funding_programme
                ),
                joinedload(CapitalSchemeEntity.capital_scheme_overviews, CapitalSchemeOverviewEntity.scheme_type),
                contains_eager(CapitalSchemeEntity.capital_scheme_bid_statuses),
                joinedload(CapitalSchemeEntity.capital_scheme_bid_statuses, CapitalSchemeBidStatusEntity.bid_status),
                contains_eager(
                    CapitalSchemeEntity.capital_scheme_authority_reviews.of_type(
                        ranked_capital_scheme_authority_reviews_alias
                    )
                ),
            )
            .join(
                CapitalSchemeEntity.capital_scheme_overviews.and_(
                    CapitalSchemeOverviewEntity.effective_date_to.is_(None)
                )
            )
            .join(
                CapitalSchemeOverviewEntity.funding_programme.and_(FundingProgrammeEntity.is_under_embargo == false())
            )
            .join(
                CapitalSchemeEntity.capital_scheme_bid_statuses.and_(
                    CapitalSchemeBidStatusEntity.effective_date_to.is_(None)
                )
            )
            .outerjoin(
                ranked_capital_scheme_authority_reviews_alias,
                and_(
                    CapitalSchemeEntity.capital_scheme_id
                    == ranked_capital_scheme_authority_reviews_alias.capital_scheme_id,
                    ranked_capital_scheme_authority_reviews.c.rank == 1,
                ),
            )
            .where(CapitalSchemeEntity.scheme_reference == reference)
        )

        row = result.unique().one_or_none()
        return row.to_domain() if row else None

    def get_references_by_bid_submitting_authority(self, authority_abbreviation: str) -> list[str]:
        result = self._session.scalars(
            select(CapitalSchemeEntity.scheme_reference)
            .join(
                CapitalSchemeEntity.capital_scheme_overviews.and_(
                    CapitalSchemeOverviewEntity.effective_date_to.is_(None)
                )
            )
            .join(
                AuthorityEntity, AuthorityEntity.authority_id == CapitalSchemeOverviewEntity.bid_submitting_authority_id
            )
            .join(
                CapitalSchemeOverviewEntity.funding_programme.and_(FundingProgrammeEntity.is_under_embargo == false())
            )
            .where(AuthorityEntity.authority_abbreviation == authority_abbreviation)
            .order_by(CapitalSchemeEntity.scheme_reference)
        )
        return list(result.all())

    def _get_authority_ids(self, capital_scheme: CapitalScheme) -> dict[str, int]:
        authority_abbreviations = [capital_scheme.overview.bid_submitting_authority]
        rows = self._session.execute(
            select(AuthorityEntity.authority_abbreviation, AuthorityEntity.authority_id).where(
                AuthorityEntity.authority_abbreviation.in_(authority_abbreviations)
            )
        )
        return {row.authority_abbreviation: row.authority_id for row in rows}

    def _get_funding_programme_ids(self, capital_scheme: CapitalScheme) -> dict[str, int]:
        funding_programme_codes = [capital_scheme.overview.funding_programme]
        rows = self._session.execute(
            select(FundingProgrammeEntity.funding_programme_code, FundingProgrammeEntity.funding_programme_id).where(
                FundingProgrammeEntity.funding_programme_code.in_(funding_programme_codes)
            )
        )
        return {row.funding_programme_code: row.funding_programme_id for row in rows}

    def _get_scheme_type_ids(self, capital_scheme: CapitalScheme) -> dict[SchemeTypeName, int]:
        scheme_type_names = [SchemeTypeName.from_domain(capital_scheme.overview.type)]
        rows = self._session.execute(
            select(SchemeTypeEntity.scheme_type_name, SchemeTypeEntity.scheme_type_id).where(
                SchemeTypeEntity.scheme_type_name.in_(scheme_type_names)
            )
        )
        return {row.scheme_type_name: row.scheme_type_id for row in rows}

    def _get_bid_status_ids(self, capital_scheme: CapitalScheme) -> dict[BidStatusName, int]:
        bid_status_names = [BidStatusName.from_domain(capital_scheme.bid_status_details.bid_status)]
        rows = self._session.execute(
            select(BidStatusEntity.bid_status_name, BidStatusEntity.bid_status_id).where(
                BidStatusEntity.bid_status_name.in_(bid_status_names)
            )
        )
        return {row.bid_status_name: row.bid_status_id for row in rows}

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
