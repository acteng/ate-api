from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession

from ate_api.unit_of_work import UnitOfWork


class DatabaseUnitOfWork(UnitOfWork):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def begin_serializable(self) -> None:
        await self._session.connection(execution_options={"isolation_level": "SERIALIZABLE"})

    async def commit(self) -> None:
        await self._session.commit()

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> bool | None:
        await self._session.reset()
        return None
