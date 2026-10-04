"""The `/swarm-forensics` slash command.

A text face of the same service the desktop app uses. Every verb here has
a button in the app. The command never changes the rules: it can start and
stop hunts and make the same IOC decisions an operator can.
"""

import json
import shlex

from .entities import EntityError
from .hunt import HuntRefused
from .iocs import IocError
from .schedule import ScheduleError
from .settings import SCHEMA, SettingsError

HELP = """\
/swarm-forensics start [goal]    start a hunt (runs until you stop it)
/swarm-forensics stop            stop the hunt
/swarm-forensics pause           pause at the next checkpoint
/swarm-forensics resume [id]     restart a paused or blocked hunt
/swarm-forensics status          hunt state and totals
/swarm-forensics log [n]          last n activity lines (default 15)
/swarm-forensics review          list proposed IOC terms
/swarm-forensics accept <id> [reason]
/swarm-forensics reject <id> [reason]
/swarm-forensics narrow <id> <narrower-term>
/swarm-forensics find <text>     search entities (agents, swarms, cases)
/swarm-forensics settings [key [value]]"""


def _status(svc):
    st = svc.hunts.status()
    hunt = st["hunt"]
    if hunt is None:
        head = "No hunts yet."
    else:
        head = "Hunt %s: %s, cycle %d. %s" % (
            hunt["id"], hunt["state"], hunt["cycle"], hunt["detail"])
    t, i = st["totals"], st["iocs"]
    return ("%s\nEvidence %d, entities %d, open leads %d.\n"
            "IOCs: %d active, %d proposed, %d inactive, %d rejected." % (
                head, t["evidence"], t["entities"], t["open_leads"],
                i["active"], i["proposed"], i["inactive"], i["rejected"]))


def _log(svc, args):
    """Show recent hunt activity. A chat command cannot stream, so this is pull-based."""
    count = int(args[0]) if args and args[0].isdigit() else 15
    hunt = svc.ledger.active_hunt() or next(iter(svc.ledger.hunts(1)), None)
    rows = svc.ledger.events(hunt["id"] if hunt else None, 0, min(count, 100))
    if not rows:
        return "No activity yet."
    lines = ["%s [%s] %s" % (r["ts"][11:19], r["kind"], r["message"]) for r in rows]
    return "Hunt %s (UTC)\n%s" % (hunt["id"] if hunt else "-", "\n".join(lines))


def _parse_value(key, text):
    kind = SCHEMA[key]["kind"]
    if kind in ("list", "multi"):
        return [p.strip() for p in text.split(",") if p.strip()]
    try:
        return json.loads(text)
    except ValueError:
        return text


def _settings(svc, args):
    if not args:
        return "\n".join("%s = %s" % (k, json.dumps(v))
                         for k, v in sorted(svc.settings.all().items()))
    key = args[0]
    if key not in SCHEMA:
        return "Unknown setting: %s" % key
    if len(args) == 1:
        return "%s = %s" % (key, json.dumps(svc.settings.get(key)))
    svc.settings.update({key: _parse_value(key, " ".join(args[1:]))})
    return "%s = %s" % (key, json.dumps(svc.settings.get(key)))


def _decide(svc, verb, args):
    if not args or not args[0].isdigit():
        return "Usage: %s <ioc-id> [reason]" % verb
    ioc_id = int(args[0])
    if verb == "narrow":
        if len(args) < 2:
            return "Usage: narrow <ioc-id> <narrower-term>"
        row = svc.iocs.decide(ioc_id, "narrow", narrower=args[1])
    else:
        row = svc.iocs.decide(ioc_id, verb, " ".join(args[1:]))
    return "%s: %s" % (row["term"], row["status"])


def handle(svc, raw_args):
    """Run one command line. Always returns text, never raises to the host."""
    try:
        words = shlex.split(raw_args or "")
    except ValueError:
        return "Could not parse the command.\n" + HELP
    verb, args = (words[0].lower() if words else "help"), words[1:]
    try:
        if verb in ("start", "hunt"):
            hunt = svc.hunts.start("command", " ".join(args))
            return ("Hunt %s started. It runs in the background and does not post to this chat.\n"
                    "Follow it with /swarm-forensics log or status, or open the Swarm Forensics "
                    "page. End it with /swarm-forensics stop." % hunt["id"])
        if verb == "stop":
            hunt = svc.hunts.stop()
            return "Hunt %s: stop requested (%s)." % (hunt["id"], hunt["state"])
        if verb == "pause":
            hunt = svc.hunts.pause()
            return "Hunt %s: pause requested." % hunt["id"]
        if verb == "resume":
            hunt = svc.hunts.resume(args[0] if args else _last_paused(svc))
            return "Hunt %s resumed." % hunt["id"]
        if verb == "status":
            return _status(svc)
        if verb == "log":
            return _log(svc, args)
        if verb == "review":
            rows = svc.iocs.list("proposed", limit=25)
            return "\n".join("%d  %s  [%s]" % (r["id"], r["term"], r["category"])
                             for r in rows) or "No proposed terms."
        if verb in ("accept", "reject", "narrow"):
            return _decide(svc, verb, args)
        if verb == "find":
            rows = svc.graph.list(query=" ".join(args), limit=20)
            return "\n".join("%s  %s  %s" % (r["type"], r["name"], r["id"])
                             for r in rows) or "No match."
        if verb == "settings":
            return _settings(svc, args)
    except (HuntRefused, IocError, EntityError, ScheduleError,
            SettingsError) as exc:
        return "Refused: %s" % exc
    return HELP


def _last_paused(svc):
    for hunt in svc.ledger.hunts(10):
        if hunt["state"] in ("paused", "blocked"):
            return hunt["id"]
    raise HuntRefused("no paused hunt to resume")
