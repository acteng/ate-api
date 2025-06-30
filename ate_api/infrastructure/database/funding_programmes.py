from typing import Self

from sqlalchemy import exists, false, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from ate_api.domain.funding_programmes import FundingProgramme, FundingProgrammeCode, FundingProgrammeRepository
from ate_api.infrastructure.database import BaseEntity


class FundingProgrammeEntity(BaseEntity):
    __tablename__ = "funding_programme"
    __table_args__ = {"schema": "common"}

    funding_programme_id: Mapped[int] = mapped_column(primary_key=True)
    funding_programme_code: Mapped[str] = mapped_column(unique=True)
    is_under_embargo: Mapped[bool]

    @classmethod
    def from_domain(cls, funding_programme: FundingProgramme) -> Self:
        return cls(funding_programme_code=str(funding_programme.code), is_under_embargo=False)

    def to_domain(self) -> FundingProgramme:
        return FundingProgramme(code=FundingProgrammeCode(self.funding_programme_code))


class DatabaseFundingProgrammeRepository(FundingProgrammeRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, funding_programme: FundingProgramme) -> None:
        self._session.add(FundingProgrammeEntity.from_domain(funding_programme))

    async def get(self, code: FundingProgrammeCode) -> FundingProgramme | None:
        result = await self._session.scalars(
            select(FundingProgrammeEntity)
            .where(FundingProgrammeEntity.funding_programme_code == str(code))
            .where(FundingProgrammeEntity.is_under_embargo == false())
        )
        row = result.one_or_none()
        return row.to_domain() if row else None

    async def exists(self, code: FundingProgrammeCode) -> bool:
        result = await self._session.scalars(
            select(
                exists()
                .where(FundingProgrammeEntity.funding_programme_code == str(code))
                .where(FundingProgrammeEntity.is_under_embargo == false())
            )
        )
        return result.one()
