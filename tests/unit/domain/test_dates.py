import re
from datetime import UTC, datetime, timedelta, tzinfo

import pytest

from ate_api.domain.dates import DateTimeRange, is_zoned


class TestDateTimeRange:
    def test_can_create_closed_range(self) -> None:
        date_time_range = DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC), datetime(2020, 2, 1, tzinfo=UTC))

        assert date_time_range.from_ == datetime(2020, 1, 1, tzinfo=UTC) and date_time_range.to == datetime(
            2020, 2, 1, tzinfo=UTC
        )

    def test_can_create_open_range(self) -> None:
        date_time_range = DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC))

        assert date_time_range.from_ == datetime(2020, 1, 1, tzinfo=UTC) and not date_time_range.to

    @pytest.mark.parametrize(
        "from_, to",
        [
            pytest.param(datetime(2020, 1, 1, tzinfo=UTC), datetime(2020, 2, 1, tzinfo=UTC), id="before"),
            pytest.param(datetime(2020, 2, 1, tzinfo=UTC), datetime(2020, 2, 1, tzinfo=UTC), id="equal to"),
        ],
    )
    def test_can_create_range_with_from_before_or_equal_to_to(self, from_: datetime, to: datetime | None) -> None:
        date_time_range = DateTimeRange(from_, to)

        assert date_time_range.from_ == from_ and date_time_range.to == to

    def test_cannot_create_range_with_from_after_to(self) -> None:
        with pytest.raises(
            ValueError,
            match=re.escape("From '2020-01-01 12:00:00+00:00' must not be after to '2019-12-31 13:00:00+00:00'"),
        ):
            DateTimeRange(datetime(2020, 1, 1, 12, tzinfo=UTC), datetime(2019, 12, 31, 13, tzinfo=UTC))

    @pytest.mark.parametrize(
        "from_, to, expected_message",
        [
            pytest.param(
                datetime(2020, 1, 1),
                datetime(2020, 2, 1, tzinfo=UTC),
                "From date and time must include a time zone: 2020-01-01 00:00:00",
                id="local from",
            ),
            pytest.param(
                datetime(2020, 1, 1, tzinfo=UTC),
                datetime(2020, 2, 1),
                "To date and time must include a time zone: 2020-02-01 00:00:00",
                id="local to",
            ),
        ],
    )
    def test_cannot_create_range_with_local_dates(self, from_: datetime, to: datetime, expected_message: str) -> None:
        with pytest.raises(ValueError, match=expected_message):
            DateTimeRange(from_, to)

    @pytest.mark.parametrize(
        "to, expected_is_open",
        [pytest.param(None, True, id="open"), pytest.param(datetime(2020, 2, 1, tzinfo=UTC), False, id="closed")],
    )
    def test_is_open(self, to: datetime | None, expected_is_open: bool) -> None:
        date_time_range = DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC), to)

        assert date_time_range.is_open == expected_is_open

    def test_close(self) -> None:
        open_range = DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC))

        closed_range = open_range.close(datetime(2020, 2, 1, tzinfo=UTC))

        assert closed_range.from_ == datetime(2020, 1, 1, tzinfo=UTC) and closed_range.to == datetime(
            2020, 2, 1, tzinfo=UTC
        )

    def test_cannot_close_when_closed(self) -> None:
        closed_range = DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC), datetime(2020, 2, 1, tzinfo=UTC))

        with pytest.raises(ValueError, match="Date time range is already closed"):
            closed_range.close(datetime(2020, 2, 1, tzinfo=UTC))


class _UnknownUtcOffsetTimezone(tzinfo):
    """
    Python's timezone class does not allow a UTC offset of None.
    """

    def tzname(self, dt: datetime | None) -> str | None:
        return None

    def utcoffset(self, dt: datetime | None) -> timedelta | None:
        return None

    def dst(self, dt: datetime | None) -> timedelta | None:
        return None


@pytest.mark.parametrize(
    "date, expected_is_zoned",
    [
        pytest.param(datetime(2000, 1, 1, tzinfo=UTC), True, id="zoned"),
        pytest.param(datetime(2000, 1, 1), False, id="local"),
        pytest.param(
            datetime(2000, 1, 1, tzinfo=_UnknownUtcOffsetTimezone()), False, id="zoned with unknown UTC offset"
        ),
    ],
)
def test_is_zoned(date: datetime, expected_is_zoned: bool) -> None:
    assert is_zoned(date) == expected_is_zoned
