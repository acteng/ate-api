from datetime import datetime

from sqlalchemy import Engine, func, select
from sqlalchemy.orm import Session

from ate_api.domain.capital_schemes import CapitalScheme, CapitalSchemeOverview
from ate_api.domain.dates import DateTimeRange
from ate_api.infrastructure.database import (
    AuthorityEntity,
    CapitalSchemeEntity,
    CapitalSchemeOverviewEntity,
)
from ate_api.infrastructure.database.capital_schemes import (
    DatabaseCapitalSchemeRepository,
)


class TestCapitalSchemeEntity:
    def test_from_domain(self) -> None:
        capital_scheme = CapitalScheme(reference="ATE00001")

        capital_scheme_entity = CapitalSchemeEntity.from_domain(capital_scheme, {})

        assert capital_scheme_entity.scheme_reference == "ATE00001"

    def test_from_domain_sets_overview(self) -> None:
        capital_scheme = CapitalScheme(reference="ATE00001")
        capital_scheme.update_overview(
            CapitalSchemeOverview(effective_date=DateTimeRange(datetime(2020, 1, 1)), bid_submitting_authority="LIV")
        )

        capital_scheme_entity = CapitalSchemeEntity.from_domain(capital_scheme, {"LIV": 1})

        (overview_entity,) = capital_scheme_entity.capital_scheme_overviews
        assert (
            overview_entity.bid_submitting_authority_id == 1
            and overview_entity.effective_date_from == datetime(2020, 1, 1)
            and overview_entity.effective_date_to is None
        )

    def test_to_domain(self) -> None:
        capital_scheme_entity = CapitalSchemeEntity(scheme_reference="ATE00001")

        capital_scheme = capital_scheme_entity.to_domain()

        assert capital_scheme.reference == "ATE00001"


class TestCapitalSchemeOverviewEntity:
    def test_from_domain(self) -> None:
        overview = CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1), datetime(2020, 2, 1)), bid_submitting_authority="LIV"
        )

        overview_entity = CapitalSchemeOverviewEntity.from_domain(overview, {"LIV": 1})

        assert (
            overview_entity.bid_submitting_authority_id == 1
            and overview_entity.effective_date_from == datetime(2020, 1, 1)
            and overview_entity.effective_date_to == datetime(2020, 2, 1)
        )


