from datetime import datetime, timezone

from sqlalchemy import Engine, func, select
from sqlalchemy.orm import Session

from ate_api.domain.capital_schemes import CapitalScheme
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
    pass


class TestCapitalSchemeOverviewEntity:
    def test_from_domain(self) -> None:
        capital_scheme = CapitalScheme(
            reference="ATE00001",
            effective_date=DateTimeRange(datetime(2020, 1, 1), datetime(2020, 2, 1)),
            bid_submitting_authority="LIV",
        )

        overview_entity = CapitalSchemeOverviewEntity.from_domain(capital_scheme, {"LIV": 1})

        assert (
            overview_entity.bid_submitting_authority_id == 1
            and overview_entity.effective_date_from == datetime(2020, 1, 1)
            and overview_entity.effective_date_to == datetime(2020, 2, 1)
        )

    def test_from_domain_when_current(self) -> None:
        capital_scheme = CapitalScheme(
            reference="ATE00001", effective_date=DateTimeRange(datetime(2020, 1, 1)), bid_submitting_authority="LIV"
        )

        overview_entity = CapitalSchemeOverviewEntity.from_domain(capital_scheme, {"LIV": 1})

        assert overview_entity.effective_date_to is None

    def test_from_domain_converts_dates_to_local_europe_london(self) -> None:
        capital_scheme = CapitalScheme(
            reference="ATE00001",
            effective_date=DateTimeRange(
                datetime(2020, 6, 1, 12, tzinfo=timezone.utc), datetime(2020, 7, 1, 12, tzinfo=timezone.utc)
            ),
            bid_submitting_authority="LIV",
        )

        overview_entity = CapitalSchemeOverviewEntity.from_domain(capital_scheme, {"LIV": 1})

        assert overview_entity.effective_date_from == datetime(
            2020, 6, 1, 13
        ) and overview_entity.effective_date_to == datetime(2020, 7, 1, 13)

    def test_to_domain(self) -> None:
        overview_entity = CapitalSchemeOverviewEntity(
            capital_scheme=CapitalSchemeEntity(scheme_reference="ATE00001"),
            bid_submitting_authority=AuthorityEntity(authority_abbreviation="LIV"),
            effective_date_from=datetime(2020, 1, 1),
            effective_date_to=datetime(2020, 2, 1),
        )

        capital_scheme = overview_entity.to_domain()

        assert (
            capital_scheme.reference == "ATE00001"
            and capital_scheme.effective_date
            == DateTimeRange(datetime(2020, 1, 1, tzinfo=timezone.utc), datetime(2020, 2, 1, tzinfo=timezone.utc))
            and capital_scheme.bid_submitting_authority == "LIV"
        )

    def test_to_domain_when_current(self) -> None:
        overview_entity = CapitalSchemeOverviewEntity(
            capital_scheme=CapitalSchemeEntity(scheme_reference="ATE00001"),
            bid_submitting_authority=AuthorityEntity(authority_abbreviation="LIV"),
            effective_date_from=datetime(2020, 1, 1),
        )

        capital_scheme = overview_entity.to_domain()

        assert capital_scheme.effective_date.to is None

    def test_to_domain_converts_dates_from_local_europe_london(self) -> None:
        overview_entity = CapitalSchemeOverviewEntity(
            capital_scheme=CapitalSchemeEntity(scheme_reference="ATE00001"),
            bid_submitting_authority=AuthorityEntity(authority_abbreviation="LIV"),
            effective_date_from=datetime(2020, 6, 1, 13),
            effective_date_to=datetime(2020, 7, 1, 13),
        )

        capital_scheme = overview_entity.to_domain()

        assert capital_scheme.effective_date == DateTimeRange(
            datetime(2020, 6, 1, 12, tzinfo=timezone.utc), datetime(2020, 7, 1, 12, tzinfo=timezone.utc)
        )


