from typing import Self

from sqlalchemy import select
from sqlalchemy.orm import Mapped, Session, mapped_column

from ate_api.domain.authorities import Authority, AuthorityRepository
from ate_api.infrastructure.database.base import BaseEntity


class AuthorityEntity(BaseEntity):
    __tablename__ = "authority"
    __table_args__ = {"schema": "authority"}

    authority_id: Mapped[int] = mapped_column(primary_key=True)
    authority_full_name: Mapped[str] = mapped_column(unique=True)
    authority_abbreviation: Mapped[str] = mapped_column(unique=True)

    @classmethod
    def from_domain(cls, authority: Authority) -> Self:
        return cls(authority_full_name=authority.full_name, authority_abbreviation=authority.abbreviation)

    def to_domain(self) -> Authority:
        return Authority(abbreviation=self.authority_abbreviation, full_name=self.authority_full_name)


class DatabaseAuthorityRepository(AuthorityRepository):
    def __init__(self, session: Session):
        self._session = session

    def add(self, authority: Authority) -> None:
        self._session.add(AuthorityEntity.from_domain(authority))

    def get(self, abbreviation: str) -> Authority | None:
        result = self._session.scalars(
            select(AuthorityEntity).where(AuthorityEntity.authority_abbreviation == abbreviation)
        )
        row = result.one_or_none()
        return row.to_domain() if row else None
