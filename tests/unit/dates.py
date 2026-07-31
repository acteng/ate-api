from datetime import UTC, datetime

dummy_datetime = datetime.fromtimestamp(0, UTC)
dummy_local_datetime = datetime.fromtimestamp(0)  # noqa: DTZ006


def local_datetime(year: int, month: int, day: int, hour: int = 0) -> datetime:
    """
    Factory method for local date times to centralise ignoring linting rule in tests.

    See: https://docs.astral.sh/ruff/rules/call-datetime-without-tzinfo/
    """
    return datetime(year, month, day, hour)  # noqa: DTZ001
