from datetime import UTC, date, datetime
from decimal import Decimal

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from ate_api.domain.authorities import AuthorityAbbreviation
from ate_api.domain.capital_scheme_milestones import Milestone
from ate_api.domain.capital_schemes.authority_reviews import CapitalSchemeAuthorityReview
from ate_api.domain.capital_schemes.bid_statuses import BidStatus, CapitalSchemeBidStatusDetails
from ate_api.domain.capital_schemes.capital_scheme_repositories import CapitalSchemeItem
from ate_api.domain.capital_schemes.capital_schemes import CapitalScheme, CapitalSchemeReference
from ate_api.domain.capital_schemes.outputs import CapitalSchemeOutput, OutputMeasure, OutputType
from ate_api.domain.capital_schemes.overviews import CapitalSchemeOverview, CapitalSchemeType
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.funding_programmes import FundingProgrammeCode
from ate_api.domain.observation_types import ObservationType
from ate_api.infrastructure.database import (
    BidStatusName,
    CapitalSchemeAuthorityReviewEntity,
    CapitalSchemeBidStatusEntity,
    CapitalSchemeEntity,
    CapitalSchemeInterventionEntity,
    CapitalSchemeMilestoneEntity,
    CapitalSchemeOverviewEntity,
    DataSourceName,
    InterventionMeasureName,
    InterventionTypeName,
    MilestoneName,
    ObservationTypeName,
    SchemeTypeName,
)
from ate_api.infrastructure.database.capital_schemes.capital_scheme_repositories import DatabaseCapitalSchemeRepository
from tests.unit.domain.dummies import dummy_bid_status_details, dummy_overview
from tests.unit.infrastructure.database.builders import (
    build_authority_entity,
    build_bid_status_entity,
    build_capital_scheme_bid_status_entity,
    build_capital_scheme_overview_entity,
    build_data_source_entity,
    build_funding_programme_entity,
    build_intervention_measure_entity,
    build_intervention_type_entity,
    build_intervention_type_measure_entity,
    build_milestone_entity,
    build_observation_type_entity,
    build_scheme_type_entity,
)


