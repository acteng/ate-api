from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def index() -> dict[str, str]:
    return {"message": "Hello World"}
