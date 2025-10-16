from fastapi import APIRouter

from ate_api.routes.capital_schemes import capital_schemes, financials, milestones

router = APIRouter(prefix="/capital-schemes", tags=["capital-schemes"])
router.include_router(milestones.router)
# lower precedence to avoid interpreting every path as a capital scheme reference
router.include_router(capital_schemes.router)
router.include_router(financials.router)
