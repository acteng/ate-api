from unittest.mock import AsyncMock

import pytest

from ate_api.infrastructure.database.unit_of_work import DatabaseUnitOfWork


class TestDatabaseUnitOfWork:
    @pytest.fixture(name="session")
    def session_fixture(self) -> AsyncMock:
        return AsyncMock()

    async def test_can_begin_serializable(self, session: AsyncMock) -> None:
        async with DatabaseUnitOfWork(session) as unit_of_work:
            await unit_of_work.begin_serializable()

        session.connection.assert_called_once_with(execution_options={"isolation_level": "SERIALIZABLE"})

    async def test_can_commit(self, session: AsyncMock) -> None:
        async with DatabaseUnitOfWork(session) as unit_of_work:
            await unit_of_work.commit()

        session.commit.assert_called_once()

    async def test_can_reset_on_exit(self, session: AsyncMock) -> None:
        async with DatabaseUnitOfWork(session):
            pass

        session.reset.assert_called_once()

    async def test_can_reset_on_exception(self, session: AsyncMock) -> None:
        with pytest.raises(RuntimeError):
            async with DatabaseUnitOfWork(session):
                raise RuntimeError()

        session.reset.assert_called_once()
