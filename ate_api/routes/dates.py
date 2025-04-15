from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from ate_api.domain.dates import DateTimeRange


class DateTimeRangeModel(BaseModel):
    from_: Annotated[datetime, Field(alias="from")]
    to: datetime | None = None

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    def to_domain(self) -> DateTimeRange:
        return DateTimeRange(self.from_, self.to)
