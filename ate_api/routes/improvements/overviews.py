from datetime import datetime
from typing import Self

from fastapi import Request
from pydantic import AnyUrl

from ate_api.domain.authorities import AuthorityAbbreviation
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.improvements.overviews import ImprovementOverview
from ate_api.routes.base import BaseModel
from ate_api.routes.data_sources import DataSourceModel
from ate_api.routes.links import path_parameter_for


class ImprovementOverviewModel(BaseModel):
    name: str
    description: str | None = None
    funding_managed_by: AnyUrl
    source: DataSourceModel

    @classmethod
    def from_domain(cls, overview: ImprovementOverview, request: Request) -> Self:
        return cls(
            name=overview.name,
            description=overview.description,
            funding_managed_by=AnyUrl(
                str(request.url_for("get_authority", abbreviation=str(overview.funding_managed_by)))
            ),
            source=DataSourceModel.from_domain(overview.data_source),
        )

    def to_domain(self, now: datetime, request: Request) -> ImprovementOverview:
        return ImprovementOverview(
            effective_date=DateTimeRange(now),
            name=self.name,
            description=self.description,
            funding_managed_by=AuthorityAbbreviation(
                path_parameter_for(request, "get_authority", "abbreviation", str(self.funding_managed_by))
            ),
            data_source=self.source.to_domain(),
        )
