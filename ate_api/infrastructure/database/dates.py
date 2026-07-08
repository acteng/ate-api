from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from ate_api.domain.dates import is_zoned

_LOCAL_TIMEZONE = ZoneInfo("Europe/London")


def zoned_to_local(zoned: datetime) -> datetime:
    if not is_zoned(zoned):
        raise ValueError(f"Date and time must include a time zone: {zoned}")

    return zoned.astimezone(_LOCAL_TIMEZONE).replace(tzinfo=None)


def local_to_zoned(local: datetime) -> datetime:
    if is_zoned(local):
        raise ValueError(f"Date and time must not include a time zone: {local}")

    return local.replace(tzinfo=_LOCAL_TIMEZONE).astimezone(UTC)
