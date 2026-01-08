from datetime import UTC, datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from ate_api.domain.capital_scheme_authority_reviews import CapitalSchemeAuthorityReview, CapitalSchemeAuthorityReviews
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeReference
from ate_api.domain.data_sources import DataSource
from ate_api.infrastructure.database import (
    CapitalSchemeAuthorityReviewEntity,
    CapitalSchemeEntity,
    DataSourceEntity,
    DataSourceName,
)
from ate_api.infrastructure.database.capital_scheme_authority_reviews import (
    DatabaseCapitalSchemeAuthorityReviewsRepository,
)
from tests.unit.infrastructure.database.builders import (
    build_capital_scheme_overview_entity,
    build_data_source_entity,
    build_funding_programme_entity,
)


class TestCapitalSchemeAuthorityReviewEntity:
    def test_from_domain(self) -> None:
        authority_review = CapitalSchemeAuthorityReview(
            review_date=datetime(2020, 1, 1, tzinfo=UTC), data_source=DataSource.AUTHORITY_UPDATE, surrogate_id=1
        )

        authority_review_entity = CapitalSchemeAuthorityReviewEntity.from_domain(
            authority_review, 2, {DataSource.AUTHORITY_UPDATE: 3}
        )

        assert (
            authority_review_entity.capital_scheme_authority_review_id == 1
            and authority_review_entity.capital_scheme_id == 2
            and authority_review_entity.review_date == datetime(2020, 1, 1)
            and authority_review_entity.data_source_id == 3
        )

    def test_from_domain_converts_dates_to_local_europe_london(self) -> None:
        authority_review = CapitalSchemeAuthorityReview(
            review_date=datetime(2020, 6, 1, 12, tzinfo=UTC), data_source=DataSource.AUTHORITY_UPDATE
        )

        authority_review_entity = CapitalSchemeAuthorityReviewEntity.from_domain(
            authority_review, 0, {DataSource.AUTHORITY_UPDATE: 0}
        )

        assert authority_review_entity.review_date == datetime(2020, 6, 1, 13)

    def test_to_domain(self) -> None:
        authority_review_entity = CapitalSchemeAuthorityReviewEntity(
            capital_scheme_authority_review_id=1,
            review_date=datetime(2020, 1, 1),
            data_source=DataSourceEntity(data_source_name=DataSourceName.AUTHORITY_UPDATE),
        )

        authority_review = authority_review_entity.to_domain()

        assert authority_review == CapitalSchemeAuthorityReview(
            review_date=datetime(2020, 1, 1, tzinfo=UTC), data_source=DataSource.AUTHORITY_UPDATE
        )
        assert authority_review.surrogate_id == 1

    def test_to_domain_converts_dates_from_local_europe_london(self) -> None:
        authority_review_entity = CapitalSchemeAuthorityReviewEntity(
            review_date=datetime(2020, 6, 1, 13),
            data_source=DataSourceEntity(data_source_name=DataSourceName.AUTHORITY_UPDATE),
        )

        authority_review = authority_review_entity.to_domain()

        assert authority_review.review_date == datetime(2020, 6, 1, 12, tzinfo=UTC)


@pytest.mark.usefixtures("data")
@pytest.mark.asyncio(loop_scope="package")
class TestDatabaseCapitalSchemeAuthorityReviewsRepository:
    async def test_add_stores_authority_review(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    build_data_source_entity(id_=1, name=DataSourceName.AUTHORITY_UPDATE),
                    CapitalSchemeEntity(scheme_reference="ATE00001"),
                ]
            )

        async with AsyncSession(engine) as session, session.begin():
            capital_scheme_authority_reviews = DatabaseCapitalSchemeAuthorityReviewsRepository(session)
            authority_reviews = CapitalSchemeAuthorityReviews(capital_scheme=CapitalSchemeReference("ATE00001"))
            authority_reviews.perform_authority_review(
                CapitalSchemeAuthorityReview(
                    review_date=datetime(2020, 2, 1, tzinfo=UTC), data_source=DataSource.AUTHORITY_UPDATE
                )
            )
            await capital_scheme_authority_reviews.add(authority_reviews)

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
            session.add(
                CapitalSchemeEntity(
                    scheme_reference="ATE00001", capital_scheme_overviews=[build_capital_scheme_overview_entity()]
                )
            )

        async with AsyncSession(engine) as session:
            capital_scheme_authority_reviews = DatabaseCapitalSchemeAuthorityReviewsRepository(session)
            authority_reviews = await capital_scheme_authority_reviews.get(CapitalSchemeReference("ATE00001"))

        assert (
            authority_reviews
            and authority_reviews.capital_scheme == CapitalSchemeReference("ATE00001")
            and not authority_reviews.authority_review
        )

    async def test_get_fetches_latest_authority_review(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    authority_review := build_data_source_entity(name=DataSourceName.AUTHORITY_UPDATE),
                    CapitalSchemeEntity(
                        capital_scheme_id=1,
                        scheme_reference="ATE00001",
                        capital_scheme_overviews=[build_capital_scheme_overview_entity()],
                    ),
                    CapitalSchemeAuthorityReviewEntity(
                        capital_scheme_id=1, review_date=datetime(2020, 3, 1), data_source=authority_review
                    ),
                    CapitalSchemeAuthorityReviewEntity(
                        capital_scheme_id=1, review_date=datetime(2020, 2, 1), data_source=authority_review
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_scheme_authority_reviews = DatabaseCapitalSchemeAuthorityReviewsRepository(session)
            authority_reviews = await capital_scheme_authority_reviews.get(CapitalSchemeReference("ATE00001"))

        assert authority_reviews and authority_reviews.authority_review == CapitalSchemeAuthorityReview(
            review_date=datetime(2020, 3, 1, tzinfo=UTC), data_source=DataSource.AUTHORITY_UPDATE
        )

    async def test_get_filters_under_embargo(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    atf3 := build_funding_programme_entity(code="ATF3", is_under_embargo=True),
                    CapitalSchemeEntity(
                        scheme_reference="ATE00001",
                        capital_scheme_overviews=[build_capital_scheme_overview_entity(funding_programme=atf3)],
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            capital_scheme_authority_reviews = DatabaseCapitalSchemeAuthorityReviewsRepository(session)
            authority_reviews = await capital_scheme_authority_reviews.get(CapitalSchemeReference("ATE00001"))

        assert not authority_reviews

    async def test_get_when_not_found(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session:
            capital_scheme_authority_reviews = DatabaseCapitalSchemeAuthorityReviewsRepository(session)
            authority_reviews = await capital_scheme_authority_reviews.get(CapitalSchemeReference("ATE00001"))

        assert not authority_reviews
