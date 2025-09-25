import pytest

from ate_api.domain.observation_types import ObservationType
from ate_api.infrastructure.database import ObservationTypeName


@pytest.mark.parametrize(
    "type_, type_name",
    [
        (ObservationType.PLANNED, ObservationTypeName.PLANNED),
        (ObservationType.ACTUAL, ObservationTypeName.ACTUAL),
    ],
)
class TestObservationTypeName:
    def test_from_domain(self, type_: ObservationType, type_name: ObservationTypeName) -> None:
        assert ObservationTypeName.from_domain(type_) == type_name

    def test_to_domain(self, type_: ObservationType, type_name: ObservationTypeName) -> None:
        assert type_name.to_domain() == type_
