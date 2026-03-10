from sqlalchemy.ext.asyncio import AsyncSession

from ate_api.unit_of_work import UnitOfWork


class DatabaseUnitOfWork(UnitOfWork):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def commit(self) -> None:
        await self._session.commit()
