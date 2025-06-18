from ate_api.domain.authorities import Authority, AuthorityAbbreviation, AuthorityRepository


class MemoryAuthorityRepository(AuthorityRepository):
    def __init__(self) -> None:
        self._authorities: dict[AuthorityAbbreviation, Authority] = {}

    def add(self, authority: Authority) -> None:
        self._authorities[authority.abbreviation] = authority

    def get(self, abbreviation: AuthorityAbbreviation) -> Authority | None:
        return self._authorities.get(abbreviation)
