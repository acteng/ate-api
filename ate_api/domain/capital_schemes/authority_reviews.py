from dataclasses import dataclass
from datetime import datetime

from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import is_zoned


@dataclass(frozen=True)
class CapitalSchemeAuthorityReview:
    review_date: datetime
    data_source: DataSource

    def __post_init__(self) -> None:
        if not is_zoned(self.review_date):
            raise ValueError(f"Review date and time must include a time zone: {self.review_date}")
