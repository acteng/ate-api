from dataclasses import dataclass, replace
from datetime import datetime
from typing import Self


@dataclass(frozen=True)
class DateTimeRange:
    from_: datetime
    to: datetime | None = None

    def __post_init__(self) -> None:
        if not is_zoned(self.from_):
            raise ValueError(f"From date and time must include a time zone: {self.from_}")

        if self.to and not is_zoned(self.to):
            raise ValueError(f"To date and time must include a time zone: {self.to}")

        if not (self.to is None or self.from_ <= self.to):
            raise ValueError(f"From '{self.from_}' must not be after to '{self.to}'")

    @property
    def is_open(self) -> bool:
        return self.to is None

    def close(self, to: datetime) -> Self:
        if not self.is_open:
            raise ValueError("Date time range is already closed")

        return replace(self, to=to)


def is_zoned(date: datetime) -> bool:
    """
    Determines if the specified date includes a time zone.

    In Python this is known as an "aware" date and time (zoned), as opposed to a "naive" date and time (local).

    See: https://docs.python.org/3.13/library/datetime.html#determining-if-an-object-is-aware-or-naive
    """
    tz = date.tzinfo
    return tz is not None and tz.utcoffset(date) is not None
