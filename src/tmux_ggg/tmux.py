import dataclasses
import pathlib
import subprocess


HOME = pathlib.Path.home()


@dataclasses.dataclass(frozen=True)
class Session:
    name: str
    path: pathlib.Path


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


def new(session: Session) -> None:
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


def attach(session: Session) -> None:
    subprocess.run(
        [
            "tmux",
            "attach-session",
            "-t",
            session.name,
        ],
        check=True,
    )
