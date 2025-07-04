from datetime import date, datetime, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from ate_api.domain.authorities import AuthorityAbbreviation
from ate_api.domain.capital_schemes.authority_reviews import CapitalSchemeAuthorityReview
from ate_api.domain.capital_schemes.bid_statuses import BidStatus, CapitalSchemeBidStatusDetails
from ate_api.domain.capital_schemes.capital_schemes import CapitalScheme, CapitalSchemeReference
from ate_api.domain.capital_schemes.milestones import CapitalSchemeMilestone, Milestone
from ate_api.domain.capital_schemes.overviews import CapitalSchemeOverview, CapitalSchemeType
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.funding_programmes import FundingProgrammeCode
from ate_api.domain.observation_types import ObservationType
from ate_api.infrastructure.database import (
    AuthorityEntity,
    BidStatusEntity,
    BidStatusName,
    CapitalSchemeAuthorityReviewEntity,
    CapitalSchemeBidStatusEntity,
    CapitalSchemeEntity,
    CapitalSchemeMilestoneEntity,
    CapitalSchemeOverviewEntity,
    FundingProgrammeEntity,
    MilestoneEntity,
    MilestoneName,
    ObservationTypeEntity,
    ObservationTypeName,
    SchemeTypeEntity,
    SchemeTypeName,
)
from ate_api.infrastructure.database.capital_schemes.capital_schemes import DatabaseCapitalSchemeRepository
from tests.unit.domain.dummies import dummy_bid_status_details, dummy_overview
from tests.unit.infrastructure.database.builders import (
    build_authority_entity,
    build_bid_status_entity,
    build_capital_scheme_bid_status_entity,
    build_capital_scheme_overview_entity,
    build_funding_programme_entity,
    build_scheme_type_entity,
)


