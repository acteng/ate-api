from enum import Enum
from typing import Self

from sqlalchemy.orm import Mapped, mapped_column

from ate_api.domain.financial_types import FinancialType
from ate_api.infrastructure.database.base import BaseEntity


class FinancialTypeName(Enum):
    EXPECTED_COST = "expected cost"
    ACTUAL_COST = "actual cost"
    FUNDING_ALLOCATION = "funding allocation"
    SPEND_TO_DATE = "spend to date"
    FUNDING_REQUEST = "funding request"

    @classmethod
    def from_domain(cls, financial_type: FinancialType) -> Self:
        return cls[financial_type.name]

    def to_domain(self) -> FinancialType:
        return FinancialType[self.name]


class FinancialTypeEntity(BaseEntity):
    __tablename__ = "financial_type"
    __table_args__ = {"schema": "common"}

    financial_type_id: Mapped[int] = mapped_column(primary_key=True)
    financial_type_name: Mapped[FinancialTypeName] = mapped_column(unique=True)
