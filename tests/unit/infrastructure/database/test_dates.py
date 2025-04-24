from datetime import datetime, timezone

from ate_api.infrastructure.database.dates import datetime_to_local


def test_datetime_to_local() -> None:
    zoned = datetime(2020, 6, 1, 12, tzinfo=timezone.utc)

    local = datetime_to_local(zoned)

    assert local == datetime(2020, 6, 1, 13)


def test_datetime_to_local_when_none() -> None:
    local = datetime_to_local(None)

    assert local is None
