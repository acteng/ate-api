from datetime import datetime

from ate_api.domain.capital_schemes.bid_statuses import CapitalSchemeBidStatus, CapitalSchemeBidStatusDetails
from ate_api.domain.dates import DateTimeRange
from ate_api.routes.capital_schemes.bid_statuses import CapitalSchemeBidStatusDetailsModel, CapitalSchemeBidStatusModel
from ate_api.routes.dates import DateTimeRangeModel


class TestCapitalSchemeBidStatusModel:
    def test_from_domain(self) -> None:
        assert (
            CapitalSchemeBidStatusModel.from_domain(CapitalSchemeBidStatus.FUNDED) == CapitalSchemeBidStatusModel.FUNDED
        )

    def test_to_domain(self) -> None:
        assert CapitalSchemeBidStatusModel.FUNDED.to_domain() == CapitalSchemeBidStatus.FUNDED


class TestCapitalSchemeBidStatusDetailsModel:
    def test_from_domain(self) -> None:
        bid_status_details = CapitalSchemeBidStatusDetails(
            effective_date=DateTimeRange(datetime(2020, 1, 1)), bid_status=CapitalSchemeBidStatus.FUNDED
        )

        bid_status_details_model = CapitalSchemeBidStatusDetailsModel.from_domain(bid_status_details)

        assert bid_status_details_model == CapitalSchemeBidStatusDetailsModel(
            effective_date=DateTimeRangeModel(from_=datetime(2020, 1, 1)), bid_status=CapitalSchemeBidStatusModel.FUNDED
        )

    def test_to_domain(self) -> None:
        bid_status_details_model = CapitalSchemeBidStatusDetailsModel(
            effective_date=DateTimeRangeModel(from_=datetime(2020, 1, 1)), bid_status=CapitalSchemeBidStatusModel.FUNDED
        )

        bid_status_details = bid_status_details_model.to_domain()

        assert bid_status_details == CapitalSchemeBidStatusDetails(
            effective_date=DateTimeRange(datetime(2020, 1, 1)), bid_status=CapitalSchemeBidStatus.FUNDED
        )
