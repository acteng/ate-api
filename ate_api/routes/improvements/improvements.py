from datetime import datetime
from typing import Annotated, Self

from fastapi import APIRouter, Depends, HTTPException, Path, Request
from pydantic import AnyUrl, ConfigDict, Field
from starlette.status import HTTP_404_NOT_FOUND

from ate_api.domain.improvements.improvements import Improvement, ImprovementReference, ImprovementRepository
from ate_api.repositories import get_improvement_repository
from ate_api.routes.base import BaseModel
from ate_api.routes.improvements.overviews import ImprovementOverviewModel


class ImprovementModel(BaseModel):
    id: Annotated[AnyUrl | None, Field(alias="@id")] = None
    reference: str
    overview: ImprovementOverviewModel

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "@id": "https://api.activetravelengland.gov.uk/improvements/IMP00001",
                    "reference": "IMP00001",
                    "overview": {
                        "name": "Wirral Package",
                        "description": 'Improvement for the "Wirral Package" capital scheme created as part of funding devolution.',
                        "fundingManagedBy": "https://api.activetravelengland.gov.uk/authorities/LIV",
                        "source": "authority update",
                    },
                }
            ]
        }
    )

    @classmethod
    def from_domain(cls, improvement: Improvement, request: Request) -> Self:
        return cls(
            id=AnyUrl(str(request.url_for("get_improvement", reference=str(improvement.reference)))),
            reference=str(improvement.reference),
            overview=ImprovementOverviewModel.from_domain(improvement.overview, request),
        )

    def to_domain(self, now: datetime, request: Request) -> Improvement:
        return Improvement(
            reference=ImprovementReference(self.reference),
            overview=self.overview.to_domain(now, request),
        )


router = APIRouter()


@router.get("/{reference}", summary="Get active travel improvement", responses={HTTP_404_NOT_FOUND: {}})
async def get_improvement(
    improvements: Annotated[ImprovementRepository, Depends(get_improvement_repository)],
    request: Request,
    reference: Annotated[str, Path(examples=["IMP00001"])],
) -> ImprovementModel:
    """
    Gets an active travel improvement.
    """
    improvement = await improvements.get(ImprovementReference(reference))

    if not improvement:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)

    return ImprovementModel.from_domain(improvement, request)
