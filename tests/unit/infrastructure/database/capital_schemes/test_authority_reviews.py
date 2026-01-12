from datetime import UTC, datetime

from ate_api.domain.capital_schemes.authority_reviews import CapitalSchemeAuthorityReview
from ate_api.domain.data_sources import DataSource
from ate_api.infrastructure.database import CapitalSchemeAuthorityReviewEntity, DataSourceEntity, DataSourceName


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
