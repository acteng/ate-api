from unittest.mock import AsyncMock

import pytest

from ate_api.infrastructure.database.unit_of_work import DatabaseUnitOfWork


class TestDatabaseUnitOfWork:
    @pytest.fixture(name="session")
    def session_fixture(self) -> AsyncMock:
        return AsyncMock()

    async def test_can_commit(self, session: AsyncMock) -> None:
        async with DatabaseUnitOfWork(session) as unit_of_work:
            await unit_of_work.commit()

        session.commit.assert_called_once()