class TestDatabaseCapitalSchemeRepository:
    def test_add(self, engine: Engine) -> None:
        with Session(engine) as session, session.begin():
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_schemes.add(CapitalScheme(reference="ATE00001"))

        with Session(engine) as session:
            (row,) = session.scalars(select(CapitalSchemeEntity))
        assert row.scheme_reference == "ATE00001"

    def test_add_overview(self, engine: Engine) -> None:
        with Session(engine) as session, session.begin():
            session.add(
                AuthorityEntity(
                    authority_id=1,
                    authority_full_name="Liverpool City Region Combined Authority",
                    authority_abbreviation="LIV",
                )
            )

        with Session(engine) as session, session.begin():
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme = CapitalScheme(reference="ATE00001")
            capital_scheme.update_overview(
                CapitalSchemeOverview(
                    effective_date=DateTimeRange(datetime(2020, 1, 1)), bid_submitting_authority="LIV"
                )
            )
            capital_schemes.add(capital_scheme)

        with Session(engine) as session:
            (row,) = session.scalars(select(CapitalSchemeOverviewEntity))
        assert (
            row.bid_submitting_authority_id == 1
            and row.effective_date_from == datetime(2020, 1, 1)
            and row.effective_date_to is None
        )

    def test_clear(self, engine: Engine) -> None:
        with Session(engine) as session, session.begin():
            session.add(
                AuthorityEntity(
                    authority_id=1,
                    authority_full_name="Liverpool City Region Combined Authority",
                    authority_abbreviation="LIV",
                )
            )
            session.add(CapitalSchemeEntity(capital_scheme_id=1, scheme_reference="ATE00001"))
            session.add(
                CapitalSchemeOverviewEntity(
                    capital_scheme_id=1, bid_submitting_authority_id=1, effective_date_from=datetime(2020, 1, 1)
                )
            )

        with Session(engine) as session, session.begin():
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_schemes.clear()

        with Session(engine) as session:
            assert session.execute(select(func.count()).select_from(CapitalSchemeEntity)).scalar_one() == 0

    def test_get(self, engine: Engine) -> None:
        with Session(engine) as session, session.begin():
            session.add(CapitalSchemeEntity(scheme_reference="ATE00001"))

        with Session(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme = capital_schemes.get("ATE00001")

        assert capital_scheme and capital_scheme.reference == "ATE00001"

    def test_get_when_not_found(self, engine: Engine) -> None:
        with Session(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme = capital_schemes.get("ATE00001")

        assert not capital_scheme

    def test_get_references_by_bid_submitting_authority(self, engine: Engine) -> None:
        with Session(engine) as session, session.begin():
            session.add(
                AuthorityEntity(
                    authority_id=1,
                    authority_full_name="Liverpool City Region Combined Authority",
                    authority_abbreviation="LIV",
                )
            )
            session.add(CapitalSchemeEntity(capital_scheme_id=1, scheme_reference="ATE00001"))
            session.add(
                CapitalSchemeOverviewEntity(
                    capital_scheme_id=1, bid_submitting_authority_id=1, effective_date_from=datetime(2020, 1, 1)
                )
            )
            session.add(CapitalSchemeEntity(capital_scheme_id=2, scheme_reference="ATE00002"))
            session.add(
                CapitalSchemeOverviewEntity(
                    capital_scheme_id=2, bid_submitting_authority_id=1, effective_date_from=datetime(2020, 1, 1)
                )
            )
            session.add(
                AuthorityEntity(
                    authority_id=2,
                    authority_full_name="West Yorkshire Combined Authority",
                    authority_abbreviation="WYO",
                )
            )
            session.add(CapitalSchemeEntity(capital_scheme_id=3, scheme_reference="ATE00003"))
            session.add(
                CapitalSchemeOverviewEntity(
                    capital_scheme_id=3, bid_submitting_authority_id=2, effective_date_from=datetime(2020, 1, 1)
                )
            )

        with Session(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            references = capital_schemes.get_references_by_bid_submitting_authority("LIV")

        assert references == ["ATE00001", "ATE00002"]

    def test_get_references_by_bid_submitting_authority_uses_current_overview(self, engine: Engine) -> None:
        with Session(engine) as session, session.begin():
            session.add(
                AuthorityEntity(
                    authority_id=1,
                    authority_full_name="Liverpool City Region Combined Authority",
                    authority_abbreviation="LIV",
                )
            )
            session.add(
                AuthorityEntity(
                    authority_id=2,
                    authority_full_name="West Yorkshire Combined Authority",
                    authority_abbreviation="WYO",
                )
            )
            session.add(CapitalSchemeEntity(capital_scheme_id=1, scheme_reference="ATE00001"))
            session.add(
                CapitalSchemeOverviewEntity(
                    capital_scheme_id=1,
                    bid_submitting_authority_id=1,
                    effective_date_from=datetime(2020, 1, 1),
                    effective_date_to=datetime(2020, 2, 1),
                )
            )
            session.add(
                CapitalSchemeOverviewEntity(
                    capital_scheme_id=1, bid_submitting_authority_id=2, effective_date_from=datetime(2020, 2, 1)
                )
            )

        with Session(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            references = capital_schemes.get_references_by_bid_submitting_authority("LIV")

        assert not references

    def test_get_references_by_bid_submitting_authority_orders_by_reference(self, engine: Engine) -> None:
        with Session(engine) as session, session.begin():
            session.add(
                AuthorityEntity(
                    authority_id=1,
                    authority_full_name="Liverpool City Region Combined Authority",
                    authority_abbreviation="LIV",
                )
            )
            session.add(CapitalSchemeEntity(capital_scheme_id=2, scheme_reference="ATE00002"))
            session.add(
                CapitalSchemeOverviewEntity(
                    capital_scheme_id=2, bid_submitting_authority_id=1, effective_date_from=datetime(2020, 1, 1)
                )
            )
            session.add(CapitalSchemeEntity(capital_scheme_id=1, scheme_reference="ATE00001"))
            session.add(
                CapitalSchemeOverviewEntity(
                    capital_scheme_id=1, bid_submitting_authority_id=1, effective_date_from=datetime(2020, 1, 1)
                )
            )

        with Session(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            references = capital_schemes.get_references_by_bid_submitting_authority("LIV")

        assert references == ["ATE00001", "ATE00002"]
