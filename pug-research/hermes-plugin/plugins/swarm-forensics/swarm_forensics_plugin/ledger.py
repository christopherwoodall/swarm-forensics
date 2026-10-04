"""Hunt ledger: hunts, events, queries, evidence, leads, cursors, candidates."""

from datetime import datetime, timezone

from . import db
from .safety import CLAIM_LEVELS, content_hash, redact_text, redact_url

ACTIVE_STATES = ("running", "waiting")
HUNT_STATES = ("running", "waiting", "paused", "blocked", "stopped")
HUNT_FIELDS = {"state", "detail", "started_utc", "ended_utc", "cycle", "owner",
               "heartbeat_utc", "stop_requested", "pause_requested", "stats"}


def _row(row):
    return {k: row[k] for k in row.keys()}


class Ledger:
    def __init__(self, database):
        self.db = database

    # -- hunts --------------------------------------------------------------

    def create_hunt(self, origin, goal, max_cycles=0, schedule_id=None):
        hunt_id = db.new_id()
        stamp = db.now()
        with self.db.connect() as conn:
            conn.execute(
                "INSERT INTO hunts(id, origin, goal, state, created_utc,"
                " started_utc, max_cycles, schedule_id)"
                " VALUES (?,?,?, 'running', ?, ?, ?, ?)",
                (hunt_id, origin, goal, stamp, stamp, int(max_cycles), schedule_id))
        return self.hunt(hunt_id)

    @staticmethod
    def _hunt_row(row):
        out = _row(row)
        out["stats"] = db.loads(out["stats"], {})
        return out

    def hunt(self, hunt_id):
        with self.db.connect() as conn:
            row = conn.execute("SELECT * FROM hunts WHERE id = ?",
                               (hunt_id,)).fetchone()
        return self._hunt_row(row) if row else None

    def hunts(self, limit=50):
        with self.db.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM hunts ORDER BY created_utc DESC, rowid DESC LIMIT ?",
                (max(1, min(int(limit), 500)),)).fetchall()
        return [self._hunt_row(r) for r in rows]

    def active_hunt(self):
        """Return the hunt that is running or waiting, if any."""
        with self.db.connect() as conn:
            row = conn.execute(
                "SELECT * FROM hunts WHERE state IN ('running','waiting')"
                " ORDER BY created_utc DESC LIMIT 1").fetchone()
        return self._hunt_row(row) if row else None

    def update_hunt(self, hunt_id, **fields):
        bad = set(fields) - HUNT_FIELDS
        if bad:
            raise ValueError("bad hunt fields: %s" % ", ".join(sorted(bad)))
        if "stats" in fields:
            fields["stats"] = db.dumps(fields["stats"])
        if not fields:
            return
        sets = ", ".join("%s = ?" % k for k in fields)
        with self.db.connect() as conn:
            conn.execute("UPDATE hunts SET %s WHERE id = ?" % sets,
                         list(fields.values()) + [hunt_id])

    # -- events -------------------------------------------------------------

    def event(self, hunt_id, kind, message, level="info", data=None):
        with self.db.connect() as conn:
            cur = conn.execute(
                "INSERT INTO events(hunt_id, ts, kind, level, message, data)"
                " VALUES (?,?,?,?,?,?)",
                (hunt_id, db.now(), kind, level, redact_text(message)[:500],
                 db.dumps(data or {})))
            return cur.lastrowid

    def events(self, hunt_id=None, after_id=0, limit=200):
        sql, args = "SELECT * FROM events WHERE id > ?", [int(after_id)]
        if hunt_id:
            sql += " AND hunt_id = ?"
            args.append(hunt_id)
        sql += " ORDER BY id DESC LIMIT ?"
        args.append(max(1, min(int(limit), 1000)))
        with self.db.connect() as conn:
            rows = conn.execute(sql, args).fetchall()
        out = []
        for row in reversed(rows):
            item = _row(row)
            item["data"] = db.loads(item["data"], {})
            out.append(item)
        return out

    # -- queries ------------------------------------------------------------

    def log_query(self, hunt_id, source, query, outcome, http_status=0,
                  result_count=0):
        with self.db.connect() as conn:
            conn.execute(
                "INSERT INTO queries(hunt_id, source, query, outcome, http_status,"
                " result_count, ts) VALUES (?,?,?,?,?,?,?)",
                (hunt_id, source, query[:500], outcome, http_status,
                 result_count, db.now()))

    def query_seen(self, source, query, hours=24):
        """True when a query finished OK recently. Throttles never count."""
        with self.db.connect() as conn:
            row = conn.execute(
                "SELECT ts FROM queries WHERE source = ? AND query = ?"
                " AND outcome = 'ok' ORDER BY id DESC LIMIT 1",
                (source, query[:500])).fetchone()
        return row is not None and _age_hours(row["ts"]) < hours

    def recent_queries(self, limit=40):
        with self.db.connect() as conn:
            rows = conn.execute(
                "SELECT source, query, outcome, result_count FROM queries"
                " ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [_row(r) for r in rows]

    def query_stats(self):
        with self.db.connect() as conn:
            rows = conn.execute(
                "SELECT outcome, COUNT(*) AS n FROM queries GROUP BY outcome"
            ).fetchall()
        return {r["outcome"]: r["n"] for r in rows}

    # -- evidence -----------------------------------------------------------

    def add_evidence(self, hunt_id, source, query, url, title, excerpt,
                     tainted=False, claim_level="L1", analysis=None):
        """Store one evidence row. Returns (evidence_id, created)."""
        url = redact_url(url)[:2000]
        excerpt = redact_text(excerpt)[:2000]
        digest = content_hash(excerpt or title or url)
        with self.db.connect() as conn:
            row = conn.execute(
                "SELECT id FROM evidence WHERE url = ? AND content_hash = ?",
                (url, digest)).fetchone()
            if row:
                return row["id"], False
            level = claim_level if claim_level in CLAIM_LEVELS else "L1"
            cur = conn.execute(
                "INSERT INTO evidence(hunt_id, source, query, url, title, excerpt,"
                " content_hash, observed_utc, claim_level, tainted, analysis)"
                " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (hunt_id, source, query[:300], url, redact_text(title)[:300],
                 excerpt, digest, db.now(), level, int(bool(tainted)),
                 db.dumps(analysis or {})))
            return cur.lastrowid, True

    def update_evidence(self, evidence_id, claim_level, analysis, tainted):
        with self.db.connect() as conn:
            conn.execute(
                "UPDATE evidence SET claim_level = ?, analysis = ?, tainted = ?"
                " WHERE id = ?",
                (claim_level if claim_level in CLAIM_LEVELS else "L1",
                 db.dumps(analysis), int(bool(tainted)), evidence_id))

    def url_known(self, url):
        with self.db.connect() as conn:
            return conn.execute("SELECT 1 FROM evidence WHERE url = ? LIMIT 1",
                                (redact_url(url)[:2000],)).fetchone() is not None

    def list_evidence(self, query=None, min_level=None, hunt_id=None,
                      limit=100, offset=0):
        sql = ("SELECT id, hunt_id, source, query, url, title, excerpt, claim_level,"
               " tainted, observed_utc FROM evidence WHERE 1=1")
        args = []
        if query:
            sql += " AND (url LIKE ? OR title LIKE ? OR excerpt LIKE ?)"
            like = "%" + query.replace("%", "") + "%"
            args += [like] * 3
        if hunt_id:
            sql += " AND hunt_id = ?"
            args.append(hunt_id)
        if min_level in CLAIM_LEVELS:
            wanted = CLAIM_LEVELS[CLAIM_LEVELS.index(min_level):]
            sql += " AND claim_level IN (%s)" % ",".join("?" * len(wanted))
            args += list(wanted)
        sql += " ORDER BY observed_utc DESC, id DESC LIMIT ? OFFSET ?"
        args += [max(1, min(int(limit), 1000)), max(0, int(offset))]
        with self.db.connect() as conn:
            return [_row(r) for r in conn.execute(sql, args).fetchall()]

    def evidence(self, evidence_id):
        with self.db.connect() as conn:
            row = conn.execute("SELECT * FROM evidence WHERE id = ?",
                               (evidence_id,)).fetchone()
        if row is None:
            return None
        out = _row(row)
        out["analysis"] = db.loads(out["analysis"], {})
        return out

    def recent_findings(self, limit=8):
        """Short summaries of the strongest recent evidence, for planning."""
        with self.db.connect() as conn:
            rows = conn.execute(
                "SELECT url, title, claim_level, analysis FROM evidence"
                " WHERE tainted = 0 AND claim_level != 'L1'"
                " ORDER BY observed_utc DESC LIMIT ?", (limit,)).fetchall()
        return [{"url": r["url"], "claim_level": r["claim_level"],
                 "summary": db.loads(r["analysis"], {}).get("summary", "")}
                for r in rows]

    # -- leads --------------------------------------------------------------

    def add_lead(self, kind, value, priority=0.5, origin="model", hunt_id=None):
        with self.db.connect() as conn:
            cur = conn.execute(
                "INSERT OR IGNORE INTO leads(hunt_id, kind, value, priority,"
                " origin, created_utc) VALUES (?,?,?,?,?,?)",
                (hunt_id, kind, value[:500], float(priority), origin, db.now()))
            return cur.rowcount > 0

    def open_leads(self, kind=None, limit=10):
        sql, args = "SELECT * FROM leads WHERE status = 'open'", []
        if kind:
            sql += " AND kind = ?"
            args.append(kind)
        sql += " ORDER BY priority DESC, id LIMIT ?"
        args.append(limit)
        with self.db.connect() as conn:
            return [_row(r) for r in conn.execute(sql, args).fetchall()]

    def close_lead(self, lead_id, status="done"):
        with self.db.connect() as conn:
            conn.execute("UPDATE leads SET status = ? WHERE id = ?",
                         (status, lead_id))

    # -- cursors ------------------------------------------------------------

    def cursor(self, source, key, default=None):
        with self.db.connect() as conn:
            row = conn.execute(
                "SELECT value FROM cursors WHERE source = ? AND key = ?",
                (source, key)).fetchone()
        return row["value"] if row else default

    def set_cursor(self, source, key, value):
        with self.db.connect() as conn:
            conn.execute(
                "INSERT INTO cursors(source, key, value) VALUES (?,?,?)"
                " ON CONFLICT(source, key) DO UPDATE SET value = excluded.value",
                (source, key, str(value)))

    # -- candidates ---------------------------------------------------------

    def add_candidates(self, rows):
        added = 0
        with self.db.connect() as conn:
            for url, template in rows:
                cur = conn.execute(
                    "INSERT OR IGNORE INTO candidates(url, template, created_utc)"
                    " VALUES (?,?,?)", (url, template, db.now()))
                added += cur.rowcount
        return added

    def unprobed_candidates(self, limit=5):
        with self.db.connect() as conn:
            return [_row(r) for r in conn.execute(
                "SELECT * FROM candidates WHERE status = 'unprobed'"
                " ORDER BY id LIMIT ?", (limit,)).fetchall()]

    def mark_candidate(self, candidate_id, hits):
        with self.db.connect() as conn:
            conn.execute(
                "UPDATE candidates SET status = ?, hits = ?, probed_utc = ?"
                " WHERE id = ?",
                ("hit" if hits else "negative", hits, db.now(), candidate_id))

    # -- totals -------------------------------------------------------------

    def totals(self):
        with self.db.connect() as conn:
            def count(table, where=""):
                return conn.execute(
                    "SELECT COUNT(*) FROM %s %s" % (table, where)).fetchone()[0]
            return {
                "evidence": count("evidence"),
                "evidence_tainted": count("evidence", "WHERE tainted = 1"),
                "entities": count("entities"),
                "links": count("links"),
                "hunts": count("hunts"),
                "open_leads": count("leads", "WHERE status = 'open'"),
                "candidates": count("candidates"),
            }


def _age_hours(stamp):
    try:
        then = datetime.fromisoformat(stamp)
    except ValueError:
        return 1e9
    return (datetime.now(timezone.utc) - then).total_seconds() / 3600.0
