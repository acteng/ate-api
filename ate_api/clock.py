from ate_api.infrastructure.clock import Clock, SystemClock


def get_clock() -> Clock:
    return SystemClock()
