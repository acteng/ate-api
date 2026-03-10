from ate_api.unit_of_work import UnitOfWork


class FakeUnitOfWork(UnitOfWork):
    def __init__(self) -> None:
        self._committed = False

    @property
    def committed(self) -> bool:
        return self._committed

    async def commit(self) -> None:
        self._committed = True
