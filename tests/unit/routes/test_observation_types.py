from ate_api.domain.observation_types import ObservationType
from ate_api.routes.observation_types import ObservationTypeModel


class TestObservationTypeModel:
    def test_from_domain(self) -> None:
        assert ObservationTypeModel.from_domain(ObservationType.ACTUAL) == ObservationTypeModel.ACTUAL

    def test_to_domain(self) -> None:
        assert ObservationTypeModel.ACTUAL.to_domain() == ObservationType.ACTUAL
