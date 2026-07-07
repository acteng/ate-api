from fastapi import APIRouter

from ate_api.routes.improvements import improvements

router = APIRouter(prefix="/improvements", tags=["improvements"])
router.include_router(improvements.router)
