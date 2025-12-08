from ate_api.domain.capital_scheme_milestones import (
    CapitalSchemeMilestones,
    CapitalSchemeMilestonesRepository,
    Milestone,
    MilestoneRepository,
)
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeReference


class MemoryMilestoneRepository(MilestoneRepository):
    async def get_all(self, is_active: bool | None = None, is_complete: bool | None = None) -> list[Milestone]:
        return [
            milestone
            for milestone in Milestone
            if (is_active is None or milestone.is_active == is_active)
            and (is_complete is None or milestone.is_complete == is_complete)
        ]


class MemoryCapitalSchemeMilestonesRepository(CapitalSchemeMilestonesRepository):
    def __init__(self) -> None:
        self._milestones: dict[CapitalSchemeReference, CapitalSchemeMilestones] = {}

    async def add(self, milestones: CapitalSchemeMilestones) -> None:
        self._milestones[milestones.capital_scheme] = milestones

    async def get(self, capital_scheme: CapitalSchemeReference) -> CapitalSchemeMilestones | None:
        return self._milestones.get(capital_scheme)
