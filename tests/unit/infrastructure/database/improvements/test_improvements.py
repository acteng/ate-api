from datetime import UTC, datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from ate_api.domain.authorities import AuthorityAbbreviation
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.improvements.improvements import Improvement, ImprovementReference
from ate_api.domain.improvements.overviews import ImprovementOverview
from ate_api.infrastructure.database import (
    AuthorityEntity,
    DataSourceEntity,
    DataSourceName,
    ImprovementEntity,
    ImprovementOverviewEntity,
)
from ate_api.infrastructure.database.improvements.improvements import DatabaseImprovementRepository
from tests.unit.dates import local_datetime
from tests.unit.infrastructure.database.builders import build_authority_entity, build_data_source_entity


class TestImprovementEntity:
    def test_from_domain(self) -> None:
        improvement = Improvement(
            reference=ImprovementReference("IMP00001"),
            overview=ImprovementOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                name="Wirral Package",
                funding_managed_by=AuthorityAbbreviation("LIV"),
                data_source=DataSource.AUTHORITY_UPDATE,
            ),
        )

        improvement_entity = ImprovementEntity.from_domain(
            improvement, {AuthorityAbbreviation("LIV"): 1}, {DataSource.AUTHORITY_UPDATE: 2}
        )

        assert improvement_entity.improvement_reference == "IMP00001"
        (overview_entity,) = improvement_entity.improvement_overviews
        assert (
            overview_entity.improvement_name == "Wirral Package"
            and overview_entity.improvement_description is None
            and overview_entity.funding_managed_by_id == 1
            and overview_entity.data_source_id == 2
            and overview_entity.effective_date_from == local_datetime(2020, 1, 1)
            and not overview_entity.effective_date_to
        )

    def test_to_domain(self) -> None:
        improvement_entity = ImprovementEntity(
            improvement_reference="IMP00001",
            improvement_overviews=[
                ImprovementOverviewEntity(
                    improvement_name="Wirral Package",
                    funding_managed_by=AuthorityEntity(authority_abbreviation="LIV"),
                    data_source=DataSourceEntity(data_source_name=DataSourceName.AUTHORITY_UPDATE),
                    effective_date_from=local_datetime(2020, 1, 1),
                )
            ],
        )

        improvement = improvement_entity.to_domain()

        assert improvement.reference == ImprovementReference("IMP00001")
        assert improvement.overview == ImprovementOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            name="Wirral Package",
            funding_managed_by=AuthorityAbbreviation("LIV"),
            data_source=DataSource.AUTHORITY_UPDATE,
        )


@pytest.mark.usefixtures("data")
@pytest.mark.asyncio(loop_scope="package")
class TestDatabaseImprovementRepository:
    async def test_add(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    build_authority_entity(id_=1, abbreviation="LIV"),
                    build_data_source_entity(id_=2, name=DataSourceName.AUTHORITY_UPDATE),
                ]
            )

        async with AsyncSession(engine) as session, session.begin():
            improvements = DatabaseImprovementRepository(session)
            await improvements.add(
                Improvement(
                    reference=ImprovementReference("IMP00001"),
                    overview=ImprovementOverview(
                        effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                        name="Wirral Package",
                        description='Improvement for the "Wirral Package" capital scheme created as part of funding devolution.',
                        funding_managed_by=AuthorityAbbreviation("LIV"),
                        data_source=DataSource.AUTHORITY_UPDATE,
                    ),
                )
            )

        async with AsyncSession(engine) as session:
            (improvement_row,) = await session.scalars(select(ImprovementEntity))
            (overview_row,) = await session.scalars(select(ImprovementOverviewEntity))
        assert improvement_row.improvement_reference == "IMP00001"
        assert (
            overview_row.improvement_id == improvement_row.improvement_id
            and overview_row.improvement_name == "Wirral Package"
            and overview_row.improvement_description
            == 'Improvement for the "Wirral Package" capital scheme created as part of funding devolution.'
            and overview_row.funding_managed_by_id == 1
            and overview_row.data_source_id == 2
            and overview_row.effective_date_from == local_datetime(2020, 1, 1)
            and not overview_row.effective_date_to
        )

    async def test_get(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    liv := build_authority_entity(abbreviation="LIV"),
                    authority_update := build_data_source_entity(name=DataSourceName.AUTHORITY_UPDATE),
                    ImprovementEntity(
                        improvement_reference="IMP00001",
                        improvement_overviews=[
                            ImprovementOverviewEntity(
                                improvement_name="Wirral Package",
                                improvement_description='Improvement for the "Wirral Package" capital scheme created as part of funding devolution.',
                                funding_managed_by=liv,
                                data_source=authority_update,
                                effective_date_from=local_datetime(2020, 1, 1),
                            )
                        ],
                    ),
                    ImprovementEntity(
                        improvement_reference="IMP00002",
                        improvement_overviews=[
                            ImprovementOverviewEntity(
                                improvement_name="School Streets",
                                funding_managed_by=liv,
                                data_source=authority_update,
                                effective_date_from=local_datetime(2020, 1, 1),
                            )
                        ],
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            improvements = DatabaseImprovementRepository(session)
            improvement = await improvements.get(ImprovementReference("IMP00001"))

        assert improvement and improvement.reference == ImprovementReference("IMP00001")
        assert improvement.overview == ImprovementOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            name="Wirral Package",
            description='Improvement for the "Wirral Package" capital scheme created as part of funding devolution.',
            funding_managed_by=AuthorityAbbreviation("LIV"),
            data_source=DataSource.AUTHORITY_UPDATE,
        )

    async def test_get_fetches_current_overview(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    liv := build_authority_entity(abbreviation="LIV"),
                    authority_update := build_data_source_entity(name=DataSourceName.AUTHORITY_UPDATE),
                    ImprovementEntity(
                        improvement_reference="IMP00001",
                        improvement_overviews=[
                            ImprovementOverviewEntity(
                                improvement_name="Wirral Package",
                                funding_managed_by=liv,
                                data_source=authority_update,
                                effective_date_from=local_datetime(2020, 1, 1),
                                effective_date_to=local_datetime(2020, 2, 1),
                            ),
                            ImprovementOverviewEntity(
                                improvement_name="School Streets",
                                funding_managed_by=liv,
                                data_source=authority_update,
                                effective_date_from=local_datetime(2020, 2, 1),
                            ),
                        ],
                    ),
                ]
            )

        async with AsyncSession(engine) as session:
            improvements = DatabaseImprovementRepository(session)
            improvement = await improvements.get(ImprovementReference("IMP00001"))

        assert improvement and improvement.overview == ImprovementOverview(
            effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)),
            name="School Streets",
            funding_managed_by=AuthorityAbbreviation("LIV"),
            data_source=DataSource.AUTHORITY_UPDATE,
        )

    async def test_get_when_no_overview(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add(ImprovementEntity(improvement_reference="IMP00001"))

        async with AsyncSession(engine) as session:
            improvements = DatabaseImprovementRepository(session)
            improvement = await improvements.get(ImprovementReference("IMP00001"))

        assert not improvement

    async def test_get_when_not_found(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session:
            improvements = DatabaseImprovementRepository(session)
            improvement = await improvements.get(ImprovementReference("IMP00001"))

        assert not improvement
