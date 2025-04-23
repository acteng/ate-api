from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.status import HTTP_404_NOT_FOUND

from ate_api.database import get_session
from ate_api.domain.capital_schemes import (
    CapitalScheme,
    CapitalSchemeOverview,
    CapitalSchemeRepository,
)
from ate_api.infrastructure.database.capital_schemes import (
    DatabaseCapitalSchemeRepository,
)
from ate_api.routes.authorities.authorities import AuthorityModel
from ate_api.routes.base import BaseModel
from ate_api.routes.dates import DateTimeRangeModel


class CapitalSchemeModel(BaseModel):
    reference: str
    overview: CapitalSchemeOverviewModel

    @staticmethod
    def link_from_identifier(reference: str, app: Starlette) -> str:
        return app.url_path_for("get_capital_scheme", reference=reference)

    @classmethod
    def from_domain(cls, capital_scheme: CapitalScheme, app: Starlette) -> CapitalSchemeModel:
        return cls(
            reference=capital_scheme.reference,
            overview=CapitalSchemeOverviewModel.from_domain(capital_scheme.overview, app),
        )

    def to_domain(self) -> CapitalScheme:
        capital_scheme = CapitalScheme(reference=self.reference)
        capital_scheme.update_overview(self.overview.to_domain())
        return capital_scheme


class CapitalSchemeOverviewModel(BaseModel):
    effective_date: DateTimeRangeModel
    bid_submitting_authority: str

    @classmethod
    def from_domain(cls, overview: CapitalSchemeOverview, app: Starlette) -> CapitalSchemeOverviewModel:
        return cls(
            effective_date=DateTimeRangeModel.from_domain(overview.effective_date),
            bid_submitting_authority=app.url_path_for("get_authority", abbreviation=overview.bid_submitting_authority),
        )

    def to_domain(self) -> CapitalSchemeOverview:
        return CapitalSchemeOverview(
            effective_date=self.effective_date.to_domain(),
            bid_submitting_authority=AuthorityModel.link_to_identifier(self.bid_submitting_authority),
        )


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

    return CapitalSchemeModel.from_domain(capital_scheme, request.app)
