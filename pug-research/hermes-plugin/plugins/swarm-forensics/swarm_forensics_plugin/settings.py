"""Typed, versioned settings stored in the database.

One schema drives validation, defaults, and the settings form in the
desktop app. Unknown keys and invalid values are refused, never coerced
silently.
"""

from . import db

SCHEMA_VERSION = 2
CLAIM_LEVELS = ["L1", "L2", "L3", "L4", "L5"]
SOURCES = ["web", "index"]


def _f(group, kind, default, label, help_text="", **extra):
    field = {"group": group, "kind": kind, "default": default,
             "label": label, "help": help_text}
    field.update(extra)
    return field


SCHEMA = {
    "hunt.default_goal": _f(
        "Hunt", "text",
        "Find public traces left by autonomous agent swarms, using known "
        "indicators and new ones mined from what the crawls return.",
        "Default hunt goal", "Used when a hunt starts without a goal."),
    "hunt.sources": _f(
        "Hunt", "multi", ["web", "index"],
        "Sources", "web uses Hermes tools; index uses enabled index sources.",
        choices=SOURCES),
    "hunt.use_model": _f(
        "Hunt", "bool", True, "Use the Hermes model",
        "Off runs a deterministic sweep of active IOCs with no model."),
    "hunt.fetch_pages": _f(
        "Hunt", "bool", True, "Read result pages",
        "Read search-result pages through the Hermes extract tool."),
    "hunt.cycle_pause_seconds": _f(
        "Hunt", "int", 30, "Pause between cycles (s)", min=5, max=86400),
    "hunt.max_queries_per_cycle": _f(
        "Hunt", "int", 6, "Queries per cycle", min=1, max=50),
    "hunt.max_pages_per_cycle": _f(
        "Hunt", "int", 6, "Pages read per cycle", min=0, max=50),
    "hunt.max_results_per_query": _f(
        "Hunt", "int", 50, "Results per query", min=1, max=500),
    "hunt.max_cycles": _f(
        "Hunt", "int", 0, "Cycle limit",
        "0 runs until the operator stops the hunt.", min=0, max=1000000),
    "hunt.request_delay_seconds": _f(
        "Hunt", "float", 2.0, "Delay between requests (s)", min=0.5, max=600),
    "hunt.require_desktop": _f(
        "Hunt", "bool", True, "Stop when the app closes",
        "A desktop hunt pauses when the app stops sending heartbeats."),
    "hunt.heartbeat_timeout_seconds": _f(
        "Hunt", "int", 90, "Heartbeat timeout (s)", min=15, max=3600),
    "model.provider": _f(
        "Model", "text", "", "Provider override",
        "Empty uses the active Hermes model. Overrides need Hermes trust flags."),
    "model.name": _f("Model", "text", "", "Model override"),
    "model.max_tokens": _f("Model", "int", 2000, "Max output tokens",
                           min=256, max=16000),
    "model.timeout_seconds": _f("Model", "int", 120, "Model timeout (s)",
                                min=10, max=1800),
    "iocs.promotion": _f(
        "IOC policy", "choice", "manual", "Promotion mode",
        "manual: an operator accepts every term. automatic: evidence rules "
        "promote terms. The model never promotes on its own.",
        choices=["manual", "automatic"]),
    "iocs.auto_min_evidence": _f(
        "IOC policy", "int", 3, "Automatic: minimum evidence items",
        min=1, max=100),
    "iocs.auto_min_sources": _f(
        "IOC policy", "int", 2, "Automatic: minimum distinct hosts",
        min=1, max=50),
    "iocs.auto_min_claim_level": _f(
        "IOC policy", "choice", "L2", "Automatic: minimum claim level",
        choices=CLAIM_LEVELS),
    "iocs.auto_max_per_day": _f(
        "IOC policy", "int", 10, "Automatic: promotions per day",
        min=0, max=1000),
    "safety.paused": _f(
        "Safety", "bool", False, "Pause all hunting",
        "Blocks every start, including schedules."),
    "safety.private_mode": _f(
        "Safety", "bool", True, "Mask watch terms in the app",
        "Terms show as bullets until clicked."),
    "safety.exclusion_terms": _f(
        "Safety", "list", [], "Excluded terms",
        "Terms never proposed as IOCs."),
    "safety.alert_on_claim_level": _f(
        "Safety", "choice", "L3", "Alert at claim level",
        choices=CLAIM_LEVELS),
    "graph.auto_entities": _f(
        "Graph", "bool", True,
        "Write artifacts, agents, swarms, and campaigns to the graph",
        "Off keeps the graph human-edited only."),
    "schedule.enabled": _f(
        "Schedule", "bool", False, "Allow scheduled hunts",
        "Master switch. Each schedule also needs operator arming. "
        "Schedules only fire while the desktop app is open."),
}


