from ate_api.domain.improvements.improvements import Improvement, ImprovementReference, ImprovementRepository


class MemoryImprovementRepository(ImprovementRepository):
    def __init__(self) -> None:
        self._improvements: dict[ImprovementReference, Improvement] = {}

    async def add(self, improvement: Improvement) -> None:
        self._improvements[improvement.reference] = improvement

    async def get(self, reference: ImprovementReference) -> Improvement | None:
        return self._improvements.get(reference)
