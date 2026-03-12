from ate_api.unit_of_work import UnitOfWork


class FakeUnitOfWork(UnitOfWork):
    def __init__(self) -> None:
        self._serializable = False
        self._committed = False

    @property
    def serializable(self) -> bool:
        return self._serializable

    @property
    def committed(self) -> bool:
        return self._committed

    async def begin_serializable(self) -> None:
        self._serializable = True

    async def commit(self) -> None:
        self._committed = True
