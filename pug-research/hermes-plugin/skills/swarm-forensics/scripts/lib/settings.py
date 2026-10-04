"""Settings schema and validator.

config.ini is the single source of truth for GUI and CLI. set_setting
validates one key against the schema and writes it through. Unknown
keys are rejected with the list of valid keys.
"""

import configparser
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent.parent  # skills/swarm-forensics/

_ENFORCING_LOCKED_MSG = (
    "firewall_mode 'enforcing' is locked: the prompt firewall has not "
    "passed the injection-resistance evaluation (see ADVERSARIAL.md "
    "objection #5). Use 'advisory' (the judge only recommends; a human "
    "decides) or 'off'."
)


class SettingsError(Exception):
    """Raised when a setting key or value fails validation."""


# key -> (kind, extra...). Kinds: bool, int(min,max), str, contact, claim,
# list, firewall. Every key is addressed as "section.option".
# NOTE: there is no [schedule] section. Hunts are human-triggered;
# nothing is scheduled, so schedule.* keys were removed (2026-10-04).
SCHEMA = {
    "hunt.default_sources": ("str",),
    "hunt.default_cap": ("int", 0, None),
    "sources.urlquery_enabled": ("bool",),
    "sources.cdx_enabled": ("bool",),
    "sources.arquivo_enabled": ("bool",),
    "sources.request_delay_seconds": ("int", 1, None),
    "sources.max_results_per_query": ("int", 1, None),
    "sources.max_terms_per_sweep": ("int", 1, None),
    "sources.urlquery_budget": ("int", 1, None),
    "sources.cdx_budget": ("int", 1, None),
    "sources.arquivo_budget": ("int", 1, None),
    "sources.user_agent": ("contact",),
    "ioc.auto_propose": ("bool",),
    "ioc.require_review_for_promote": ("bool",),
    "research.watch_urls": ("list",),
    "research.novelty_min_chars": ("int", 1, None),
    "safety.paused": ("bool",),
    "safety.private_mode": ("bool",),
    "safety.firewall_mode": ("firewall",),
    "safety.alert_on_claim_level": ("claim",),
    "safety.exclusion_terms": ("list",),
    "chat.model_enabled": ("bool",),
    "chat.endpoint": ("str",),
    "chat.api_key_env": ("str",),
    "chat.model": ("str",),
}

_TRUE = {"true", "1", "yes", "on"}
_FALSE = {"false", "0", "no", "off"}
_CLAIM_LEVELS = ("L1", "L2", "L3", "L4", "L5")


def _parse_bool(value):
    v = str(value).strip().lower()
    if v in _TRUE:
        return "true"
    if v in _FALSE:
        return "false"
    raise SettingsError(f"not a boolean: {value!r} (use true/false)")


def _parse_int(value, lo, hi, key):
    try:
        n = int(str(value).strip())
    except ValueError:
        raise SettingsError(f"{key}: not an integer: {value!r}")
    if lo is not None and n < lo:
        raise SettingsError(f"{key}: {n} is below minimum {lo}")
    if hi is not None and n > hi:
        raise SettingsError(f"{key}: {n} is above maximum {hi}")
    return str(n)


def validate(key, value):
    """Validate one setting. Returns (section, option, stored_string)."""
    if key not in SCHEMA:
        valid = "\n  ".join(sorted(SCHEMA))
        raise SettingsError(f"unknown setting: {key!r}\nvalid keys:\n  {valid}")
    kind = SCHEMA[key][0]
    section, option = key.split(".", 1)
    if kind == "bool":
        stored = _parse_bool(value)
    elif kind == "int":
        _, lo, hi = SCHEMA[key]
        stored = _parse_int(value, lo, hi, key)
    elif kind == "contact":
        stored = str(value).strip()
        if "@" not in stored and "http" not in stored:
            raise SettingsError(
                "user_agent MUST include a contact string (an email or "
                "URL) so source operators can reach the hunter")
        if not stored:
            raise SettingsError("user_agent MUST NOT be empty")
    elif kind == "str":
        stored = str(value).strip()
    elif kind == "firewall":
        v = str(value).strip().lower()
        if v == "enforcing":
            raise SettingsError(_ENFORCING_LOCKED_MSG)
        if v not in ("off", "advisory"):
            raise SettingsError(
                f"firewall_mode MUST be off or advisory, not {value!r}. "
                + _ENFORCING_LOCKED_MSG)
        stored = v
    elif kind == "claim":
        v = str(value).strip().upper()
        if v not in _CLAIM_LEVELS:
            raise SettingsError(
                f"alert_on_claim_level MUST be one of "
                f"{', '.join(_CLAIM_LEVELS)}, not {value!r}")
        stored = v
    elif kind == "list":
        items = [l.strip() for l in str(value).splitlines() if l.strip()]
        stored = "\n" + "\n".join(items) if items else ""
    else:
        raise SettingsError(f"internal error: no validator for {key!r}")
    return section, option, stored


def _writable_path():
    # The live file is config.ini; create it from the example once.
    live = HERE / "config.ini"
    example = HERE / "config.example.ini"
    if not live.exists() and example.exists():
        live.write_text(example.read_text(encoding="utf-8"),
                        encoding="utf-8")
    return live


def set_setting(cfg, key, value):
    """Validate and persist one setting. Returns the stored string."""
    section, option, stored = validate(key, value)
    path = _writable_path()
    parser = configparser.ConfigParser()
    parser.read(path, encoding="utf-8")
    if not parser.has_section(section):
        parser.add_section(section)
    parser.set(section, option, stored)
    with path.open("w", encoding="utf-8") as f:
        parser.write(f)
    cfg.setdefault(section, {})[option] = stored
    return stored


def _typed(section, option, raw):
    kind = SCHEMA[f"{section}.{option}"][0]
    if kind == "bool":
        return raw.strip().lower() in _TRUE
    if kind == "int":
        return int(raw)
    if kind == "list":
        return [l.strip() for l in raw.splitlines() if l.strip()]
    return raw


def get_settings(cfg):
    """Return all schema settings with typed values from cfg."""
    out = {}
    for key in sorted(SCHEMA):
        section, option = key.split(".", 1)
        raw = cfg.get(section, {}).get(option, "")
        try:
            out[key] = _typed(section, option, raw)
        except (ValueError, KeyError):
            out[key] = raw
    return out
