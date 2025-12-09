from datetime import date, datetime
from enum import Enum
from typing import Self

from sqlalchemy import ForeignKey, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, contains_eager, mapped_column, relationship

from ate_api.domain.capital_scheme_milestones import (
    CapitalSchemeMilestone,
    CapitalSchemeMilestones,
    CapitalSchemeMilestonesRepository,
    Milestone,
    MilestoneRepository,
)
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeReference
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.observation_types import ObservationType
from ate_api.infrastructure.database.base import BaseEntity
from ate_api.infrastructure.database.capital_schemes.capital_schemes import CapitalSchemeEntity
from ate_api.infrastructure.database.data_sources import DataSourceEntity, DataSourceName
from ate_api.infrastructure.database.dates import local_to_zoned, zoned_to_local
from ate_api.infrastructure.database.observation_types import ObservationTypeEntity, ObservationTypeName


class MilestoneName(Enum):
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


class MilestoneEntity(BaseEntity):
    __tablename__ = "milestone"
    __table_args__ = {"schema": "capital_scheme"}

    milestone_id: Mapped[int] = mapped_column(primary_key=True)
    milestone_name: Mapped[MilestoneName] = mapped_column(unique=True)
    stage_order: Mapped[int]
    is_active: Mapped[bool]
    is_complete: Mapped[bool]


class CapitalSchemeMilestoneEntity(BaseEntity):
    __tablename__ = "capital_scheme_milestone"
    __table_args__ = {"schema": "capital_scheme"}

    capital_scheme_milestone_id: Mapped[int] = mapped_column(primary_key=True)
    capital_scheme_id = mapped_column(ForeignKey(CapitalSchemeEntity.capital_scheme_id), nullable=False)
    milestone_id = mapped_column(ForeignKey(MilestoneEntity.milestone_id), nullable=False)
    milestone: Mapped[MilestoneEntity] = relationship(lazy="raise")
    status_date: Mapped[date]
    observation_type_id = mapped_column(ForeignKey(ObservationTypeEntity.observation_type_id), nullable=False)
    observation_type: Mapped[ObservationTypeEntity] = relationship(lazy="raise")
    data_source_id = mapped_column(ForeignKey(DataSourceEntity.data_source_id), nullable=False)
    data_source: Mapped[DataSourceEntity] = relationship(lazy="raise")
    effective_date_from: Mapped[datetime]
    effective_date_to: Mapped[datetime | None]

    @classmethod
    def from_domain(
        cls,
        milestone: CapitalSchemeMilestone,
        capital_scheme_id: int,
        milestone_ids: dict[Milestone, int],
        observation_type_ids: dict[ObservationType, int],
        data_source_ids: dict[DataSource, int],
    ) -> Self:
        return cls(
            capital_scheme_milestone_id=milestone.surrogate_id,
            capital_scheme_id=capital_scheme_id,
            milestone_id=milestone_ids[milestone.milestone],
            status_date=milestone.status_date,
            observation_type_id=observation_type_ids[milestone.observation_type],
            data_source_id=data_source_ids[milestone.data_source],
            effective_date_from=zoned_to_local(milestone.effective_date.from_),
            effective_date_to=zoned_to_local(milestone.effective_date.to) if milestone.effective_date.to else None,
        )

    def to_domain(self) -> CapitalSchemeMilestone:
        return CapitalSchemeMilestone(
            effective_date=DateTimeRange(
                local_to_zoned(self.effective_date_from),
                local_to_zoned(self.effective_date_to) if self.effective_date_to else None,
            ),
            milestone=self.milestone.milestone_name.to_domain(),
            observation_type=self.observation_type.observation_type_name.to_domain(),
            status_date=self.status_date,
            data_source=self.data_source.data_source_name.to_domain(),
            surrogate_id=self.capital_scheme_milestone_id,
        )


