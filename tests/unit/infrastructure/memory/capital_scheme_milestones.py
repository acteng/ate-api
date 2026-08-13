from ate_api.domain.capital_scheme_milestones import CapitalSchemeMilestones, CapitalSchemeMilestonesRepository
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeReference


class MemoryCapitalSchemeMilestonesRepository(CapitalSchemeMilestonesRepository):
    def __init__(self) -> None:
        self._milestones: dict[CapitalSchemeReference, CapitalSchemeMilestones] = {}

    async def add(self, milestones: CapitalSchemeMilestones) -> None:
        self._milestones[milestones.capital_scheme] = milestones

    async def get(self, capital_scheme: CapitalSchemeReference) -> CapitalSchemeMilestones | None:
        return self._milestones.get(capital_scheme)

    async def update(self, milestones: CapitalSchemeMilestones) -> None:
        self._milestones[milestones.capital_scheme] = milestones
