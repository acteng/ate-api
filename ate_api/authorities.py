from fastapi import APIRouter
from pydantic import AliasGenerator, BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

router = APIRouter()


class AuthorityModel(BaseModel):
    abbreviation: str
    full_name: str

    model_config = ConfigDict(alias_generator=AliasGenerator(serialization_alias=to_camel))


@router.get("/authorities/{authority_abbreviation}")
async def get_authority(authority_abbreviation: str) -> AuthorityModel:
    return AuthorityModel(abbreviation="LIV", full_name="Liverpool City Region Combined Authority")
