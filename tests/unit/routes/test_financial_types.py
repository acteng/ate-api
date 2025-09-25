import pytest

from ate_api.domain.financial_types import FinancialType
from ate_api.routes.financial_types import FinancialTypeModel


@pytest.mark.parametrize(
    "type_, type_model",
    [
        (FinancialType.EXPECTED_COST, FinancialTypeModel.EXPECTED_COST),
        (FinancialType.ACTUAL_COST, FinancialTypeModel.ACTUAL_COST),
        (FinancialType.FUNDING_ALLOCATION, FinancialTypeModel.FUNDING_ALLOCATION),
        (FinancialType.SPEND_TO_DATE, FinancialTypeModel.SPEND_TO_DATE),
        (FinancialType.FUNDING_REQUEST, FinancialTypeModel.FUNDING_REQUEST),
    ],
)
class TestFinancialTypeModel:
    def test_from_domain(self, type_: FinancialType, type_model: FinancialTypeModel) -> None:
        assert FinancialTypeModel.from_domain(type_) == type_model

    def test_to_domain(self, type_: FinancialType, type_model: FinancialTypeModel) -> None:
        assert type_model.to_domain() == type_
