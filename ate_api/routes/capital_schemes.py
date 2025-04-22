from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from sqlalchemy.orm import Session
from starlette.applications import Starlette
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
from ate_api.routes.dates import DateTimeRangeModel


class CapitalSchemeModel(BaseModel):
    reference: str
    overview: CapitalSchemeOverviewModel

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    @staticmethod
    def link_from_identifier(reference: str, app: Starlette) -> str:
        return app.url_path_for("get_capital_scheme", reference=reference)

    def to_domain(self) -> CapitalScheme:
        capital_scheme = CapitalScheme(reference=self.reference)
        capital_scheme.update_overview(self.overview.to_domain())
        return capital_scheme


class CapitalSchemeOverviewModel(BaseModel):
    effective_date: DateTimeRangeModel
    bid_submitting_authority: str

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    def to_domain(self) -> CapitalSchemeOverview:
        return CapitalSchemeOverview(
            effective_date=self.effective_date.to_domain(),
            bid_submitting_authority=AuthorityModel.link_to_identifier(self.bid_submitting_authority),
        )


router = APIRouter(tags=["capital-schemes"])


def get_capital_scheme_repository(session: Annotated[Session, Depends(get_session)]) -> CapitalSchemeRepository:
    return DatabaseCapitalSchemeRepository(session)


@router.get("/capital-schemes/{reference}", summary="Get capital scheme", responses={HTTP_404_NOT_FOUND: {}})
def get_capital_scheme(
    capital_schemes: Annotated[CapitalSchemeRepository, Depends(get_capital_scheme_repository)], reference: str
) -> dict[str, str]:
    """
    Gets a capital scheme.
    """
    capital_scheme = capital_schemes.get(reference)

    if not capital_scheme:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)

    return {"reference": capital_scheme.reference}
