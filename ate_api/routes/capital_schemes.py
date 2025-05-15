from datetime import datetime
from enum import Enum
from typing import Annotated, Self

from fastapi import APIRouter, Depends, HTTPException
from pydantic import AnyUrl, Field
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.status import HTTP_404_NOT_FOUND

from ate_api.database import get_session
from ate_api.domain.capital_schemes.authority_reviews import (
    CapitalSchemeAuthorityReview,
)
from ate_api.domain.capital_schemes.bid_statuses import (
    CapitalSchemeBidStatus,
    CapitalSchemeBidStatusDetails,
)
from ate_api.domain.capital_schemes.capital_schemes import (
    CapitalScheme,
    CapitalSchemeRepository,
)
from ate_api.domain.capital_schemes.overviews import (
    CapitalSchemeOverview,
    CapitalSchemeType,
)
from ate_api.infrastructure.database.capital_schemes import (
    DatabaseCapitalSchemeRepository,
)
from ate_api.routes.base import BaseModel
from ate_api.routes.dates import DateTimeRangeModel
from ate_api.routes.links import path_parameter_for


class CapitalSchemeTypeModel(str, Enum):
    DEVELOPMENT = "development"
    CONSTRUCTION = "construction"

    @classmethod
    def from_domain(cls, type_: CapitalSchemeType) -> Self:
        return cls[type_.name]

    def to_domain(self) -> CapitalSchemeType:
        return CapitalSchemeType[self.name]


class CapitalSchemeOverviewModel(BaseModel):
    effective_date: DateTimeRangeModel
    name: str
    bid_submitting_authority: AnyUrl
    funding_programme: AnyUrl
    type_: Annotated[CapitalSchemeTypeModel, Field(alias="type")]

    @classmethod
    def from_domain(cls, overview: CapitalSchemeOverview, request: Request) -> Self:
        return cls(
            effective_date=DateTimeRangeModel.from_domain(overview.effective_date),
            name=overview.name,
            bid_submitting_authority=AnyUrl(
                str(request.url_for("get_authority", abbreviation=overview.bid_submitting_authority))
            ),
            funding_programme=AnyUrl(str(request.url_for("get_funding_programme", code=overview.funding_programme))),
            type_=CapitalSchemeTypeModel.from_domain(overview.type),
        )

    def to_domain(self, request: Request) -> CapitalSchemeOverview:
        return CapitalSchemeOverview(
            effective_date=self.effective_date.to_domain(),
            name=self.name,
            bid_submitting_authority=path_parameter_for(
                request, "get_authority", "abbreviation", str(self.bid_submitting_authority)
            ),
            funding_programme=path_parameter_for(request, "get_funding_programme", "code", str(self.funding_programme)),
            type=self.type_.to_domain(),
        )


class CapitalSchemeBidStatusModel(str, Enum):
    SUBMITTED = "submitted"
    FUNDED = "funded"
    NOT_FUNDED = "not funded"
    SPLIT = "split"
    DELETED = "deleted"

    @classmethod
    def from_domain(cls, bid_status: CapitalSchemeBidStatus) -> Self:
        return cls[bid_status.name]

    def to_domain(self) -> CapitalSchemeBidStatus:
        return CapitalSchemeBidStatus[self.name]


class CapitalSchemeBidStatusDetailsModel(BaseModel):
    effective_date: DateTimeRangeModel
    bid_status: CapitalSchemeBidStatusModel

    @classmethod
    def from_domain(cls, bid_status_details: CapitalSchemeBidStatusDetails) -> Self:
        return cls(
            effective_date=DateTimeRangeModel.from_domain(bid_status_details.effective_date),
            bid_status=CapitalSchemeBidStatusModel.from_domain(bid_status_details.bid_status),
        )

    def to_domain(self) -> CapitalSchemeBidStatusDetails:
        return CapitalSchemeBidStatusDetails(
            effective_date=self.effective_date.to_domain(), bid_status=self.bid_status.to_domain()
        )


class CapitalSchemeAuthorityReviewModel(BaseModel):
    review_date: datetime

    @classmethod
    def from_domain(cls, authority_review: CapitalSchemeAuthorityReview) -> Self:
        return cls(review_date=authority_review.review_date)

    def to_domain(self) -> CapitalSchemeAuthorityReview:
        return CapitalSchemeAuthorityReview(review_date=self.review_date)


class CapitalSchemeModel(BaseModel):
    reference: str
    overview: CapitalSchemeOverviewModel
    bid_status_details: CapitalSchemeBidStatusDetailsModel
    authority_review: CapitalSchemeAuthorityReviewModel | None = None

    @classmethod
    def from_domain(cls, capital_scheme: CapitalScheme, request: Request) -> Self:
        return cls(
            reference=capital_scheme.reference,
            overview=CapitalSchemeOverviewModel.from_domain(capital_scheme.overview, request),
            bid_status_details=CapitalSchemeBidStatusDetailsModel.from_domain(capital_scheme.bid_status_details),
            authority_review=(
                CapitalSchemeAuthorityReviewModel.from_domain(capital_scheme.authority_review)
                if capital_scheme.authority_review
                else None
            ),
        )

    def to_domain(self, request: Request) -> CapitalScheme:
        capital_scheme = CapitalScheme(
            reference=self.reference,
            overview=self.overview.to_domain(request),
            bid_status_details=self.bid_status_details.to_domain(),
        )

        if self.authority_review:
            capital_scheme.perform_authority_review(self.authority_review.to_domain())

        return capital_scheme


router = APIRouter(prefix="/capital-schemes", tags=["capital-schemes"])


def get_capital_scheme_repository(session: Annotated[Session, Depends(get_session)]) -> CapitalSchemeRepository:
    return DatabaseCapitalSchemeRepository(session)


@router.get("/{reference}", summary="Get capital scheme", responses={HTTP_404_NOT_FOUND: {}})
def get_capital_scheme(
    capital_schemes: Annotated[CapitalSchemeRepository, Depends(get_capital_scheme_repository)],
    request: Request,
    reference: str,
) -> CapitalSchemeModel:
    """
    Gets a capital scheme.
    """
    capital_scheme = capital_schemes.get(reference)

    if not capital_scheme:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)

    return CapitalSchemeModel.from_domain(capital_scheme, request)
