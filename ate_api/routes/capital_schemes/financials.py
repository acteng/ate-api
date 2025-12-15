from datetime import datetime
from typing import Annotated, Self

from fastapi import APIRouter, Depends, HTTPException
from pydantic import field_validator
from pydantic_core import PydanticCustomError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND

from ate_api.clock import get_clock
from ate_api.database import get_session
from ate_api.domain.capital_scheme_financials import (
    CapitalSchemeFinancial,
    CapitalSchemeFinancials,
    CapitalSchemeFinancialsRepository,
)
from ate_api.domain.capital_schemes.capital_schemes import CapitalSchemeReference
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.moneys import Money
from ate_api.infrastructure.clock import Clock
from ate_api.repositories import get_capital_scheme_financials_repository
from ate_api.routes.base import BaseModel
from ate_api.routes.collections import CollectionModel
from ate_api.routes.data_sources import DataSourceModel
from ate_api.routes.financial_types import FinancialTypeModel


class CapitalSchemeFinancialModel(BaseModel):
    type: FinancialTypeModel
    amount: int
    source: DataSourceModel

    @classmethod
    def from_domain(cls, financial: CapitalSchemeFinancial) -> Self:
        return cls(
            type=FinancialTypeModel.from_domain(financial.type),
            amount=financial.amount.amount,
            source=DataSourceModel.from_domain(financial.data_source),
        )

    def to_domain(self, now: datetime) -> CapitalSchemeFinancial:
        return CapitalSchemeFinancial(
            effective_date=DateTimeRange(now),
            type=self.type.to_domain(),
            amount=Money(self.amount),
            data_source=self.source.to_domain(),
        )


class CreateCapitalSchemeFinancialModel(CapitalSchemeFinancialModel):
    @field_validator("type", mode="before")
    @classmethod
    def check_type(cls, type_: FinancialTypeModel) -> FinancialTypeModel:
        if type_ == FinancialTypeModel.FUNDING_ALLOCATION:
            raise PydanticCustomError("enum", "Funding allocation cannot be created")
        return type_


class CapitalSchemeFinancialsModel(CollectionModel[CapitalSchemeFinancialModel]):
    @classmethod
    def from_domain(cls, financials: CapitalSchemeFinancials) -> Self:
        return cls(items=[CapitalSchemeFinancialModel.from_domain(financial) for financial in financials.financials])


router = APIRouter()


@router.post(
    "/{reference}/financials",
    status_code=HTTP_201_CREATED,
    summary="Create capital scheme financial",
    responses={HTTP_404_NOT_FOUND: {}},
)
async def create_financial(
    clock: Annotated[Clock, Depends(get_clock)],
    capital_scheme_financials: Annotated[
        CapitalSchemeFinancialsRepository, Depends(get_capital_scheme_financials_repository)
    ],
    session: Annotated[AsyncSession, Depends(get_session)],
    reference: str,
    financial_model: CreateCapitalSchemeFinancialModel,
) -> CapitalSchemeFinancialModel:
    """
    Creates a financial for a capital scheme.
    """
    financials = await capital_scheme_financials.get(CapitalSchemeReference(reference))

    if not financials:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)

    financial = financial_model.to_domain(clock.now)
    financials.change_financial(financial)
    await capital_scheme_financials.update(financials)
    await session.commit()

    return CapitalSchemeFinancialModel.from_domain(financial)
