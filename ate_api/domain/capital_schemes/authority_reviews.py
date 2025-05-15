from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CapitalSchemeAuthorityReview:
    review_date: datetime
