from typing import Self

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from ate_api.domain.authorities import Authority, AuthorityAbbreviation, AuthorityRepository
from ate_api.infrastructure.database.base import BaseEntity


class AuthorityEntity(BaseEntity):
    __tablename__ = "authority"
    __table_args__ = {"schema": "authority"}

    authority_id: Mapped[int] = mapped_column(primary_key=True)
    authority_full_name: Mapped[str] = mapped_column(unique=True)
    authority_abbreviation: Mapped[str] = mapped_column(unique=True)

    @classmethod
    def from_domain(cls, authority: Authority) -> Self:
        return cls(authority_full_name=authority.full_name, authority_abbreviation=str(authority.abbreviation))

    def to_domain(self) -> Authority:
        return Authority(
            abbreviation=AuthorityAbbreviation(self.authority_abbreviation), full_name=self.authority_full_name
        )


class DatabaseAuthorityRepository(AuthorityRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, authority: Authority) -> None:
        self._session.add(AuthorityEntity.from_domain(authority))

    async def get(self, abbreviation: AuthorityAbbreviation) -> Authority | None:
        result = await self._session.scalars(
            select(AuthorityEntity).where(AuthorityEntity.authority_abbreviation == str(abbreviation))
        )
        row = result.one_or_none()
        return row.to_domain() if row else None
