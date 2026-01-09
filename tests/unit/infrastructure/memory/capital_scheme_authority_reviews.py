from ate_api.domain.capital_scheme_authority_reviews import (
    CapitalSchemeAuthorityReviews,
    CapitalSchemeAuthorityReviewsRepository,
)
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeReference


class MemoryCapitalSchemeAuthorityReviewsRepository(CapitalSchemeAuthorityReviewsRepository):
    def __init__(self) -> None:
        self._authority_reviews: dict[CapitalSchemeReference, CapitalSchemeAuthorityReviews] = {}

    async def add(self, authority_reviews: CapitalSchemeAuthorityReviews) -> None:
        self._authority_reviews[authority_reviews.capital_scheme] = authority_reviews

    async def get(self, capital_scheme: CapitalSchemeReference) -> CapitalSchemeAuthorityReviews | None:
        return self._authority_reviews.get(capital_scheme)

    async def update(self, authority_reviews: CapitalSchemeAuthorityReviews) -> None:
        self._authority_reviews[authority_reviews.capital_scheme] = authority_reviews
