import pytest

from ate_api.domain.observation_types import ObservationType
from ate_api.routes.observation_types import ObservationTypeModel


@pytest.mark.parametrize(
    "type_, type_model",
    [
        (ObservationType.PLANNED, ObservationTypeModel.PLANNED),
        (ObservationType.ACTUAL, ObservationTypeModel.ACTUAL),
    ],
)
class TestObservationTypeModel:
    def test_from_domain(self, type_: ObservationType, type_model: ObservationTypeModel) -> None:
        assert ObservationTypeModel.from_domain(type_) == type_model

    def test_to_domain(self, type_: ObservationType, type_model: ObservationTypeModel) -> None:
        assert type_model.to_domain() == type_
