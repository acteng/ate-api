from tests.unit.infrastructure.memory.unit_of_work import FakeUnitOfWork


class TestFakeUnitOfWork:
    async def test_can_create(self) -> None:
        unit_of_work = FakeUnitOfWork()

        assert not unit_of_work.committed

    async def test_can_commit(self) -> None:
        async with FakeUnitOfWork() as unit_of_work:
            await unit_of_work.commit()

        assert unit_of_work.committed
