from datetime import datetime

from ate_api.domain.dates import DateTimeRange


class TestDateTimeRange:
    def test_create_closed(self) -> None:
        date_range = DateTimeRange(datetime(2020, 1, 1), datetime(2020, 2, 1))

        assert date_range.from_ == datetime(2020, 1, 1) and date_range.to == datetime(2020, 2, 1)

    def test_create_open(self) -> None:
        date_range = DateTimeRange(datetime(2020, 1, 1))

        assert date_range.from_ == datetime(2020, 1, 1) and not date_range.to
