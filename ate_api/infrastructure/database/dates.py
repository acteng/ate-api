from datetime import datetime
from zoneinfo import ZoneInfo

_TIMEZONE = ZoneInfo("Europe/London")


def datetime_to_local(zoned: datetime) -> datetime:
    return zoned.astimezone(_TIMEZONE).replace(tzinfo=None)
