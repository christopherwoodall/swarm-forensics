"""Hunt lifecycle: worker thread, state machine, lease, and scheduler.

States: running, waiting (between cycles), paused, blocked, stopped.

- A human starts every hunt (command, app click) or arms a schedule first.
- A hunt runs until the operator stops it or a cycle limit is reached.
- Closing the app pauses a desktop hunt. A person must resume it.
- A host restart never resumes a hunt. It marks it paused.
- Many hunts may run at once, up to hunt.max_active_hunts.
- One worker runs per hunt. The database row is the lease.
"""

import os
import threading
import time
import uuid
from datetime import datetime, timezone

from . import db, schedule
from .ledger import ACTIVE_STATES
from .research import Blocked, Engine

LEASE_SECONDS = 120
POLL_SECONDS = 0.5
BEAT_SECONDS = 10
MAX_CYCLE_ERRORS = 3
DESKTOP_ORIGINS = ("desktop", "schedule")


class HuntRefused(RuntimeError):
    """Raised when a request breaks a rule (paused, already running)."""


def _parse(stamp):
    try:
        return datetime.fromisoformat(stamp)
    except (TypeError, ValueError):
        return None


def _age(stamp):
    then = _parse(stamp)
    if then is None:
        return 1e9
    return (datetime.now(timezone.utc) - then).total_seconds()


class Control:
    """What the engine sees: a stop flag and an interruptible wait."""

    def __init__(self, service, hunt_id):
        self.service = service
        self.hunt_id = hunt_id
        self.reason = None
        self._beat = 0.0

    def stopped(self):
        return self._check()

    def wait(self, seconds):
        """Sleep up to `seconds`. Return True when the hunt should stop."""
        end = time.monotonic() + max(0.0, seconds)
        while True:
            if self._check():
                return True
            left = end - time.monotonic()
            if left <= 0:
                return False
            time.sleep(min(POLL_SECONDS, left))

    def _check(self):
        svc = self.service
        if svc.shutdown.is_set():
            self.reason = ("paused", "host process is shutting down")
            return True
        hunt = svc.ledger.hunt(self.hunt_id)
        if hunt is None or hunt["stop_requested"]:
            self.reason = ("stopped", "stopped by operator")
            return True
        if hunt["pause_requested"]:
            self.reason = ("paused", "paused by operator")
            return True
        cfg = svc.settings.all()
        if cfg["safety.paused"]:
            self.reason = ("paused", "all hunting is paused in settings")
            return True
        if (cfg["hunt.require_desktop"] and hunt["origin"] in DESKTOP_ORIGINS
                and not svc.desktop_alive(cfg)):
            self.reason = ("paused", "the app closed; operator restart required")
            return True
        if time.monotonic() - self._beat > BEAT_SECONDS:
            self._beat = time.monotonic()
            svc.ledger.update_hunt(self.hunt_id, heartbeat_utc=db.now())
        return False


