from ate_api.domain.financial_types import FinancialType
from ate_api.routes.financial_types import FinancialTypeModel


class TestFinancialTypeModel:
    def test_from_domain(self) -> None:
        assert FinancialTypeModel.from_domain(FinancialType.FUNDING_ALLOCATION) == FinancialTypeModel.FUNDING_ALLOCATION

    def test_to_domain(self) -> None:
        assert FinancialTypeModel.FUNDING_ALLOCATION.to_domain() == FinancialType.FUNDING_ALLOCATION
