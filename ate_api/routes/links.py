from starlette.routing import compile_path


def get_path_parameter(path: str, path_template: str, parameter: str) -> str | None:
    path_regex, _, _ = compile_path(path_template)
    match = path_regex.match(path)

    if not match:
        return None

    if parameter not in match.groupdict():
        raise ValueError(f"Unknown path parameter: {parameter}")

    return match.group(parameter)
