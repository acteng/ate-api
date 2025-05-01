from starlette.datastructures import URL
from starlette.requests import Request
from starlette.routing import Route, compile_path


def path_parameter_for(request: Request, name: str, parameter: str, url: str) -> str:
    route = next((route for route in request.app.routes if isinstance(route, Route) and route.name == name), None)

    if not route:
        raise ValueError(f"Unknown route: {name}")

    url_obj = URL(url)

    base_url = url_obj.replace(path="/")
    if base_url != request.base_url:
        raise ValueError(f"Unmatched base URL: {base_url}")

    path = url_obj.path
    path_regex, _, _ = compile_path(route.path)
    match = path_regex.match(path)

    if not match:
        raise ValueError(f"Unmatched path: {path}")

    if parameter not in match.groupdict():
        raise ValueError(f"Unknown path parameter: {parameter}")

    return match.group(parameter)
