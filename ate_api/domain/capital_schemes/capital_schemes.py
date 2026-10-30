from dataclasses import dataclass

from ate_api.domain.authorities import AuthorityAbbreviation
from ate_api.domain.capital_schemes.authority_reviews import CapitalSchemeAuthorityReview
from ate_api.domain.capital_schemes.outputs import CapitalSchemeOutput
from ate_api.domain.capital_schemes.overviews import CapitalSchemeOverview
from ate_api.domain.capital_schemes.statuses import CapitalSchemeStatus, Status
from ate_api.domain.funding_programmes import FundingProgrammeCode


class CapitalSchemeReference:
    def __init__(self, reference: str):
        self._reference = reference

    def __eq__(self, other: object) -> bool:
        return isinstance(other, CapitalSchemeReference) and self._reference == other._reference

    def __hash__(self) -> int:
        return hash(self._reference)

    def __str__(self) -> str:
        return self._reference

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._reference!r})"


class CapitalScheme:
    def __init__(
        self,
        reference: CapitalSchemeReference,
        overview: CapitalSchemeOverview,
        status: CapitalSchemeStatus,
    ):
        self._reference = reference
        self._overview = overview
        self._status = status
        self._outputs: list[CapitalSchemeOutput] = []
        self._authority_review: CapitalSchemeAuthorityReview | None = None

    @property
    def reference(self) -> CapitalSchemeReference:
        return self._reference

    @property
    def overview(self) -> CapitalSchemeOverview:
        return self._overview

    @property
    def status(self) -> CapitalSchemeStatus:
        return self._status

    @property
    def outputs(self) -> list[CapitalSchemeOutput]:
        return list(self._outputs)

    def change_output(self, output: CapitalSchemeOutput) -> None:
        self._outputs.append(output)

    @property
    def authority_review(self) -> CapitalSchemeAuthorityReview | None:
        return self._authority_review

    def perform_authority_review(self, authority_review: CapitalSchemeAuthorityReview) -> None:
        self._authority_review = authority_review


@dataclass(frozen=True)
class CapitalSchemeItem:
    reference: CapitalSchemeReference
    overview: CapitalSchemeOverview
    status: CapitalSchemeStatus
    authority_review: CapitalSchemeAuthorityReview | None


class CapitalSchemeRepository:
    async def add(self, capital_scheme: CapitalScheme) -> None:
        raise NotImplementedError()

    async def get(self, reference: CapitalSchemeReference) -> CapitalScheme | None:
        raise NotImplementedError()

    async def get_items_by_funding_managed_by(
        self,
        authority_abbreviation: AuthorityAbbreviation,
        funding_programme_codes: list[FundingProgrammeCode] | None = None,
        status: Status | None = None,
    ) -> list[CapitalSchemeItem]:
        raise NotImplementedError()

    async def update(self, capital_scheme: CapitalScheme) -> None:
        raise NotImplementedError()
