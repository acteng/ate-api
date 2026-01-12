from dataclasses import dataclass, field
from datetime import datetime

from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import is_zoned


@dataclass(frozen=True)
class CapitalSchemeAuthorityReview:
    review_date: datetime
    data_source: DataSource
    surrogate_id: int | None = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not is_zoned(self.review_date):
            raise ValueError(f"Review date and time must include a time zone: {self.review_date}")
