from datetime import datetime, timezone

import pytest
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from ate_api.domain.capital_schemes.authority_reviews import CapitalSchemeAuthorityReview
from ate_api.domain.capital_schemes.bid_statuses import CapitalSchemeBidStatus, CapitalSchemeBidStatusDetails
from ate_api.domain.capital_schemes.capital_schemes import CapitalScheme
from ate_api.domain.capital_schemes.overviews import CapitalSchemeOverview, CapitalSchemeType
from ate_api.domain.dates import DateTimeRange
from ate_api.infrastructure.database import (
    AuthorityEntity,
    BidStatusEntity,
    BidStatusName,
    CapitalSchemeAuthorityReviewEntity,
    CapitalSchemeBidStatusEntity,
    CapitalSchemeEntity,
    CapitalSchemeOverviewEntity,
    FundingProgrammeEntity,
    SchemeTypeEntity,
    SchemeTypeName,
)
from ate_api.infrastructure.database.capital_schemes.capital_schemes import DatabaseCapitalSchemeRepository
from tests.unit.domain.dummies import dummy_bid_status_details, dummy_overview
from tests.unit.infrastructure.database.dummies import dummy_bid_status_entity, dummy_overview_entity


class TestCapitalSchemeEntity:
    def test_from_domain(self) -> None:
        capital_scheme = CapitalScheme(
            reference="ATE00001",
            overview=CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1)),
                name="Wirral Package",
                bid_submitting_authority="LIV",
                funding_programme="ATF3",
                type=CapitalSchemeType.CONSTRUCTION,
            ),
            bid_status_details=CapitalSchemeBidStatusDetails(
                effective_date=DateTimeRange(datetime(2020, 2, 1)),
                bid_status=CapitalSchemeBidStatus.FUNDED,
            ),
        )

        capital_scheme_entity = CapitalSchemeEntity.from_domain(
            capital_scheme, {"LIV": 1}, {"ATF3": 1}, {SchemeTypeName.CONSTRUCTION: 1}, {BidStatusName.FUNDED: 1}
        )

        assert capital_scheme_entity.scheme_reference == "ATE00001"
        (overview_entity,) = capital_scheme_entity.capital_scheme_overviews
        assert (
            overview_entity.scheme_name == "Wirral Package"
            and overview_entity.bid_submitting_authority_id == 1
            and overview_entity.funding_programme_id == 1
            and overview_entity.scheme_type_id == 1
            and overview_entity.effective_date_from == datetime(2020, 1, 1)
            and overview_entity.effective_date_to is None
        )
        (bid_status_entity,) = capital_scheme_entity.capital_scheme_bid_statuses
        assert (
            bid_status_entity.bid_status_id == 1
            and bid_status_entity.effective_date_from == datetime(2020, 2, 1)
            and bid_status_entity.effective_date_to is None
        )
        assert not capital_scheme_entity.capital_scheme_authority_reviews

    def test_from_domain_sets_authority_review(self) -> None:
        capital_scheme = CapitalScheme(
            reference="ATE00001", overview=dummy_overview(), bid_status_details=dummy_bid_status_details()
        )
        capital_scheme.perform_authority_review(CapitalSchemeAuthorityReview(review_date=datetime(2020, 2, 1)))

        capital_scheme_entity = CapitalSchemeEntity.from_domain(
            capital_scheme, {"dummy": 1}, {"dummy": 1}, {SchemeTypeName.DEVELOPMENT: 1}, {BidStatusName.NOT_FUNDED: 1}
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

        assert (
            capital_scheme.reference == "ATE00001"
            and capital_scheme.overview
            == CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=timezone.utc)),
                name="Wirral Package",
                bid_submitting_authority="LIV",
                funding_programme="ATF3",
                type=CapitalSchemeType.CONSTRUCTION,
            )
            and capital_scheme.bid_status_details
            == CapitalSchemeBidStatusDetails(
                effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=timezone.utc)),
                bid_status=CapitalSchemeBidStatus.FUNDED,
            )
            and not capital_scheme.authority_review
        )

    def test_to_domain_sets_authority_review(self) -> None:
        capital_scheme_entity = CapitalSchemeEntity(
            scheme_reference="ATE00001",
            capital_scheme_overviews=[dummy_overview_entity()],
            capital_scheme_bid_statuses=[dummy_bid_status_entity()],
            capital_scheme_authority_reviews=[CapitalSchemeAuthorityReviewEntity(review_date=datetime(2020, 1, 1))],
        )

        capital_scheme = capital_scheme_entity.to_domain()

        assert capital_scheme.authority_review == CapitalSchemeAuthorityReview(
            review_date=datetime(2020, 1, 1, tzinfo=timezone.utc)
        )


