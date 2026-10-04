"""Session identity reads that work on every host path.

Slash commands and tools run on host worker threads where Hermes binds
HERMES_SESSION_* through ContextVars (gateway/session_context.py), not
os.environ. Reading os.getenv there returns "" and the plugin loses the
calling session. Read through get_session_env when it is importable; it
falls back to os.environ itself. Tests may replace ``_host_env``.
"""

import os

try:
    from gateway.session_context import get_session_env as _host_env
except Exception:  # outside the Hermes process (unit tests, plain CLI)
    _host_env = None


def _get(name):
    if _host_env is not None:
        try:
            value = _host_env(name, "")
        except Exception:
            value = ""
        if value:
            return value
    return os.getenv(name, "") or ""


def session_id():
    """The runtime (ephemeral) session id, or ''."""
    return _get("HERMES_SESSION_ID")


def session_key():
    """The durable session key, or ''. The chat injector routes on this."""
    return _get("HERMES_SESSION_KEY")


def any_session():
    """Any session identity for lookup: runtime id first, then durable key."""
    return session_id() or session_key() or None
