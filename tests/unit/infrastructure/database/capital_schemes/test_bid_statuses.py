from datetime import datetime, timezone

import pytest

from ate_api.domain.capital_schemes.bid_statuses import BidStatus, CapitalSchemeBidStatusDetails
from ate_api.domain.dates import DateTimeRange
from ate_api.infrastructure.database import BidStatusEntity, BidStatusName, CapitalSchemeBidStatusEntity


@pytest.mark.parametrize(
    "bid_status, bid_status_name",
    [
        (BidStatus.SUBMITTED, BidStatusName.SUBMITTED),
        (BidStatus.FUNDED, BidStatusName.FUNDED),
        (BidStatus.NOT_FUNDED, BidStatusName.NOT_FUNDED),
        (BidStatus.SPLIT, BidStatusName.SPLIT),
        (BidStatus.DELETED, BidStatusName.DELETED),
    ],
)
class TestBidStatusName:
    def test_to_domain(self, bid_status: BidStatus, bid_status_name: BidStatusName) -> None:
        assert bid_status_name.to_domain() == bid_status

    def test_from_domain(self, bid_status: BidStatus, bid_status_name: BidStatusName) -> None:
        assert BidStatusName.from_domain(bid_status) == bid_status_name


class TestCapitalSchemeBidStatusEntity:
    def test_from_domain(self) -> None:
        bid_status_details = CapitalSchemeBidStatusDetails(
            effective_date=DateTimeRange(datetime(2020, 1, 1), datetime(2020, 2, 1)),
            bid_status=BidStatus.FUNDED,
        )

        bid_status_entity = CapitalSchemeBidStatusEntity.from_domain(bid_status_details, {BidStatus.FUNDED: 1})

        assert (
            bid_status_entity.bid_status_id == 1
            and bid_status_entity.effective_date_from == datetime(2020, 1, 1)
            and bid_status_entity.effective_date_to == datetime(2020, 2, 1)
        )

    def test_from_domain_when_current(self) -> None:
        bid_status_details = CapitalSchemeBidStatusDetails(
            effective_date=DateTimeRange(datetime(2020, 1, 1)), bid_status=BidStatus.FUNDED
        )

        bid_status_entity = CapitalSchemeBidStatusEntity.from_domain(bid_status_details, {BidStatus.FUNDED: 0})

        assert not bid_status_entity.effective_date_to

    def test_from_domain_converts_dates_to_local_europe_london(self) -> None:
        bid_status_details = CapitalSchemeBidStatusDetails(
            effective_date=DateTimeRange(
                datetime(2020, 6, 1, 12, tzinfo=timezone.utc), datetime(2020, 7, 1, 12, tzinfo=timezone.utc)
            ),
            bid_status=BidStatus.FUNDED,
        )

        bid_status_entity = CapitalSchemeBidStatusEntity.from_domain(bid_status_details, {BidStatus.FUNDED: 0})

        assert bid_status_entity.effective_date_from == datetime(2020, 6, 1, 13)
        assert bid_status_entity.effective_date_to == datetime(2020, 7, 1, 13)

    def test_to_domain(self) -> None:
        bid_status_entity = CapitalSchemeBidStatusEntity(
            bid_status=BidStatusEntity(bid_status_name=BidStatusName.FUNDED),
            effective_date_from=datetime(2020, 1, 1),
            effective_date_to=datetime(2020, 2, 1),
        )

        bid_status_details = bid_status_entity.to_domain()

        assert bid_status_details == CapitalSchemeBidStatusDetails(
            effective_date=DateTimeRange(
                datetime(2020, 1, 1, tzinfo=timezone.utc), datetime(2020, 2, 1, tzinfo=timezone.utc)
            ),
            bid_status=BidStatus.FUNDED,
        )

    def test_to_domain_when_current(self) -> None:
        bid_status_entity = CapitalSchemeBidStatusEntity(
            bid_status=BidStatusEntity(bid_status_name=BidStatusName.FUNDED),
            effective_date_from=datetime(2020, 1, 1),
        )

        bid_status_details = bid_status_entity.to_domain()

        assert not bid_status_details.effective_date.to

    def test_to_domain_converts_dates_from_local_europe_london(self) -> None:
        bid_status_entity = CapitalSchemeBidStatusEntity(
            bid_status=BidStatusEntity(bid_status_name=BidStatusName.FUNDED),
            effective_date_from=datetime(2020, 6, 1, 13),
            effective_date_to=datetime(2020, 7, 1, 13),
        )

        bid_status_details = bid_status_entity.to_domain()

        assert bid_status_details.effective_date == DateTimeRange(
            datetime(2020, 6, 1, 12, tzinfo=timezone.utc), datetime(2020, 7, 1, 12, tzinfo=timezone.utc)
        )
