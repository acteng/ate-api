import pytest

from ate_api.routes.links import get_path_parameter


def test_get_path_parameter() -> None:
    assert get_path_parameter("/foo/xyz", "/foo/{bar}", "bar") == "xyz"


def test_get_path_parameter_when_not_matched() -> None:
    assert get_path_parameter("not a link", "/foo/{bar}", "bar") is None


def test_get_path_parameter_when_unknown() -> None:
    with pytest.raises(ValueError, match="Unknown path parameter: baz"):
        get_path_parameter("/foo/xyz", "/foo/{bar}", "baz")
