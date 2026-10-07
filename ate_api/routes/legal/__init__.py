from fastapi import APIRouter
from starlette.responses import FileResponse

router = APIRouter(include_in_schema=False)


@router.get("/.well-known/security.txt")
async def security() -> FileResponse:
    return FileResponse("ate_api/routes/legal/security.txt")
