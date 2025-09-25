import pytest

from ate_api.domain.financial_types import FinancialType
from ate_api.infrastructure.database import FinancialTypeName


@pytest.mark.parametrize(
    "type_, type_name",
    [
        (FinancialType.EXPECTED_COST, FinancialTypeName.EXPECTED_COST),
        (FinancialType.ACTUAL_COST, FinancialTypeName.ACTUAL_COST),
        (FinancialType.FUNDING_ALLOCATION, FinancialTypeName.FUNDING_ALLOCATION),
        (FinancialType.SPEND_TO_DATE, FinancialTypeName.SPEND_TO_DATE),
        (FinancialType.FUNDING_REQUEST, FinancialTypeName.FUNDING_REQUEST),
    ],
)
class TestFinancialTypeName:
    def test_from_domain(self, type_: FinancialType, type_name: FinancialTypeName) -> None:
        assert FinancialTypeName.from_domain(type_) == type_name

    def test_to_domain(self, type_: FinancialType, type_name: FinancialTypeName) -> None:
        assert type_name.to_domain() == type_
