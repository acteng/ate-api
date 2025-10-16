from datetime import UTC, datetime
from typing import Any
from unittest.mock import patch

import pytest

from ate_api.infrastructure.clock import SystemClock
from tests.unit.infrastructure.clock import FakeClock


class TestSystemClock:
    @pytest.fixture(name="clock")
    def clock_fixture(self) -> SystemClock:
        return SystemClock()

    @patch("ate_api.infrastructure.clock.datetime")
    def test_get_now(self, mock_datetime: Any, clock: SystemClock) -> None:
        mock_datetime.now.return_value = datetime(2020, 1, 2, 12)

        assert clock.now == datetime(2020, 1, 2, 12)

    @patch("ate_api.infrastructure.clock.datetime")
    def test_get_now_returns_utc(self, mock_datetime: Any, clock: SystemClock) -> None:
        mock_datetime.now.return_value = datetime.min

        _ = clock.now

        assert mock_datetime.now.call_args.args == (UTC,)

    def test_set_now(self, clock: SystemClock) -> None:
        with pytest.raises(NotImplementedError):
            clock.now = datetime(2020, 1, 2)


class TestFakeClock:
    @pytest.fixture(name="clock")
    def clock_fixture(self) -> FakeClock:
        return FakeClock()

    def test_get_now_initially_returns_epoch(self, clock: FakeClock) -> None:
        assert clock.now == datetime(1970, 1, 1, tzinfo=UTC)

    def test_set_now(self, clock: FakeClock) -> None:
        clock.now = datetime(2020, 1, 2, 12, tzinfo=UTC)

        assert clock.now == datetime(2020, 1, 2, 12, tzinfo=UTC)

    def test_cannot_set_now_with_local_date(self, clock: FakeClock) -> None:
        with pytest.raises(ValueError, match="Now date and time must include a time zone: 2020-01-02 12:00:00"):
            clock.now = datetime(2020, 1, 2, 12)
