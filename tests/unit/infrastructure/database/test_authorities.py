import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from ate_api.domain.authorities import Authority, AuthorityAbbreviation
from ate_api.infrastructure.database.authorities import AuthorityEntity, DatabaseAuthorityRepository


class TestAuthorityEntity:
    def test_from_domain(self) -> None:
        authority = Authority(abbreviation=AuthorityAbbreviation("LIV"), full_name="Liverpool")

        authority_entity = AuthorityEntity.from_domain(authority)

        assert authority_entity.authority_full_name == "Liverpool" and authority_entity.authority_abbreviation == "LIV"

    def test_to_domain(self) -> None:
        authority_entity = AuthorityEntity(authority_full_name="Liverpool", authority_abbreviation="LIV")

        authority = authority_entity.to_domain()

        assert authority.abbreviation == AuthorityAbbreviation("LIV") and authority.full_name == "Liverpool"


@pytest.mark.usefixtures("data")
@pytest.mark.asyncio(loop_scope="package")
class TestDatabaseAuthorityRepository:
    async def test_add(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            authorities = DatabaseAuthorityRepository(session)
            await authorities.add(Authority(abbreviation=AuthorityAbbreviation("LIV"), full_name="Liverpool"))

        async with AsyncSession(engine) as session:
            (row,) = await session.scalars(select(AuthorityEntity))
        assert row.authority_full_name == "Liverpool" and row.authority_abbreviation == "LIV"

    async def test_get(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add_all(
                [
                    AuthorityEntity(authority_full_name="Liverpool", authority_abbreviation="LIV"),
                    AuthorityEntity(authority_full_name="West Yorkshire", authority_abbreviation="WYO"),
                ]
            )

        async with AsyncSession(engine) as session:
            authorities = DatabaseAuthorityRepository(session)
            authority = await authorities.get(AuthorityAbbreviation("LIV"))

        assert (
            authority and authority.abbreviation == AuthorityAbbreviation("LIV") and authority.full_name == "Liverpool"
        )

    async def test_get_when_not_found(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session:
            authorities = DatabaseAuthorityRepository(session)
            authority = await authorities.get(AuthorityAbbreviation("LIV"))

        assert not authority

    async def test_exists(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session, session.begin():
            session.add(AuthorityEntity(authority_full_name="Liverpool", authority_abbreviation="LIV"))

        async with AsyncSession(engine) as session:
            authorities = DatabaseAuthorityRepository(session)
            exists = await authorities.exists(AuthorityAbbreviation("LIV"))

        assert exists

    async def test_exists_when_not_found(self, engine: AsyncEngine) -> None:
        async with AsyncSession(engine) as session:
            authorities = DatabaseAuthorityRepository(session)
            exists = await authorities.get(AuthorityAbbreviation("LIV"))

        assert not exists
