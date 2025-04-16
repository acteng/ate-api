from ate_api.domain.authorities import Authority, AuthorityRepository


class MemoryAuthorityRepository(AuthorityRepository):
    def __init__(self) -> None:
        self._authorities = dict[str, Authority]()

    def add(self, authority: Authority) -> None:
        self._authorities[authority.abbreviation] = authority

    def clear(self) -> None:
        self._authorities.clear()

    def get(self, abbreviation: str) -> Authority | None:
        return self._authorities.get(abbreviation)
