"""The `/swarm-forensics` slash command.

A text face of the same service the desktop app uses. Every verb here has
a button in the app. The command never changes the rules: it can start and
stop hunts and make the same IOC decisions an operator can.
"""

import json
import os
import shlex

from .entities import EntityError
from .hunt import HuntRefused
from .iocs import IocError
from .schedule import ScheduleError
from .settings import SCHEMA, SettingsError

HELP = """\
/swarm-forensics start [goal]            start a guided hunt in this session
/swarm-forensics attach [id]             attach this chat session to a running hunt
/swarm-forensics session [goal]          start an interactive hunt in this session
/swarm-forensics subhunt [parent] [goal] spawn a child crawler hunt
/swarm-forensics tools [id] [n]          show recent tool calls and rationale
/swarm-forensics stop [id]               stop the hunt (and any sub-hunts)
/swarm-forensics pause [id]              pause at the next checkpoint
/swarm-forensics resume [id]             restart a paused or blocked hunt
/swarm-forensics status                  hunt state and totals
/swarm-forensics log [n]                 last n activity lines (default 15)
/swarm-forensics review                  list proposed IOC terms
/swarm-forensics accept <id> [reason]    accept a proposed IOC
/swarm-forensics reject <id> [reason]    reject a proposed IOC
/swarm-forensics benign <id|term>        mark an indicator as benign
/swarm-forensics narrow <id> <term>      narrow an IOC term
/swarm-forensics find <text>             search artifacts, agents, swarms
/swarm-forensics settings [key [value]]  read or change a setting
/swarm-forensics reset [--force]         wipe all data and start from scratch"""


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
            session_id = os.getenv("HERMES_SESSION_ID") or os.getenv("HERMES_SESSION_KEY") or None
            session_key = os.getenv("HERMES_SESSION_KEY") or ""
            origin = "session" if session_id else "command"
            hunt = svc.hunts.start(origin, goal_text, session_id=session_id)
            if session_id:
                svc.ledger.bind_session(hunt["id"], session_id, session_key)
            max_depth = svc.settings.get("hunt.max_depth")
            if session_id:
                return (
                    "Hunt %s started (session-native, depth %d).\n"
                    "Bound Hermes Session: %s\n"
                    "Goal: %s\n\n"
                    "Agent should now investigate using native tools:\n"
                    "- Direct the hunt or execute /goal %s\n"
                    "- Call sf_get_context to view active indicators, leads, and context.\n"
                    "- Call sf_search_index to query web archive indexes.\n"
                    "- Call sf_record_evidence to record excerpts and claim levels.\n"
                    "- Call sf_mirror_url to capture and safely mirror untrusted text.\n"
                    "- Call sf_analyze_corpus to run deterministic TTP analysis.\n"
                    "- Call sf_spawn_subhunt to spawn child crawlers (up to depth %d).\n"
                    "- Stop with /swarm-forensics stop %s"
                    % (
                        hunt["id"], hunt.get("depth", 0), session_id, hunt["goal"],
                        hunt["goal"], max_depth, hunt["id"],
                    )
                )
            return (
                "Hunt %s started in background mode (depth %d).\n"
                "Goal: %s\n\n"
                "To interact with this hunt in chat, run:\n"
                "- /swarm-forensics attach %s\n"
                "- Watch progress with /swarm-forensics log %s\n"
                "- Stop with /swarm-forensics stop %s"
                % (
                    hunt["id"], hunt.get("depth", 0), hunt["goal"],
                    hunt["id"], hunt["id"], hunt["id"],
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
            calling_sid = os.getenv("HERMES_SESSION_ID") or os.getenv("HERMES_SESSION_KEY") or None
            calling_skey = os.getenv("HERMES_SESSION_KEY") or ""
            if calling_sid:
                svc.ledger.bind_session(hunt["id"], calling_sid, calling_skey)
                bound_label = calling_sid
            else:
                bound_label = hunt.get("session_id") or "unbound"
            children = svc.ledger.child_hunts(hunt["id"])
            leads = svc.ledger.open_leads("query", 3)
            lead_summary = ", ".join(ld["value"] for ld in leads) or "none"
            events = svc.ledger.events(hunt["id"], 0, 8)
            tool_evs = [
                e for e in events
                if e["kind"] in ("tool_call", "search", "sweep", "page")
            ]
            rat_evs = [
                e for e in events
                if e["kind"] in ("rationale", "finding", "plan", "state")
            ]
            tool_summary = (
                "\n".join("- [%s] %s" % (e["kind"], e["message"]) for e in tool_evs[:4])
                or "- no tool calls yet"
            )
            rat_summary = (
                "\n".join("- [%s] %s" % (e["kind"], e["message"]) for e in rat_evs[:4])
                or "- no analysis rationale yet"
            )
            return (
                "Attached to Hunt %s (Session %s)\n"
                "State: %s | Depth: %d | Cycle: %d | Parent: %s\n"
                "Goal: %s\n"
                "Child sub-hunts: %d | Open leads: %s\n\n"
                "Tool calls & queries:\n%s\n\n"
                "Analysis rationale & findings:\n%s\n\n"
                "You can now guide this hunt session using Swarm Forensics tools (sf_*)."
                % (
                    hunt["id"], bound_label, hunt["state"],
                    hunt.get("depth", 0), hunt["cycle"],
                    hunt.get("parent_hunt_id") or "none (root)",
                    hunt["goal"], len(children), lead_summary,
                    tool_summary, rat_summary,
                )
            )
        if verb in ("subhunt", "spawn"):
            active = svc.ledger.active_hunt()
            if not args and not active:
                return "No active hunt found. Usage: /swarm-forensics subhunt [parent_id] [goal]"
            if args and len(args[0]) >= 8 and (svc.ledger.hunt(args[0]) or "-" in args[0]):
                parent_id = args[0]
                goal = " ".join(args[1:]).strip() if len(args) > 1 else None
            else:
                if not active:
                    return "No active hunt found. Provide a parent hunt ID."
                parent_id = active["id"]
                goal = " ".join(args).strip() if args else None
            child = svc.hunts.spawn_subhunt(parent_id, goal=goal)
            return "Spawned child hunt %s at depth %d under %s (Goal: %s)" % (
                child["id"], child["depth"], child["parent_hunt_id"], child["goal"],
            )
        if verb in ("tools", "tool_calls", "rationale"):
            target_id = args[0].strip() if args and not args[0].isdigit() else None
            hunt = (svc.ledger.hunt(target_id) if target_id else None) or svc.ledger.active_hunt()
            hid = hunt["id"] if hunt else None
            n = int(args[-1]) if args and args[-1].isdigit() else 10
            events = svc.ledger.events(hid, 0, n * 2)
            matched = [
                e for e in events
                if e["kind"] in ("tool_call", "search", "sweep", "page", "rationale", "finding")
            ][:n]
            if not matched:
                return "No tool calls or rationale logged yet%s." % (
                    (" for hunt " + hid) if hid else ""
                )
            lines = ["- [%s] %s" % (e["kind"], e["message"]) for e in matched]
            return "Tool calls and rationale%s:\n%s" % (
                (" (hunt " + hid + ")") if hid else "",
                "\n".join(lines),
            )
        if verb == "reset":
            if "--force" not in args and "confirm" not in args:
                return (
                    "Refused. Reset will wipe all data and start from scratch.\n"
                    "Run: /swarm-forensics reset --force"
                )
            svc.reset_all_data()
            return "All Swarm Forensics data has been wiped. Started fresh from scratch."
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
