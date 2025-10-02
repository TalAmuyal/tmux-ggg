import json
import pathlib

from . import (
    app,
    configurations,
)


WORKSPACES_FILE_NAME = "workspaces.json"
PROJECTS_FILE_NAME = "projects.json"


def _get_paths_from_file(
    file_path: pathlib.Path,
) -> tuple[pathlib.Path, ...]:
    if not file_path.exists():
        return ()

    return tuple(
        pathlib.Path(p)
        for p in json.loads(file_path.read_text())
    )


def get_session_roots() -> tuple[pathlib.Path, ...]:
    config_dir = configurations.get_shared_data_directory(app.NAME)

    workspace_config_path = config_dir / WORKSPACES_FILE_NAME
    roots = [
        p
        for workspace in _get_paths_from_file(workspace_config_path)
        for p in workspace.iterdir()
        if p.is_dir()
        if p.name[0] not in ("_", ".")
        if " " not in p.name
    ]

    project_config_path = config_dir / PROJECTS_FILE_NAME
    roots.extend(_get_paths_from_file(project_config_path))

    return tuple(roots)


def add_workspace(path: pathlib.Path) -> bool:
    return _add_path(
        path=path,
        file_name=WORKSPACES_FILE_NAME,
    )


def add_project(path: pathlib.Path) -> bool:
    return _add_path(
        path=path,
        file_name=PROJECTS_FILE_NAME,
    )


def _add_path(
    *,
    path: pathlib.Path,
    file_name: str,
) -> bool:
    config_dir = configurations.get_shared_data_directory(app.NAME)
    if not config_dir.exists():
        config_dir.mkdir(parents=True, exist_ok=True)

    config_path = config_dir / file_name

    paths = _get_paths_from_file(config_path)
    if path in paths:
        return False

    paths = (*paths, path)
    new_content = json.dumps(
        [
            str(p)
            for p in paths
        ]
    )
    config_path.write_text(new_content)
    return True
