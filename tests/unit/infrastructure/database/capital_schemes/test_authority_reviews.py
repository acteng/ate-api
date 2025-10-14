from datetime import UTC, datetime

from ate_api.domain.capital_schemes.authority_reviews import CapitalSchemeAuthorityReview
from ate_api.infrastructure.database import CapitalSchemeAuthorityReviewEntity


class TestCapitalSchemeAuthorityReviewEntity:
    def test_from_domain(self) -> None:
        authority_review = CapitalSchemeAuthorityReview(review_date=datetime(2020, 1, 1))

        authority_review_entity = CapitalSchemeAuthorityReviewEntity.from_domain(authority_review)

        assert authority_review_entity.review_date == datetime(2020, 1, 1)

    def test_from_domain_converts_dates_to_local_europe_london(self) -> None:
        authority_review = CapitalSchemeAuthorityReview(review_date=datetime(2020, 6, 1, 12, tzinfo=UTC))

        authority_review_entity = CapitalSchemeAuthorityReviewEntity.from_domain(authority_review)

        assert authority_review_entity.review_date == datetime(2020, 6, 1, 13)

    def test_to_domain(self) -> None:
        authority_review_entity = CapitalSchemeAuthorityReviewEntity(review_date=datetime(2020, 1, 1))

        authority_review = authority_review_entity.to_domain()

        assert authority_review == CapitalSchemeAuthorityReview(review_date=datetime(2020, 1, 1, tzinfo=UTC))

    def test_to_domain_converts_dates_from_local_europe_london(self) -> None:
        authority_review_entity = CapitalSchemeAuthorityReviewEntity(review_date=datetime(2020, 6, 1, 13))

        authority_review = authority_review_entity.to_domain()

        assert authority_review == CapitalSchemeAuthorityReview(review_date=datetime(2020, 6, 1, 12, tzinfo=UTC))
