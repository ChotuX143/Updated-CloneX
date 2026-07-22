from pathlib import Path
from urllib.parse import urlparse

from git import Repo
from git.exc import (
    GitCommandError,
    InvalidGitRepositoryError,
    NoSuchPathError,
)


def valid_github_url(url: str) -> bool:
    """Check whether origin is a valid GitHub URL."""
    if url.startswith("git@github.com:"):
        return True

    try:
        parsed = urlparse(url)
        return (
            parsed.scheme in {"http", "https"}
            and parsed.hostname == "github.com"
        )
    except ValueError:
        return False


def git() -> None:
    """Fetch repository updates without crashing the bot."""
    app_path = Path(file).resolve().parents[2]

    # Heroku/Docker deployment usually does not contain .git metadata.
    if not (app_path / ".git").exists():
        print("[INFO] .git directory not found. Auto-update skipped.")
        return

    try:
        repo = Repo(str(app_path))

        if "origin" not in [remote.name for remote in repo.remotes]:
            print("[WARNING] Git origin not found. Auto-update skipped.")
            return

        origin = repo.remote("origin")
        origin_url = next(iter(origin.urls), "")

        if not valid_github_url(origin_url):
            print("[WARNING] Invalid GitHub origin URL. Auto-update skipped.")
            return

        origin.fetch(prune=True)
        print("[INFO] Git updates fetched successfully.")

    except (
        InvalidGitRepositoryError,
        NoSuchPathError,
        GitCommandError,
        ValueError,
    ) as error:
        # Git failure should never stop the Telegram bot.
        print(f"[WARNING] Git auto-update skipped: {error}")
