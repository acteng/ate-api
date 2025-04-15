from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DateTimeRange:
    from_: datetime
    to: datetime | None = None
