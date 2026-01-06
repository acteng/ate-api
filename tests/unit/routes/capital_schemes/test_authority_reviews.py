from datetime import UTC, datetime

from ate_api.domain.capital_schemes.authority_reviews import CapitalSchemeAuthorityReview
from ate_api.domain.data_sources import DataSource
from ate_api.routes.capital_schemes.authority_reviews import CapitalSchemeAuthorityReviewModel
from ate_api.routes.data_sources import DataSourceModel


class TestCapitalSchemeAuthorityReviewModel:
    def test_from_domain(self) -> None:
        authority_review = CapitalSchemeAuthorityReview(
            review_date=datetime(2020, 1, 1, tzinfo=UTC), data_source=DataSource.AUTHORITY_UPDATE
        )

        authority_review_model = CapitalSchemeAuthorityReviewModel.from_domain(authority_review)

        assert authority_review_model == CapitalSchemeAuthorityReviewModel(
            review_date=datetime(2020, 1, 1, tzinfo=UTC), source=DataSourceModel.AUTHORITY_UPDATE
        )

    def test_to_domain(self) -> None:
        authority_review_model = CapitalSchemeAuthorityReviewModel(
            review_date=datetime(2020, 1, 1, tzinfo=UTC), source=DataSourceModel.AUTHORITY_UPDATE
        )

        authority_review = authority_review_model.to_domain()

        assert authority_review == CapitalSchemeAuthorityReview(
            review_date=datetime(2020, 1, 1, tzinfo=UTC), data_source=DataSource.AUTHORITY_UPDATE
        )
