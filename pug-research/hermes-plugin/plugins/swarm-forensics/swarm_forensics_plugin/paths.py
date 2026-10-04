"""State locations.

State lives outside the plugin directory, under the active Hermes
profile, so plugin updates never touch the hunt database.
"""

import os
from pathlib import Path

PLUGIN_ID = "swarm-forensics"
DB_NAME = "swarm-forensics.db"
ENV_STATE_DIR = "SWARM_FORENSICS_STATE_DIR"

PACKAGE_DIR = Path(__file__).resolve().parent
SEEDS_DIR = PACKAGE_DIR / "seeds"


def hermes_home():
    """Return the active Hermes home (profile-aware when Hermes is importable)."""
    try:
        from hermes_constants import get_hermes_home
        return Path(get_hermes_home())
    except Exception:
        return Path(os.environ.get("HERMES_HOME") or Path.home() / ".hermes")


def state_dir():
    """Return the state directory and create it."""
    override = os.environ.get(ENV_STATE_DIR)
    base = Path(override) if override else hermes_home() / PLUGIN_ID
    base.mkdir(parents=True, exist_ok=True)
    return base


def db_path():
    return state_dir() / DB_NAME
