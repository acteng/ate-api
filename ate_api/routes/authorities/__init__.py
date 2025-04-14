from fastapi import APIRouter

from ate_api.routes.authorities import authorities, capital_schemes

router = APIRouter(tags=["authorities"])
router.include_router(authorities.router)
router.include_router(capital_schemes.router)