class HuntService:
    def __init__(self, database, parts, notify=None):
        self.db = database
        self.p = parts
        self.settings = parts.settings
        self.ledger = parts.ledger
        self.notify = notify or (lambda event, payload: None)
        self.owner = "%d:%s" % (os.getpid(), uuid.uuid4().hex[:8])
        self.shutdown = threading.Event()
        self._lock = threading.RLock()
        self._workers = {}
        self._scheduler = None

    # -- desktop lease --------------------------------------------------------

    def heartbeat(self):
        """The desktop app calls this while it is open."""
        self.ledger.set_cursor("meta", "desktop_heartbeat", db.now())
        return self.status()

    def desktop_alive(self, cfg=None):
        cfg = cfg or self.settings.all()
        beat = self.ledger.cursor("meta", "desktop_heartbeat")
        return beat is not None and \
            _age(beat) <= cfg["hunt.heartbeat_timeout_seconds"]

    # -- recovery -------------------------------------------------------------

    def recover(self):
        """Pause hunts that look active but have no live worker.

        Never resumes anything. Called at startup and before each start.
        """
        with self._lock:
            for hunt in self.ledger.hunts(50):
                if hunt["state"] not in ACTIVE_STATES:
                    continue
                if hunt.get("origin") == "session":
                    continue
                hid = hunt["id"]
                worker = self._workers.get(hid)
                if worker and worker.is_alive() and hunt["owner"] == self.owner:
                    continue
                if hunt["owner"] != self.owner and \
                        _age(hunt["heartbeat_utc"]) < LEASE_SECONDS:
                    continue  # another process holds a fresh lease
                self._finish(hid, "paused",
                             "interrupted: host restarted; operator restart required")

    # -- operator actions -------------------------------------------------------

    def start(self, origin="desktop", goal=None, max_cycles=0, schedule_id=None,
              parent_hunt_id=None, depth=0, session_id=None):
        cfg = self.settings.all()
        if cfg["safety.paused"]:
            raise HuntRefused("all hunting is paused in settings")
        with self._lock:
            self.recover()
            depth = int(depth)
            if depth > cfg["hunt.max_depth"]:
                raise HuntRefused("maximum sub-hunt depth (%d) exceeded" % cfg["hunt.max_depth"])
            active = self.ledger.active_hunts()
            if len(active) >= cfg["hunt.max_active_hunts"]:
                msg = "max concurrent hunts limit (%d) reached" % cfg["hunt.max_active_hunts"]
                raise HuntRefused(msg)
            if origin in ("desktop", "command", "session"):
                self.ledger.set_cursor("meta", "desktop_heartbeat", db.now())
            hunt = self.ledger.create_hunt(
                origin, (goal or "").strip() or cfg["hunt.default_goal"],
                max_cycles or cfg["hunt.max_cycles"], schedule_id,
                parent_hunt_id=parent_hunt_id, depth=depth, session_id=session_id)
            if origin != "session":
                self._spawn(hunt["id"])
        self.ledger.event(hunt["id"], "state", "hunt started (%s, depth %d)" % (origin, depth))
        return self.ledger.hunt(hunt["id"])

    def spawn_subhunt(self, parent_id, goal=None, max_cycles=None):
        cfg = self.settings.all()
        if cfg["safety.paused"]:
            raise HuntRefused("all hunting is paused in settings")
        with self._lock:
            self.recover()
            parent = self.ledger.hunt(parent_id)
            if parent is None:
                raise HuntRefused("parent hunt %s not found" % parent_id)
            parent_depth = parent.get("depth", 0)
            if parent_depth >= cfg["hunt.max_depth"]:
                raise HuntRefused("parent hunt already at max depth (%d)" % cfg["hunt.max_depth"])
            sub_depth = parent_depth + 1
            active = self.ledger.active_hunts()
            if len(active) >= cfg["hunt.max_active_hunts"]:
                msg = "max concurrent hunts (%d) reached" % cfg["hunt.max_active_hunts"]
                raise HuntRefused(msg)
            child_goal = (goal or "").strip() or ("Subhunt of %s" % parent_id)
            child = self.ledger.create_hunt(
                origin="subhunt", goal=child_goal,
                max_cycles=max_cycles or cfg["hunt.max_cycles"],
                parent_hunt_id=parent_id, depth=sub_depth,
                session_id=parent.get("session_id"))
            self._spawn(child["id"])
        self.ledger.event(
            parent_id, "state",
            "spawned child hunt %s at depth %d" % (child["id"], sub_depth))
        self.ledger.event(
            child["id"], "state",
            "child hunt started under %s at depth %d" % (parent_id, sub_depth))
        return self.ledger.hunt(child["id"])

    def resume(self, hunt_id):
        cfg = self.settings.all()
        if cfg["safety.paused"]:
            raise HuntRefused("all hunting is paused in settings")
        with self._lock:
            self.recover()
            hunt = self.ledger.hunt(hunt_id)
            if hunt is None:
                raise HuntRefused("hunt not found")
            if hunt["state"] not in ("paused", "blocked"):
                raise HuntRefused("only a paused or blocked hunt can resume")
            active = self.ledger.active_hunts()
            if len(active) >= cfg["hunt.max_active_hunts"]:
                msg = "max concurrent hunts (%d) reached" % cfg["hunt.max_active_hunts"]
                raise HuntRefused(msg)
            if hunt["origin"] in DESKTOP_ORIGINS:
                self.ledger.set_cursor("meta", "desktop_heartbeat", db.now())
            self.ledger.update_hunt(hunt_id, state="running", detail="resumed",
                                    stop_requested=0, pause_requested=0,
                                    ended_utc=None)
            self._spawn(hunt_id)
        self.ledger.event(hunt_id, "state", "hunt resumed by operator")
        return self.ledger.hunt(hunt_id)

    def pause(self, hunt_id=None):
        if hunt_id:
            hunt = self.ledger.hunt(hunt_id)
            if hunt:
                if hunt["state"] in ACTIVE_STATES and self._alive_for(hunt["id"]):
                    self.ledger.update_hunt(hunt["id"], pause_requested=1)
                elif hunt["state"] in ACTIVE_STATES:
                    self._finish(hunt["id"], "paused", "paused by operator")
                for child in self.ledger.child_hunts(hunt["id"]):
                    if child["state"] in ACTIVE_STATES:
                        self.pause(child["id"])
                return self.ledger.hunt(hunt["id"])
        hunt = self._target(hunt_id)
        if hunt["state"] in ACTIVE_STATES and self._alive_for(hunt["id"]):
            self.ledger.update_hunt(hunt["id"], pause_requested=1)
        elif hunt["state"] in ACTIVE_STATES:
            self._finish(hunt["id"], "paused", "paused by operator")
        for child in self.ledger.child_hunts(hunt["id"]):
            if child["state"] in ACTIVE_STATES:
                self.pause(child["id"])
        return self.ledger.hunt(hunt["id"])

    def stop(self, hunt_id=None):
        if hunt_id:
            hunt = self.ledger.hunt(hunt_id)
            if hunt is None:
                raise HuntRefused("hunt %s not found" % hunt_id)
            if hunt["state"] in ACTIVE_STATES and self._alive_for(hunt["id"]):
                self.ledger.update_hunt(hunt["id"], stop_requested=1)
            elif hunt["state"] != "stopped":
                self._finish(hunt["id"], "stopped", "stopped by operator")
            for child in self.ledger.child_hunts(hunt["id"]):
                if child["state"] in ACTIVE_STATES:
                    self.stop(child["id"])
            return self.ledger.hunt(hunt["id"])
        active = self.ledger.active_hunts()
        if not active:
            return None
        for h in active:
            self.stop(h["id"])
        return active[0]

    def _target(self, hunt_id, allow_idle=False):
        hunt = self.ledger.hunt(hunt_id) if hunt_id else self.ledger.active_hunt()
        if hunt is None and allow_idle and not hunt_id:
            paused = [h for h in self.ledger.hunts(5)
                      if h["state"] in ("paused", "blocked")]
            hunt = paused[0] if paused else None
        if hunt is None:
            raise HuntRefused("no hunt to act on")
        return hunt

    def _alive_for(self, hunt_id):
        worker = self._workers.get(hunt_id)
        hunt = self.ledger.hunt(hunt_id)
        return bool(worker and worker.is_alive()
                    and hunt and hunt["owner"] == self.owner)

    # -- worker -------------------------------------------------------------

    def _spawn(self, hunt_id):
        self.ledger.update_hunt(hunt_id, owner=self.owner,
                                heartbeat_utc=db.now())
        worker = threading.Thread(
            target=self._run, args=(hunt_id,), name="swarm-forensics-hunt-%s" % hunt_id[:8],
            daemon=True)
        self._workers[hunt_id] = worker
        worker.start()

    def _finish(self, hunt_id, state, detail):
        self.ledger.update_hunt(hunt_id, state=state, detail=detail,
                                ended_utc=db.now(), stop_requested=0,
                                pause_requested=0)
        self._workers.pop(hunt_id, None)
        self.ledger.event(hunt_id, "state", "%s: %s" % (state, detail),
                          level="warn" if state in ("blocked", "paused") else "info")
        self.notify("hunt.state", {"hunt_id": hunt_id, "state": state,
                                   "detail": detail})

    def _run(self, hunt_id):
        ctl = Control(self, hunt_id)
        engine = Engine(self.p, ctl)
        errors = 0
        try:
            while True:
                if ctl.stopped():
                    self._finish(hunt_id, *ctl.reason)
                    return
                hunt = self.ledger.hunt(hunt_id)
                self.ledger.update_hunt(hunt_id, state="running", detail="",
                                        cycle=hunt["cycle"] + 1,
                                        heartbeat_utc=db.now())
                self.notify("hunt.cycle", {"hunt_id": hunt_id,
                                           "cycle": hunt["cycle"] + 1})
                try:
                    totals = engine.run_cycle(hunt)
                    errors = 0
                except Blocked as exc:
                    self._finish(hunt_id, "blocked", str(exc))
                    return
                except Exception as exc:  # A bad cycle must not kill the worker.
                    errors += 1
                    self.ledger.event(hunt_id, "error", "cycle failed: %s" % exc,
                                      level="error")
                    if errors >= MAX_CYCLE_ERRORS:
                        self._finish(hunt_id, "blocked",
                                     "%d cycles failed in a row: %s"
                                     % (MAX_CYCLE_ERRORS, exc))
                        return
                    totals = {}
                hunt = self.ledger.hunt(hunt_id)
                stats = hunt["stats"]
                for key, value in totals.items():
                    stats[key] = stats.get(key, 0) + value
                self.ledger.update_hunt(hunt_id, stats=stats)
                self.ledger.event(
                    hunt_id, "cycle", "cycle %d done: %s" % (
                        hunt["cycle"], ", ".join(
                            "%d %s" % (v, k) for k, v in totals.items()) or "no work"),
                    data=totals)
                self.notify("hunt.cycle.done", {"hunt_id": hunt_id,
                                                "cycle": hunt["cycle"],
                                                "totals": totals})
                if ctl.stopped():
                    self._finish(hunt_id, *ctl.reason)
                    return
                if hunt["max_cycles"] and hunt["cycle"] >= hunt["max_cycles"]:
                    self._finish(hunt_id, "stopped", "cycle limit reached")
                    return
                pause = self.settings.get("hunt.cycle_pause_seconds")
                self.ledger.update_hunt(hunt_id, state="waiting",
                                        detail="next cycle in %ds" % pause)
                ctl.wait(pause)
        except Exception as exc:
            self._finish(hunt_id, "blocked", "worker crashed: %s" % exc)

    # -- schedules ----------------------------------------------------------

    def schedules(self):
        with self.db.connect() as conn:
            return [dict(r) for r in conn.execute(
                "SELECT * FROM schedules ORDER BY name").fetchall()]

    def add_schedule(self, name, kind, spec, goal, max_cycles=5):
        schedule.validate(kind, spec)
        name = str(name or "").strip()[:80]
        if not name:
            raise schedule.ScheduleError("name is required")
        sid = db.new_id()
        with self.db.connect() as conn:
            conn.execute(
                "INSERT INTO schedules(id, name, kind, spec, goal, max_cycles)"
                " VALUES (?,?,?,?,?,?)",
                (sid, name, kind, spec.strip(), (goal or "").strip()[:2000],
                 max(1, min(int(max_cycles), 1000))))
        return sid

    def arm_schedule(self, sid, armed):
        """Operator opt-in. Only an armed schedule can start a hunt."""
        with self.db.connect() as conn:
            row = conn.execute("SELECT * FROM schedules WHERE id = ?",
                               (sid,)).fetchone()
            if row is None:
                raise schedule.ScheduleError("schedule not found")
            if armed:
                nxt = schedule.next_after(row["kind"], row["spec"],
                                          schedule.utcnow())
                conn.execute(
                    "UPDATE schedules SET enabled = 1, armed_utc = ?,"
                    " next_run_utc = ? WHERE id = ?",
                    (db.now(), nxt.isoformat(timespec="seconds"), sid))
            else:
                conn.execute("UPDATE schedules SET enabled = 0, armed_utc = NULL,"
                             " next_run_utc = NULL WHERE id = ?", (sid,))

    def delete_schedule(self, sid):
        with self.db.connect() as conn:
            return conn.execute("DELETE FROM schedules WHERE id = ?",
                                (sid,)).rowcount > 0

    def tick(self):
        """Start due schedules. Safe to call often. Returns started hunt or None."""
        cfg = self.settings.all()
        if not cfg["schedule.enabled"] or cfg["safety.paused"]:
            return None
        if not self.desktop_alive(cfg) or \
                len(self.ledger.active_hunts()) >= cfg["hunt.max_active_hunts"]:
            return None
        now_dt = schedule.utcnow()
        for row in self.schedules():
            due = _parse(row["next_run_utc"])
            if not row["enabled"] or due is None or due > now_dt:
                continue
            nxt = schedule.next_after(row["kind"], row["spec"], now_dt)
            with self.db.connect() as conn:
                conn.execute(
                    "UPDATE schedules SET last_run_utc = ?, next_run_utc = ?"
                    " WHERE id = ?", (db.now(), nxt.isoformat(timespec="seconds"),
                                      row["id"]))
            try:
                return self.start("schedule", row["goal"], row["max_cycles"],
                                  row["id"])
            except HuntRefused:
                return None
        return None

    def ensure_scheduler(self):
        """Start the scheduler thread once. Called by the dashboard process."""
        with self._lock:
            if self._scheduler and self._scheduler.is_alive():
                return
            self._scheduler = threading.Thread(
                target=self._schedule_loop, name="swarm-forensics-scheduler",
                daemon=True)
            self._scheduler.start()

    def _schedule_loop(self):
        while not self.shutdown.wait(30):
            try:
                self.tick()
            except Exception as exc:
                self.ledger.event(None, "error", "scheduler error: %s" % exc,
                                  level="error")

    # -- status -------------------------------------------------------------

    def status(self):
        self.recover()
        cfg = self.settings.all()
        hunt = self.ledger.active_hunt()
        if hunt is None:
            recent = self.ledger.hunts(1)
            hunt = recent[0] if recent else None
        active_list = self.ledger.active_hunts()
        return {
            "hunt": hunt,
            "running": bool(hunt and hunt["state"] in ACTIVE_STATES),
            "active_hunts": active_list,
            "desktop_alive": self.desktop_alive(cfg),
            "paused_all": cfg["safety.paused"],
            "iocs": self.p.iocs.counts(),
            "totals": self.ledger.totals(),
            "queries": self.ledger.query_stats(),
            "next_schedule": self._next_schedule(),
            "narration_blocked":
                self.ledger.cursor("narrate", "blocked") == "1",
        }

    def _next_schedule(self):
        upcoming = [s["next_run_utc"] for s in self.schedules()
                    if s["enabled"] and s["next_run_utc"]]
        return min(upcoming) if upcoming else None
