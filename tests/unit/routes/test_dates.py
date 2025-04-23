from datetime import datetime

from ate_api.domain.dates import DateTimeRange
from ate_api.routes.dates import DateTimeRangeModel


class TestDateTimeRangeModel:
    def test_from_domain(self) -> None:
        date_time_range = DateTimeRange(datetime(2020, 1, 1), datetime(2020, 2, 1))

        date_time_range_model = DateTimeRangeModel.from_domain(date_time_range)

        assert date_time_range_model == DateTimeRangeModel(from_=datetime(2020, 1, 1), to=datetime(2020, 2, 1))

    def test_from_domain_when_open(self) -> None:
        date_time_range = DateTimeRange(datetime(2020, 1, 1))

        date_time_range_model = DateTimeRangeModel.from_domain(date_time_range)

        assert date_time_range_model == DateTimeRangeModel(from_=datetime(2020, 1, 1))

    def test_to_domain(self) -> None:
        date_time_range_model = DateTimeRangeModel(from_=datetime(2020, 1, 1), to=datetime(2020, 2, 1))

        date_time_range = date_time_range_model.to_domain()

        assert date_time_range == DateTimeRange(datetime(2020, 1, 1), datetime(2020, 2, 1))

    def test_to_domain_when_open(self) -> None:
        date_time_range_model = DateTimeRangeModel(from_=datetime(2020, 1, 1))

        date_time_range = date_time_range_model.to_domain()

        assert date_time_range == DateTimeRange(datetime(2020, 1, 1))