class DatabaseMilestoneRepository(MilestoneRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_all(self, is_active: bool | None = None, is_complete: bool | None = None) -> list[Milestone]:
        statement = select(MilestoneEntity).order_by(MilestoneEntity.stage_order)

        if is_active is not None:
            statement = statement.where(MilestoneEntity.is_active == is_active)

        if is_complete is not None:
            statement = statement.where(MilestoneEntity.is_complete == is_complete)

        result = await self._session.scalars(statement)
        rows = result.all()
        return [row.milestone_name.to_domain() for row in rows]


class DatabaseCapitalSchemeMilestonesRepository(CapitalSchemeMilestonesRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, milestones: CapitalSchemeMilestones) -> None:
        capital_scheme_id = await self._get_capital_scheme_id(milestones)
        milestone_ids = await self._get_milestone_ids(milestones)
        observation_type_ids = await self._get_observation_type_ids(milestones)
        data_source_ids = await self._get_data_source_ids(milestones)

        self._session.add_all(
            CapitalSchemeMilestoneEntity.from_domain(
                milestone, capital_scheme_id, milestone_ids, observation_type_ids, data_source_ids
            )
            for milestone in milestones.milestones
        )

    async def get(self, capital_scheme: CapitalSchemeReference) -> CapitalSchemeMilestones | None:
        result = await self._session.scalars(
            select(CapitalSchemeMilestoneEntity)
            .options(
                contains_eager(CapitalSchemeMilestoneEntity.milestone),
                contains_eager(CapitalSchemeMilestoneEntity.observation_type),
                contains_eager(CapitalSchemeMilestoneEntity.data_source),
            )
            .join(CapitalSchemeEntity)
            .join(MilestoneEntity)
            .join(ObservationTypeEntity)
            .join(DataSourceEntity)
            .where(CapitalSchemeEntity.scheme_reference == str(capital_scheme))
            .where(CapitalSchemeMilestoneEntity.effective_date_to.is_(None))
            .order_by(MilestoneEntity.stage_order)
            .order_by(ObservationTypeEntity.observation_type_id)
        )
        rows = result.all()

        milestones = CapitalSchemeMilestones(capital_scheme=capital_scheme)
        for row in rows:
            milestones.change_milestone(row.to_domain())
        return milestones

    async def _get_capital_scheme_id(self, milestones: CapitalSchemeMilestones) -> int:
        capital_scheme_reference = str(milestones.capital_scheme)
        rows = await self._session.scalars(
            select(CapitalSchemeEntity.capital_scheme_id).where(
                CapitalSchemeEntity.scheme_reference == capital_scheme_reference
            )
        )
        return rows.one()

    async def _get_milestone_ids(self, milestones: CapitalSchemeMilestones) -> dict[Milestone, int]:
        milestone_names = {MilestoneName.from_domain(milestone.milestone) for milestone in milestones.milestones}
        rows = await self._session.execute(
            select(MilestoneEntity.milestone_name, MilestoneEntity.milestone_id).where(
                MilestoneEntity.milestone_name.in_(milestone_names)
            )
        )
        return {row.milestone_name.to_domain(): row.milestone_id for row in rows}

    async def _get_observation_type_ids(self, milestones: CapitalSchemeMilestones) -> dict[ObservationType, int]:
        observation_type_names = {
            ObservationTypeName.from_domain(milestone.observation_type) for milestone in milestones.milestones
        }
        rows = await self._session.execute(
            select(ObservationTypeEntity.observation_type_name, ObservationTypeEntity.observation_type_id).where(
                ObservationTypeEntity.observation_type_name.in_(observation_type_names)
            )
        )
        return {row.observation_type_name.to_domain(): row.observation_type_id for row in rows}

    async def _get_data_source_ids(self, milestones: CapitalSchemeMilestones) -> dict[DataSource, int]:
        data_source_names = {DataSourceName.from_domain(milestone.data_source) for milestone in milestones.milestones}
        rows = await self._session.execute(
            select(DataSourceEntity.data_source_name, DataSourceEntity.data_source_id).where(
                DataSourceEntity.data_source_name.in_(data_source_names)
            )
        )
        return {row.data_source_name.to_domain(): row.data_source_id for row in rows}
