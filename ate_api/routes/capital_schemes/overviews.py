from datetime import datetime
from typing import Self

from fastapi import Request
from pydantic import AnyUrl

from ate_api.domain.capital_schemes.overviews import CapitalSchemeOverview
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.improvements.improvements import ImprovementReference
from ate_api.routes.base import BaseModel
from ate_api.routes.links import path_parameter_for


class CapitalSchemeOverviewModel(BaseModel):
    name: str
    improvement: AnyUrl | None

    @classmethod
    def from_domain(cls, overview: CapitalSchemeOverview, request: Request) -> Self:
        return cls(
            name=overview.name,
            improvement=(
                AnyUrl(str(request.url_for("get_improvement", reference=str(overview.improvement))))
                if overview.improvement
                else None
            ),
        )

    def to_domain(self, now: datetime, request: Request) -> CapitalSchemeOverview:
        return CapitalSchemeOverview(
            effective_date=DateTimeRange(now),
            name=self.name,
            improvement=(
                ImprovementReference(path_parameter_for(request, "get_improvement", "reference", str(self.improvement)))
                if self.improvement
                else None
            ),
        )
