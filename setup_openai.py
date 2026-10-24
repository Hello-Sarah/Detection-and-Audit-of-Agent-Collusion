"""Securely write local OpenAI API settings to the git-ignored .env file."""
from __future__ import annotations

import os
import shlex
import tempfile
from getpass import getpass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ENV_FILE = ROOT / ".env"
DEFAULT_MODEL = "gpt-5-mini"
DEFAULT_BASE_URL = "https://api.openai.com/v1"


def main() -> None:
    print("OpenAI API setup. The key is entered without echo and is not printed or sent anywhere by this setup script.")
    if ENV_FILE.exists():
        replace = input("An existing .env file is present. Replace its OpenAI settings? [y/N] ").strip().lower()
        if replace not in {"y", "yes"}:
            print("Kept the existing .env file unchanged.")
            return

    api_key = getpass("Paste your OpenAI API key (input stays hidden): ").strip()
    if not api_key:
        raise SystemExit("No key entered; nothing was saved.")
    model = input(f"Model ID [{DEFAULT_MODEL}]: ").strip() or DEFAULT_MODEL
    base_url = input(f"API base URL [{DEFAULT_BASE_URL}]: ").strip() or DEFAULT_BASE_URL
    if not base_url.startswith(("https://", "http://")):
        raise SystemExit("API base URL must start with https:// or http://; nothing was saved.")

    contents = "\n".join((
        f"OPENAI_API_KEY={shlex.quote(api_key)}",
        f"OPENAI_MODEL={shlex.quote(model)}",
        f"OPENAI_BASE_URL={shlex.quote(base_url.rstrip('/'))}",
        "",
    ))
    fd, temp_name = tempfile.mkstemp(prefix=".env.", dir=ROOT, text=True)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(contents)
        os.replace(temp_name, ENV_FILE)
        os.chmod(ENV_FILE, 0o600)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise
    print(f"Saved OpenAI settings to {ENV_FILE.name} with owner-only permissions. The key was not displayed.")
    print("Run: python harness.py --mode live --condition A --runs 1")


if __name__ == "__main__":
    main()
