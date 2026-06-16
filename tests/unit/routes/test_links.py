import pytest
from fastapi import APIRouter, FastAPI, Request

from ate_api.routes.links import path_parameter_for


@pytest.fixture(name="app")
def app_fixture() -> FastAPI:
    app = FastAPI()

    @app.get("/foo/{bar}")
    def foo(bar: str) -> None:
        pass

    subrouter = APIRouter()

    @subrouter.get("/subrouter/foo/{bar}")
    def subrouter_foo(bar: str) -> None:
        pass

    app.include_router(subrouter)

    return app


def test_path_parameter_for(http_request: Request, base_url: str) -> None:
    assert path_parameter_for(http_request, "foo", "bar", f"{base_url}/foo/xyz") == "xyz"


def test_path_parameter_for_when_subrouter(http_request: Request, base_url: str) -> None:
    assert path_parameter_for(http_request, "subrouter_foo", "bar", f"{base_url}/subrouter/foo/xyz") == "xyz"


def test_path_parameter_for_when_unknown_route(http_request: Request, base_url: str) -> None:
    with pytest.raises(ValueError, match="Unknown route: baz"):
        path_parameter_for(http_request, "baz", "bar", f"{base_url}/foo/xyz")


@pytest.mark.parametrize(
    "unmatched_base_url",
    [
        pytest.param("http://example.org/", id="different host"),
        pytest.param("https://example.com/", id="different scheme"),
        pytest.param("http://example.com:8000/", id="different port"),
        pytest.param("/", id="relative URL"),
    ],
)
def test_path_parameter_for_when_unmatched_base_url(
    http_request: Request, base_url: str, unmatched_base_url: str
) -> None:
    with pytest.raises(ValueError, match=f"Unmatched base URL: {unmatched_base_url}"):
        path_parameter_for(http_request, "foo", "bar", f"{unmatched_base_url}foo/xyz")


def test_path_parameter_for_when_unmatched_path(http_request: Request, base_url: str) -> None:
    with pytest.raises(ValueError, match="Unmatched path: /baz"):
        path_parameter_for(http_request, "foo", "bar", f"{base_url}/baz")


def test_path_parameter_for_when_unknown_parameter(http_request: Request, base_url: str) -> None:
    with pytest.raises(ValueError, match="Unknown path parameter: baz"):
        path_parameter_for(http_request, "foo", "baz", f"{base_url}/foo/xyz")