class TestDatabaseCapitalSchemeRepository:
    def test_add(self, engine: Engine) -> None:
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
            capital_schemes.add(
                CapitalScheme(
                    reference="ATE00001",
                    effective_date=DateTimeRange(datetime(2020, 1, 1)),
                    bid_submitting_authority="LIV",
                )
            )

        with Session(engine) as session:
            (capital_scheme_row,) = session.scalars(select(CapitalSchemeEntity))
            (overview_row,) = session.scalars(select(CapitalSchemeOverviewEntity))
        assert capital_scheme_row.scheme_reference == "ATE00001"
        assert (
            overview_row.capital_scheme_id == capital_scheme_row.capital_scheme_id
            and overview_row.bid_submitting_authority_id == 1
            and overview_row.effective_date_from == datetime(2020, 1, 1)
            and overview_row.effective_date_to is None
        )

    def test_clear(self, engine: Engine) -> None:
        with Session(engine) as session, session.begin():
            session.add_all(
                [
                    AuthorityEntity(
                        authority_id=1,
                        authority_full_name="Liverpool City Region Combined Authority",
                        authority_abbreviation="LIV",
                    ),
                    CapitalSchemeEntity(capital_scheme_id=1, scheme_reference="ATE00001"),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_id=1, bid_submitting_authority_id=1, effective_date_from=datetime(2020, 1, 1)
                    ),
                ]
            )

        with Session(engine) as session, session.begin():
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_schemes.clear()

        with Session(engine) as session:
            assert session.execute(select(func.count()).select_from(CapitalSchemeEntity)).scalar_one() == 0

    def test_get(self, engine: Engine) -> None:
        with Session(engine) as session, session.begin():
            session.add_all(
                [
                    AuthorityEntity(
                        authority_id=1,
                        authority_full_name="Liverpool City Region Combined Authority",
                        authority_abbreviation="LIV",
                    ),
                    CapitalSchemeEntity(capital_scheme_id=1, scheme_reference="ATE00001"),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_id=1, bid_submitting_authority_id=1, effective_date_from=datetime(2020, 1, 1)
                    ),
                    CapitalSchemeEntity(capital_scheme_id=2, scheme_reference="ATE00002"),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_id=2, bid_submitting_authority_id=1, effective_date_from=datetime(2020, 1, 1)
                    ),
                ]
            )

        with Session(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme = capital_schemes.get("ATE00001")

        assert (
            capital_scheme
            and capital_scheme.reference == "ATE00001"
            and capital_scheme.effective_date == DateTimeRange(datetime(2020, 1, 1, tzinfo=timezone.utc))
            and capital_scheme.bid_submitting_authority == "LIV"
        )

    def test_get_uses_current_overview(self, engine: Engine) -> None:
        with Session(engine) as session, session.begin():
            session.add_all(
                [
                    AuthorityEntity(
                        authority_id=1,
                        authority_full_name="Liverpool City Region Combined Authority",
                        authority_abbreviation="LIV",
                    ),
                    CapitalSchemeEntity(capital_scheme_id=1, scheme_reference="ATE00001"),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_id=1,
                        bid_submitting_authority_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=datetime(2020, 2, 1),
                    ),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_id=1, bid_submitting_authority_id=1, effective_date_from=datetime(2020, 2, 1)
                    ),
                ]
            )

        with Session(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme = capital_schemes.get("ATE00001")

        assert (
            capital_scheme
            and capital_scheme.reference == "ATE00001"
            and capital_scheme.effective_date == DateTimeRange(datetime(2020, 2, 1, tzinfo=timezone.utc))
            and capital_scheme.bid_submitting_authority == "LIV"
        )

    def test_get_when_not_found(self, engine: Engine) -> None:
        with Session(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            capital_scheme = capital_schemes.get("ATE00001")

        assert not capital_scheme

    def test_get_references_by_bid_submitting_authority(self, engine: Engine) -> None:
        with Session(engine) as session, session.begin():
            session.add_all(
                [
                    AuthorityEntity(
                        authority_id=1,
                        authority_full_name="Liverpool City Region Combined Authority",
                        authority_abbreviation="LIV",
                    ),
                    CapitalSchemeEntity(capital_scheme_id=1, scheme_reference="ATE00001"),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_id=1, bid_submitting_authority_id=1, effective_date_from=datetime(2020, 1, 1)
                    ),
                    CapitalSchemeEntity(capital_scheme_id=2, scheme_reference="ATE00002"),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_id=2, bid_submitting_authority_id=1, effective_date_from=datetime(2020, 1, 1)
                    ),
                    AuthorityEntity(
                        authority_id=2,
                        authority_full_name="West Yorkshire Combined Authority",
                        authority_abbreviation="WYO",
                    ),
                    CapitalSchemeEntity(capital_scheme_id=3, scheme_reference="ATE00003"),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_id=3, bid_submitting_authority_id=2, effective_date_from=datetime(2020, 1, 1)
                    ),
                ]
            )

        with Session(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            references = capital_schemes.get_references_by_bid_submitting_authority("LIV")

        assert references == ["ATE00001", "ATE00002"]

    def test_get_references_by_bid_submitting_authority_uses_current_overview(self, engine: Engine) -> None:
        with Session(engine) as session, session.begin():
            session.add_all(
                [
                    AuthorityEntity(
                        authority_id=1,
                        authority_full_name="Liverpool City Region Combined Authority",
                        authority_abbreviation="LIV",
                    ),
                    AuthorityEntity(
                        authority_id=2,
                        authority_full_name="West Yorkshire Combined Authority",
                        authority_abbreviation="WYO",
                    ),
                    CapitalSchemeEntity(capital_scheme_id=1, scheme_reference="ATE00001"),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_id=1,
                        bid_submitting_authority_id=1,
                        effective_date_from=datetime(2020, 1, 1),
                        effective_date_to=datetime(2020, 2, 1),
                    ),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_id=1, bid_submitting_authority_id=2, effective_date_from=datetime(2020, 2, 1)
                    ),
                ]
            )

        with Session(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            references = capital_schemes.get_references_by_bid_submitting_authority("LIV")

        assert not references

    def test_get_references_by_bid_submitting_authority_orders_by_reference(self, engine: Engine) -> None:
        with Session(engine) as session, session.begin():
            session.add_all(
                [
                    AuthorityEntity(
                        authority_id=1,
                        authority_full_name="Liverpool City Region Combined Authority",
                        authority_abbreviation="LIV",
                    ),
                    CapitalSchemeEntity(capital_scheme_id=2, scheme_reference="ATE00002"),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_id=2, bid_submitting_authority_id=1, effective_date_from=datetime(2020, 1, 1)
                    ),
                    CapitalSchemeEntity(capital_scheme_id=1, scheme_reference="ATE00001"),
                    CapitalSchemeOverviewEntity(
                        capital_scheme_id=1, bid_submitting_authority_id=1, effective_date_from=datetime(2020, 1, 1)
                    ),
                ]
            )

        with Session(engine) as session:
            capital_schemes = DatabaseCapitalSchemeRepository(session)
            references = capital_schemes.get_references_by_bid_submitting_authority("LIV")

        assert references == ["ATE00001", "ATE00002"]
