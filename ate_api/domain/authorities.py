class Authority:
    def __init__(self, abbreviation: str, full_name: str):
        self._abbreviation = abbreviation
        self._full_name = full_name

    @property
    def abbreviation(self) -> str:
        return self._abbreviation

    @property
    def full_name(self) -> str:
        return self._full_name


class AuthorityRepository:
    def add(self, authority: Authority) -> None:
        raise NotImplementedError()

    def clear(self) -> None:
        raise NotImplementedError()

    def get_by_abbreviation(self, abbreviation: str) -> Authority | None:
        raise NotImplementedError()
