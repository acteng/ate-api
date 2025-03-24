from sqlalchemy import Engine, func, select
from sqlalchemy.orm import Session

from ate_api.domain import Authority
from ate_api.infrastructure.database import AuthorityEntity, DatabaseAuthorityRepository


class TestAuthorityEntity:
    def test_from_domain(self) -> None:
        authority = Authority(abbreviation="LIV", full_name="Liverpool City Region Combined Authority")

        authority_entity = AuthorityEntity.from_domain(authority)

        assert (
            authority_entity.authority_full_name == "Liverpool City Region Combined Authority"
            and authority_entity.authority_abbreviation == "LIV"
        )

    def test_to_domain(self) -> None:
        authority_entity = AuthorityEntity(
            authority_full_name="Liverpool City Region Combined Authority", authority_abbreviation="LIV"
        )

        authority = authority_entity.to_domain()

        assert authority.abbreviation == "LIV" and authority.full_name == "Liverpool City Region Combined Authority"


class TestDatabaseAuthorityRepository:
    def test_add(self, engine: Engine) -> None:
        with Session(engine) as session, session.begin():
            authorities = DatabaseAuthorityRepository(session)
            authorities.add(Authority(abbreviation="LIV", full_name="Liverpool City Region Combined Authority"))

        with Session(engine) as session:
            (row,) = session.scalars(select(AuthorityEntity))
        assert (
            row.authority_full_name == "Liverpool City Region Combined Authority"
            and row.authority_abbreviation == "LIV"
        )

    def test_clear(self, engine: Engine) -> None:
        with Session(engine) as session, session.begin():
            session.add(
                AuthorityEntity(
                    authority_full_name="Liverpool City Region Combined Authority", authority_abbreviation="LIV"
                )
            )

        with Session(engine) as session, session.begin():
            authorities = DatabaseAuthorityRepository(session)
            authorities.clear()

        with Session(engine) as session:
            assert session.execute(select(func.count()).select_from(AuthorityEntity)).scalar_one() == 0

    def test_get_by_abbreviation(self, engine: Engine) -> None:
        with Session(engine) as session, session.begin():
            session.add(
                AuthorityEntity(
                    authority_full_name="Liverpool City Region Combined Authority", authority_abbreviation="LIV"
                )
            )

        with Session(engine) as session:
            authorities = DatabaseAuthorityRepository(session)
            authority = authorities.get_by_abbreviation("LIV")

        assert (
            authority
            and authority.abbreviation == "LIV"
            and authority.full_name == "Liverpool City Region Combined Authority"
        )
