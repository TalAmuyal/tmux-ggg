import pathlib

import typer

from . import (
    configured_paths,
    session_chooser,
    tmux,
)
from .app import NAME


app = typer.Typer()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
) -> None:
    if ctx.invoked_subcommand == add.__name__:
        return

    roots = configured_paths.get_session_roots()

    missing_roots = [
        root
        for root in roots
        if not root.exists()
    ]
    if missing_roots:
        typer.echo("The following roots could not be found, aborting:")
        for root in missing_roots:
            typer.echo(f"- {root}")
        raise typer.Abort()

    if not roots:
        typer.echo(f"No roots are defined, please use `{NAME} {add.__name__} ...`")
        raise typer.Abort()

    active_sessions, _ = tmux.get_active_sessions()
    choices = [
        session
        for session in get_potential_sessions(roots)
        if session.name not in active_sessions
    ]

    if not choices:
        typer.echo("No available sessions")
        return

    chosen_session = session_chooser.choose(choices)
    if chosen_session is None:
        typer.echo("No session chosen")
        return

    tmux.new(chosen_session)
    tmux.attach(chosen_session)


def get_potential_sessions(
    roots: tuple[pathlib.Path, ...],
) -> list[tmux.Session]:
    return [
        tmux.Session(
            name=folder_name_to_session_name(p.name),
            path=p,
        )
        for p in roots
    ]


def folder_name_to_session_name(folder_name: str) -> str:
    name_parts = folder_name.split("_")
    if len(name_parts) == 1 and "-" in folder_name:
        return folder_name
    return " ".join(part.capitalize() for part in name_parts)


def make_dir_path_option(long: str) -> typer.Option:
    return typer.Option(
        None,
        f"--{long}",
        f"-{long[0]}",
        help=f"{long.title()} directory",
        exists=True,
        file_okay=False,
        dir_okay=True,
    )


@app.command()
def add(
    workspace: pathlib.Path | None = make_dir_path_option("workspace"),
    project: pathlib.Path | None = make_dir_path_option("project"),
    exist_ok: bool = False,
) -> None:
    if workspace is None and project is None:
        raise typer.BadParameter("Specify either --workspace or --project")
    if workspace and project:
        raise typer.BadParameter("Specify either --workspace or --project, not both")
    elif workspace:
        if not configured_paths.add_workspace(workspace):
            typer.echo("Workspace already registered")
            if exist_ok:
                pass
            else:
                raise typer.Abort()
    elif project:
        configured_paths.add_project(project)
    else:
        raise RuntimeError("Unreachable")
