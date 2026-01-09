from datetime import UTC, datetime

import pytest

from ate_api.domain.capital_scheme_authority_reviews import CapitalSchemeAuthorityReview, CapitalSchemeAuthorityReviews
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeReference
from ate_api.domain.data_sources import DataSource
from tests.unit.infrastructure.memory.capital_scheme_authority_reviews import (
    MemoryCapitalSchemeAuthorityReviewsRepository,
)


class TestMemoryCapitalSchemeAuthorityReviewsRepository:
    @pytest.fixture(name="capital_scheme_authority_reviews")
    def capital_scheme_authority_reviews_fixture(self) -> MemoryCapitalSchemeAuthorityReviewsRepository:
        return MemoryCapitalSchemeAuthorityReviewsRepository()

    async def test_add(self, capital_scheme_authority_reviews: MemoryCapitalSchemeAuthorityReviewsRepository) -> None:
        authority_reviews = CapitalSchemeAuthorityReviews(capital_scheme=CapitalSchemeReference("ATE00001"))
        authority_review = CapitalSchemeAuthorityReview(
            review_date=datetime(2020, 2, 1, tzinfo=UTC), data_source=DataSource.AUTHORITY_UPDATE
        )
        authority_reviews.perform_authority_review(authority_review)

        await capital_scheme_authority_reviews.add(authority_reviews)

        actual_authority_reviews = await capital_scheme_authority_reviews.get(CapitalSchemeReference("ATE00001"))
        assert (
            actual_authority_reviews
            and actual_authority_reviews.capital_scheme == CapitalSchemeReference("ATE00001")
            and actual_authority_reviews.authority_review == authority_review
        )

    async def test_get(self, capital_scheme_authority_reviews: MemoryCapitalSchemeAuthorityReviewsRepository) -> None:
        authority_reviews = CapitalSchemeAuthorityReviews(capital_scheme=CapitalSchemeReference("ATE00001"))
        authority_review = CapitalSchemeAuthorityReview(
            review_date=datetime(2020, 2, 1, tzinfo=UTC), data_source=DataSource.AUTHORITY_UPDATE
        )
        authority_reviews.perform_authority_review(authority_review)
        await capital_scheme_authority_reviews.add(authority_reviews)

        actual_authority_reviews = await capital_scheme_authority_reviews.get(CapitalSchemeReference("ATE00001"))

        assert (
            actual_authority_reviews
            and actual_authority_reviews.capital_scheme == CapitalSchemeReference("ATE00001")
            and actual_authority_reviews.authority_review == authority_review
        )

    async def test_get_when_not_found(
        self, capital_scheme_authority_reviews: MemoryCapitalSchemeAuthorityReviewsRepository
    ) -> None:
        authority_reviews = await capital_scheme_authority_reviews.get(CapitalSchemeReference("ATE00001"))

        assert not authority_reviews

    async def test_update(
        self, capital_scheme_authority_reviews: MemoryCapitalSchemeAuthorityReviewsRepository
    ) -> None:
        authority_reviews = CapitalSchemeAuthorityReviews(capital_scheme=CapitalSchemeReference("ATE00001"))
        authority_reviews.perform_authority_review(
            CapitalSchemeAuthorityReview(
                review_date=datetime(2020, 2, 1, tzinfo=UTC), data_source=DataSource.AUTHORITY_UPDATE
            )
        )
        await capital_scheme_authority_reviews.add(authority_reviews)
        authority_review2 = CapitalSchemeAuthorityReview(
            review_date=datetime(2020, 3, 1, tzinfo=UTC), data_source=DataSource.AUTHORITY_UPDATE
        )
        authority_reviews.perform_authority_review(authority_review2)

        await capital_scheme_authority_reviews.update(authority_reviews)

        actual_authority_reviews = await capital_scheme_authority_reviews.get(CapitalSchemeReference("ATE00001"))
        assert (
            actual_authority_reviews
            and actual_authority_reviews.capital_scheme == CapitalSchemeReference("ATE00001")
            and actual_authority_reviews.authority_review == authority_review2
        )
