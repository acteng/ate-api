import pytest
from fastapi import FastAPI

from ate_api.routes.links import path_parameter_for


@pytest.fixture(name="app")
def app_fixture() -> FastAPI:
    app = FastAPI()

    @app.get("/foo/{bar}")
    def foo(bar: str) -> None:
        pass

    return app


def test_path_parameter_for(app: FastAPI) -> None:
    assert path_parameter_for(app, "foo", "bar", "/foo/xyz") == "xyz"


def test_path_parameter_for_when_unknown_route(app: FastAPI) -> None:
    with pytest.raises(ValueError, match="Unknown route: baz"):
        path_parameter_for(app, "baz", "bar", "/foo/xyz")


def test_path_parameter_for_when_unmatched_path(app: FastAPI) -> None:
    with pytest.raises(ValueError, match="Unmatched path: not a link"):
        path_parameter_for(app, "foo", "bar", "not a link")


def test_path_parameter_for_when_unknown_parameter(app: FastAPI) -> None:
    with pytest.raises(ValueError, match="Unknown path parameter: baz"):
        path_parameter_for(app, "foo", "baz", "/foo/xyz")
