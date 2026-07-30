from datetime import UTC, datetime

import pytest

from ate_api.domain.capital_schemes.statuses import CapitalSchemeStatus, Status
from ate_api.domain.dates import DateTimeRange
from ate_api.infrastructure.database import CapitalSchemeSchemeStatusEntity, SchemeStatusEntity, SchemeStatusName


@pytest.mark.parametrize(
    "status, scheme_status_name",
    [
        (Status.PIPELINE, SchemeStatusName.PIPELINE),
        (Status.ACTIVE, SchemeStatusName.ACTIVE),
        (Status.PAUSED, SchemeStatusName.PAUSED),
        (Status.CONCLUDED, SchemeStatusName.CONCLUDED),
        (Status.DELETED, SchemeStatusName.DELETED),
    ],
)
class TestSchemeStatusName:
    def test_from_domain(self, status: Status, scheme_status_name: SchemeStatusName) -> None:
        assert SchemeStatusName.from_domain(status) == scheme_status_name

    def test_to_domain(self, status: Status, scheme_status_name: SchemeStatusName) -> None:
        assert scheme_status_name.to_domain() == status


class TestCapitalSchemeSchemeStatusEntity:
    def test_from_domain(self) -> None:
        status = CapitalSchemeStatus(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)), status=Status.ACTIVE
        )

        scheme_status_entity = CapitalSchemeSchemeStatusEntity.from_domain(status, {Status.ACTIVE: 1})

        assert (
            scheme_status_entity.scheme_status_id == 1
            and scheme_status_entity.effective_date_from == datetime(2020, 1, 1)
            and not scheme_status_entity.effective_date_to
        )

    def test_from_domain_when_historic(self) -> None:
        status = CapitalSchemeStatus(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC), datetime(2020, 2, 1, tzinfo=UTC)),
            status=Status.ACTIVE,
        )

        scheme_status_entity = CapitalSchemeSchemeStatusEntity.from_domain(status, {Status.ACTIVE: 0})

        assert scheme_status_entity.effective_date_to == datetime(2020, 2, 1)

    def test_from_domain_converts_dates_to_local_europe_london(self) -> None:
        status = CapitalSchemeStatus(
            effective_date=DateTimeRange(datetime(2020, 6, 1, 12, tzinfo=UTC), datetime(2020, 7, 1, 12, tzinfo=UTC)),
            status=Status.ACTIVE,
        )

        scheme_status_entity = CapitalSchemeSchemeStatusEntity.from_domain(status, {Status.ACTIVE: 0})

        assert scheme_status_entity.effective_date_from == datetime(2020, 6, 1, 13)
        assert scheme_status_entity.effective_date_to == datetime(2020, 7, 1, 13)

    def test_to_domain(self) -> None:
        scheme_status_entity = CapitalSchemeSchemeStatusEntity(
            scheme_status=SchemeStatusEntity(scheme_status_name=SchemeStatusName.ACTIVE),
            effective_date_from=datetime(2020, 1, 1),
        )

        status = scheme_status_entity.to_domain()

        assert status == CapitalSchemeStatus(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)), status=Status.ACTIVE
        )

    def test_to_domain_when_historic(self) -> None:
        scheme_status_entity = CapitalSchemeSchemeStatusEntity(
            scheme_status=SchemeStatusEntity(scheme_status_name=SchemeStatusName.ACTIVE),
            effective_date_from=datetime(2020, 1, 1),
            effective_date_to=datetime(2020, 2, 1),
        )

        status = scheme_status_entity.to_domain()

        assert status.effective_date.to == datetime(2020, 2, 1, tzinfo=UTC)

    def test_to_domain_converts_dates_from_local_europe_london(self) -> None:
        scheme_status_entity = CapitalSchemeSchemeStatusEntity(
            scheme_status=SchemeStatusEntity(scheme_status_name=SchemeStatusName.ACTIVE),
            effective_date_from=datetime(2020, 6, 1, 13),
            effective_date_to=datetime(2020, 7, 1, 13),
        )

        status = scheme_status_entity.to_domain()

        assert status.effective_date == DateTimeRange(
            datetime(2020, 6, 1, 12, tzinfo=UTC), datetime(2020, 7, 1, 12, tzinfo=UTC)
        )
