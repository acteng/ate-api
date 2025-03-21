from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class Authority:
    def __init__(self, abbreviation: str, full_name: str):
        self._abbreviation = abbreviation
        self._full_name = full_name

    @property
    def abbreviation(self) -> str:
        return self._abbreviation

    @property
    def full_name(self) -> str:
        return self._full_name


class AuthorityRepository:
    def add(self, authority: Authority) -> None:
        raise NotImplementedError()

    def get_by_abbreviation(self, abbreviation: str) -> Authority:
        raise NotImplementedError()


class MemoryAuthorityRepository(AuthorityRepository):
    def __init__(self) -> None:
        self._authorities = dict[str, Authority]()

    def add(self, authority: Authority) -> None:
        self._authorities[authority.abbreviation] = authority

    def get_by_abbreviation(self, abbreviation: str) -> Authority:
        return self._authorities[abbreviation]


class AuthorityModel(BaseModel):
    abbreviation: str
    full_name: str

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    @classmethod
    def from_domain(cls, authority: Authority) -> AuthorityModel:
        return AuthorityModel(abbreviation=authority.abbreviation, full_name=authority.full_name)

    def to_domain(self) -> Authority:
        return Authority(abbreviation=self.abbreviation, full_name=self.full_name)


router = APIRouter()
_authorities = MemoryAuthorityRepository()
_authorities.add(Authority(abbreviation="GMA", full_name="Greater Manchester Combined Authority"))


async def get_authority_repository() -> AuthorityRepository:
    return _authorities


@router.get("/authorities/{abbreviation}")
async def get_authority(
    authorities: Annotated[AuthorityRepository, Depends(get_authority_repository)], abbreviation: str
) -> AuthorityModel:
    authority = authorities.get_by_abbreviation(abbreviation)
    return AuthorityModel.from_domain(authority)
