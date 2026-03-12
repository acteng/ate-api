from collections.abc import Awaitable
from typing import Callable

import pytest
from sqlalchemy.exc import DBAPIError

from ate_api.routes.concurrency import RetryError, retry_on_serialization_failure


class TestRetryOnSerializationFailure:
    async def test_delegates(self) -> None:
        result = await pass_through("bar")

        assert result == "bar"

    async def test_retries_on_serialization_failure(self) -> None:
        raise_serialization_failure = create_raise_serialization_failure(raise_count=2, max_retries=3)

        call_count = await raise_serialization_failure()

        assert call_count == 3

    async def test_raises_retry_error_after_max_retries(self) -> None:
        raise_serialization_failure = create_raise_serialization_failure(raise_count=3, max_retries=3)

        with pytest.raises(RetryError, match="Retry failed after 3 attempts") as exception_info:
            await raise_serialization_failure()
        assert isinstance(exception_info.value.__cause__, DBAPIError)

    async def test_raises_other_exception(self) -> None:
        with pytest.raises(RuntimeError, match="foo"):
            await raise_other_exception()

    # TODO: test jitter


@retry_on_serialization_failure(max_retries=1)
async def pass_through(foo: str) -> str:
    return foo


def create_raise_serialization_failure(raise_count: int, max_retries: int) -> Callable[[], Awaitable[int]]:
    call_count = 0

    @retry_on_serialization_failure(max_retries=max_retries)
    async def _raise_serialization_failure() -> int:
        nonlocal call_count

        call_count += 1

        if call_count <= raise_count:
            raise create_serialization_failure()

        return call_count

    return _raise_serialization_failure


@retry_on_serialization_failure(max_retries=1)
async def raise_other_exception() -> None:
    raise RuntimeError("foo")


def create_serialization_failure() -> DBAPIError:
    # See: https://www.postgresql.org/docs/current/mvcc-serialization-failure-handling.html
    serialization_failure = "40001"

    db_api_error = Exception()
    setattr(db_api_error, "sqlstate", serialization_failure)
    return DBAPIError(statement=None, params=None, orig=db_api_error)