class TestCapitalSchemeEntity:
    def test_from_domain(self) -> None:
        capital_scheme = CapitalScheme(
            reference=CapitalSchemeReference("ATE00001"),
            overview=CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1)),
                name="Wirral Package",
                bid_submitting_authority=AuthorityAbbreviation("LIV"),
                funding_programme=FundingProgrammeCode("ATF3"),
                type=CapitalSchemeType.CONSTRUCTION,
            ),
            bid_status_details=CapitalSchemeBidStatusDetails(
                effective_date=DateTimeRange(datetime(2020, 2, 1)),
                bid_status=BidStatus.FUNDED,
            ),
        )

        capital_scheme_entity = CapitalSchemeEntity.from_domain(
            capital_scheme,
            {AuthorityAbbreviation("LIV"): 1},
            {FundingProgrammeCode("ATF3"): 2},
            {CapitalSchemeType.CONSTRUCTION: 3},
            {BidStatus.FUNDED: 4},
            {},
            {},
        )

        assert capital_scheme_entity.scheme_reference == "ATE00001"
        (overview_entity,) = capital_scheme_entity.capital_scheme_overviews
        assert (
            overview_entity.scheme_name == "Wirral Package"
            and overview_entity.bid_submitting_authority_id == 1
            and overview_entity.funding_programme_id == 2
            and overview_entity.scheme_type_id == 3
            and overview_entity.effective_date_from == datetime(2020, 1, 1)
            and not overview_entity.effective_date_to
        )
        (bid_status_entity,) = capital_scheme_entity.capital_scheme_bid_statuses
        assert (
            bid_status_entity.bid_status_id == 4
            and bid_status_entity.effective_date_from == datetime(2020, 2, 1)
            and not bid_status_entity.effective_date_to
        )
        assert not capital_scheme_entity.capital_scheme_authority_reviews

    def test_from_domain_sets_milestones(self) -> None:
        capital_scheme = CapitalScheme(
            reference=CapitalSchemeReference("ATE00001"),
            overview=dummy_overview(),
            bid_status_details=dummy_bid_status_details(),
        )
        capital_scheme.change_milestone(
            CapitalSchemeMilestone(
                effective_date=DateTimeRange(datetime(2020, 1, 1)),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 2, 1),
            )
        )
        capital_scheme.change_milestone(
            CapitalSchemeMilestone(
                effective_date=DateTimeRange(datetime(2020, 1, 1)),
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 3, 1),
            )
        )

        capital_scheme_entity = CapitalSchemeEntity.from_domain(
            capital_scheme,
            {AuthorityAbbreviation("dummy"): 0},
            {FundingProgrammeCode("dummy"): 0},
            {CapitalSchemeType.DEVELOPMENT: 0},
            {BidStatus.SUBMITTED: 0},
            {Milestone.DETAILED_DESIGN_COMPLETED: 1, Milestone.CONSTRUCTION_STARTED: 2},
            {ObservationType.ACTUAL: 3},
        )

        milestone_entity1, milestone_entity2 = capital_scheme_entity.capital_scheme_milestones
        assert (
            milestone_entity1.milestone_id == 1
            and milestone_entity1.status_date == date(2020, 2, 1)
            and milestone_entity1.observation_type_id == 3
            and milestone_entity1.effective_date_from == datetime(2020, 1, 1)
            and not milestone_entity1.effective_date_to
        )
        assert (
            milestone_entity2.milestone_id == 2
            and milestone_entity2.status_date == date(2020, 3, 1)
            and milestone_entity2.observation_type_id == 3
            and milestone_entity2.effective_date_from == datetime(2020, 1, 1)
            and not milestone_entity2.effective_date_to
        )

    def test_from_domain_sets_authority_review(self) -> None:
        capital_scheme = CapitalScheme(
            reference=CapitalSchemeReference("ATE00001"),
            overview=dummy_overview(),
            bid_status_details=dummy_bid_status_details(),
        )
        capital_scheme.perform_authority_review(CapitalSchemeAuthorityReview(review_date=datetime(2020, 2, 1)))

        capital_scheme_entity = CapitalSchemeEntity.from_domain(
            capital_scheme,
            {AuthorityAbbreviation("dummy"): 0},
            {FundingProgrammeCode("dummy"): 0},
            {CapitalSchemeType.DEVELOPMENT: 0},
            {BidStatus.SUBMITTED: 0},
            {},
            {},
        )

        (authority_review_entity,) = capital_scheme_entity.capital_scheme_authority_reviews
        assert authority_review_entity.review_date == datetime(2020, 2, 1)

    def test_to_domain(self) -> None:
        capital_scheme_entity = CapitalSchemeEntity(
            scheme_reference="ATE00001",
            capital_scheme_overviews=[
                CapitalSchemeOverviewEntity(
                    scheme_name="Wirral Package",
                    bid_submitting_authority=AuthorityEntity(authority_abbreviation="LIV"),
                    funding_programme=FundingProgrammeEntity(funding_programme_code="ATF3"),
                    scheme_type=SchemeTypeEntity(scheme_type_name=SchemeTypeName.CONSTRUCTION),
                    effective_date_from=datetime(2020, 1, 1),
                )
            ],
            capital_scheme_bid_statuses=[
                CapitalSchemeBidStatusEntity(
                    bid_status=BidStatusEntity(bid_status_name=BidStatusName.FUNDED),
                    effective_date_from=datetime(2020, 2, 1),
                )
            ],
        )

        capital_scheme = capital_scheme_entity.to_domain()

        assert capital_scheme.reference == CapitalSchemeReference("ATE00001")
        assert capital_scheme.overview == CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=timezone.utc)),
            name="Wirral Package",
            bid_submitting_authority=AuthorityAbbreviation("LIV"),
            funding_programme=FundingProgrammeCode("ATF3"),
            type=CapitalSchemeType.CONSTRUCTION,
        )
        assert capital_scheme.bid_status_details == CapitalSchemeBidStatusDetails(
            effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=timezone.utc)),
            bid_status=BidStatus.FUNDED,
        )
        assert not capital_scheme.milestones
        assert not capital_scheme.authority_review

    def test_to_domain_sets_milestones(self) -> None:
        capital_scheme_entity = CapitalSchemeEntity(
            scheme_reference="ATE00001",
            capital_scheme_overviews=[build_capital_scheme_overview_entity()],
            capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity()],
            capital_scheme_milestones=[
                CapitalSchemeMilestoneEntity(
                    milestone=MilestoneEntity(milestone_name=MilestoneName.DETAILED_DESIGN_COMPLETED),
                    observation_type=ObservationTypeEntity(observation_type_name=ObservationTypeName.ACTUAL),
                    status_date=date(2020, 2, 1),
                    effective_date_from=datetime(2020, 1, 1),
                ),
                CapitalSchemeMilestoneEntity(
                    milestone=MilestoneEntity(milestone_name=MilestoneName.CONSTRUCTION_STARTED),
                    observation_type=ObservationTypeEntity(observation_type_name=ObservationTypeName.ACTUAL),
                    status_date=date(2020, 3, 1),
                    effective_date_from=datetime(2020, 1, 1),
                ),
            ],
        )

        capital_scheme = capital_scheme_entity.to_domain()

        assert capital_scheme.milestones == [
            CapitalSchemeMilestone(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=timezone.utc)),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 2, 1),
            ),
            CapitalSchemeMilestone(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=timezone.utc)),
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 3, 1),
            ),
        ]

    def test_to_domain_sets_authority_review(self) -> None:
        capital_scheme_entity = CapitalSchemeEntity(
            scheme_reference="ATE00001",
            capital_scheme_overviews=[build_capital_scheme_overview_entity()],
            capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity()],
            capital_scheme_authority_reviews=[CapitalSchemeAuthorityReviewEntity(review_date=datetime(2020, 1, 1))],
        )

        capital_scheme = capital_scheme_entity.to_domain()

        assert capital_scheme.authority_review == CapitalSchemeAuthorityReview(
            review_date=datetime(2020, 1, 1, tzinfo=timezone.utc)
        )


