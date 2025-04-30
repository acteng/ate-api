from typing import Self

from sqlalchemy import delete, select
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
    def from_domain(cls, funding_programme: FundingProgramme) -> Self:
        return cls(funding_programme_code=funding_programme.code)

    def to_domain(self) -> FundingProgramme:
        return FundingProgramme(code=self.funding_programme_code)


class DatabaseFundingProgrammeRepository(FundingProgrammeRepository):
    def __init__(self, session: Session):
        self._session = session

    def add(self, funding_programme: FundingProgramme) -> None:
        self._session.add(FundingProgrammeEntity.from_domain(funding_programme))

    def clear(self) -> None:
        self._session.execute(delete(FundingProgrammeEntity))

    def get(self, code: str) -> FundingProgramme | None:
        result = self._session.scalars(
            select(FundingProgrammeEntity).where(FundingProgrammeEntity.funding_programme_code == code)
        )
        row = result.one_or_none()
        return row.to_domain() if row else None