@pytest.mark.usefixtures("data")
@pytest.mark.asyncio(loop_scope="package")
class TestDatabaseCapitalSchemeRepository:
    async def test_add(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    build_authority_entity(id_=1, abbreviation="LIV"),
                    build_funding_programme_entity(id_=1, code="ATF3"),
                    build_scheme_type_entity(id_=1, name=SchemeTypeName.CONSTRUCTION),
                    build_bid_status_entity(id_=1, name=BidStatusName.FUNDED),
                ]
            )

        async with AsyncSession(engine) as session, session.begin():
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            await capital_schemes.add(
                CapitalScheme(
                    reference=CapitalSchemeReference("ATE00001"),
                    overview=CapitalSchemeOverview(
                        effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                        name="Wirral Package",
                        bid_submitting_authority=AuthorityAbbreviation("LIV"),
                        funding_programme=FundingProgrammeCode("ATF3"),
                        type=CapitalSchemeType.CONSTRUCTION,
                    ),
                    bid_status_details=CapitalSchemeBidStatusDetails(
                        effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)), bid_status=BidStatus.FUNDED
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

    async def test_add_stores_outputs(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    build_authority_entity(),
                    build_funding_programme_entity(),
                    build_scheme_type_entity(),
                    build_bid_status_entity(),
                    widening_existing_footway := build_intervention_type_entity(
                        name=InterventionTypeName.WIDENING_EXISTING_FOOTWAY
                    ),
                    new_segregated_cycling_facility := build_intervention_type_entity(
                        name=InterventionTypeName.NEW_SEGREGATED_CYCLING_FACILITY
                    ),
                    miles := build_intervention_measure_entity(name=InterventionMeasureName.MILES),
                    build_intervention_type_measure_entity(id_=1, type_=widening_existing_footway, measure=miles),
                    build_intervention_type_measure_entity(id_=2, type_=new_segregated_cycling_facility, measure=miles),
                    build_observation_type_entity(id_=1, name=ObservationTypeName.ACTUAL),
                ]
            )

        async with AsyncSession(engine) as session, session.begin():
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme = CapitalScheme(
                reference=CapitalSchemeReference("ATE00001"),
                overview=dummy_overview(),
                bid_status_details=dummy_bid_status_details(),
            )
            capital_scheme.change_output(
                CapitalSchemeOutput(
                    effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                    type=OutputType.WIDENING_EXISTING_FOOTWAY,
                    measure=OutputMeasure.MILES,
                    observation_type=ObservationType.ACTUAL,
                    value=Decimal(1.5),
                )
            )
            capital_scheme.change_output(
                CapitalSchemeOutput(
                    effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                    type=OutputType.NEW_SEGREGATED_CYCLING_FACILITY,
                    measure=OutputMeasure.MILES,
                    observation_type=ObservationType.ACTUAL,
                    value=Decimal(2),
                )
            )
            await capital_schemes.add(capital_scheme)

        async with AsyncSession(engine) as session:
            (capital_scheme_row,) = await session.scalars(select(CapitalSchemeEntity))
            intervention_row1, intervention_row2 = await session.scalars(select(CapitalSchemeInterventionEntity))
        assert (
            intervention_row1.capital_scheme_id == capital_scheme_row.capital_scheme_id
            and intervention_row1.intervention_type_measure_id == 1
            and intervention_row1.intervention_value == Decimal(1.5)
            and intervention_row1.observation_type_id == 1
            and intervention_row1.effective_date_from == datetime(2020, 1, 1)
            and not intervention_row1.effective_date_to
        )
        assert (
            intervention_row2.capital_scheme_id == capital_scheme_row.capital_scheme_id
            and intervention_row2.intervention_type_measure_id == 2
            and intervention_row2.intervention_value == Decimal(2)
            and intervention_row2.observation_type_id == 1
            and intervention_row2.effective_date_from == datetime(2020, 1, 1)
            and not intervention_row2.effective_date_to
        )

    async def test_add_stores_authority_review(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    build_authority_entity(),
                    build_funding_programme_entity(),
                    build_scheme_type_entity(),
                    build_bid_status_entity(),
                    build_data_source_entity(id_=1, name=DataSourceName.AUTHORITY_UPDATE),
                ]
            )

        async with AsyncSession(engine) as session, session.begin():
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme = CapitalScheme(
                reference=CapitalSchemeReference("ATE00001"),
                overview=dummy_overview(),
                bid_status_details=dummy_bid_status_details(),
            )
            capital_scheme.perform_authority_review(
                CapitalSchemeAuthorityReview(
                    review_date=datetime(2020, 2, 1, tzinfo=UTC), data_source=DataSource.AUTHORITY_UPDATE
                )
            )
            await capital_schemes.add(capital_scheme)

        async with AsyncSession(engine) as session:
            (capital_scheme_row,) = await session.scalars(select(CapitalSchemeEntity))
            (authority_review_row,) = await session.scalars(select(CapitalSchemeAuthorityReviewEntity))
        assert (
            authority_review_row.capital_scheme_id == capital_scheme_row.capital_scheme_id
            and authority_review_row.review_date == datetime(2020, 2, 1)
            and authority_review_row.data_source_id == 1
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
                            )
                        ],
                        capital_scheme_bid_statuses=[
                            CapitalSchemeBidStatusEntity(bid_status=funded, effective_date_from=datetime(2020, 1, 1))
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
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            name="Wirral Package",
            bid_submitting_authority=AuthorityAbbreviation("LIV"),
            funding_programme=FundingProgrammeCode("ATF3"),
            type=CapitalSchemeType.CONSTRUCTION,
        )
        assert capital_scheme.bid_status_details == CapitalSchemeBidStatusDetails(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)), bid_status=BidStatus.FUNDED
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
            effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)),
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
            effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)), bid_status=BidStatus.NOT_FUNDED
        )

    async def test_get_fetches_current_outputs(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    widening_existing_footway := build_intervention_type_entity(
                        name=InterventionTypeName.WIDENING_EXISTING_FOOTWAY
                    ),
                    new_segregated_cycling_facility := build_intervention_type_entity(
                        name=InterventionTypeName.NEW_SEGREGATED_CYCLING_FACILITY
                    ),
                    miles := build_intervention_measure_entity(name=InterventionMeasureName.MILES),
                    widening_existing_footway_miles := build_intervention_type_measure_entity(
                        type_=widening_existing_footway, measure=miles
                    ),
                    new_segregated_cycling_facility_miles := build_intervention_type_measure_entity(
                        type_=new_segregated_cycling_facility, measure=miles
                    ),
                    actual := build_observation_type_entity(name=ObservationTypeName.ACTUAL),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00001",
                        capital_scheme_overviews=[build_capital_scheme_overview_entity()],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity()],
                        capital_scheme_interventions=[
                            CapitalSchemeInterventionEntity(
                                intervention_type_measure=widening_existing_footway_miles,
                                intervention_value=Decimal("1.000000"),
                                observation_type=actual,
                                effective_date_from=datetime(2020, 1, 1),
                                effective_date_to=datetime(2020, 2, 1),
                            ),
                            CapitalSchemeInterventionEntity(
                                intervention_type_measure=widening_existing_footway_miles,
                                intervention_value=Decimal("1.500000"),
                                observation_type=actual,
                                effective_date_from=datetime(2020, 2, 1),
                            ),
                            CapitalSchemeInterventionEntity(
                                intervention_type_measure=new_segregated_cycling_facility_miles,
                                intervention_value=Decimal("2.000000"),
                                observation_type=actual,
                                effective_date_from=datetime(2020, 2, 1),
                            ),
                        ],
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme = await capital_schemes.get(CapitalSchemeReference("ATE00001"))

        assert capital_scheme and capital_scheme.outputs == [
            CapitalSchemeOutput(
                effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)),
                type=OutputType.WIDENING_EXISTING_FOOTWAY,
                measure=OutputMeasure.MILES,
                observation_type=ObservationType.ACTUAL,
                value=Decimal(1.5),
            ),
            CapitalSchemeOutput(
                effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)),
                type=OutputType.NEW_SEGREGATED_CYCLING_FACILITY,
                measure=OutputMeasure.MILES,
                observation_type=ObservationType.ACTUAL,
                value=Decimal(2),
            ),
        ]

    async def test_get_fetches_current_outputs_ordered_by_type_then_measure(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    widening_existing_footway := build_intervention_type_entity(
                        name=InterventionTypeName.WIDENING_EXISTING_FOOTWAY
                    ),
                    new_segregated_cycling_facility := build_intervention_type_entity(
                        name=InterventionTypeName.NEW_SEGREGATED_CYCLING_FACILITY
                    ),
                    miles := build_intervention_measure_entity(name=InterventionMeasureName.MILES),
                    number_of_junctions := build_intervention_measure_entity(
                        name=InterventionMeasureName.NUMBER_OF_JUNCTIONS
                    ),
                    widening_existing_footway_miles := build_intervention_type_measure_entity(
                        type_=widening_existing_footway, measure=miles
                    ),
                    new_segregated_cycling_facility_miles := build_intervention_type_measure_entity(
                        type_=new_segregated_cycling_facility, measure=miles
                    ),
                    new_segregated_cycling_facility_number_of_junctions := build_intervention_type_measure_entity(
                        type_=new_segregated_cycling_facility, measure=number_of_junctions
                    ),
                    actual := build_observation_type_entity(name=ObservationTypeName.ACTUAL),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00001",
                        capital_scheme_overviews=[build_capital_scheme_overview_entity()],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity()],
                        capital_scheme_interventions=[
                            CapitalSchemeInterventionEntity(
                                intervention_type_measure=new_segregated_cycling_facility_number_of_junctions,
                                intervention_value=Decimal("3.000000"),
                                observation_type=actual,
                                effective_date_from=datetime(2020, 1, 1),
                            ),
                            CapitalSchemeInterventionEntity(
                                intervention_type_measure=new_segregated_cycling_facility_miles,
                                intervention_value=Decimal("2.000000"),
                                observation_type=actual,
                                effective_date_from=datetime(2020, 1, 1),
                            ),
                            CapitalSchemeInterventionEntity(
                                intervention_type_measure=widening_existing_footway_miles,
                                intervention_value=Decimal("1.500000"),
                                observation_type=actual,
                                effective_date_from=datetime(2020, 1, 1),
                            ),
                        ],
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme = await capital_schemes.get(CapitalSchemeReference("ATE00001"))

        assert capital_scheme and capital_scheme.outputs == [
            CapitalSchemeOutput(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                type=OutputType.WIDENING_EXISTING_FOOTWAY,
                measure=OutputMeasure.MILES,
                observation_type=ObservationType.ACTUAL,
                value=Decimal(1.5),
            ),
            CapitalSchemeOutput(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                type=OutputType.NEW_SEGREGATED_CYCLING_FACILITY,
                measure=OutputMeasure.MILES,
                observation_type=ObservationType.ACTUAL,
                value=Decimal(2),
            ),
            CapitalSchemeOutput(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                type=OutputType.NEW_SEGREGATED_CYCLING_FACILITY,
                measure=OutputMeasure.NUMBER_OF_JUNCTIONS,
                observation_type=ObservationType.ACTUAL,
                value=Decimal(3),
            ),
        ]

    async def test_get_fetches_latest_authority_review(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    authority_review := build_data_source_entity(name=DataSourceName.AUTHORITY_UPDATE),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00001",
                        capital_scheme_overviews=[build_capital_scheme_overview_entity()],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity()],
                        capital_scheme_authority_reviews=[
                            CapitalSchemeAuthorityReviewEntity(
                                review_date=datetime(2020, 2, 1), data_source=authority_review
                            ),
                            CapitalSchemeAuthorityReviewEntity(
                                review_date=datetime(2020, 3, 1), data_source=authority_review
                            ),
                        ],
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme = await capital_schemes.get(CapitalSchemeReference("ATE00001"))

        assert capital_scheme and capital_scheme.authority_review == CapitalSchemeAuthorityReview(
            review_date=datetime(2020, 3, 1, tzinfo=UTC), data_source=DataSource.AUTHORITY_UPDATE
        )

    async def test_get_fetches_latest_authority_review_when_tie(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    authority_review := build_data_source_entity(name=DataSourceName.AUTHORITY_UPDATE),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00001",
                        capital_scheme_overviews=[build_capital_scheme_overview_entity()],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity()],
                        capital_scheme_authority_reviews=[
                            CapitalSchemeAuthorityReviewEntity(
                                review_date=datetime(2020, 2, 1), data_source=authority_review
                            ),
                            CapitalSchemeAuthorityReviewEntity(
                                review_date=datetime(2020, 2, 1), data_source=authority_review
                            ),
                        ],
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme = await capital_schemes.get(CapitalSchemeReference("ATE00001"))

        assert capital_scheme and capital_scheme.authority_review == CapitalSchemeAuthorityReview(
            review_date=datetime(2020, 2, 1, tzinfo=UTC), data_source=DataSource.AUTHORITY_UPDATE
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

    async def test_get_items_by_bid_submitting_authority(self, engine: AsyncEngine) -> None:
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
                            CapitalSchemeOverviewEntity(
                                scheme_name="Wirral Package",
                                bid_submitting_authority=liv,
                                funding_programme=atf3,
                                scheme_type=construction,
                                effective_date_from=datetime(2020, 1, 1),
                            )
                        ],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity(bid_status=funded)],
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
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity(bid_status=funded)],
                    ),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00003",
                        capital_scheme_overviews=[
                            CapitalSchemeOverviewEntity(
                                scheme_name="Hospital Fields Road",
                                bid_submitting_authority=wyo,
                                funding_programme=atf3,
                                scheme_type=construction,
                                effective_date_from=datetime(2020, 1, 1),
                            )
                        ],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity(bid_status=funded)],
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme_items = await capital_schemes.get_items_by_bid_submitting_authority(
                AuthorityAbbreviation("LIV")
            )

        assert capital_scheme_items == [
            CapitalSchemeItem(
                reference=CapitalSchemeReference("ATE00001"),
                overview=CapitalSchemeOverview(
                    effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                    name="Wirral Package",
                    bid_submitting_authority=AuthorityAbbreviation("LIV"),
                    funding_programme=FundingProgrammeCode("ATF3"),
                    type=CapitalSchemeType.CONSTRUCTION,
                ),
                authority_review=None,
            ),
            CapitalSchemeItem(
                reference=CapitalSchemeReference("ATE00002"),
                overview=CapitalSchemeOverview(
                    effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                    name="School Streets",
                    bid_submitting_authority=AuthorityAbbreviation("LIV"),
                    funding_programme=FundingProgrammeCode("ATF3"),
                    type=CapitalSchemeType.CONSTRUCTION,
                ),
                authority_review=None,
            ),
        ]

    async def test_get_items_by_bid_submitting_authority_fetches_current_overview(self, engine: AsyncEngine) -> None:
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
            capital_scheme_items = await capital_schemes.get_items_by_bid_submitting_authority(
                AuthorityAbbreviation("LIV")
            )

        assert not capital_scheme_items

    async def test_get_items_by_bid_submitting_authority_fetches_latest_authority_review(
        self, engine: AsyncEngine
    ) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    liv := build_authority_entity(abbreviation="LIV"),
                    authority_review := build_data_source_entity(name=DataSourceName.AUTHORITY_UPDATE),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00001",
                        capital_scheme_overviews=[build_capital_scheme_overview_entity(bid_submitting_authority=liv)],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity()],
                        capital_scheme_authority_reviews=[
                            CapitalSchemeAuthorityReviewEntity(
                                review_date=datetime(2020, 2, 1), data_source=authority_review
                            ),
                            CapitalSchemeAuthorityReviewEntity(
                                review_date=datetime(2020, 3, 1), data_source=authority_review
                            ),
                        ],
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme_items = await capital_schemes.get_items_by_bid_submitting_authority(
                AuthorityAbbreviation("LIV")
            )

        assert [capital_scheme_item.authority_review for capital_scheme_item in capital_scheme_items] == [
            CapitalSchemeAuthorityReview(
                review_date=datetime(2020, 3, 1, tzinfo=UTC), data_source=DataSource.AUTHORITY_UPDATE
            )
        ]

    async def test_get_items_by_bid_submitting_authority_fetches_latest_authority_review_when_tie(
        self, engine: AsyncEngine
    ) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    liv := build_authority_entity(abbreviation="LIV"),
                    authority_review := build_data_source_entity(name=DataSourceName.AUTHORITY_UPDATE),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00001",
                        capital_scheme_overviews=[build_capital_scheme_overview_entity(bid_submitting_authority=liv)],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity()],
                        capital_scheme_authority_reviews=[
                            CapitalSchemeAuthorityReviewEntity(
                                review_date=datetime(2020, 2, 1), data_source=authority_review
                            ),
                            CapitalSchemeAuthorityReviewEntity(
                                review_date=datetime(2020, 2, 1), data_source=authority_review
                            ),
                        ],
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme_items = await capital_schemes.get_items_by_bid_submitting_authority(
                AuthorityAbbreviation("LIV")
            )

        assert [capital_scheme_item.authority_review for capital_scheme_item in capital_scheme_items] == [
            CapitalSchemeAuthorityReview(
                review_date=datetime(2020, 2, 1, tzinfo=UTC), data_source=DataSource.AUTHORITY_UPDATE
            )
        ]

    async def test_get_items_by_bid_submitting_authority_filters_under_embargo(self, engine: AsyncEngine) -> None:
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
                            )
                        ],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity(bid_status=funded)],
                    ),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00002",
                        capital_scheme_overviews=[
                            build_capital_scheme_overview_entity(
                                bid_submitting_authority=liv, funding_programme=atf4, type_=construction
                            )
                        ],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity(bid_status=funded)],
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme_items = await capital_schemes.get_items_by_bid_submitting_authority(
                AuthorityAbbreviation("LIV")
            )

        assert [capital_scheme_item.reference for capital_scheme_item in capital_scheme_items] == [
            CapitalSchemeReference("ATE00001")
        ]

    async def test_get_items_by_bid_submitting_authority_filters_by_funding_programme(
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
                            )
                        ],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity(bid_status=funded)],
                    ),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00003",
                        capital_scheme_overviews=[
                            build_capital_scheme_overview_entity(
                                bid_submitting_authority=liv, funding_programme=atf5, type_=construction
                            )
                        ],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity(bid_status=funded)],
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme_items = await capital_schemes.get_items_by_bid_submitting_authority(
                AuthorityAbbreviation("LIV"),
                funding_programme_codes=[FundingProgrammeCode("ATF3"), FundingProgrammeCode("ATF4")],
            )

        assert [capital_scheme_item.reference for capital_scheme_item in capital_scheme_items] == [
            CapitalSchemeReference("ATE00001"),
            CapitalSchemeReference("ATE00002"),
        ]

    async def test_get_items_by_bid_submitting_authority_filters_by_current_bid_status(
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
                            )
                        ],
                        capital_scheme_bid_statuses=[
                            CapitalSchemeBidStatusEntity(bid_status=funded, effective_date_from=datetime(2020, 1, 1))
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
            capital_scheme_items = await capital_schemes.get_items_by_bid_submitting_authority(
                AuthorityAbbreviation("LIV"), bid_status=BidStatus.FUNDED
            )

        assert [capital_scheme_item.reference for capital_scheme_item in capital_scheme_items] == [
            CapitalSchemeReference("ATE00001")
        ]

    async def test_get_items_by_bid_submitting_authority_filters_by_current_milestones(
        self, engine: AsyncEngine
    ) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    liv := build_authority_entity(abbreviation="LIV"),
                    atf3 := build_funding_programme_entity(code="ATF3"),
                    construction := build_scheme_type_entity(name=SchemeTypeName.CONSTRUCTION),
                    funded := build_bid_status_entity(name=BidStatusName.FUNDED),
                    detailed_design_completed := build_milestone_entity(name=MilestoneName.DETAILED_DESIGN_COMPLETED),
                    construction_started := build_milestone_entity(name=MilestoneName.CONSTRUCTION_STARTED),
                    construction_completed := build_milestone_entity(name=MilestoneName.CONSTRUCTION_COMPLETED),
                    actual := build_observation_type_entity(name=ObservationTypeName.ACTUAL),
                    atf4_bid := build_data_source_entity(name=DataSourceName.ATF4_BID),
                    CapitalSchemeEntity(
                        capital_scheme_id=1,
                        scheme_reference="ATE00001",
                        capital_scheme_overviews=[
                            build_capital_scheme_overview_entity(
                                bid_submitting_authority=liv, funding_programme=atf3, type_=construction
                            )
                        ],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity(bid_status=funded)],
                    ),
                    CapitalSchemeMilestoneEntity(
                        capital_scheme_id=1,
                        milestone=detailed_design_completed,
                        status_date=date(2020, 2, 1),
                        observation_type=actual,
                        data_source=atf4_bid,
                        effective_date_from=datetime(2020, 1, 1),
                    ),
                    CapitalSchemeEntity(
                        capital_scheme_id=2,
                        scheme_reference="ATE00002",
                        capital_scheme_overviews=[
                            build_capital_scheme_overview_entity(
                                bid_submitting_authority=liv, funding_programme=atf3, type_=construction
                            )
                        ],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity(bid_status=funded)],
                    ),
                    CapitalSchemeMilestoneEntity(
                        capital_scheme_id=2,
                        milestone=construction_started,
                        status_date=date(2020, 3, 1),
                        observation_type=actual,
                        data_source=atf4_bid,
                        effective_date_from=datetime(2020, 1, 1),
                    ),
                    CapitalSchemeEntity(
                        capital_scheme_id=3,
                        scheme_reference="ATE00003",
                        capital_scheme_overviews=[
                            build_capital_scheme_overview_entity(
                                bid_submitting_authority=liv, funding_programme=atf3, type_=construction
                            )
                        ],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity(bid_status=funded)],
                    ),
                    CapitalSchemeMilestoneEntity(
                        capital_scheme_id=3,
                        milestone=construction_completed,
                        status_date=date(2020, 4, 1),
                        observation_type=actual,
                        data_source=atf4_bid,
                        effective_date_from=datetime(2020, 1, 1),
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme_items = await capital_schemes.get_items_by_bid_submitting_authority(
                AuthorityAbbreviation("LIV"),
                current_milestones=[Milestone.DETAILED_DESIGN_COMPLETED, Milestone.CONSTRUCTION_STARTED],
            )

        assert [capital_scheme_item.reference for capital_scheme_item in capital_scheme_items] == [
            CapitalSchemeReference("ATE00001"),
            CapitalSchemeReference("ATE00002"),
        ]

    async def test_get_items_by_bid_submitting_authority_filters_by_no_current_milestone(
        self, engine: AsyncEngine
    ) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    liv := build_authority_entity(abbreviation="LIV"),
                    atf3 := build_funding_programme_entity(code="ATF3"),
                    construction := build_scheme_type_entity(name=SchemeTypeName.CONSTRUCTION),
                    funded := build_bid_status_entity(name=BidStatusName.FUNDED),
                    construction_started := build_milestone_entity(name=MilestoneName.CONSTRUCTION_STARTED),
                    actual := build_observation_type_entity(name=ObservationTypeName.ACTUAL),
                    atf4_bid := build_data_source_entity(name=DataSourceName.ATF4_BID),
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
                        capital_scheme_id=2,
                        scheme_reference="ATE00002",
                        capital_scheme_overviews=[
                            build_capital_scheme_overview_entity(
                                bid_submitting_authority=liv, funding_programme=atf3, type_=construction
                            )
                        ],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity(bid_status=funded)],
                    ),
                    CapitalSchemeMilestoneEntity(
                        capital_scheme_id=2,
                        milestone=construction_started,
                        status_date=date(2020, 3, 1),
                        observation_type=actual,
                        data_source=atf4_bid,
                        effective_date_from=datetime(2020, 1, 1),
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme_items = await capital_schemes.get_items_by_bid_submitting_authority(
                AuthorityAbbreviation("LIV"), current_milestones=[None]
            )

        assert [capital_scheme_item.reference for capital_scheme_item in capital_scheme_items] == [
            CapitalSchemeReference("ATE00001")
        ]

    async def test_get_items_by_bid_submitting_authority_selects_actual_observation_type(
        self, engine: AsyncEngine
    ) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    liv := build_authority_entity(abbreviation="LIV"),
                    atf3 := build_funding_programme_entity(code="ATF3"),
                    construction := build_scheme_type_entity(name=SchemeTypeName.CONSTRUCTION),
                    detailed_design_completed := build_milestone_entity(name=MilestoneName.DETAILED_DESIGN_COMPLETED),
                    planned := build_observation_type_entity(name=ObservationTypeName.PLANNED),
                    atf4_bid := build_data_source_entity(name=DataSourceName.ATF4_BID),
                    CapitalSchemeEntity(
                        capital_scheme_id=1,
                        scheme_reference="ATE00001",
                        capital_scheme_overviews=[
                            build_capital_scheme_overview_entity(
                                bid_submitting_authority=liv, funding_programme=atf3, type_=construction
                            )
                        ],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity()],
                    ),
                    CapitalSchemeMilestoneEntity(
                        capital_scheme_id=1,
                        milestone=detailed_design_completed,
                        status_date=date(2020, 2, 1),
                        observation_type=planned,
                        data_source=atf4_bid,
                        effective_date_from=datetime(2020, 1, 1),
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme_items = await capital_schemes.get_items_by_bid_submitting_authority(
                AuthorityAbbreviation("LIV"), current_milestones=[Milestone.DETAILED_DESIGN_COMPLETED]
            )

        assert not capital_scheme_items

    async def test_get_items_by_bid_submitting_authority_selects_latest_milestone(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    liv := build_authority_entity(abbreviation="LIV"),
                    atf3 := build_funding_programme_entity(code="ATF3"),
                    construction := build_scheme_type_entity(name=SchemeTypeName.CONSTRUCTION),
                    detailed_design_completed := build_milestone_entity(
                        name=MilestoneName.DETAILED_DESIGN_COMPLETED, stage_order=1
                    ),
                    construction_started := build_milestone_entity(
                        name=MilestoneName.CONSTRUCTION_STARTED, stage_order=2
                    ),
                    actual := build_observation_type_entity(name=ObservationTypeName.ACTUAL),
                    atf4_bid := build_data_source_entity(name=DataSourceName.ATF4_BID),
                    CapitalSchemeEntity(
                        capital_scheme_id=1,
                        scheme_reference="ATE00001",
                        capital_scheme_overviews=[
                            build_capital_scheme_overview_entity(
                                bid_submitting_authority=liv, funding_programme=atf3, type_=construction
                            )
                        ],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity()],
                    ),
                    CapitalSchemeMilestoneEntity(
                        capital_scheme_id=1,
                        milestone=detailed_design_completed,
                        status_date=date(2020, 2, 1),
                        observation_type=actual,
                        data_source=atf4_bid,
                        effective_date_from=datetime(2020, 1, 1),
                    ),
                    CapitalSchemeMilestoneEntity(
                        capital_scheme_id=1,
                        milestone=construction_started,
                        status_date=date(2020, 2, 1),
                        observation_type=actual,
                        data_source=atf4_bid,
                        effective_date_from=datetime(2020, 1, 1),
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme_items = await capital_schemes.get_items_by_bid_submitting_authority(
                AuthorityAbbreviation("LIV"), current_milestones=[Milestone.DETAILED_DESIGN_COMPLETED]
            )

        assert not capital_scheme_items

    async def test_get_items_by_bid_submitting_authority_selects_current_milestone(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    liv := build_authority_entity(abbreviation="LIV"),
                    atf3 := build_funding_programme_entity(code="ATF3"),
                    construction := build_scheme_type_entity(name=SchemeTypeName.CONSTRUCTION),
                    detailed_design_completed := build_milestone_entity(name=MilestoneName.DETAILED_DESIGN_COMPLETED),
                    construction_started := build_milestone_entity(name=MilestoneName.CONSTRUCTION_STARTED),
                    actual := build_observation_type_entity(name=ObservationTypeName.ACTUAL),
                    atf4_bid := build_data_source_entity(name=DataSourceName.ATF4_BID),
                    CapitalSchemeEntity(
                        capital_scheme_id=1,
                        scheme_reference="ATE00001",
                        capital_scheme_overviews=[
                            build_capital_scheme_overview_entity(
                                bid_submitting_authority=liv, funding_programme=atf3, type_=construction
                            )
                        ],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity()],
                    ),
                    CapitalSchemeMilestoneEntity(
                        capital_scheme_id=1,
                        milestone=detailed_design_completed,
                        status_date=date(2020, 2, 1),
                        observation_type=actual,
                        data_source=atf4_bid,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=datetime(2020, 2, 1),
                    ),
                    CapitalSchemeMilestoneEntity(
                        capital_scheme_id=1,
                        milestone=construction_started,
                        status_date=date(2020, 3, 1),
                        observation_type=actual,
                        data_source=atf4_bid,
                        effective_date_from=datetime(2020, 2, 1),
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme_items = await capital_schemes.get_items_by_bid_submitting_authority(
                AuthorityAbbreviation("LIV"), current_milestones=[Milestone.DETAILED_DESIGN_COMPLETED]
            )

        assert not capital_scheme_items

    async def test_get_items_by_bid_submitting_authority_orders_by_reference(self, engine: AsyncEngine) -> None:
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
                            )
                        ],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity(bid_status=funded)],
                    ),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00001",
                        capital_scheme_overviews=[
                            build_capital_scheme_overview_entity(
                                bid_submitting_authority=liv, funding_programme=atf3, type_=construction
                            )
                        ],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity(bid_status=funded)],
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme_items = await capital_schemes.get_items_by_bid_submitting_authority(
                AuthorityAbbreviation("LIV")
            )

        assert [capital_scheme_item.reference for capital_scheme_item in capital_scheme_items] == [
            CapitalSchemeReference("ATE00001"),
            CapitalSchemeReference("ATE00002"),
        ]

    async def test_get_items_by_bid_submitting_authority_when_no_overview(self, engine: AsyncEngine) -> None:
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
            capital_scheme_items = await capital_schemes.get_items_by_bid_submitting_authority(
                AuthorityAbbreviation("LIV")
            )

        assert not capital_scheme_items

    async def test_get_items_by_bid_submitting_authority_when_no_bid_status(self, engine: AsyncEngine) -> None:
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
                            )
                        ],
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme_items = await capital_schemes.get_items_by_bid_submitting_authority(
                AuthorityAbbreviation("LIV")
            )

        assert not capital_scheme_items

    async def test_get_items_by_bid_submitting_authority_when_none(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add(build_authority_entity(abbreviation="LIV"))

        async with AsyncSession(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme_items = await capital_schemes.get_items_by_bid_submitting_authority(
                AuthorityAbbreviation("LIV")
            )

        assert not capital_scheme_items

    async def test_update_updates_authority_review(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    authority_update := build_data_source_entity(id_=1, name=DataSourceName.AUTHORITY_UPDATE),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00001",
                        capital_scheme_overviews=[build_capital_scheme_overview_entity()],
                        capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity()],
                        capital_scheme_authority_reviews=[
                            CapitalSchemeAuthorityReviewEntity(
                                review_date=datetime(2020, 2, 1), data_source=authority_update
                            )
                        ],
                    ),
                ]
            )

        async with AsyncSession(engine) as session, session.begin():
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme = await capital_schemes.get(CapitalSchemeReference("ATE00001"))
            assert capital_scheme
            capital_scheme.perform_authority_review(
                CapitalSchemeAuthorityReview(
                    review_date=datetime(2020, 3, 1, tzinfo=UTC), data_source=DataSource.AUTHORITY_UPDATE
                )
            )
            await capital_schemes.update(capital_scheme)

        async with AsyncSession(engine) as session:
            (capital_scheme_row,) = await session.scalars(select(CapitalSchemeEntity))
            _, authority_review_row2 = await session.scalars(select(CapitalSchemeAuthorityReviewEntity))
        assert (
            authority_review_row2.capital_scheme_id == capital_scheme_row.capital_scheme_id
            and authority_review_row2.review_date == datetime(2020, 3, 1)
            and authority_review_row2.data_source_id == 1
        )

    async def test_update_when_no_authority_review(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add(
                CapitalSchemeEntity(
                    scheme_reference="ATE00001",
                    capital_scheme_overviews=[build_capital_scheme_overview_entity()],
                    capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity()],
                )
            )

        async with AsyncSession(engine) as session, session.begin():
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme = await capital_schemes.get(CapitalSchemeReference("ATE00001"))
            assert capital_scheme
            await capital_schemes.update(capital_scheme)

        async with AsyncSession(engine) as session:
            authority_review_count = await session.scalar(
                select(func.count()).select_from(CapitalSchemeAuthorityReviewEntity)
            )
        assert authority_review_count == 0
