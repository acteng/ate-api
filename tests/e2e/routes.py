from typing import Annotated

from fastapi import APIRouter, Response
from fastapi.params import Depends
from sqlalchemy import delete
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from ate_api.database import get_session
from ate_api.domain.authorities import AuthorityRepository
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeRepository
from ate_api.domain.funding_programmes import FundingProgrammeRepository
from ate_api.infrastructure.database import (
    AuthorityEntity,
    CapitalSchemeAuthorityReviewEntity,
    CapitalSchemeBidStatusEntity,
    CapitalSchemeEntity,
    CapitalSchemeOverviewEntity,
    FundingProgrammeEntity,
)
from ate_api.routes.authorities.authorities import AuthorityModel, get_authority_repository
from ate_api.routes.capital_schemes.capital_schemes import CapitalSchemeModel, get_capital_scheme_repository
from ate_api.routes.funding_programmes import FundingProgrammeModel, get_funding_programme_repository

router = APIRouter(prefix="/test")


@router.post("/funding-programmes", status_code=HTTP_201_CREATED, response_class=Response)
def create_funding_programme(
    funding_programmes: Annotated[FundingProgrammeRepository, Depends(get_funding_programme_repository)],
    session: Annotated[Session, Depends(get_session)],
    funding_programme: FundingProgrammeModel,
) -> None:
    funding_programmes.add(funding_programme.to_domain())
    session.commit()


@router.delete("/funding-programmes", status_code=HTTP_204_NO_CONTENT)
def delete_funding_programmes(session: Annotated[Session, Depends(get_session)]) -> Response:
    session.execute(delete(FundingProgrammeEntity))
    session.commit()
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.post("/authorities", status_code=HTTP_201_CREATED, response_class=Response)
def create_authority(
    authorities: Annotated[AuthorityRepository, Depends(get_authority_repository)],
    session: Annotated[Session, Depends(get_session)],
    authority: AuthorityModel,
) -> None:
    authorities.add(authority.to_domain())
    session.commit()


@router.delete("/authorities", status_code=HTTP_204_NO_CONTENT)
def delete_authorities(session: Annotated[Session, Depends(get_session)]) -> Response:
    session.execute(delete(AuthorityEntity))
    session.commit()
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.post("/capital-schemes", status_code=HTTP_201_CREATED, response_class=Response)
def create_capital_scheme(
    capital_schemes: Annotated[CapitalSchemeRepository, Depends(get_capital_scheme_repository)],
    session: Annotated[Session, Depends(get_session)],
    request: Request,
    capital_scheme: CapitalSchemeModel,
) -> None:
    capital_schemes.add(capital_scheme.to_domain(request))
    session.commit()


@router.delete("/capital-schemes", status_code=HTTP_204_NO_CONTENT)
def delete_capital_schemes(session: Annotated[Session, Depends(get_session)]) -> Response:
    session.execute(delete(CapitalSchemeOverviewEntity))
    session.execute(delete(CapitalSchemeBidStatusEntity))
    session.execute(delete(CapitalSchemeAuthorityReviewEntity))
    session.execute(delete(CapitalSchemeEntity))
    session.commit()
    return Response(status_code=HTTP_204_NO_CONTENT)