@pytest.mark.usefixtures("data")
class TestDatabaseCapitalSchemeRepository:
    def test_add(self, engine: Engine) -> None:
        with Session(engine) as session, session.begin():
            session.add_all(
                [
                    FundingProgrammeEntity(
                        funding_programme_id=1, funding_programme_code="ATF3", is_under_embargo=False
                    ),
                    AuthorityEntity(authority_id=1, authority_full_name="Liverpool", authority_abbreviation="LIV"),
                    BidStatusEntity(bid_status_id=1, bid_status_name=BidStatusName.FUNDED),
                    SchemeTypeEntity(scheme_type_id=1, scheme_type_name=SchemeTypeName.CONSTRUCTION),
                ]
            )

        with Session(engine) as session, session.begin():
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_schemes.add(
                CapitalScheme(
                    reference="ATE00001",
                    overview=CapitalSchemeOverview(
                        effective_date=DateTimeRange(datetime(2020, 1, 1)),
                        name="Wirral Package",
                        bid_submitting_authority="LIV",
                        funding_programme="ATF3",
                        type=CapitalSchemeType.CONSTRUCTION,
                    ),
                    bid_status_details=CapitalSchemeBidStatusDetails(
                        effective_date=DateTimeRange(datetime(2020, 2, 1)),
                        bid_status=CapitalSchemeBidStatus.FUNDED,
                    ),
                )
            )

        with Session(engine) as session:
            (capital_scheme_row,) = session.scalars(select(CapitalSchemeEntity))
            (overview_row,) = session.scalars(select(CapitalSchemeOverviewEntity))
            (bid_status_row,) = session.scalars(select(CapitalSchemeBidStatusEntity))
        assert capital_scheme_row.scheme_reference == "ATE00001"
        assert (
            overview_row.capital_scheme_id == capital_scheme_row.capital_scheme_id
            and overview_row.scheme_name == "Wirral Package"
            and overview_row.bid_submitting_authority_id == 1
            and overview_row.funding_programme_id == 1
            and overview_row.scheme_type_id == 1
            and overview_row.effective_date_from == datetime(2020, 1, 1)
            and overview_row.effective_date_to is None
        )
        assert (
            bid_status_row.capital_scheme_id == capital_scheme_row.capital_scheme_id
            and bid_status_row.bid_status_id == 1
            and bid_status_row.effective_date_from == datetime(2020, 2, 1)
            and bid_status_row.effective_date_to is None
        )

    def test_add_stores_authority_review(self, engine: Engine) -> None:
        with Session(engine) as session, session.begin():
            session.add_all(
                [
                    FundingProgrammeEntity(
                        funding_programme_id=1, funding_programme_code="dummy", is_under_embargo=False
                    ),
                    AuthorityEntity(authority_id=1, authority_full_name="dummy", authority_abbreviation="dummy"),
                    BidStatusEntity(bid_status_id=1, bid_status_name=BidStatusName.NOT_FUNDED),
                    SchemeTypeEntity(scheme_type_id=1, scheme_type_name=SchemeTypeName.DEVELOPMENT),
                ]
            )

        with Session(engine) as session, session.begin():
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme = CapitalScheme(
                reference="ATE00001", overview=dummy_overview(), bid_status_details=dummy_bid_status_details()
            )
            capital_scheme.perform_authority_review(CapitalSchemeAuthorityReview(review_date=datetime(2020, 2, 1)))
            capital_schemes.add(capital_scheme)

        with Session(engine) as session:
            (capital_scheme_row,) = session.scalars(select(CapitalSchemeEntity))
            (authority_review_row,) = session.scalars(select(CapitalSchemeAuthorityReviewEntity))
        assert (
            authority_review_row.capital_scheme_id == capital_scheme_row.capital_scheme_id
            and authority_review_row.review_date == datetime(2020, 2, 1)
        )

    def test_get(self, engine: Engine) -> None:
        with Session(engine) as session, session.begin():
            session.add_all(
                [
                    FundingProgrammeEntity(
                        funding_programme_id=1, funding_programme_code="ATF3", is_under_embargo=False
                    ),
                    AuthorityEntity(authority_id=1, authority_full_name="Liverpool", authority_abbreviation="LIV"),
                    BidStatusEntity(bid_status_id=1, bid_status_name=BidStatusName.FUNDED),
                    SchemeTypeEntity(scheme_type_id=1, scheme_type_name=SchemeTypeName.CONSTRUCTION),
                    CapitalSchemeEntity(capital_scheme_id=1, scheme_reference="ATE00001"),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_id=1,
                        scheme_name="Wirral Package",
                        bid_submitting_authority_id=1,
                        funding_programme_id=1,
                        scheme_type_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                    ),
                    CapitalSchemeBidStatusEntity(
                        capital_scheme_id=1,
                        bid_status_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                    ),
                    CapitalSchemeEntity(capital_scheme_id=2, scheme_reference="ATE00002"),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_id=2,
                        scheme_name="School Streets",
                        bid_submitting_authority_id=1,
                        funding_programme_id=1,
                        scheme_type_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                    ),
                    CapitalSchemeBidStatusEntity(
                        capital_scheme_id=2,
                        bid_status_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                    ),
                ]
            )

        with Session(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme = capital_schemes.get("ATE00001")

        assert (
            capital_scheme
            and capital_scheme.reference == "ATE00001"
            and capital_scheme.overview
            == CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=timezone.utc)),
                name="Wirral Package",
                bid_submitting_authority="LIV",
                funding_programme="ATF3",
                type=CapitalSchemeType.CONSTRUCTION,
            )
            and not capital_scheme.authority_review
        )

    def test_get_fetches_current_overview(self, engine: Engine) -> None:
        with Session(engine) as session, session.begin():
            session.add_all(
                [
                    FundingProgrammeEntity(
                        funding_programme_id=1, funding_programme_code="ATF3", is_under_embargo=False
                    ),
                    AuthorityEntity(authority_id=1, authority_full_name="Liverpool", authority_abbreviation="LIV"),
                    BidStatusEntity(bid_status_id=1, bid_status_name=BidStatusName.FUNDED),
                    SchemeTypeEntity(scheme_type_id=1, scheme_type_name=SchemeTypeName.CONSTRUCTION),
                    CapitalSchemeEntity(capital_scheme_id=1, scheme_reference="ATE00001"),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_id=1,
                        scheme_name="Wirral Package",
                        bid_submitting_authority_id=1,
                        funding_programme_id=1,
                        scheme_type_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=datetime(2020, 2, 1),
                    ),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_id=1,
                        scheme_name="School Streets",
                        bid_submitting_authority_id=1,
                        funding_programme_id=1,
                        scheme_type_id=1,
                        effective_date_from=datetime(2020, 2, 1),
                    ),
                    CapitalSchemeBidStatusEntity(
                        capital_scheme_id=1,
                        bid_status_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                    ),
                ]
            )

        with Session(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme = capital_schemes.get("ATE00001")

        assert (
            capital_scheme
            and capital_scheme.reference == "ATE00001"
            and capital_scheme.overview
            == CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=timezone.utc)),
                name="School Streets",
                bid_submitting_authority="LIV",
                funding_programme="ATF3",
                type=CapitalSchemeType.CONSTRUCTION,
            )
        )

    def test_get_fetches_current_bid_status(self, engine: Engine) -> None:
        with Session(engine) as session, session.begin():
            session.add_all(
                [
                    FundingProgrammeEntity(
                        funding_programme_id=1, funding_programme_code="ATF3", is_under_embargo=False
                    ),
                    AuthorityEntity(authority_id=1, authority_full_name="Liverpool", authority_abbreviation="LIV"),
                    BidStatusEntity(bid_status_id=1, bid_status_name=BidStatusName.FUNDED),
                    BidStatusEntity(bid_status_id=2, bid_status_name=BidStatusName.NOT_FUNDED),
                    SchemeTypeEntity(scheme_type_id=1, scheme_type_name=SchemeTypeName.CONSTRUCTION),
                    CapitalSchemeEntity(capital_scheme_id=1, scheme_reference="ATE00001"),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_id=1,
                        scheme_name="Wirral Package",
                        bid_submitting_authority_id=1,
                        funding_programme_id=1,
                        scheme_type_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                    ),
                    CapitalSchemeBidStatusEntity(
                        capital_scheme_id=1,
                        bid_status_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=datetime(2020, 2, 1),
                    ),
                    CapitalSchemeBidStatusEntity(
                        capital_scheme_id=1,
                        bid_status_id=2,
                        effective_date_from=datetime(2020, 2, 1),
                    ),
                ]
            )

        with Session(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme = capital_schemes.get("ATE00001")

        assert (
            capital_scheme
            and capital_scheme.reference == "ATE00001"
            and capital_scheme.bid_status_details
            == CapitalSchemeBidStatusDetails(
                effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=timezone.utc)),
                bid_status=CapitalSchemeBidStatus.NOT_FUNDED,
            )
        )

    def test_get_fetches_latest_authority_review(self, engine: Engine) -> None:
        with Session(engine) as session, session.begin():
            session.add_all(
                [
                    FundingProgrammeEntity(
                        funding_programme_id=1, funding_programme_code="ATF3", is_under_embargo=False
                    ),
                    AuthorityEntity(authority_id=1, authority_full_name="Liverpool", authority_abbreviation="LIV"),
                    BidStatusEntity(bid_status_id=1, bid_status_name=BidStatusName.FUNDED),
                    SchemeTypeEntity(scheme_type_id=1, scheme_type_name=SchemeTypeName.CONSTRUCTION),
                    CapitalSchemeEntity(capital_scheme_id=1, scheme_reference="ATE00001"),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_id=1,
                        scheme_name="Wirral Package",
                        bid_submitting_authority_id=1,
                        funding_programme_id=1,
                        scheme_type_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                    ),
                    CapitalSchemeBidStatusEntity(
                        capital_scheme_id=1,
                        bid_status_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                    ),
                    CapitalSchemeAuthorityReviewEntity(capital_scheme_id=1, review_date=datetime(2020, 2, 1)),
                    CapitalSchemeAuthorityReviewEntity(capital_scheme_id=1, review_date=datetime(2020, 3, 1)),
                ]
            )

        with Session(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme = capital_schemes.get("ATE00001")

        assert capital_scheme and capital_scheme.authority_review == CapitalSchemeAuthorityReview(
            review_date=datetime(2020, 3, 1, tzinfo=timezone.utc)
        )

    def test_get_filters_under_embargo(self, engine: Engine) -> None:
        with Session(engine) as session, session.begin():
            session.add_all(
                [
                    FundingProgrammeEntity(
                        funding_programme_id=1, funding_programme_code="ATF3", is_under_embargo=True
                    ),
                    AuthorityEntity(authority_id=1, authority_full_name="Liverpool", authority_abbreviation="LIV"),
                    BidStatusEntity(bid_status_id=1, bid_status_name=BidStatusName.FUNDED),
                    SchemeTypeEntity(scheme_type_id=1, scheme_type_name=SchemeTypeName.CONSTRUCTION),
                    CapitalSchemeEntity(capital_scheme_id=1, scheme_reference="ATE00001"),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_id=1,
                        scheme_name="Wirral Package",
                        bid_submitting_authority_id=1,
                        funding_programme_id=1,
                        scheme_type_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                    ),
                    CapitalSchemeBidStatusEntity(
                        capital_scheme_id=1,
                        bid_status_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                    ),
                ]
            )

        with Session(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme = capital_schemes.get("ATE00001")

        assert not capital_scheme

    def test_get_when_not_found(self, engine: Engine) -> None:
        with Session(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme = capital_schemes.get("ATE00001")

        assert not capital_scheme

    def test_get_references_by_bid_submitting_authority(self, engine: Engine) -> None:
        with Session(engine) as session, session.begin():
            session.add_all(
                [
                    FundingProgrammeEntity(
                        funding_programme_id=1, funding_programme_code="ATF3", is_under_embargo=False
                    ),
                    AuthorityEntity(authority_id=1, authority_full_name="Liverpool", authority_abbreviation="LIV"),
                    AuthorityEntity(authority_id=2, authority_full_name="West Yorkshire", authority_abbreviation="WYO"),
                    SchemeTypeEntity(scheme_type_id=1, scheme_type_name=SchemeTypeName.CONSTRUCTION),
                    CapitalSchemeEntity(capital_scheme_id=1, scheme_reference="ATE00001"),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_id=1,
                        scheme_name="Wirral Package",
                        bid_submitting_authority_id=1,
                        funding_programme_id=1,
                        scheme_type_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                    ),
                    CapitalSchemeEntity(capital_scheme_id=2, scheme_reference="ATE00002"),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_id=2,
                        scheme_name="School Streets",
                        bid_submitting_authority_id=1,
                        funding_programme_id=1,
                        scheme_type_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                    ),
                    CapitalSchemeEntity(capital_scheme_id=3, scheme_reference="ATE00003"),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_id=3,
                        scheme_name="Hospital Fields Road",
                        bid_submitting_authority_id=2,
                        funding_programme_id=1,
                        scheme_type_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                    ),
                ]
            )

        with Session(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            references = capital_schemes.get_references_by_bid_submitting_authority("LIV")

        assert references == ["ATE00001", "ATE00002"]

    def test_get_references_by_bid_submitting_authority_fetches_current_overview(self, engine: Engine) -> None:
        with Session(engine) as session, session.begin():
            session.add_all(
                [
                    FundingProgrammeEntity(
                        funding_programme_id=1, funding_programme_code="ATF3", is_under_embargo=False
                    ),
                    AuthorityEntity(authority_id=1, authority_full_name="Liverpool", authority_abbreviation="LIV"),
                    AuthorityEntity(authority_id=2, authority_full_name="West Yorkshire", authority_abbreviation="WYO"),
                    SchemeTypeEntity(scheme_type_id=1, scheme_type_name=SchemeTypeName.CONSTRUCTION),
                    CapitalSchemeEntity(capital_scheme_id=1, scheme_reference="ATE00001"),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_id=1,
                        scheme_name="Wirral Package",
                        bid_submitting_authority_id=1,
                        funding_programme_id=1,
                        scheme_type_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=datetime(2020, 2, 1),
                    ),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_id=1,
                        scheme_name="School Streets",
                        bid_submitting_authority_id=2,
                        funding_programme_id=1,
                        scheme_type_id=1,
                        effective_date_from=datetime(2020, 2, 1),
                    ),
                ]
            )

        with Session(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            references = capital_schemes.get_references_by_bid_submitting_authority("LIV")

        assert not references

    def test_get_references_by_bid_submitting_authority_filters_under_embargo(self, engine: Engine) -> None:
        with Session(engine) as session, session.begin():
            session.add_all(
                [
                    FundingProgrammeEntity(
                        funding_programme_id=1, funding_programme_code="ATF3", is_under_embargo=True
                    ),
                    AuthorityEntity(authority_id=1, authority_full_name="Liverpool", authority_abbreviation="LIV"),
                    SchemeTypeEntity(scheme_type_id=1, scheme_type_name=SchemeTypeName.CONSTRUCTION),
                    CapitalSchemeEntity(capital_scheme_id=1, scheme_reference="ATE00001"),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_id=1,
                        scheme_name="Wirral Package",
                        bid_submitting_authority_id=1,
                        funding_programme_id=1,
                        scheme_type_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                    ),
                ]
            )

        with Session(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            references = capital_schemes.get_references_by_bid_submitting_authority("LIV")

        assert not references

    def test_get_references_by_bid_submitting_authority_orders_by_reference(self, engine: Engine) -> None:
        with Session(engine) as session, session.begin():
            session.add_all(
                [
                    FundingProgrammeEntity(
                        funding_programme_id=1, funding_programme_code="ATF3", is_under_embargo=False
                    ),
                    AuthorityEntity(authority_id=1, authority_full_name="Liverpool", authority_abbreviation="LIV"),
                    SchemeTypeEntity(scheme_type_id=1, scheme_type_name=SchemeTypeName.CONSTRUCTION),
                    CapitalSchemeEntity(capital_scheme_id=2, scheme_reference="ATE00002"),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_id=2,
                        scheme_name="School Streets",
                        bid_submitting_authority_id=1,
                        funding_programme_id=1,
                        scheme_type_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                    ),
                    CapitalSchemeEntity(capital_scheme_id=1, scheme_reference="ATE00001"),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_id=1,
                        scheme_name="Wirral Package",
                        bid_submitting_authority_id=1,
                        funding_programme_id=1,
                        scheme_type_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                    ),
                ]
            )

        with Session(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            references = capital_schemes.get_references_by_bid_submitting_authority("LIV")

        assert references == ["ATE00001", "ATE00002"]
