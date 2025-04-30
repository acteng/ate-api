from datetime import datetime
from typing import Annotated, Self

from pydantic import Field

from ate_api.domain.dates import DateTimeRange
from ate_api.routes.base import BaseModel


class DateTimeRangeModel(BaseModel):
    from_: Annotated[datetime, Field(alias="from")]
    to: datetime | None = None

    @classmethod
    def from_domain(cls, date_time_range: DateTimeRange) -> Self:
        return cls(from_=date_time_range.from_, to=date_time_range.to)

    def to_domain(self) -> DateTimeRange:
        return DateTimeRange(self.from_, self.to)
