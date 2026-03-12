from datetime import date, datetime
from enum import Enum
from typing import Annotated, Self

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import ConfigDict
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND

from ate_api.clock import get_clock
from ate_api.database import get_unit_of_work
from ate_api.domain.capital_scheme_milestones import (
    CapitalSchemeMilestone,
    CapitalSchemeMilestones,
    CapitalSchemeMilestonesRepository,
    Milestone,
    MilestoneRepository,
)
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeReference
from ate_api.domain.dates import DateTimeRange
from ate_api.infrastructure.clock import Clock
from ate_api.repositories import get_capital_scheme_milestones_repository, get_milestone_repository
from ate_api.routes.base import BaseModel
from ate_api.routes.collections import CollectionModel
from ate_api.routes.concurrency import retry_on_serialization_failure
from ate_api.routes.data_sources import DataSourceModel
from ate_api.routes.observation_types import ObservationTypeModel
from ate_api.unit_of_work import UnitOfWork


class MilestoneModel(str, Enum):
    PUBLIC_CONSULTATION_COMPLETED = "public consultation completed"
    FEASIBILITY_DESIGN_STARTED = "feasibility design started"
    FEASIBILITY_DESIGN_COMPLETED = "feasibility design completed"
    PRELIMINARY_DESIGN_COMPLETED = "preliminary design completed"
    OUTLINE_DESIGN_COMPLETED = "outline design completed"
    DETAILED_DESIGN_COMPLETED = "detailed design completed"
    CONSTRUCTION_STARTED = "construction started"
    CONSTRUCTION_COMPLETED = "construction completed"
    FUNDING_COMPLETED = "funding completed"
    NOT_PROGRESSED = "not progressed"
    SUPERSEDED = "superseded"
    REMOVED = "removed"

    @classmethod
    def from_domain(cls, milestone: Milestone) -> Self:
        return cls[milestone.name]

    def to_domain(self) -> Milestone:
        return Milestone[self.name]


class MilestonesModel(CollectionModel[MilestoneModel]):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "items": [
                        "public consultation completed",
                        "feasibility design started",
                        "feasibility design completed",
                        "preliminary design completed",
                        "outline design completed",
                        "detailed design completed",
                        "construction started",
                        "construction completed",
                    ]
                }
            ]
        }
    )


class CapitalSchemeMilestoneModel(BaseModel):
    milestone: MilestoneModel
    observation_type: ObservationTypeModel
    status_date: date
    source: DataSourceModel

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "milestone": "detailed design completed",
                    "observationType": "actual",
                    "statusDate": "2020-03-01",
                    "source": "ATF4 bid",
                }
            ]
        }
    )

    @classmethod
    def from_domain(cls, milestone: CapitalSchemeMilestone) -> Self:
        return cls(
            milestone=MilestoneModel.from_domain(milestone.milestone),
            observation_type=ObservationTypeModel.from_domain(milestone.observation_type),
            status_date=milestone.status_date,
            source=DataSourceModel.from_domain(milestone.data_source),
        )

    def to_domain(self, now: datetime) -> CapitalSchemeMilestone:
        return CapitalSchemeMilestone(
            effective_date=DateTimeRange(now),
            milestone=self.milestone.to_domain(),
            observation_type=self.observation_type.to_domain(),
            status_date=self.status_date,
            data_source=self.source.to_domain(),
        )


class CapitalSchemeMilestonesModel(CollectionModel[CapitalSchemeMilestoneModel]):
    current_milestone: MilestoneModel | None = None

    @classmethod
    def from_domain(cls, milestones: CapitalSchemeMilestones) -> Self:
        return cls(
            current_milestone=(
                MilestoneModel.from_domain(milestones.current_milestone) if milestones.current_milestone else None
            ),
            items=[CapitalSchemeMilestoneModel.from_domain(milestone) for milestone in milestones.milestones],
        )


router = APIRouter()


@router.get("/milestones", summary="Get capital scheme milestones")
async def get_milestones(
    milestones: Annotated[MilestoneRepository, Depends(get_milestone_repository)],
    is_active: Annotated[bool | None, Query(alias="active", examples=[True])] = None,
    is_complete: Annotated[bool | None, Query(alias="complete", examples=[False])] = None,
) -> MilestonesModel:
    """
    Gets the capital scheme milestones.
    """
    all_milestones = await milestones.get_all(is_active=is_active, is_complete=is_complete)

    return MilestonesModel(items=[MilestoneModel.from_domain(milestone) for milestone in all_milestones])


@router.post(
    "/{reference}/milestones",
    status_code=HTTP_201_CREATED,
    summary="Create capital scheme milestones",
    responses={HTTP_404_NOT_FOUND: {}},
)
@retry_on_serialization_failure(max_retries=5, jitter=0.1)
async def create_milestones(
    clock: Annotated[Clock, Depends(get_clock)],
    capital_scheme_milestones: Annotated[
        CapitalSchemeMilestonesRepository, Depends(get_capital_scheme_milestones_repository)
    ],
    unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)],
    reference: Annotated[str, Path(examples=["ATE00001"])],
    milestones_model: CollectionModel[CapitalSchemeMilestoneModel],
) -> CollectionModel[CapitalSchemeMilestoneModel]:
    """
    Creates milestones for a capital scheme.
    """
    async with unit_of_work:
        await unit_of_work.begin_serializable()

        milestones = await capital_scheme_milestones.get(CapitalSchemeReference(reference))

        if not milestones:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND)

        now = clock.now
        new_milestones = [milestone_model.to_domain(now) for milestone_model in milestones_model.items]
        for milestone in new_milestones:
            milestones.change_milestone(milestone)
        await capital_scheme_milestones.update(milestones)
        await unit_of_work.commit()

    return CollectionModel[CapitalSchemeMilestoneModel](
        items=[CapitalSchemeMilestoneModel.from_domain(milestone) for milestone in new_milestones]
    )
