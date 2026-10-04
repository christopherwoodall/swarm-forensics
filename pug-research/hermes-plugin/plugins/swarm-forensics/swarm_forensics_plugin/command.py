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
/swarm-forensics start [goal]    start a guided hunt in this session
/swarm-forensics attach [id]     attach this chat session to a running hunt
/swarm-forensics session [goal]  start an interactive hunt in this chat session
/swarm-forensics stop [id]       stop the hunt (and any sub-hunts)
/swarm-forensics pause [id]      pause at the next checkpoint
/swarm-forensics resume [id]     restart a paused or blocked hunt
/swarm-forensics status          hunt state and totals
/swarm-forensics log [n]         last n activity lines (default 15)
/swarm-forensics review          list proposed IOC terms
/swarm-forensics accept <id> [reason]
/swarm-forensics reject <id> [reason]
/swarm-forensics benign <id> [reason]
/swarm-forensics narrow <id> <narrower-term>
/swarm-forensics find <text>     search entities (artifacts, agents, swarms, campaigns)
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
        if verb in ("start", "hunt", "session"):
            goal_text = " ".join(args).strip()
            from . import db
            sid = "sf-session-" + db.new_id()[:8]
            hunt = svc.hunts.start("command", goal_text, session_id=sid)
            max_depth = svc.settings.get("hunt.max_depth")
            return (
                "Hunt %s started (depth %d). Session %s active.\n"
                "Goal: %s\n\n"
                "You can guide this hunter in chat like a normal Hermes agent:\n"
                "- Direct investigation focus, provide leads, or ask for updates.\n"
                "- Call sf_get_context to view findings, leads, and active indicators.\n"
                "- Call sf_search_index to query archives, crt.sh, and research indexes.\n"
                "- Call sf_record_evidence to record evidence excerpts and claim levels.\n"
                "- Call sf_spawn_subhunt to spawn child crawler hunts (up to depth %d).\n"
                "- Re-attach in any session: /swarm-forensics attach %s\n"
                "- Watch progress with /swarm-forensics log %s\n"
                "- Stop with /swarm-forensics stop %s"
                % (
                    hunt["id"], hunt.get("depth", 0), sid, hunt["goal"],
                    max_depth, hunt["id"], hunt["id"], hunt["id"],
                )
            )
        if verb == "attach":
            target_id = args[0].strip() if args else None
            hunt = None
            if target_id:
                hunt = svc.ledger.hunt(target_id) or svc.ledger.hunt_by_session(target_id)
            else:
                hunt = svc.ledger.active_hunt() or next(iter(svc.ledger.hunts(1)), None)
            if not hunt:
                return "Hunt not found%s." % ((" for '%s'" % target_id) if target_id else "")
            children = svc.ledger.child_hunts(hunt["id"])
            leads = svc.ledger.open_leads("query", 3)
            lead_summary = ", ".join(ld["value"] for ld in leads) or "none"
            events = svc.ledger.events(hunt["id"], 0, 4)
            event_lines = ["- [%s] %s" % (e["kind"], e["message"]) for e in events]
            event_summary = "\n".join(event_lines) or "- no events yet"
            return (
                "Attached to Hunt %s (Session %s)\n"
                "State: %s | Depth: %d | Cycle: %d | Parent: %s\n"
                "Goal: %s\n"
                "Child sub-hunts: %d\n"
                "Open leads: %s\n\n"
                "Recent activity:\n%s\n\n"
                "You can now guide this hunt session using Swarm Forensics tools (sf_*)."
                % (hunt["id"], hunt.get("session_id") or "unbound", hunt["state"],
                   hunt.get("depth", 0), hunt["cycle"], hunt.get("parent_hunt_id") or "none (root)",
                   hunt["goal"], len(children), lead_summary, event_summary)
            )
        if verb == "stop":
            target = args[0] if args else None
            hunt = svc.hunts.stop(target)
            if not hunt:
                return "No active hunt to stop."
            return "Hunt %s: stop requested (%s)." % (hunt["id"], hunt["state"])
        if verb == "pause":
            target = args[0] if args else None
            hunt = svc.hunts.pause(target)
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
        if verb == "session":
            goal = " ".join(args) or "investigate agent traces"
            leads = svc.ledger.open_leads("query", 5)
            lead_summary = ", ".join(lead["value"] for lead in leads) or "none yet"
            return (
                "Interactive Hunt Session Initiated.\n"
                "Goal: %s\n"
                "Open leads: %s\n\n"
                "You can command the hunt directly using Swarm Forensics tools:\n"
                "- Call sf_get_context to inspect indicators and sources.\n"
                "- Call sf_search_index to sweep web archive indexes.\n"
                "- Call sf_record_evidence to save findings.\n"
                "- Call sf_propose_ioc to suggest new indicator terms.\n"
                "- Call sf_manage_entity to create and tag swarms, agents, or artifacts.\n"
                "- Call sf_triage_item to mark items as benign or active." % (goal, lead_summary)
            )
        if verb in ("accept", "reject", "narrow", "benign"):
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
