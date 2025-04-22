from datetime import datetime
from typing import Annotated

from pydantic import Field

from ate_api.domain.dates import DateTimeRange
from ate_api.routes.base import BaseModel


class DateTimeRangeModel(BaseModel):
    from_: Annotated[datetime, Field(alias="from")]
    to: datetime | None = None

    def to_domain(self) -> DateTimeRange:
        return DateTimeRange(self.from_, self.to)
