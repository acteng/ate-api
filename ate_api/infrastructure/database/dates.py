from datetime import datetime
from zoneinfo import ZoneInfo

_TIMEZONE = ZoneInfo("Europe/London")


def zoned_to_local(zoned: datetime) -> datetime:
    return zoned.astimezone(_TIMEZONE).replace(tzinfo=None)
