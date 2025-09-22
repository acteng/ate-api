from datetime import datetime
from typing import Self

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ate_api.domain.capital_schemes.financials import CapitalSchemeFinancial
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.financial_types import FinancialType
from ate_api.domain.moneys import Money
from ate_api.infrastructure.database import BaseEntity
from ate_api.infrastructure.database.dates import local_to_zoned, zoned_to_local
from ate_api.infrastructure.database.financial_types import FinancialTypeEntity


class CapitalSchemeFinancialEntity(BaseEntity):
    __tablename__ = "capital_scheme_financial"
    __table_args__ = {"schema": "capital_scheme"}

    capital_scheme_financial_id: Mapped[int] = mapped_column(primary_key=True)
    capital_scheme_id = mapped_column(ForeignKey("capital_scheme.capital_scheme.capital_scheme_id"), nullable=False)
    financial_type_id = mapped_column(ForeignKey(FinancialTypeEntity.financial_type_id), nullable=False)
    financial_type: Mapped[FinancialTypeEntity] = relationship(lazy="raise")
    amount: Mapped[int]
    effective_date_from: Mapped[datetime]
    effective_date_to: Mapped[datetime | None]

    @classmethod
    def from_domain(cls, financial: CapitalSchemeFinancial, financial_type_ids: dict[FinancialType, int]) -> Self:
        return cls(
            financial_type_id=financial_type_ids[financial.type],
            amount=financial.amount.amount,
            effective_date_from=zoned_to_local(financial.effective_date.from_),
            effective_date_to=zoned_to_local(financial.effective_date.to) if financial.effective_date.to else None,
        )

    def to_domain(self) -> CapitalSchemeFinancial:
        return CapitalSchemeFinancial(
            effective_date=DateTimeRange(
                local_to_zoned(self.effective_date_from),
                local_to_zoned(self.effective_date_to) if self.effective_date_to else None,
            ),
            type=self.financial_type.financial_type_name.to_domain(),
            amount=Money(self.amount),
        )