class SettingsError(ValueError):
    def __init__(self, errors):
        super().__init__("; ".join("%s: %s" % kv for kv in errors.items()))
        self.errors = errors


def _coerce(key, field, value):
    kind = field["kind"]
    if kind == "bool":
        if isinstance(value, bool):
            return value
        raise ValueError("must be true or false")
    if kind in ("int", "float"):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("must be a number")
        out = int(value) if kind == "int" else float(value)
        if kind == "int" and out != value:
            raise ValueError("must be a whole number")
        if "min" in field and out < field["min"]:
            raise ValueError("must be at least %s" % field["min"])
        if "max" in field and out > field["max"]:
            raise ValueError("must be at most %s" % field["max"])
        return out
    if kind == "text":
        if not isinstance(value, str):
            raise ValueError("must be text")
        return value.strip()[:2000]
    if kind == "choice":
        if value not in field["choices"]:
            raise ValueError("must be one of %s" % ", ".join(field["choices"]))
        return value
    if kind == "multi":
        if not isinstance(value, list) or not value:
            raise ValueError("must be a non-empty list")
        if key == "hunt.sources":
            remapped = []
            for v in value:
                if v in ("urlquery", "cdx", "arquivo", "index"):
                    if "index" not in remapped:
                        remapped.append("index")
                elif v in field["choices"] and v not in remapped:
                    remapped.append(v)
            value = remapped
            if not value:
                raise ValueError("must be a non-empty list")
        bad = [v for v in value if v not in field["choices"]]
        if bad:
            raise ValueError("unknown: %s" % ", ".join(map(str, bad)))
        return [c for c in field["choices"] if c in value]
    if kind == "list":
        if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
            raise ValueError("must be a list of text")
        return sorted({v.strip() for v in value if v.strip()})
    raise ValueError("unsupported kind")


def validate(updates):
    """Return cleaned updates, or raise SettingsError with every problem."""
    clean, errors = {}, {}
    for key, value in (updates or {}).items():
        field = SCHEMA.get(key)
        if field is None:
            errors[key] = "unknown setting"
            continue
        try:
            clean[key] = _coerce(key, field, value)
        except ValueError as exc:
            errors[key] = str(exc)
    if errors:
        raise SettingsError(errors)
    return clean


class Settings:
    def __init__(self, database):
        self.db = database

    def all(self):
        values = {k: f["default"] for k, f in SCHEMA.items()}
        with self.db.connect() as conn:
            for row in conn.execute("SELECT key, value FROM settings"):
                if row["key"] in SCHEMA:
                    stored = db.loads(row["value"], None)
                    try:
                        values[row["key"]] = _coerce(
                            row["key"], SCHEMA[row["key"]], stored)
                    except ValueError:
                        pass  # A bad stored value falls back to the default.
        return values

    def get(self, key):
        return self.all()[key]

    def update(self, updates):
        clean = validate(updates)
        stamp = db.now()
        with self.db.connect() as conn:
            for key, value in clean.items():
                conn.execute(
                    "INSERT INTO settings(key, value, updated_utc) VALUES (?,?,?)"
                    " ON CONFLICT(key) DO UPDATE SET value = excluded.value,"
                    " updated_utc = excluded.updated_utc",
                    (key, db.dumps(value), stamp))
        return self.all()

    @staticmethod
    def schema():
        return {"version": SCHEMA_VERSION, "fields": SCHEMA}
