"""Config loader. INI via stdlib configparser; no YAML dependency."""

import configparser
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent.parent  # skills/swarm-forensics/


def _defaults():
    # Defaults follow HERMES_DESKTOP.md section 3 (adversarial mitigations):
    # human-triggered hunts only (no [schedule] section exists), smaller
    # pages, longer delays, quarantine-by-default.
    return {
        "hunt": {
            "default_sources": "urlquery,cdx,arquivo",
            "default_cap": "200",
        },
        "sources": {
            "urlquery_enabled": "true",
            "cdx_enabled": "true",
            "arquivo_enabled": "true",
            "request_delay_seconds": "5",
            "max_results_per_query": "50",
            "max_terms_per_sweep": "200",
            "urlquery_budget": "60",
            "cdx_budget": "60",
            "arquivo_budget": "60",
            "user_agent": ("swarm-forensics/0.1 "
                           "(+https://github.com/christopherwoodall/swarm-forensics)"),
        },
        "ioc": {
            "auto_propose": "false",
            "require_review_for_promote": "true",
        },
        "research": {
            "watch_urls": "",
            "novelty_min_chars": "4",
        },
        "safety": {
            "paused": "false",
            "private_mode": "true",
            "firewall_mode": "advisory",
            "alert_on_claim_level": "L3",
            "exclusion_terms": "",
        },
        "chat": {
            "model_enabled": "false",
            "endpoint": "",
            "api_key_env": "SWARM_FORENSICS_CHAT_KEY",
            "model": "",
        },
        "paths": {
            "state_dir": "state",
        },
    }


def load_config(path=None, state_dir=None):
    """Load config.ini, falling back to config.example.ini, then defaults."""
    cfg = configparser.ConfigParser()
    cfg.read_dict(_defaults())
    candidates = []
    if path:
        candidates.append(Path(path))
    candidates += [HERE / "config.ini", HERE / "config.example.ini"]
    for c in candidates:
        if c.exists():
            cfg.read(c)
            break
    out = {s: dict(cfg[s]) for s in cfg.sections()}
    out["_config_source"] = str(candidates[0] if path else
                                next((c for c in candidates if c.exists()), "defaults"))
    if state_dir:
        out["paths"]["state_dir"] = state_dir
    return out


def state_path(cfg, *parts):
    base = Path(cfg["paths"]["state_dir"])
    if not base.is_absolute():
        base = HERE / base
    return base.joinpath(*parts)


def ensure_state(cfg):
    for sub in ("hits", "candidates", "jobs", "queries"):
        state_path(cfg, sub).mkdir(parents=True, exist_ok=True)
    for f in ("cursors.json", "research_seen.json", "review.json",
              "throttles.jsonl"):
        p = state_path(cfg, f)
        if not p.exists():
            p.write_text("{}\n" if f.endswith(".json") else "",
                         encoding="utf-8")
