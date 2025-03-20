from __future__ import annotations

from fastapi import APIRouter
from pydantic import AliasGenerator, BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

router = APIRouter()


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


class AuthorityModel(BaseModel):
    abbreviation: str
    full_name: str

    model_config = ConfigDict(alias_generator=AliasGenerator(serialization_alias=to_camel))

    @classmethod
    def from_domain(cls, authority: Authority) -> AuthorityModel:
        return AuthorityModel(abbreviation=authority.abbreviation, full_name=authority.full_name)


@router.get("/authorities/{abbreviation}")
async def get_authority(abbreviation: str) -> AuthorityModel:
    authority = Authority(abbreviation="LIV", full_name="Liverpool City Region Combined Authority")
    return AuthorityModel.from_domain(authority)
