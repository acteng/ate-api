from fastapi import APIRouter

from ate_api.routes.capital_schemes import capital_schemes

router = APIRouter(prefix="/capital-schemes", tags=["capital-schemes"])
router.include_router(capital_schemes.router)
