from datetime import UTC, datetime

from ate_api.domain.dates import is_zoned
from ate_api.infrastructure.clock import Clock


class FakeClock(Clock):
    def __init__(self) -> None:
        self._now = datetime(1970, 1, 1, tzinfo=UTC)

    @property
    def now(self) -> datetime:
        return self._now

    @now.setter
    def now(self, now: datetime) -> None:
        if not is_zoned(now):
            raise ValueError(f"Now date and time must include a time zone: {now}")

        self._now = now
