from datetime import datetime

from ate_api.domain.capital_schemes.authority_reviews import (
    CapitalSchemeAuthorityReview,
)
from ate_api.routes.capital_schemes.authority_reviews import (
    CapitalSchemeAuthorityReviewModel,
)


class TestCapitalSchemeAuthorityReviewModel:
    def test_from_domain(self) -> None:
        authority_review = CapitalSchemeAuthorityReview(review_date=datetime(2020, 1, 1))

        authority_review_model = CapitalSchemeAuthorityReviewModel.from_domain(authority_review)

        assert authority_review_model == CapitalSchemeAuthorityReviewModel(review_date=datetime(2020, 1, 1))

    def test_to_domain(self) -> None:
        authority_review_model = CapitalSchemeAuthorityReviewModel(review_date=datetime(2020, 1, 1))

        authority_review = authority_review_model.to_domain()

        assert authority_review == CapitalSchemeAuthorityReview(review_date=datetime(2020, 1, 1))
