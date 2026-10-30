"""Paths and .env loading shared by the bot, the call webhook and the eval runner."""

import os
from pathlib import Path

ROOT = Path(__file__).parent.parent
CRM_FILE = ROOT / "crm.sqlite"


def load_env(path=ROOT / ".env"):
    """Put KEY=VALUE lines from .env into os.environ; a variable already set wins."""
    for line in path.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())
