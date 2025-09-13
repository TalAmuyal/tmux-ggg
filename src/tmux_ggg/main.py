import dataclasses
import json
import pathlib
import platform
import subprocess
import sys

import typer


APP_NAME = sys.argv[0].split("/")[-1]
SESSION_ROOTS_FILE_NAME = "config.json"
HOME = pathlib.Path.home()


@dataclasses.dataclass(frozen=True)
class Session:
    name: str
    path: pathlib.Path


app = typer.Typer()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
) -> None:
    if ctx.invoked_subcommand == add.__name__:
        return

    roots = get_session_roots()

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
        typer.echo(f"No roots are defined, please run `{APP_NAME} {add.__name__} path/to/projects/dir`")
        raise typer.Abort()

    active_sessions, _ = get_active_sessions()
    choices = [
        session
        for session in get_potential_sessions(roots)
        if session.name not in active_sessions
    ]

    if not choices:
        typer.echo("No available sessions")
        return

    chosen_session = choose(choices)
    if chosen_session is None:
        typer.echo("No session chosen")
        return

    tmux_new(chosen_session)
    tmux_attach(chosen_session)


def get_session_roots() -> tuple[pathlib.Path, ...]:
    p = get_shared_data_directory(APP_NAME) / SESSION_ROOTS_FILE_NAME
    if not p.exists():
        return ()

    return tuple(
        pathlib.Path(root)
        for root in json.loads(p.read_text())
    )


def get_shared_data_directory(app_name: str) -> pathlib.Path:
    if platform.system() == "Windows":
        data_dir = HOME / "AppData" / "Local" / app_name
    elif platform.system() == "Darwin":
        data_dir = HOME / "Library" / "Application Support" / app_name
    else:  # Linux and other Unix-like systems
        data_dir = HOME / ".local" / "share" / app_name

    return data_dir


def get_active_sessions() -> tuple[list[str], str | None]:
    proc = subprocess.run(
        ["tmux", "list-sessions"],
        capture_output=True,
    )
    if proc.returncode != 0:
        return [], None

    lines = proc.stdout.decode().strip().splitlines()

    attached_index = None
    for i, line in enumerate(lines):
        if line.startswith("*") or "attached" in line:
            attached_index = i

    names = [line.strip("*").strip().split(":")[0] for line in lines]

    attached = None if attached_index is None else names[attached_index]

    return names, attached


def get_potential_sessions(
    roots: tuple[pathlib.Path, ...],
) -> list[Session]:
    return [
        Session(
            name=folder_name_to_session_name(path.name),
            path=path,
        )
        for source in roots
        for path in sorted(source.iterdir())
        if path.is_dir()
        if not path.name.startswith("_")
        if not path.name.startswith(".")
        if " " not in path.name
    ]


def folder_name_to_session_name(folder_name: str) -> str:
    folder_name = folder_name.replace("_", "-")
    name_parts = folder_name.split("-")
    return "-".join(part.capitalize() for part in name_parts)


def choose(choices: list[Session]) -> Session | None:
    for i, session in enumerate(choices, start=1):
        typer.echo(f"{i}. {session.name}")

    while True:
        try:
            raw_choice = input("\n")
            if not raw_choice:
                print("\033[F", end="")
                return None
        except (EOFError, KeyboardInterrupt):
            typer.echo()
            return None

        if 0 < (index := int(raw_choice)) <= len(choices):
            return choices[index - 1]
        else:
            typer.echo("Not in range")


def tmux_new(session: Session) -> None:
    subprocess.run(
        [
            "tmux",
            "-f",
            f"{HOME}/.config/tmux/config",
            "new-session",
            "-d",
            "-s",
            session.name,
            "-c",
            session.path,
            "active-neovim",
        ],
        check=True,
    )


def tmux_attach(session: Session) -> None:
    subprocess.run(
        [
            "tmux",
            "attach-session",
            "-t",
            session.name,
        ],
        check=True,
    )


@app.command()
def add(
    path: pathlib.Path,
    exist_ok: bool = False,
) -> None:
    if not path.exists():
        typer.echo(f"Path `{path}` does not exist")
        raise typer.Abort()

    roots_file_path = get_shared_data_directory(APP_NAME) / SESSION_ROOTS_FILE_NAME
    if not (parent_dir := roots_file_path.parent).exists():
        parent_dir.mkdir(parents=True, exist_ok=True)

    roots = get_session_roots()
    if path in roots:
        typer.echo(f"Path already in {roots_file_path}")
        if exist_ok:
            pass
        else:
            raise typer.Abort()
    else:
        roots = (*roots, path)
        new_content = json.dumps(
            [
                str(p)
                for p in roots
            ]
        )
        roots_file_path.write_text(new_content)
