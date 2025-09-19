from ate_api.domain.financial_types import FinancialType
from ate_api.infrastructure.database import FinancialTypeName


class TestFinancialTypeName:
    def test_from_domain(self) -> None:
        assert FinancialTypeName.from_domain(FinancialType.FUNDING_ALLOCATION) == FinancialTypeName.FUNDING_ALLOCATION

    def test_to_domain(self) -> None:
        assert FinancialTypeName.FUNDING_ALLOCATION.to_domain() == FinancialType.FUNDING_ALLOCATION
