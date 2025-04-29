from sqlalchemy import Engine, func, select
from sqlalchemy.orm import Session

from ate_api.domain.funding_programmes import FundingProgramme
from ate_api.infrastructure.database import FundingProgrammeEntity
from ate_api.infrastructure.database.funding_programmes import (
    DatabaseFundingProgrammeRepository,
)


class TestFundingProgrammeEntity:
    def test_from_domain(self) -> None:
        funding_programme = FundingProgramme(code="ATF3")

        funding_programme_entity = FundingProgrammeEntity.from_domain(funding_programme)

        assert funding_programme_entity.funding_programme_code == "ATF3"


class TestDatabaseFundingProgrammeRepository:
    def test_add(self, engine: Engine) -> None:
        with Session(engine) as session, session.begin():
            funding_programmes = DatabaseFundingProgrammeRepository(session)
            funding_programmes.add(FundingProgramme(code="ATF3"))

        with Session(engine) as session:
            (row,) = session.scalars(select(FundingProgrammeEntity))
        assert row.funding_programme_code == "ATF3"

    def test_clear(self, engine: Engine) -> None:
        with Session(engine) as session, session.begin():
            session.add(FundingProgrammeEntity(funding_programme_code="ATF3"))

        with Session(engine) as session, session.begin():
            funding_programmes = DatabaseFundingProgrammeRepository(session)
            funding_programmes.clear()

        with Session(engine) as session:
            assert session.execute(select(func.count()).select_from(FundingProgrammeEntity)).scalar_one() == 0
