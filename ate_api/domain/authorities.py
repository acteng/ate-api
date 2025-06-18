from typing import Any


class AuthorityAbbreviation:
    def __init__(self, abbreviation: str):
        self._abbreviation = abbreviation

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, AuthorityAbbreviation) and self._abbreviation == other._abbreviation

    def __hash__(self) -> int:
        return hash(self._abbreviation)

    def __str__(self) -> str:
        return self._abbreviation

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({repr(self._abbreviation)})"


class Authority:
    def __init__(self, abbreviation: AuthorityAbbreviation, full_name: str):
        self._abbreviation = abbreviation
        self._full_name = full_name

    @property
    def abbreviation(self) -> AuthorityAbbreviation:
        return self._abbreviation

    @property
    def full_name(self) -> str:
        return self._full_name


class AuthorityRepository:
    def add(self, authority: Authority) -> None:
        raise NotImplementedError()

    def get(self, abbreviation: AuthorityAbbreviation) -> Authority | None:
        raise NotImplementedError()
