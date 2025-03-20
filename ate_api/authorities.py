from fastapi import APIRouter

router = APIRouter()


@router.get("/authorities/{authority_abbreviation}")
async def get_authority(authority_abbreviation: str) -> dict[str, str]:
    return {"abbreviation": "LIV", "fullName": "Liverpool City Region Combined Authority"}
