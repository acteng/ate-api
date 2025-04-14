from fastapi import APIRouter

router = APIRouter()


@router.get(
    "/authorities/{abbreviation}/capital-schemes/bid-submitting", summary="Get authority bid submitting capital schemes"
)
def get_authority_bid_submitting_capital_schemes(abbreviation: str) -> None:
    """
    Gets the capital schemes submitted by an authority.
    """
    pass
