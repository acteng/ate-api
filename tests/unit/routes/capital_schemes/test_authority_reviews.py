from datetime import UTC, datetime

import pytest

from ate_api.domain.capital_schemes.authority_reviews import CapitalSchemeAuthorityReview
from ate_api.routes.capital_schemes.authority_reviews import CapitalSchemeAuthorityReviewModel


class TestCapitalSchemeAuthorityReviewModel:
    def test_can_create(self) -> None:
        authority_review = CapitalSchemeAuthorityReview(review_date=datetime(2020, 1, 1, tzinfo=UTC))

        assert authority_review.review_date == datetime(2020, 1, 1, tzinfo=UTC)

    def test_cannot_create_with_local_review_date(self) -> None:
        with pytest.raises(ValueError, match="Review date and time must include a time zone: 2020-01-01 00:00:00"):
            CapitalSchemeAuthorityReview(review_date=datetime(2020, 1, 1))

    def test_from_domain(self) -> None:
        authority_review = CapitalSchemeAuthorityReview(review_date=datetime(2020, 1, 1, tzinfo=UTC))

        authority_review_model = CapitalSchemeAuthorityReviewModel.from_domain(authority_review)

        assert authority_review_model == CapitalSchemeAuthorityReviewModel(review_date=datetime(2020, 1, 1, tzinfo=UTC))

    def test_to_domain(self) -> None:
        authority_review_model = CapitalSchemeAuthorityReviewModel(review_date=datetime(2020, 1, 1, tzinfo=UTC))

        authority_review = authority_review_model.to_domain()

        assert authority_review == CapitalSchemeAuthorityReview(review_date=datetime(2020, 1, 1, tzinfo=UTC))
