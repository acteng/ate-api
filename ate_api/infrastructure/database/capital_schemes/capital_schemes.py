from typing import Self

from sqlalchemy.orm import Mapped, mapped_column, relationship

from ate_api.domain.authorities import AuthorityAbbreviation
from ate_api.domain.capital_schemes.bid_statuses import BidStatus
from ate_api.domain.capital_schemes.capital_schemes import CapitalScheme, CapitalSchemeReference
from ate_api.domain.capital_schemes.outputs import OutputMeasure, OutputType
from ate_api.domain.capital_schemes.overviews import CapitalSchemeType
from ate_api.domain.data_sources import DataSource
from ate_api.domain.funding_programmes import FundingProgrammeCode
from ate_api.domain.observation_types import ObservationType
from ate_api.infrastructure.database.base import BaseEntity
from ate_api.infrastructure.database.capital_schemes.authority_reviews import CapitalSchemeAuthorityReviewEntity
from ate_api.infrastructure.database.capital_schemes.bid_statuses import CapitalSchemeBidStatusEntity
from ate_api.infrastructure.database.capital_schemes.interventions import CapitalSchemeInterventionEntity
from ate_api.infrastructure.database.capital_schemes.overviews import CapitalSchemeOverviewEntity


class CapitalSchemeEntity(BaseEntity):
    __tablename__ = "capital_scheme"
    __table_args__ = {"schema": "capital_scheme"}

    capital_scheme_id: Mapped[int] = mapped_column(primary_key=True)
    scheme_reference: Mapped[str] = mapped_column(unique=True)
    capital_scheme_overviews: Mapped[list[CapitalSchemeOverviewEntity]] = relationship(lazy="raise")
    capital_scheme_bid_statuses: Mapped[list[CapitalSchemeBidStatusEntity]] = relationship(lazy="raise")
    capital_scheme_interventions: Mapped[list[CapitalSchemeInterventionEntity]] = relationship(lazy="raise")
    capital_scheme_authority_reviews: Mapped[list[CapitalSchemeAuthorityReviewEntity]] = relationship(lazy="raise")

    @classmethod
    def from_domain(
        cls,
        capital_scheme: CapitalScheme,
        authority_ids: dict[AuthorityAbbreviation, int],
        funding_programme_ids: dict[FundingProgrammeCode, int],
        scheme_type_ids: dict[CapitalSchemeType, int],
        bid_status_ids: dict[BidStatus, int],
        observation_type_ids: dict[ObservationType, int],
        intervention_type_measure_ids: dict[tuple[OutputType, OutputMeasure], int],
        data_source_ids: dict[DataSource, int],
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
            capital_scheme_interventions=[
                CapitalSchemeInterventionEntity.from_domain(output, intervention_type_measure_ids, observation_type_ids)
                for output in capital_scheme.outputs
            ],
            capital_scheme_authority_reviews=(
                [CapitalSchemeAuthorityReviewEntity.from_domain(capital_scheme.authority_review, data_source_ids)]
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

        for capital_scheme_intervention in self.capital_scheme_interventions:
            capital_scheme.change_output(capital_scheme_intervention.to_domain())

        if self.capital_scheme_authority_reviews:
            (capital_scheme_authority_review,) = self.capital_scheme_authority_reviews
            capital_scheme.perform_authority_review(capital_scheme_authority_review.to_domain())

        return capital_scheme
