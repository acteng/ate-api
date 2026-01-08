from datetime import UTC, datetime

import pytest

from ate_api.domain.capital_scheme_authority_reviews import CapitalSchemeAuthorityReview, CapitalSchemeAuthorityReviews
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeReference
from ate_api.domain.data_sources import DataSource


class TestCapitalSchemeAuthorityReview:
    def test_can_create(self) -> None:
        authority_review = CapitalSchemeAuthorityReview(
            review_date=datetime(2020, 1, 1, tzinfo=UTC), data_source=DataSource.AUTHORITY_UPDATE
        )

        assert (
            authority_review.review_date == datetime(2020, 1, 1, tzinfo=UTC)
            and authority_review.data_source == DataSource.AUTHORITY_UPDATE
        )

    def test_cannot_create_with_local_review_date(self) -> None:
        with pytest.raises(ValueError, match="Review date and time must include a time zone: 2020-01-01 00:00:00"):
            CapitalSchemeAuthorityReview(review_date=datetime(2020, 1, 1), data_source=DataSource.AUTHORITY_UPDATE)


class TestCapitalSchemeAuthorityReviews:
    def test_create(self) -> None:
        authority_reviews = CapitalSchemeAuthorityReviews(capital_scheme=CapitalSchemeReference("ATE00001"))

        assert (
            authority_reviews.capital_scheme == CapitalSchemeReference("ATE00001")
            and not authority_reviews.authority_review
        )

    def test_perform_authority_review(self) -> None:
        authority_reviews = CapitalSchemeAuthorityReviews(capital_scheme=CapitalSchemeReference("ATE00001"))
        authority_review = CapitalSchemeAuthorityReview(
            review_date=datetime(2020, 2, 1, tzinfo=UTC), data_source=DataSource.AUTHORITY_UPDATE
        )

        authority_reviews.perform_authority_review(authority_review)

        assert authority_reviews.authority_review == authority_review
