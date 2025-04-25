from datetime import datetime, timezone

from ate_api.infrastructure.database.dates import zoned_to_local


def test_zoned_to_local() -> None:
    zoned = datetime(2020, 6, 1, 12, tzinfo=timezone.utc)

    local = zoned_to_local(zoned)

    assert local == datetime(2020, 6, 1, 13)
