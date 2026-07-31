from datetime import datetime

from tests.unit.dates import dummy_datetime, dummy_local_datetime, local_datetime


def test_dummy_datetime() -> None:
    assert dummy_datetime.tzinfo


def test_dummy_local_datetime() -> None:
    assert not dummy_local_datetime.tzinfo


def test_local_datetime() -> None:
    assert local_datetime(2020, 1, 2) == datetime(2020, 1, 2, tzinfo=None)  # noqa: DTZ001


def test_local_datetime_with_hour() -> None:
    assert local_datetime(2020, 1, 2, 12) == datetime(2020, 1, 2, 12, tzinfo=None)  # noqa: DTZ001
