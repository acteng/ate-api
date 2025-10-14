from datetime import datetime

import pytest

from ate_api.domain.dates import DateTimeRange


class TestDateTimeRange:
    def test_can_create_closed_range(self) -> None:
        date_time_range = DateTimeRange(datetime(2020, 1, 1), datetime(2020, 2, 1))

        assert date_time_range.from_ == datetime(2020, 1, 1) and date_time_range.to == datetime(2020, 2, 1)

    def test_can_create_open_range(self) -> None:
        date_time_range = DateTimeRange(datetime(2020, 1, 1))

        assert date_time_range.from_ == datetime(2020, 1, 1) and not date_time_range.to

    @pytest.mark.parametrize(
        "from_, to",
        [
            pytest.param(datetime(2020, 1, 1), datetime(2020, 2, 1), id="before"),
            pytest.param(datetime(2020, 2, 1), datetime(2020, 2, 1), id="equal to"),
        ],
    )
    def test_can_create_range_with_from_before_or_equal_to_to(self, from_: datetime, to: datetime | None) -> None:
        date_time_range = DateTimeRange(from_, to)

        assert date_time_range.from_ == from_ and date_time_range.to == to

    def test_cannot_create_range_with_from_after_to(self) -> None:
        with pytest.raises(ValueError, match="From '2020-01-01 12:00:00' must not be after to '2019-12-31 13:00:00'"):
            DateTimeRange(datetime(2020, 1, 1, 12), datetime(2019, 12, 31, 13))
