'''"""
Safe Git updater for VILLAIN Bot.

File location:
VILLAIN/core/git.py
"""

from future import annotations

import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Final


LOGGER: Final = logging.getLogger(name)

TRUE_VALUES: Final = {
    "1",
    "true",
    "yes",
    "on",
    "enable",
    "enabled",
}


def is_enabled(value: str | None) -> bool:
    """
    Check whether an environment variable is enabled.
    """

    return str(value or "").strip().lower() in TRUE_VALUES


def run_git_command(
    app_path: Path,
    *arguments: str,
) -> subprocess.CompletedProcess[str]:
    """
    Run a Git command inside the bot repository.
    """

    return subprocess.run(
        ["git", *arguments],
        cwd=app_path,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=120,
    )


def git() -> bool:
    """
    Safely update the bot repository.

    Heroku Config Vars:

    AUTO_UPDATE=true
    GIT_REMOTE=origin
    UPSTREAM_BRANCH=main

    If AUTO_UPDATE is disabled or missing,
    the bot will start without running Git pull.

    This function never crashes the bot.
    """

    try:
        # Important fix:
        # Correct variable is file, not file.
        #
        # /app/VILLAIN/core/git.py
        # parents[0] = /app/VILLAIN/core
        # parents[1] = /app/VILLAIN
        # parents[2] = /app

        app_path = Path(file).resolve().parents[2]

    except (NameError, IndexError, OSError) as error:
        LOGGER.warning(
            "Unable to detect application directory: %s",
            error,
        )
        return False

    # Automatic update is disabled by default.
    # This prevents startup crashes on Heroku containers.
    if not is_enabled(os.getenv("AUTO_UPDATE")):
        LOGGER.info(
            "Automatic Git update is disabled. "
            "Bot startup will continue."
        )
        return True

    # Check whether Git is installed.
    if shutil.which("git") is None:
        LOGGER.warning(
            "Git executable was not found. "
            "Skipping automatic update."
        )
        return False

    # Check whether repository contains a .git folder.
    git_folder = app_path / ".git"

    if not git_folder.is_dir():
        LOGGER.warning(
            "No .git directory found in %s. "
            "Skipping automatic update.",
            app_path,
        )
        return False

    remote = os.getenv(
        "GIT_REMOTE",
        "origin",
    ).strip() or "origin"

    configured_branch = os.getenv(
        "UPSTREAM_BRANCH",
        "",
    ).strip()

    try:
        # Confirm that this is a valid Git repository.
        repository_check = run_git_command(
            app_path,
            "rev-parse",
            "--is-inside-work-tree",
        )

        if repository_check.returncode != 0:
            LOGGER.warning(
                "Invalid Git repository: %s",
                repository_check.stderr.strip(),
            )
            return False

        # Check whether the configured remote exists.
        remote_check = run_git_command(
            app_path,
            "remote",
            "get-url",
            remote,
        )

        if remote_check.returncode != 0:
            LOGGER.warning(
                "Git remote '%s' was not found: %s",
                remote,
                remote_check.stderr.strip(),
            )
            return False

        # Use UPSTREAM_BRANCH when provided.
        if configured_branch:
            branch = configured_branch

        else:
            # Otherwise detect the current branch.
            branch_check = run_git_command(
                app_path,
                "rev-parse",
                "--abbrev-ref",
                "HEAD",
            )

            if branch_check.returncode != 0:
                LOGGER.warning(
                    "Unable to detect current Git branch: %s",
                    branch_check.stderr.strip(),
                )
                return False

            branch = branch_check.stdout.strip()

            if not branch or branch == "HEAD":
                LOGGER.warning(
                    "Repository is using detached HEAD. "
                    "Add UPSTREAM_BRANCH in Heroku Config Vars."
                )
                return False

        LOGGER.info(
            "Checking updates from %s/%s...",
            remote,
            branch,
        )

        # Fetch latest repository information.
        fetch_result = run_git_command(
            app_path,
            "fetch",
            "--prune",
            remote,
            branch,
        )

        if fetch_result.returncode != 0:
            LOGGER.warning(
                "Git fetch failed: %s",
                fetch_result.stderr.strip(),
            )
            return False

        # Pull only when fast-forward is possible.
        # This prevents accidental merge conflicts.
        pull_result = run_git_command(
            app_path,
            "pull",
            "--ff-only",
            remote,
            branch,
        )

        if pull_result.returncode != 0:
            LOGGER.warning(
                "Git pull failed: %s",
                pull_result.stderr.strip(),
            )
            return False

        output = pull_result.stdout.strip()

        if output:
            LOGGER.info(
                "Git update completed: %s",
                output,
            )
        else:
            LOGGER.info(
                "Git update completed successfully."
            )

        return True

    except subprocess.TimeoutExpired:
        LOGGER.warning(
            "Git update timed out. "
            "Bot startup will continue without updating."
        )
        return False

    except FileNotFoundError:
        LOGGER.warning(
            "Git command was not found. "
            "Bot startup will continue."
        )
        return False

    except PermissionError as error:
        LOGGER.warning(
            "Git permission error: %s",
            error,
        )
        return False

    except Exception as error:
        LOGGER.exception(
            "Unexpected Git update error: %s",
            error,
        )
        return False


all = ["git"]
