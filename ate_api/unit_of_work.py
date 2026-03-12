from types import TracebackType
from typing import Self


class UnitOfWork:
    async def begin_serializable(self) -> None:
        raise NotImplementedError()

    async def commit(self) -> None:
        raise NotImplementedError()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ) -> bool | None:
        return None