@pytest.mark.usefixtures("data")
@pytest.mark.asyncio(loop_scope="package")
class TestDatabaseCapitalSchemeRepository:
    async def test_add(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    AuthorityEntity(authority_id=1, authority_full_name="Liverpool", authority_abbreviation="LIV"),
                    FundingProgrammeEntity(
                        funding_programme_id=1,
                        funding_programme_code="ATF3",
                        is_under_embargo=False,
                        is_eligible_for_authority_update=False,
                    ),
                    SchemeTypeEntity(scheme_type_id=1, scheme_type_name=SchemeTypeName.CONSTRUCTION),
                    BidStatusEntity(bid_status_id=1, bid_status_name=BidStatusName.FUNDED),
                ]
            )

        async with AsyncSession(engine) as session, session.begin():
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            await capital_schemes.add(
                CapitalScheme(
                    reference=CapitalSchemeReference("ATE00001"),
                    overview=CapitalSchemeOverview(
                        effective_date=DateTimeRange(datetime(2020, 1, 1)),
                        name="Wirral Package",
                        bid_submitting_authority=AuthorityAbbreviation("LIV"),
                        funding_programme=FundingProgrammeCode("ATF3"),
                        type=CapitalSchemeType.CONSTRUCTION,
                    ),
                    bid_status_details=CapitalSchemeBidStatusDetails(
                        effective_date=DateTimeRange(datetime(2020, 2, 1)),
                        bid_status=BidStatus.FUNDED,
                    ),
                )
            )

        async with AsyncSession(engine) as session:
            (capital_scheme_row,) = await session.scalars(select(CapitalSchemeEntity))
            (overview_row,) = await session.scalars(select(CapitalSchemeOverviewEntity))
            (bid_status_row,) = await session.scalars(select(CapitalSchemeBidStatusEntity))
        assert capital_scheme_row.scheme_reference == "ATE00001"
        assert (
            overview_row.capital_scheme_id == capital_scheme_row.capital_scheme_id
            and overview_row.scheme_name == "Wirral Package"
            and overview_row.bid_submitting_authority_id == 1
            and overview_row.funding_programme_id == 1
            and overview_row.scheme_type_id == 1
            and overview_row.effective_date_from == datetime(2020, 1, 1)
            and not overview_row.effective_date_to
        )
        assert (
            bid_status_row.capital_scheme_id == capital_scheme_row.capital_scheme_id
            and bid_status_row.bid_status_id == 1
            and bid_status_row.effective_date_from == datetime(2020, 2, 1)
            and not bid_status_row.effective_date_to
        )

    async def test_add_stores_milestones(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    build_authority_entity(),
                    build_funding_programme_entity(),
                    build_scheme_type_entity(),
                    build_bid_status_entity(),
                    MilestoneEntity(
                        milestone_id=1, milestone_name=MilestoneName.DETAILED_DESIGN_COMPLETED, stage_order=1
                    ),
                    MilestoneEntity(milestone_id=2, milestone_name=MilestoneName.CONSTRUCTION_STARTED, stage_order=2),
                    ObservationTypeEntity(observation_type_id=1, observation_type_name=ObservationTypeName.ACTUAL),
                ]
            )

        async with AsyncSession(engine) as session, session.begin():
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme = CapitalScheme(
                reference=CapitalSchemeReference("ATE00001"),
                overview=dummy_overview(),
                bid_status_details=dummy_bid_status_details(),
            )
            capital_scheme.change_milestone(
                CapitalSchemeMilestone(
                    effective_date=DateTimeRange(datetime(2020, 1, 1)),
                    milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                    observation_type=ObservationType.ACTUAL,
                    status_date=date(2020, 2, 1),
                )
            )
            capital_scheme.change_milestone(
                CapitalSchemeMilestone(
                    effective_date=DateTimeRange(datetime(2020, 1, 1)),
                    milestone=Milestone.CONSTRUCTION_STARTED,
                    observation_type=ObservationType.ACTUAL,
                    status_date=date(2020, 3, 1),
                )
            )
            await capital_schemes.add(capital_scheme)

        async with AsyncSession(engine) as session:
            (capital_scheme_row,) = await session.scalars(select(CapitalSchemeEntity))
            milestone_row1, milestone_row2 = await session.scalars(select(CapitalSchemeMilestoneEntity))
        assert (
            milestone_row1.capital_scheme_id == capital_scheme_row.capital_scheme_id
            and milestone_row1.milestone_id == 1
            and milestone_row1.status_date == date(2020, 2, 1)
            and milestone_row1.observation_type_id == 1
            and milestone_row1.effective_date_from == datetime(2020, 1, 1)
            and not milestone_row1.effective_date_to
        )
        assert (
            milestone_row2.capital_scheme_id == capital_scheme_row.capital_scheme_id
            and milestone_row2.milestone_id == 2
            and milestone_row2.status_date == date(2020, 3, 1)
            and milestone_row2.observation_type_id == 1
            and milestone_row2.effective_date_from == datetime(2020, 1, 1)
            and not milestone_row2.effective_date_to
        )

    async def test_add_stores_authority_review(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    build_authority_entity(),
                    build_funding_programme_entity(),
                    build_scheme_type_entity(),
                    build_bid_status_entity(),
                ]
            )

        async with AsyncSession(engine) as session, session.begin():
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme = CapitalScheme(
                reference=CapitalSchemeReference("ATE00001"),
                overview=dummy_overview(),
                bid_status_details=dummy_bid_status_details(),
            )
            capital_scheme.perform_authority_review(CapitalSchemeAuthorityReview(review_date=datetime(2020, 2, 1)))
            await capital_schemes.add(capital_scheme)

        async with AsyncSession(engine) as session:
            (capital_scheme_row,) = await session.scalars(select(CapitalSchemeEntity))
            (authority_review_row,) = await session.scalars(select(CapitalSchemeAuthorityReviewEntity))
        assert (
            authority_review_row.capital_scheme_id == capital_scheme_row.capital_scheme_id
            and authority_review_row.review_date == datetime(2020, 2, 1)
        )

    async def test_get(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    liv := build_authority_entity(abbreviation="LIV"),
                    atf3 := build_funding_programme_entity(code="ATF3"),
                    construction := build_scheme_type_entity(name=SchemeTypeName.CONSTRUCTION),
                    funded := build_bid_status_entity(name=BidStatusName.FUNDED),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00001",
                        capital_scheme_overviews=[
                            CapitalSchemeOverviewEntity(
                                scheme_name="Wirral Package",
                                bid_submitting_authority=liv,
                                funding_programme=atf3,
                                scheme_type=construction,
                                effective_date_from=datetime(2020, 1, 1),
                            ),
                        ],
                        capital_scheme_bid_statuses=[
                            CapitalSchemeBidStatusEntity(bid_status=funded, effective_date_from=datetime(2020, 1, 1)),
                        ],
                    ),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00002",
                        capital_scheme_overviews=[
                            CapitalSchemeOverviewEntity(
                                scheme_name="School Streets",
                                bid_submitting_authority=liv,
                                funding_programme=atf3,
                                scheme_type=construction,
                                effective_date_from=datetime(2020, 1, 1),
                            )
                        ],
                        capital_scheme_bid_statuses=[
                            CapitalSchemeBidStatusEntity(bid_status=funded, effective_date_from=datetime(2020, 1, 1))
                        ],
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme = await capital_schemes.get(CapitalSchemeReference("ATE00001"))

        assert capital_scheme and capital_scheme.reference == CapitalSchemeReference("ATE00001")
        assert capital_scheme.overview == CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=timezone.utc)),
            name="Wirral Package",
            bid_submitting_authority=AuthorityAbbreviation("LIV"),
            funding_programme=FundingProgrammeCode("ATF3"),
            type=CapitalSchemeType.CONSTRUCTION,
        )
        assert capital_scheme.bid_status_details == CapitalSchemeBidStatusDetails(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=timezone.utc)),
            bid_status=BidStatus.FUNDED,
        )
        assert not capital_scheme.authority_review

    async def test_get_fetches_current_overview(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    liv := build_authority_entity(abbreviation="LIV"),
                    atf3 := build_funding_programme_entity(code="ATF3"),
                    construction := build_scheme_type_entity(name=SchemeTypeName.CONSTRUCTION),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00001",
                        capital_scheme_overviews=[
                            CapitalSchemeOverviewEntity(
                                scheme_name="Wirral Package",
                                bid_submitting_authority=liv,
                                funding_programme=atf3,
                                scheme_type=construction,
                                effective_date_from=datetime(2020, 1, 1),
                                effective_date_to=datetime(2020, 2, 1),
                            ),
                            CapitalSchemeOverviewEntity(
                                scheme_name="School Streets",
                                bid_submitting_authority=liv,
                                funding_programme=atf3,
                                scheme_type=construction,
                                effective_date_from=datetime(2020, 2, 1),
                            ),
                        ],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity()],
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme = await capital_schemes.get(CapitalSchemeReference("ATE00001"))

        assert capital_scheme and capital_scheme.overview == CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=timezone.utc)),
            name="School Streets",
            bid_submitting_authority=AuthorityAbbreviation("LIV"),
            funding_programme=FundingProgrammeCode("ATF3"),
            type=CapitalSchemeType.CONSTRUCTION,
        )

    async def test_get_fetches_current_bid_status(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    funded := build_bid_status_entity(name=BidStatusName.FUNDED),
                    not_funded := build_bid_status_entity(name=BidStatusName.NOT_FUNDED),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00001",
                        capital_scheme_overviews=[build_capital_scheme_overview_entity()],
                        capital_scheme_bid_statuses=[
                            CapitalSchemeBidStatusEntity(
                                bid_status=funded,
                                effective_date_from=datetime(2020, 1, 1),
                                effective_date_to=datetime(2020, 2, 1),
                            ),
                            CapitalSchemeBidStatusEntity(
                                bid_status=not_funded, effective_date_from=datetime(2020, 2, 1)
                            ),
                        ],
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme = await capital_schemes.get(CapitalSchemeReference("ATE00001"))

        assert capital_scheme and capital_scheme.bid_status_details == CapitalSchemeBidStatusDetails(
            effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=timezone.utc)),
            bid_status=BidStatus.NOT_FUNDED,
        )

    async def test_get_fetches_current_milestones(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    detailed_design_completed := MilestoneEntity(
                        milestone_name=MilestoneName.DETAILED_DESIGN_COMPLETED, stage_order=1
                    ),
                    construction_started := MilestoneEntity(
                        milestone_name=MilestoneName.CONSTRUCTION_STARTED, stage_order=2
                    ),
                    actual := ObservationTypeEntity(observation_type_name=ObservationTypeName.ACTUAL),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00001",
                        capital_scheme_overviews=[build_capital_scheme_overview_entity()],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity()],
                        capital_scheme_milestones=[
                            CapitalSchemeMilestoneEntity(
                                milestone=detailed_design_completed,
                                observation_type=actual,
                                status_date=date(2020, 3, 1),
                                effective_date_from=datetime(2020, 1, 1),
                                effective_date_to=datetime(2020, 2, 1),
                            ),
                            CapitalSchemeMilestoneEntity(
                                milestone=detailed_design_completed,
                                observation_type=actual,
                                status_date=date(2020, 4, 1),
                                effective_date_from=datetime(2020, 2, 1),
                            ),
                            CapitalSchemeMilestoneEntity(
                                milestone=construction_started,
                                observation_type=actual,
                                status_date=date(2020, 5, 1),
                                effective_date_from=datetime(2020, 2, 1),
                            ),
                        ],
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme = await capital_schemes.get(CapitalSchemeReference("ATE00001"))

        assert capital_scheme and capital_scheme.milestones == [
            CapitalSchemeMilestone(
                effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=timezone.utc)),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 4, 1),
            ),
            CapitalSchemeMilestone(
                effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=timezone.utc)),
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 5, 1),
            ),
        ]

    async def test_get_fetches_current_milestones_ordered_by_milestone_stage_order_then_observation_type(
        self, engine: AsyncEngine
    ) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    detailed_design_completed := MilestoneEntity(
                        milestone_name=MilestoneName.DETAILED_DESIGN_COMPLETED, stage_order=1
                    ),
                    construction_started := MilestoneEntity(
                        milestone_name=MilestoneName.CONSTRUCTION_STARTED, stage_order=2
                    ),
                    planned := ObservationTypeEntity(observation_type_name=ObservationTypeName.PLANNED),
                    actual := ObservationTypeEntity(observation_type_name=ObservationTypeName.ACTUAL),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00001",
                        capital_scheme_overviews=[build_capital_scheme_overview_entity()],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity()],
                        capital_scheme_milestones=[
                            CapitalSchemeMilestoneEntity(
                                milestone=construction_started,
                                observation_type=actual,
                                status_date=date(2020, 4, 1),
                                effective_date_from=datetime(2020, 1, 1),
                            ),
                            CapitalSchemeMilestoneEntity(
                                milestone=detailed_design_completed,
                                observation_type=actual,
                                status_date=date(2020, 3, 1),
                                effective_date_from=datetime(2020, 1, 1),
                            ),
                            CapitalSchemeMilestoneEntity(
                                milestone=detailed_design_completed,
                                observation_type=planned,
                                status_date=date(2020, 2, 1),
                                effective_date_from=datetime(2020, 1, 1),
                            ),
                        ],
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme = await capital_schemes.get(CapitalSchemeReference("ATE00001"))

        assert capital_scheme and capital_scheme.milestones == [
            CapitalSchemeMilestone(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=timezone.utc)),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.PLANNED,
                status_date=date(2020, 2, 1),
            ),
            CapitalSchemeMilestone(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=timezone.utc)),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 3, 1),
            ),
            CapitalSchemeMilestone(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=timezone.utc)),
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 4, 1),
            ),
        ]

    async def test_get_fetches_latest_authority_review(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add(
                CapitalSchemeEntity(
                    scheme_reference="ATE00001",
                    capital_scheme_overviews=[build_capital_scheme_overview_entity()],
                    capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity()],
                    capital_scheme_authority_reviews=[
                        CapitalSchemeAuthorityReviewEntity(review_date=datetime(2020, 2, 1)),
                        CapitalSchemeAuthorityReviewEntity(review_date=datetime(2020, 3, 1)),
                    ],
                )
            )

        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme = await capital_schemes.get(CapitalSchemeReference("ATE00001"))

        assert capital_scheme and capital_scheme.authority_review == CapitalSchemeAuthorityReview(
            review_date=datetime(2020, 3, 1, tzinfo=timezone.utc)
        )

    async def test_get_filters_under_embargo(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    atf3 := build_funding_programme_entity(code="ATF3", is_under_embargo=True),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00001",
                        capital_scheme_overviews=[build_capital_scheme_overview_entity(funding_programme=atf3)],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity()],
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme = await capital_schemes.get(CapitalSchemeReference("ATE00001"))

        assert not capital_scheme

    async def test_get_when_no_overview(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add(
                CapitalSchemeEntity(
                    scheme_reference="ATE00001", capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity()]
                )
            )

        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme = await capital_schemes.get(CapitalSchemeReference("ATE00001"))

        assert not capital_scheme

    async def test_get_when_no_bid_status(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add(
                CapitalSchemeEntity(
                    scheme_reference="ATE00001", capital_scheme_overviews=[build_capital_scheme_overview_entity()]
                )
            )

        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme = await capital_schemes.get(CapitalSchemeReference("ATE00001"))

        assert not capital_scheme

    async def test_get_when_not_found(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme = await capital_schemes.get(CapitalSchemeReference("ATE00001"))

        assert not capital_scheme

    async def test_get_references_by_bid_submitting_authority(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    liv := build_authority_entity(full_name="Liverpool", abbreviation="LIV"),
                    wyo := build_authority_entity(full_name="West Yorkshire", abbreviation="WYO"),
                    atf3 := build_funding_programme_entity(code="ATF3"),
                    construction := build_scheme_type_entity(name=SchemeTypeName.CONSTRUCTION),
                    funded := build_bid_status_entity(name=BidStatusName.FUNDED),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00001",
                        capital_scheme_overviews=[
                            build_capital_scheme_overview_entity(
                                bid_submitting_authority=liv, funding_programme=atf3, type_=construction
                            )
                        ],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity(bid_status=funded)],
                    ),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00002",
                        capital_scheme_overviews=[
                            build_capital_scheme_overview_entity(
                                bid_submitting_authority=liv, funding_programme=atf3, type_=construction
                            ),
                        ],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity(bid_status=funded)],
                    ),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00003",
                        capital_scheme_overviews=[
                            build_capital_scheme_overview_entity(
                                bid_submitting_authority=wyo, funding_programme=atf3, type_=construction
                            ),
                        ],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity(bid_status=funded)],
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            references = await capital_schemes.get_references_by_bid_submitting_authority(AuthorityAbbreviation("LIV"))

        assert references == [CapitalSchemeReference("ATE00001"), CapitalSchemeReference("ATE00002")]

    async def test_get_references_by_bid_submitting_authority_fetches_current_overview(
        self, engine: AsyncEngine
    ) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    liv := build_authority_entity(full_name="Liverpool", abbreviation="LIV"),
                    wyo := build_authority_entity(full_name="West Yorkshire", abbreviation="WYO"),
                    atf3 := build_funding_programme_entity(code="ATF3"),
                    construction := build_scheme_type_entity(name=SchemeTypeName.CONSTRUCTION),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00001",
                        capital_scheme_overviews=[
                            CapitalSchemeOverviewEntity(
                                scheme_name="Wirral Package",
                                bid_submitting_authority=liv,
                                funding_programme=atf3,
                                scheme_type=construction,
                                effective_date_from=datetime(2020, 1, 1),
                                effective_date_to=datetime(2020, 2, 1),
                            ),
                            CapitalSchemeOverviewEntity(
                                scheme_name="School Streets",
                                bid_submitting_authority=wyo,
                                funding_programme=atf3,
                                scheme_type=construction,
                                effective_date_from=datetime(2020, 2, 1),
                            ),
                        ],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity()],
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            references = await capital_schemes.get_references_by_bid_submitting_authority(AuthorityAbbreviation("LIV"))

        assert not references

    async def test_get_references_by_bid_submitting_authority_filters_under_embargo(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    liv := build_authority_entity(abbreviation="LIV"),
                    atf3 := build_funding_programme_entity(code="ATF3", is_under_embargo=False),
                    atf4 := build_funding_programme_entity(code="ATF4", is_under_embargo=True),
                    construction := build_scheme_type_entity(name=SchemeTypeName.CONSTRUCTION),
                    funded := build_bid_status_entity(name=BidStatusName.FUNDED),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00001",
                        capital_scheme_overviews=[
                            build_capital_scheme_overview_entity(
                                bid_submitting_authority=liv, funding_programme=atf3, type_=construction
                            ),
                        ],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity(bid_status=funded)],
                    ),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00002",
                        capital_scheme_overviews=[
                            build_capital_scheme_overview_entity(
                                bid_submitting_authority=liv, funding_programme=atf4, type_=construction
                            ),
                        ],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity(bid_status=funded)],
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            references = await capital_schemes.get_references_by_bid_submitting_authority(AuthorityAbbreviation("LIV"))

        assert references == [CapitalSchemeReference("ATE00001")]

    async def test_get_references_by_bid_submitting_authority_filters_by_funding_programme(
        self, engine: AsyncEngine
    ) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    liv := build_authority_entity(abbreviation="LIV"),
                    atf3 := build_funding_programme_entity(code="ATF3"),
                    atf4 := build_funding_programme_entity(code="ATF4"),
                    atf5 := build_funding_programme_entity(code="ATF5"),
                    construction := build_scheme_type_entity(name=SchemeTypeName.CONSTRUCTION),
                    funded := build_bid_status_entity(name=BidStatusName.FUNDED),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00001",
                        capital_scheme_overviews=[
                            build_capital_scheme_overview_entity(
                                bid_submitting_authority=liv, funding_programme=atf3, type_=construction
                            )
                        ],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity(bid_status=funded)],
                    ),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00002",
                        capital_scheme_overviews=[
                            build_capital_scheme_overview_entity(
                                bid_submitting_authority=liv, funding_programme=atf4, type_=construction
                            ),
                        ],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity(bid_status=funded)],
                    ),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00003",
                        capital_scheme_overviews=[
                            build_capital_scheme_overview_entity(
                                bid_submitting_authority=liv, funding_programme=atf5, type_=construction
                            ),
                        ],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity(bid_status=funded)],
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            references = await capital_schemes.get_references_by_bid_submitting_authority(
                AuthorityAbbreviation("LIV"),
                funding_programme_codes=[FundingProgrammeCode("ATF3"), FundingProgrammeCode("ATF4")],
            )

        assert references == [CapitalSchemeReference("ATE00001"), CapitalSchemeReference("ATE00002")]

    async def test_get_references_by_bid_submitting_authority_filters_by_current_bid_status(
        self, engine: AsyncEngine
    ) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    liv := build_authority_entity(abbreviation="LIV"),
                    atf3 := build_funding_programme_entity(code="ATF3"),
                    construction := build_scheme_type_entity(name=SchemeTypeName.CONSTRUCTION),
                    funded := build_bid_status_entity(name=BidStatusName.FUNDED),
                    not_funded := build_bid_status_entity(name=BidStatusName.NOT_FUNDED),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00001",
                        capital_scheme_overviews=[
                            build_capital_scheme_overview_entity(
                                bid_submitting_authority=liv, funding_programme=atf3, type_=construction
                            ),
                        ],
                        capital_scheme_bid_statuses=[
                            CapitalSchemeBidStatusEntity(bid_status=funded, effective_date_from=datetime(2020, 1, 1)),
                        ],
                    ),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00002",
                        capital_scheme_overviews=[
                            build_capital_scheme_overview_entity(
                                bid_submitting_authority=liv, funding_programme=atf3, type_=construction
                            )
                        ],
                        capital_scheme_bid_statuses=[
                            CapitalSchemeBidStatusEntity(
                                bid_status=funded,
                                effective_date_from=datetime(2020, 1, 1),
                                effective_date_to=datetime(2020, 2, 1),
                            ),
                            CapitalSchemeBidStatusEntity(
                                bid_status=not_funded, effective_date_from=datetime(2020, 2, 1)
                            ),
                        ],
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            references = await capital_schemes.get_references_by_bid_submitting_authority(
                AuthorityAbbreviation("LIV"), bid_status=BidStatus.FUNDED
            )

        assert references == [CapitalSchemeReference("ATE00001")]

    async def test_get_references_by_bid_submitting_authority_filters_by_current_milestones(
        self, engine: AsyncEngine
    ) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    liv := build_authority_entity(abbreviation="LIV"),
                    atf3 := build_funding_programme_entity(code="ATF3"),
                    construction := build_scheme_type_entity(name=SchemeTypeName.CONSTRUCTION),
                    funded := build_bid_status_entity(name=BidStatusName.FUNDED),
                    detailed_design_completed := MilestoneEntity(
                        milestone_name=MilestoneName.DETAILED_DESIGN_COMPLETED, stage_order=1
                    ),
                    construction_started := MilestoneEntity(
                        milestone_name=MilestoneName.CONSTRUCTION_STARTED, stage_order=2
                    ),
                    construction_completed := MilestoneEntity(
                        milestone_name=MilestoneName.CONSTRUCTION_COMPLETED, stage_order=3
                    ),
                    actual := ObservationTypeEntity(observation_type_name=ObservationTypeName.ACTUAL),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00001",
                        capital_scheme_overviews=[
                            build_capital_scheme_overview_entity(
                                bid_submitting_authority=liv, funding_programme=atf3, type_=construction
                            ),
                        ],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity(bid_status=funded)],
                        capital_scheme_milestones=[
                            CapitalSchemeMilestoneEntity(
                                milestone=detailed_design_completed,
                                status_date=date(2020, 2, 1),
                                observation_type=actual,
                                effective_date_from=datetime(2020, 1, 1),
                            ),
                        ],
                    ),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00002",
                        capital_scheme_overviews=[
                            build_capital_scheme_overview_entity(
                                bid_submitting_authority=liv, funding_programme=atf3, type_=construction
                            ),
                        ],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity(bid_status=funded)],
                        capital_scheme_milestones=[
                            CapitalSchemeMilestoneEntity(
                                milestone=construction_started,
                                status_date=date(2020, 3, 1),
                                observation_type=actual,
                                effective_date_from=datetime(2020, 1, 1),
                            ),
                        ],
                    ),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00003",
                        capital_scheme_overviews=[
                            build_capital_scheme_overview_entity(
                                bid_submitting_authority=liv, funding_programme=atf3, type_=construction
                            ),
                        ],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity(bid_status=funded)],
                        capital_scheme_milestones=[
                            CapitalSchemeMilestoneEntity(
                                milestone=construction_completed,
                                status_date=date(2020, 4, 1),
                                observation_type=actual,
                                effective_date_from=datetime(2020, 1, 1),
                            ),
                        ],
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            references = await capital_schemes.get_references_by_bid_submitting_authority(
                AuthorityAbbreviation("LIV"),
                current_milestones=[Milestone.DETAILED_DESIGN_COMPLETED, Milestone.CONSTRUCTION_STARTED],
            )

        assert references == [CapitalSchemeReference("ATE00001"), CapitalSchemeReference("ATE00002")]

    async def test_get_references_by_bid_submitting_authority_selects_actual_observation_type(
        self, engine: AsyncEngine
    ) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    liv := build_authority_entity(abbreviation="LIV"),
                    atf3 := build_funding_programme_entity(code="ATF3"),
                    construction := build_scheme_type_entity(name=SchemeTypeName.CONSTRUCTION),
                    detailed_design_completed := MilestoneEntity(
                        milestone_name=MilestoneName.DETAILED_DESIGN_COMPLETED, stage_order=1
                    ),
                    planned := ObservationTypeEntity(observation_type_name=ObservationTypeName.PLANNED),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00001",
                        capital_scheme_overviews=[
                            build_capital_scheme_overview_entity(
                                bid_submitting_authority=liv, funding_programme=atf3, type_=construction
                            ),
                        ],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity()],
                        capital_scheme_milestones=[
                            CapitalSchemeMilestoneEntity(
                                milestone=detailed_design_completed,
                                status_date=date(2020, 2, 1),
                                observation_type=planned,
                                effective_date_from=datetime(2020, 1, 1),
                            ),
                        ],
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            references = await capital_schemes.get_references_by_bid_submitting_authority(
                AuthorityAbbreviation("LIV"), current_milestones=[Milestone.DETAILED_DESIGN_COMPLETED]
            )

        assert not references

    async def test_get_references_by_bid_submitting_authority_selects_latest_milestone(
        self, engine: AsyncEngine
    ) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    liv := build_authority_entity(abbreviation="LIV"),
                    atf3 := build_funding_programme_entity(code="ATF3"),
                    construction := build_scheme_type_entity(name=SchemeTypeName.CONSTRUCTION),
                    detailed_design_completed := MilestoneEntity(
                        milestone_name=MilestoneName.DETAILED_DESIGN_COMPLETED, stage_order=1
                    ),
                    construction_started := MilestoneEntity(
                        milestone_name=MilestoneName.CONSTRUCTION_STARTED, stage_order=2
                    ),
                    actual := ObservationTypeEntity(observation_type_name=ObservationTypeName.ACTUAL),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00001",
                        capital_scheme_overviews=[
                            build_capital_scheme_overview_entity(
                                bid_submitting_authority=liv, funding_programme=atf3, type_=construction
                            ),
                        ],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity()],
                        capital_scheme_milestones=[
                            CapitalSchemeMilestoneEntity(
                                milestone=detailed_design_completed,
                                status_date=date(2020, 2, 1),
                                observation_type=actual,
                                effective_date_from=datetime(2020, 1, 1),
                            ),
                            CapitalSchemeMilestoneEntity(
                                milestone=construction_started,
                                status_date=date(2020, 2, 1),
                                observation_type=actual,
                                effective_date_from=datetime(2020, 1, 1),
                            ),
                        ],
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            references = await capital_schemes.get_references_by_bid_submitting_authority(
                AuthorityAbbreviation("LIV"), current_milestones=[Milestone.DETAILED_DESIGN_COMPLETED]
            )

        assert not references

    async def test_get_references_by_bid_submitting_authority_selects_current_milestone(
        self, engine: AsyncEngine
    ) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    liv := build_authority_entity(abbreviation="LIV"),
                    atf3 := build_funding_programme_entity(code="ATF3"),
                    construction := build_scheme_type_entity(name=SchemeTypeName.CONSTRUCTION),
                    detailed_design_completed := MilestoneEntity(
                        milestone_name=MilestoneName.DETAILED_DESIGN_COMPLETED, stage_order=1
                    ),
                    construction_started := MilestoneEntity(
                        milestone_name=MilestoneName.CONSTRUCTION_STARTED, stage_order=2
                    ),
                    actual := ObservationTypeEntity(observation_type_name=ObservationTypeName.ACTUAL),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00001",
                        capital_scheme_overviews=[
                            build_capital_scheme_overview_entity(
                                bid_submitting_authority=liv, funding_programme=atf3, type_=construction
                            ),
                        ],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity()],
                        capital_scheme_milestones=[
                            CapitalSchemeMilestoneEntity(
                                milestone=detailed_design_completed,
                                status_date=date(2020, 2, 1),
                                observation_type=actual,
                                effective_date_from=datetime(2020, 1, 1),
                                effective_date_to=datetime(2020, 2, 1),
                            ),
                            CapitalSchemeMilestoneEntity(
                                milestone=construction_started,
                                status_date=date(2020, 3, 1),
                                observation_type=actual,
                                effective_date_from=datetime(2020, 2, 1),
                            ),
                        ],
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            references = await capital_schemes.get_references_by_bid_submitting_authority(
                AuthorityAbbreviation("LIV"), current_milestones=[Milestone.DETAILED_DESIGN_COMPLETED]
            )

        assert not references

    async def test_get_references_by_bid_submitting_authority_orders_by_reference(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    liv := build_authority_entity(abbreviation="LIV"),
                    atf3 := build_funding_programme_entity(code="ATF3"),
                    construction := build_scheme_type_entity(name=SchemeTypeName.CONSTRUCTION),
                    funded := build_bid_status_entity(name=BidStatusName.FUNDED),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00002",
                        capital_scheme_overviews=[
                            build_capital_scheme_overview_entity(
                                bid_submitting_authority=liv, funding_programme=atf3, type_=construction
                            ),
                        ],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity(bid_status=funded)],
                    ),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00001",
                        capital_scheme_overviews=[
                            build_capital_scheme_overview_entity(
                                bid_submitting_authority=liv, funding_programme=atf3, type_=construction
                            ),
                        ],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity(bid_status=funded)],
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            references = await capital_schemes.get_references_by_bid_submitting_authority(AuthorityAbbreviation("LIV"))

        assert references == [CapitalSchemeReference("ATE00001"), CapitalSchemeReference("ATE00002")]

    async def test_get_references_by_bid_submitting_authority_when_no_overview(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    build_authority_entity(abbreviation="LIV"),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00001",
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity()],
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            references = await capital_schemes.get_references_by_bid_submitting_authority(AuthorityAbbreviation("LIV"))

        assert not references

    async def test_get_references_by_bid_submitting_authority_when_no_bid_status(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    liv := build_authority_entity(abbreviation="LIV"),
                    atf3 := build_funding_programme_entity(code="ATF3"),
                    construction := build_scheme_type_entity(name=SchemeTypeName.CONSTRUCTION),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00001",
                        capital_scheme_overviews=[
                            build_capital_scheme_overview_entity(
                                bid_submitting_authority=liv, funding_programme=atf3, type_=construction
                            ),
                        ],
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            references = await capital_schemes.get_references_by_bid_submitting_authority(AuthorityAbbreviation("LIV"))

        assert not references

    async def test_get_references_by_bid_submitting_authority_when_none(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add(build_authority_entity(abbreviation="LIV"))

        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            references = await capital_schemes.get_references_by_bid_submitting_authority(AuthorityAbbreviation("LIV"))

        assert not references
