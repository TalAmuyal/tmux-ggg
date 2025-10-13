"""
API to get Git-related information, like current branch, status, etc.
"""

import pathlib
import subprocess


def get_current_branch(
    path: pathlib.Path,
) -> str | None:
    """Get the current Git branch name."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=path,
            capture_output=True,
            text=True,
            check=True,
        )
        branch = result.stdout.strip()
        return None if branch == "HEAD" else branch
    except subprocess.CalledProcessError:
        return None


def is_repo_clean(
    path: pathlib.Path,
) -> bool | None:
    """Check if the Git repository is clean (no uncommitted changes)."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=path,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip() == ""
    except subprocess.CalledProcessError as e:
        if "not a git repository" in e.stderr.lower():
            return True
        raise
