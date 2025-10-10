from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ate_api.database import get_session
from ate_api.domain.authorities import AuthorityRepository
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeRepository
from ate_api.domain.capital_schemes.milestones import MilestoneRepository
from ate_api.domain.funding_programmes import FundingProgrammeRepository
from ate_api.infrastructure.database.authorities import DatabaseAuthorityRepository
from ate_api.infrastructure.database.capital_schemes.capital_schemes import DatabaseCapitalSchemeRepository
from ate_api.infrastructure.database.capital_schemes.milestones import DatabaseMilestoneRepository
from ate_api.infrastructure.database.funding_programmes import DatabaseFundingProgrammeRepository


def get_funding_programme_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> FundingProgrammeRepository:
    return DatabaseFundingProgrammeRepository(session)


def get_authority_repository(session: Annotated[AsyncSession, Depends(get_session)]) -> AuthorityRepository:
    return DatabaseAuthorityRepository(session)


def get_capital_scheme_repository(session: Annotated[AsyncSession, Depends(get_session)]) -> CapitalSchemeRepository:
    return DatabaseCapitalSchemeRepository(session)


def get_milestone_repository(session: Annotated[AsyncSession, Depends(get_session)]) -> MilestoneRepository:
    return DatabaseMilestoneRepository(session)
