from datetime import datetime, timezone

from ate_api.domain.capital_schemes.bid_statuses import CapitalSchemeBidStatus, CapitalSchemeBidStatusDetails
from ate_api.domain.dates import DateTimeRange
from ate_api.infrastructure.database import BidStatusEntity, BidStatusName, CapitalSchemeBidStatusEntity


class TestBidStatusName:
    def test_to_domain(self) -> None:
        assert BidStatusName.FUNDED.to_domain() == CapitalSchemeBidStatus.FUNDED

    def test_from_domain(self) -> None:
        assert BidStatusName.from_domain(CapitalSchemeBidStatus.FUNDED) == BidStatusName.FUNDED


class TestCapitalSchemeBidStatusEntity:
    def test_from_domain(self) -> None:
        bid_status_details = CapitalSchemeBidStatusDetails(
            effective_date=DateTimeRange(datetime(2020, 1, 1), datetime(2020, 2, 1)),
            bid_status=CapitalSchemeBidStatus.FUNDED,
        )

        bid_status_entity = CapitalSchemeBidStatusEntity.from_domain(
            bid_status_details, {CapitalSchemeBidStatus.FUNDED: 1}
        )

        assert (
            bid_status_entity.bid_status_id == 1
            and bid_status_entity.effective_date_from == datetime(2020, 1, 1)
            and bid_status_entity.effective_date_to == datetime(2020, 2, 1)
        )

    def test_from_domain_when_current(self) -> None:
        bid_status_details = CapitalSchemeBidStatusDetails(
            effective_date=DateTimeRange(datetime(2020, 1, 1)), bid_status=CapitalSchemeBidStatus.FUNDED
        )

        bid_status_entity = CapitalSchemeBidStatusEntity.from_domain(
            bid_status_details, {CapitalSchemeBidStatus.FUNDED: 1}
        )

        assert not bid_status_entity.effective_date_to

    def test_from_domain_converts_dates_to_local_europe_london(self) -> None:
        bid_status_details = CapitalSchemeBidStatusDetails(
            effective_date=DateTimeRange(
                datetime(2020, 6, 1, 12, tzinfo=timezone.utc), datetime(2020, 7, 1, 12, tzinfo=timezone.utc)
            ),
            bid_status=CapitalSchemeBidStatus.FUNDED,
        )

        bid_status_entity = CapitalSchemeBidStatusEntity.from_domain(
            bid_status_details, {CapitalSchemeBidStatus.FUNDED: 1}
        )

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
            bid_status=CapitalSchemeBidStatus.FUNDED,
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
