import pytest
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from ate_api.domain.authorities import Authority
from ate_api.infrastructure.database.authorities import AuthorityEntity, DatabaseAuthorityRepository


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


@pytest.mark.usefixtures("data")
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

    def test_get(self, engine: Engine) -> None:
        with Session(engine) as session, session.begin():
            session.add_all(
                [
                    AuthorityEntity(
                        authority_full_name="Liverpool City Region Combined Authority", authority_abbreviation="LIV"
                    ),
                    AuthorityEntity(
                        authority_full_name="West Yorkshire Combined Authority", authority_abbreviation="WYO"
                    ),
                ]
            )

        with Session(engine) as session:
            authorities = DatabaseAuthorityRepository(session)
            authority = authorities.get("LIV")

        assert (
            authority
            and authority.abbreviation == "LIV"
            and authority.full_name == "Liverpool City Region Combined Authority"
        )

    def test_get_when_not_found(self, engine: Engine) -> None:
        with Session(engine) as session:
            authorities = DatabaseAuthorityRepository(session)
            authority = authorities.get("LIV")

        assert not authority
