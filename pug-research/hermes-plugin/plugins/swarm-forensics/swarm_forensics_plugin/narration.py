"""Chat narration: post hunt digests and drive prompts into bound sessions.

The events table already records everything a hunt does. This module is the
bridge into the chat window: it polls for new events on hunts with session
bindings and posts a batched digest through ctx.inject_message, which the
host routes to the live session by its durable session_key. Session-origin
hunts have no worker, so when they go idle the narrator also posts a
continuation prompt to keep the native agent hunting.

An injected message can start a model turn when the session is idle. That
costs tokens, so digests are throttled (narrate.min_interval_seconds) and
drives stop after three posts in a row that produce no new activity.
"""

import logging
import threading
import time

from .ledger import ACTIVE_STATES

logger = logging.getLogger(__name__)

POLL_SECONDS = 5
MAX_LINES = 12
MAX_CHARS = 1200
MAX_DRY_DRIVES = 3
MAX_TARGET_FAILURES = 3
MUTE_SECONDS = 600
DIGEST_KINDS = ("search", "tool_call", "sweep", "page", "finding", "state",
                "cycle", "plan", "rationale", "error", "evidence")
RATIONALE_KINDS = ("plan", "rationale")


class Narrator:
    """Polls hunt activity and injects chat updates into bound sessions."""

    def __init__(self, service):
        self.svc = service
        self._ctx = None
        self._thread = None
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._last_post = {}       # (hunt_id, target) -> monotonic ts
        self._last_activity = {}   # hunt_id -> monotonic ts
        self._activity_mark = {}   # hunt_id -> (event id, corpus id)
        self._dry_drives = {}      # hunt_id -> consecutive dry drives
        self._target_failures = {}  # target -> consecutive failed posts
        self._target_muted = {}    # target -> monotonic ts to retry after
        self._blocked = False
        self._denied_logged = set()

    def attach(self, ctx):
        """Give the narrator the plugin context; start the poll loop once."""
        if ctx is None or not hasattr(ctx, "inject_message"):
            return
        with self._lock:
            self._ctx = ctx
            if self._thread and self._thread.is_alive():
                return
            self._stop.clear()
            self._thread = threading.Thread(
                target=self._loop, name="swarm-forensics-narrator", daemon=True)
            self._thread.start()

    def stop(self):
        self._stop.set()

    # -- loop ---------------------------------------------------------------

    def _loop(self):
        while not self._stop.wait(POLL_SECONDS):
            try:
                self.tick()
            except Exception as exc:
                logger.warning("narrator tick failed: %s", exc)

    def tick(self):
        """One pass over hunts with bindings. Safe to call directly."""
        ctx = self._ctx
        if ctx is None:
            return
        cfg = self.svc.settings.all()
        if not cfg["narrate.enabled"]:
            return
        for hunt in self.svc.ledger.hunts(10):
            bindings = [b for b in self.svc.ledger.bindings_for_hunt(hunt["id"])
                        if b.get("session_key") or b.get("session_id")]
            if not bindings:
                continue
            for binding in bindings:
                target = binding.get("session_key") or binding.get("session_id")
                self._digest(ctx, hunt, target, cfg)
            if hunt.get("origin") == "session" and hunt["state"] in ACTIVE_STATES:
                self._drive(ctx, hunt, bindings[0], cfg)

    # -- digest -------------------------------------------------------------

    def _digest(self, ctx, hunt, target, cfg):
        hid = hunt["id"]
        key = "%s:%s" % (hid, target)
        cursor = self.svc.ledger.cursor("narrate", key)
        rows = self.svc.ledger.events(hid, int(cursor or 0), 200)
        if cursor is None:
            # First sight of this pair: skip the backlog, start from now.
            self.svc.ledger.set_cursor("narrate", key, rows[-1]["id"] if rows else 0)
            return
        if not rows:
            return
        fresh = [e for e in rows if e["kind"] in DIGEST_KINDS]
        if not fresh:
            self.svc.ledger.set_cursor("narrate", key, rows[-1]["id"])
            return
        now = time.monotonic()
        if now - self._last_post.get((hid, target), 0) \
                < cfg["narrate.min_interval_seconds"]:
            return  # Throttled. The cursor stays; the next post covers it all.
        self._last_post[(hid, target)] = now  # stamp the attempt, win or lose
        if self._post(ctx, target, self._digest_text(hunt, fresh)):
            self.svc.ledger.set_cursor("narrate", key, rows[-1]["id"])
        # On a refusal the cursor holds, so the missed digest posts once
        # the operator allows injection.

    def _digest_text(self, hunt, rows):
        head = "[swarm-forensics] hunt %s: %s, cycle %d" % (
            hunt["id"][:8], hunt["state"], hunt["cycle"])
        rationale = None
        lines = []
        if len(rows) > MAX_LINES:
            lines.append("- (+%d earlier events)" % (len(rows) - MAX_LINES))
        for e in rows[-MAX_LINES:]:
            if e["kind"] in RATIONALE_KINDS:
                rationale = e["message"]
            lines.append("- [%s] %s" % (e["kind"], e["message"][:140]))
        body = [head] + lines
        if rationale:
            body.append("thinking: %s" % rationale[:200])
        body.append("(/swarm-forensics log %s 30 for more; "
                    "/swarm-forensics stop %s to stop)" % (hunt["id"], hunt["id"]))
        return "\n".join(body)[:MAX_CHARS]

    # -- drive (session-origin hunts) ----------------------------------------

    def _drive(self, ctx, hunt, binding, cfg):
        hid = hunt["id"]
        recent = self.svc.ledger.events(hid, 0, 10)
        latest_c = self.svc.ledger.corpus_observations(hunt_id=hid, limit=1)
        current = (recent[-1]["id"] if recent else 0,
                   latest_c[0]["id"] if latest_c else 0)
        now = time.monotonic()
        # A hunt that has only its start event never got a first turn: the
        # slash command answers without waking the model, so the first drive
        # must NOT wait for drive_idle_seconds. Kick off on first sight.
        fresh = (hid not in self._activity_mark
                 and not latest_c
                 and all(e["kind"] == "state" for e in recent))
        if not fresh:
            if self._activity_mark.get(hid) != current:
                self._activity_mark[hid] = current
                self._last_activity[hid] = now
                self._dry_drives[hid] = 0
                return
            if now - self._last_activity.get(hid, now) \
                    < cfg["narrate.drive_idle_seconds"]:
                return
        if self._dry_drives.get(hid, 0) >= MAX_DRY_DRIVES:
            return
        target = binding.get("session_key") or binding.get("session_id")
        leads = self.svc.ledger.open_leads("query", 3)
        lead_str = ", ".join(ld["value"] for ld in leads) or "none logged"
        header = ("is ready. Kick off the investigation:"
                  if fresh else "is idle. Continue the hunt:")
        text = (
            "[swarm-forensics] hunt %s %s\n"
            "- sf_get_context for current indicators and leads\n"
            "- run searches (sf_search_index or web_search)\n"
            "- record findings with sf_record_evidence\n"
            "Open leads: %s\n"
            "Reply with a one-line status, then keep working. "
            "/swarm-forensics stop %s ends the hunt."
            % (hid[:8], header, lead_str, hid))
        if self._post(ctx, target, text):
            self._activity_mark[hid] = current
            self._dry_drives[hid] = self._dry_drives.get(hid, 0) + 1
            self._last_activity[hid] = now

    # -- injection ------------------------------------------------------------

    def _post(self, ctx, target, text):
        """Inject one message. Mute a target that keeps failing.

        A failed target is usually a dead session (an old binding), not a
        consent problem. After MAX_TARGET_FAILURES in a row the target goes
        quiet for MUTE_SECONDS and its failures stop raising the global
        ``narration_blocked`` flag, so one stale binding cannot hide that
        live sessions are receiving updates.
        """
        muted_until = self._target_muted.get(target)
        if muted_until is not None and time.monotonic() < muted_until:
            return False
        try:
            ok = ctx.inject_message(text, session_key=target)
        except Exception as exc:
            logger.warning("narration inject failed: %s", exc)
            ok = False
        if ok:
            self._target_failures.pop(target, None)
            self._target_muted.pop(target, None)
            if self._blocked:
                self._blocked = False
                self.svc.ledger.set_cursor("narrate", "blocked", "0")
            return True
        failures = self._target_failures.get(target, 0) + 1
        self._target_failures[target] = failures
        if failures >= MAX_TARGET_FAILURES:
            if target not in self._target_muted:
                logger.info("narration to session %s muted after %d failures",
                            target, failures)
            self._target_muted[target] = time.monotonic() + MUTE_SECONDS
            return False
        if not self._blocked:
            self._blocked = True
            self.svc.ledger.set_cursor("narrate", "blocked", "1")
        if target not in self._denied_logged:
            self._denied_logged.add(target)
            logger.info(
                "narration to session %s was refused; set plugins.entries."
                "swarm-forensics.allow_gateway_injection: true to allow it",
                target)
        return False
