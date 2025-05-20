from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DateTimeRange:
    from_: datetime
    to: datetime | None = None

    def __post_init__(self) -> None:
        if not (self.to is None or self.from_ <= self.to):
            raise ValueError(f"From '{self.from_}' must not be after to '{self.to}'")
