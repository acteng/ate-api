from enum import Enum
from typing import Annotated, Self

from fastapi import APIRouter, Depends, HTTPException
from pydantic import Field
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.status import HTTP_404_NOT_FOUND

from ate_api.database import get_session
from ate_api.domain.capital_schemes import (
    CapitalScheme,
    CapitalSchemeRepository,
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
    bid_submitting_authority: str
    funding_programme: str
    type_: Annotated[CapitalSchemeTypeModel, Field(alias="type")]

    @classmethod
    def from_domain(cls, capital_scheme: CapitalScheme, request: Request) -> Self:
        return cls(
            effective_date=DateTimeRangeModel.from_domain(capital_scheme.effective_date),
            name=capital_scheme.name,
            bid_submitting_authority=str(
                request.url_for("get_authority", abbreviation=capital_scheme.bid_submitting_authority)
            ),
            funding_programme=str(request.url_for("get_funding_programme", code=capital_scheme.funding_programme)),
            type_=CapitalSchemeTypeModel.from_domain(capital_scheme.type),
        )

    def to_domain(self, reference: str, request: Request) -> CapitalScheme:
        return CapitalScheme(
            reference=reference,
            effective_date=self.effective_date.to_domain(),
            name=self.name,
            bid_submitting_authority=path_parameter_for(
                request, "get_authority", "abbreviation", self.bid_submitting_authority
            ),
            funding_programme=path_parameter_for(request, "get_funding_programme", "code", self.funding_programme),
            type_=self.type_.to_domain(),
        )


class CapitalSchemeModel(BaseModel):
    reference: str
    overview: CapitalSchemeOverviewModel

    @classmethod
    def from_domain(cls, capital_scheme: CapitalScheme, request: Request) -> Self:
        return cls(
            reference=capital_scheme.reference,
            overview=CapitalSchemeOverviewModel.from_domain(capital_scheme, request),
        )

    def to_domain(self, request: Request) -> CapitalScheme:
        return self.overview.to_domain(self.reference, request)


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
