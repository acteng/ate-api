import asyncio
from functools import wraps
from random import random
from typing import Awaitable, Callable

from sqlalchemy.exc import DBAPIError


class RetryError(Exception):
    pass


def retry_on_serialization_failure[**P, T](
    max_retries: int, jitter: float = 0
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    def _decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @wraps(func)
        async def _retry(*args: P.args, **kwargs: P.kwargs) -> T:
            for retry in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except DBAPIError as exception:
                    if not _is_serialization_failure(exception):
                        raise
                    if retry + 1 == max_retries:
                        raise RetryError(f"Retry failed after {max_retries} attempts") from exception

                await asyncio.sleep(jitter * random())

            raise RuntimeError()

        return _retry

    return _decorator


def _is_serialization_failure(exception: DBAPIError) -> bool:
    sqlstate: str = getattr(exception.orig, "sqlstate")
    # See: https://www.postgresql.org/docs/current/mvcc-serialization-failure-handling.html
    serialization_failure = "40001"

    return sqlstate == serialization_failure
