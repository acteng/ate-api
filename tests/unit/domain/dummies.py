from datetime import UTC, datetime

from ate_api.domain.dates import DateTimeRange


def dummy_date_time_range() -> DateTimeRange:
    return DateTimeRange(datetime.fromtimestamp(0, UTC))
