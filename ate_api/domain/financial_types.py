from enum import Enum, auto


class FinancialType(Enum):
    EXPECTED_COST = auto()
    ACTUAL_COST = auto()
    FUNDING_ALLOCATION = auto()
    SPEND_TO_DATE = auto()
    FUNDING_REQUEST = auto()
