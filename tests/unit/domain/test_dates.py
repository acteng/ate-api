from datetime import datetime

import pytest

from ate_api.domain.dates import DateTimeRange


class TestDateTimeRange:
    def test_create_closed(self) -> None:
        date_range = DateTimeRange(datetime(2020, 1, 1), datetime(2020, 2, 1))

        assert date_range.from_ == datetime(2020, 1, 1) and date_range.to == datetime(2020, 2, 1)

    def test_create_open(self) -> None:
        date_range = DateTimeRange(datetime(2020, 1, 1))

        assert date_range.from_ == datetime(2020, 1, 1) and not date_range.to

    @pytest.mark.parametrize(
        "from_, to",
        [
            (datetime(2020, 1, 1), datetime(2020, 2, 1)),
            (datetime(2020, 2, 1), datetime(2020, 2, 1)),
            (datetime(2020, 1, 1), None),
        ],
    )
    def test_from_before_or_equal_to_to(self, from_: datetime, to: datetime | None) -> None:
        DateTimeRange(from_, to)

    def test_from_after_to(self) -> None:
        with pytest.raises(ValueError, match="From '2020-01-01 12:00:00' must not be after to '2019-12-31 13:00:00'"):
            DateTimeRange(datetime(2020, 1, 1, 12), datetime(2019, 12, 31, 13))
