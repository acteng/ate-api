from ate_api.domain.observation_types import ObservationType
from ate_api.infrastructure.database import ObservationTypeName


class TestObservationTypeName:
    def test_from_domain(self) -> None:
        assert ObservationTypeName.from_domain(ObservationType.ACTUAL) == ObservationTypeName.ACTUAL

    def test_to_domain(self) -> None:
        assert ObservationTypeName.ACTUAL.to_domain() == ObservationType.ACTUAL
