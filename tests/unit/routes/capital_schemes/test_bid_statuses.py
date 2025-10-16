from datetime import UTC, datetime

import pytest

from ate_api.domain.capital_schemes.bid_statuses import BidStatus, CapitalSchemeBidStatusDetails
from ate_api.domain.dates import DateTimeRange
from ate_api.routes.capital_schemes.bid_statuses import BidStatusModel, CapitalSchemeBidStatusDetailsModel


@pytest.mark.parametrize(
    "bid_status, bid_status_model",
    [
        (BidStatus.SUBMITTED, BidStatusModel.SUBMITTED),
        (BidStatus.FUNDED, BidStatusModel.FUNDED),
        (BidStatus.NOT_FUNDED, BidStatusModel.NOT_FUNDED),
        (BidStatus.SPLIT, BidStatusModel.SPLIT),
        (BidStatus.DELETED, BidStatusModel.DELETED),
    ],
)
class TestBidStatusModel:
    def test_from_domain(self, bid_status: BidStatus, bid_status_model: BidStatusModel) -> None:
        assert BidStatusModel.from_domain(bid_status) == bid_status_model

    def test_to_domain(self, bid_status: BidStatus, bid_status_model: BidStatusModel) -> None:
        assert bid_status_model.to_domain() == bid_status


class TestCapitalSchemeBidStatusDetailsModel:
    def test_from_domain(self) -> None:
        bid_status_details = CapitalSchemeBidStatusDetails(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)), bid_status=BidStatus.FUNDED
        )

        bid_status_details_model = CapitalSchemeBidStatusDetailsModel.from_domain(bid_status_details)

        assert bid_status_details_model == CapitalSchemeBidStatusDetailsModel(bid_status=BidStatusModel.FUNDED)

    def test_to_domain(self) -> None:
        bid_status_details_model = CapitalSchemeBidStatusDetailsModel(bid_status=BidStatusModel.FUNDED)

        bid_status_details = bid_status_details_model.to_domain(datetime(2020, 1, 1, tzinfo=UTC))

        assert bid_status_details == CapitalSchemeBidStatusDetails(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)), bid_status=BidStatus.FUNDED
        )
