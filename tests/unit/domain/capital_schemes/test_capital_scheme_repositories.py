from datetime import UTC, datetime

import pytest

from ate_api.domain.capital_schemes.capital_scheme_repositories import CapitalSchemeItemAuthorityReview


class TestCapitalSchemeItemAuthorityReview:
    def test_can_create(self) -> None:
        authority_review = CapitalSchemeItemAuthorityReview(review_date=datetime(2020, 2, 1, tzinfo=UTC))

        assert authority_review.review_date == datetime(2020, 2, 1, tzinfo=UTC)

    def test_cannot_create_with_local_review_date(self) -> None:
        with pytest.raises(ValueError, match="Review date and time must include a time zone: 2020-02-01 00:00:00"):
            CapitalSchemeItemAuthorityReview(review_date=datetime(2020, 2, 1))
