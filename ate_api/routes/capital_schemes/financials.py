from datetime import datetime
from typing import Annotated, Self

from fastapi import APIRouter, Depends, HTTPException, Path, Request
from pydantic import AnyUrl, ConfigDict
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND

from ate_api.clock import get_clock
from ate_api.database import get_unit_of_work
from ate_api.domain.capital_scheme_financials import (
    CapitalSchemeFinancials,
    CapitalSchemeFinancialsRepository,
    CapitalSchemeFunding,
    CapitalSchemeSpend,
)
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeReference
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.funding_programmes import FundingProgrammeCode
from ate_api.domain.moneys import Money
from ate_api.infrastructure.clock import Clock
from ate_api.repositories import get_capital_scheme_financials_repository
from ate_api.routes.base import BaseModel
from ate_api.routes.collections import CollectionModel
from ate_api.routes.concurrency import retry_on_serialization_failure
from ate_api.routes.data_sources import DataSourceModel
from ate_api.routes.links import path_parameter_for
from ate_api.unit_of_work import UnitOfWork


class CapitalSchemeFundingModel(BaseModel):
    funding_programme: AnyUrl
    amount: int
    source: DataSourceModel

    @classmethod
    def from_domain(cls, funding: CapitalSchemeFunding, request: Request) -> Self:
        return cls(
            funding_programme=AnyUrl(
                str(request.url_for("get_funding_programme", code=str(funding.funding_programme)))
            ),
            amount=funding.amount.amount,
            source=DataSourceModel.from_domain(funding.data_source),
        )

    def to_domain(self, now: datetime, request: Request) -> CapitalSchemeFunding:
        return CapitalSchemeFunding(
            effective_date=DateTimeRange(now),
            funding_programme=FundingProgrammeCode(
                path_parameter_for(request, "get_funding_programme", "code", str(self.funding_programme))
            ),
            amount=Money(self.amount),
            data_source=self.source.to_domain(),
        )


class CapitalSchemeSpendModel(BaseModel):
    amount: int
    source: DataSourceModel

    model_config = ConfigDict(json_schema_extra={"examples": [{"amount": 2_000_000, "source": "ATF3 bid"}]})

    @classmethod
    def from_domain(cls, spend: CapitalSchemeSpend) -> Self:
        return cls(amount=spend.amount.amount, source=DataSourceModel.from_domain(spend.data_source))

    def to_domain(self, now: datetime) -> CapitalSchemeSpend:
        return CapitalSchemeSpend(
            effective_date=DateTimeRange(now),
            amount=Money(self.amount),
            data_source=self.source.to_domain(),
        )


class CapitalSchemeFinancialsModel(BaseModel):
    funding: CollectionModel[CapitalSchemeFundingModel]
    spend: CapitalSchemeSpendModel | None

    @classmethod
    def from_domain(cls, financials: CapitalSchemeFinancials, request: Request) -> Self:
        return cls(
            funding=CollectionModel[CapitalSchemeFundingModel](
                items=[CapitalSchemeFundingModel.from_domain(funding, request) for funding in financials.fundings]
            ),
            spend=CapitalSchemeSpendModel.from_domain(financials.spend) if financials.spend else None,
        )


router = APIRouter()


@router.post(
    "/{reference}/financials/spend",
    status_code=HTTP_201_CREATED,
    summary="Create capital scheme spend",
    responses={HTTP_404_NOT_FOUND: {}},
)
@retry_on_serialization_failure(max_retries=5, jitter=0.1)
async def create_spend(
    clock: Annotated[Clock, Depends(get_clock)],
    capital_scheme_financials: Annotated[
        CapitalSchemeFinancialsRepository, Depends(get_capital_scheme_financials_repository)
    ],
    unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)],
    reference: Annotated[str, Path(examples=["ATE00001"])],
    spend_model: CapitalSchemeSpendModel,
) -> CapitalSchemeSpendModel:
    """
    Creates a spend for a capital scheme.
    """
    async with unit_of_work:
        await unit_of_work.begin_serializable()

        financials = await capital_scheme_financials.get(CapitalSchemeReference(reference))

        if not financials:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND)

        spend = spend_model.to_domain(clock.now)
        financials.change_spend(spend)
        await capital_scheme_financials.update(financials)
        await unit_of_work.commit()

    return CapitalSchemeSpendModel.from_domain(spend)
