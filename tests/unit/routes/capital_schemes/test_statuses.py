from datetime import UTC, datetime

import pytest

from ate_api.domain.capital_schemes.statuses import CapitalSchemeStatus, Status
from ate_api.domain.dates import DateTimeRange
from ate_api.routes.capital_schemes.statuses import CapitalSchemeStatusModel, StatusModel


@pytest.mark.parametrize(
    "status, status_model",
    [
        (Status.PIPELINE, StatusModel.PIPELINE),
        (Status.ACTIVE, StatusModel.ACTIVE),
        (Status.PAUSED, StatusModel.PAUSED),
        (Status.CONCLUDED, StatusModel.CONCLUDED),
        (Status.DELETED, StatusModel.DELETED),
    ],
)
class TestStatusModel:
    def test_from_domain(self, status: Status, status_model: StatusModel) -> None:
        assert StatusModel.from_domain(status) == status_model

    def test_to_domain(self, status: Status, status_model: StatusModel) -> None:
        assert status_model.to_domain() == status


class TestCapitalSchemeStatusModel:
    def test_from_domain(self) -> None:
        status = CapitalSchemeStatus(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)), status=Status.ACTIVE
        )

        status_model = CapitalSchemeStatusModel.from_domain(status)

        assert status_model == CapitalSchemeStatusModel(status=StatusModel.ACTIVE)

    def test_to_domain(self) -> None:
        status_model = CapitalSchemeStatusModel(status=StatusModel.ACTIVE)

        status = status_model.to_domain(datetime(2020, 1, 1, tzinfo=UTC))

        assert status == CapitalSchemeStatus(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)), status=Status.ACTIVE
        )
