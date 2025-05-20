from datetime import datetime


class Clock:
    @property
    def now(self) -> datetime:
        raise NotImplementedError()

    @now.setter
    def now(self, now: datetime) -> None:
        raise NotImplementedError()


class SystemClock(Clock):
    @property
    def now(self) -> datetime:
        return datetime.now()

    @now.setter
    def now(self, now: datetime) -> None:
        raise NotImplementedError()
