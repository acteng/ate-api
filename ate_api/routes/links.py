from starlette.applications import Starlette
from starlette.routing import Route, compile_path


def path_parameter_for(app: Starlette, name: str, parameter: str, path: str) -> str:
    route = next((route for route in app.routes if isinstance(route, Route) and route.name == name), None)

    if not route:
        raise ValueError(f"Unknown route: {name}")

    path_regex, _, _ = compile_path(route.path)
    match = path_regex.match(path)

    if not match:
        raise ValueError(f"Unmatched path: {path}")

    if parameter not in match.groupdict():
        raise ValueError(f"Unknown path parameter: {parameter}")

    return match.group(parameter)
