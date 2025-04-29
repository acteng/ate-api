from __future__ import annotations

from sqlalchemy import delete
from sqlalchemy.orm import Mapped, Session, mapped_column

from ate_api.domain.funding_programmes import (
    FundingProgramme,
    FundingProgrammeRepository,
)
from ate_api.infrastructure.database import BaseEntity


class FundingProgrammeEntity(BaseEntity):
    __tablename__ = "funding_programme"
    __table_args__ = {"schema": "common"}

    funding_programme_id: Mapped[int] = mapped_column(primary_key=True)
    funding_programme_code: Mapped[str] = mapped_column(unique=True)

    @classmethod
    def from_domain(cls, funding_programme: FundingProgramme) -> FundingProgrammeEntity:
        return cls(funding_programme_code=funding_programme.code)


class DatabaseFundingProgrammeRepository(FundingProgrammeRepository):
    def __init__(self, session: Session):
        self._session = session

    def add(self, funding_programme: FundingProgramme) -> None:
        self._session.add(FundingProgrammeEntity.from_domain(funding_programme))

    def clear(self) -> None:
        self._session.execute(delete(FundingProgrammeEntity))
