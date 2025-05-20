from datetime import datetime
from enum import Enum
from typing import Annotated, Self

from pydantic import AnyUrl, Field
from starlette.requests import Request

from ate_api.domain.authorities import AuthorityAbbreviation
from ate_api.domain.capital_schemes.overviews import CapitalSchemeOverview, CapitalSchemeType
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.funding_programmes import FundingProgrammeCode
from ate_api.routes.base import BaseModel
from ate_api.routes.links import path_parameter_for


class CapitalSchemeTypeModel(str, Enum):
    DEVELOPMENT = "development"
    CONSTRUCTION = "construction"

    @classmethod
    def from_domain(cls, type_: CapitalSchemeType) -> Self:
        return cls[type_.name]

    def to_domain(self) -> CapitalSchemeType:
        return CapitalSchemeType[self.name]


class CapitalSchemeOverviewModel(BaseModel):
    name: str
    bid_submitting_authority: AnyUrl
    funding_programme: AnyUrl
    type_: Annotated[CapitalSchemeTypeModel, Field(alias="type")]

    @classmethod
    def from_domain(cls, overview: CapitalSchemeOverview, request: Request) -> Self:
        return cls(
            name=overview.name,
            bid_submitting_authority=AnyUrl(
                str(request.url_for("get_authority", abbreviation=str(overview.bid_submitting_authority)))
            ),
            funding_programme=AnyUrl(
                str(request.url_for("get_funding_programme", code=str(overview.funding_programme)))
            ),
            type_=CapitalSchemeTypeModel.from_domain(overview.type),
        )

    def to_domain(self, now: datetime, request: Request) -> CapitalSchemeOverview:
        return CapitalSchemeOverview(
            effective_date=DateTimeRange(now),
            name=self.name,
            bid_submitting_authority=AuthorityAbbreviation(
                path_parameter_for(request, "get_authority", "abbreviation", str(self.bid_submitting_authority))
            ),
            funding_programme=FundingProgrammeCode(
                path_parameter_for(request, "get_funding_programme", "code", str(self.funding_programme))
            ),
            type=self.type_.to_domain(),
        )
