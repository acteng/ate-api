from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Request, Response
from fastapi.params import Body, Depends
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from ate_api.clock import get_clock
from ate_api.database import get_session, get_unit_of_work
from ate_api.domain.authorities import AuthorityRepository
from ate_api.domain.capital_schemes.capital_scheme_repositories import CapitalSchemeRepository
from ate_api.domain.funding_programmes import FundingProgrammeRepository
from ate_api.infrastructure.clock import Clock
from ate_api.infrastructure.database import (
    AuthorityEntity,
    CapitalSchemeAuthorityReviewEntity,
    CapitalSchemeBidStatusEntity,
    CapitalSchemeEntity,
    CapitalSchemeFinancialEntity,
    CapitalSchemeInterventionEntity,
    CapitalSchemeMilestoneEntity,
    CapitalSchemeOverviewEntity,
    FundingProgrammeEntity,
)
from ate_api.repositories import (
    get_authority_repository,
    get_capital_scheme_repository,
    get_funding_programme_repository,
)
from ate_api.routes.authorities.authorities import AuthorityModel
from ate_api.routes.capital_schemes.capital_schemes import CapitalSchemeModel
from ate_api.routes.funding_programmes import FundingProgrammeModel
from ate_api.unit_of_work import UnitOfWork

router = APIRouter(prefix="/test")


@router.put("/clock", status_code=HTTP_204_NO_CONTENT, response_class=Response)
async def set_clock(clock: Annotated[Clock, Depends(get_clock)], now: Annotated[datetime, Body()]) -> None:
    clock.now = now


@router.post("/funding-programmes", status_code=HTTP_201_CREATED, response_class=Response)
async def create_funding_programme(
    funding_programmes: Annotated[FundingProgrammeRepository, Depends(get_funding_programme_repository)],
    unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)],
    funding_programme: FundingProgrammeModel,
) -> None:
    async with unit_of_work:
        await funding_programmes.add(funding_programme.to_domain())
        await unit_of_work.commit()


@router.delete("/funding-programmes", status_code=HTTP_204_NO_CONTENT)
async def delete_funding_programmes(
    unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Response:
    async with unit_of_work:
        await session.execute(delete(FundingProgrammeEntity))
        await unit_of_work.commit()
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.post("/authorities", status_code=HTTP_201_CREATED, response_class=Response)
async def create_authority(
    authorities: Annotated[AuthorityRepository, Depends(get_authority_repository)],
    unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)],
    authority: AuthorityModel,
) -> None:
    async with unit_of_work:
        await authorities.add(authority.to_domain())
        await unit_of_work.commit()


@router.delete("/authorities", status_code=HTTP_204_NO_CONTENT)
async def delete_authorities(
    unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Response:
    async with unit_of_work:
        await session.execute(delete(AuthorityEntity))
        await unit_of_work.commit()
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.post("/capital-schemes", status_code=HTTP_201_CREATED, response_class=Response)
async def create_capital_scheme(
    clock: Annotated[Clock, Depends(get_clock)],
    capital_schemes: Annotated[CapitalSchemeRepository, Depends(get_capital_scheme_repository)],
    unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)],
    request: Request,
    capital_scheme: CapitalSchemeModel,
) -> None:
    async with unit_of_work:
        await capital_schemes.add(capital_scheme.to_domain(clock.now, request))
        await unit_of_work.commit()


@router.delete("/capital-schemes", status_code=HTTP_204_NO_CONTENT)
async def delete_capital_schemes(
    unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> Response:
    async with unit_of_work:
        await session.execute(delete(CapitalSchemeOverviewEntity))
        await session.execute(delete(CapitalSchemeBidStatusEntity))
        await session.execute(delete(CapitalSchemeFinancialEntity))
        await session.execute(delete(CapitalSchemeMilestoneEntity))
        await session.execute(delete(CapitalSchemeInterventionEntity))
        await session.execute(delete(CapitalSchemeAuthorityReviewEntity))
        await session.execute(delete(CapitalSchemeEntity))
        await unit_of_work.commit()
    return Response(status_code=HTTP_204_NO_CONTENT)
