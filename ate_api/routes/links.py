from fastapi import Request
from fastapi.datastructures import URL
from fastapi.routing import RouteContext, iter_route_contexts
from starlette.routing import compile_path


def path_parameter_for(request: Request, name: str, parameter: str, url: str) -> str:
    route_context = next(
        (
            route_context
            for route_context in iter_route_contexts(request.app.routes)
            if isinstance(route_context, RouteContext) and route_context.name == name
        ),
        None,
    )

    if not route_context:
        raise ValueError(f"Unknown route: {name}")

    url_obj = URL(url)

    base_url = url_obj.replace(path="/")
    if base_url != request.base_url:
        raise ValueError(f"Unmatched base URL: {base_url}")

    path = url_obj.path
    if not route_context.path:
        raise ValueError(f"Route {name} has no valid path")

    path_regex, _, _ = compile_path(route_context.path)
    match = path_regex.match(path)

    if not match:
        raise ValueError(f"Unmatched path: {path}")

    if parameter not in match.groupdict():
        raise ValueError(f"Unknown path parameter: {parameter}")

    return match.group(parameter)
