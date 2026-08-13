from fastapi import APIRouter

from ate_api.routes.capital_schemes import authority_reviews, capital_schemes, financials, milestones

router = APIRouter(prefix="/capital-schemes", tags=["capital-schemes"])
router.include_router(capital_schemes.router)
router.include_router(financials.router)
router.include_router(milestones.router)
router.include_router(authority_reviews.router)
