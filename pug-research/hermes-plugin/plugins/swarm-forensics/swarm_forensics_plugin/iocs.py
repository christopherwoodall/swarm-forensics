"""IOC list: seed import, proposals, audited transitions, promotion policy.

Terms are never deleted. Every status change writes an audit row with the
actor and the reason. The model can propose a term and attach evidence.
It cannot promote one. Promotion is either a human decision, or an
evidence rule the operator turned on. A human rejection stays final.
"""

import re

from . import db
from .paths import SEEDS_DIR
from .safety import CLAIM_LEVELS, host_of, term_is_specific

SEED_RULE_TERMS = [
    ("zz=oai", "nonce_grammar"), ("zzbulk", "nonce_grammar"),
    ("prepnonce", "nonce_grammar"), ("wbdisable", "nonce_grammar"),
    ("arqcb", "nonce_grammar"),
    ("jqp.vercel.app", "relay"), ("allorigins.hexlet.app", "relay"),
    ("r.jina.ai", "relay"), ("da.gd", "relay"),
    ("OAI_META_1312", "watch_term"), ("AgentSECCountyLinker", "watch_term"),
    ("sec.govwayback.com", "watch_term"),
    ("county.json", "basin_target"), ("regcf.json", "basin_target"),
    ("vizhub.healthdata.org", "basin_target"), ("api.datausa.io", "basin_target"),
]

STATUSES = ("proposed", "active", "inactive", "rejected", "benign")
# actor -> {from_status: allowed to_status}
_TRANSITIONS = {
    "human": {"proposed": ("active", "rejected", "benign"),
              "active": ("inactive", "benign", "rejected"),
              "inactive": ("active", "benign", "rejected"),
              "rejected": ("proposed", "benign", "active"),
              "benign": ("proposed", "active", "inactive", "rejected")},
    "policy": {"proposed": ("active",)},
}


class IocError(ValueError):
    pass


def _ioc(row):
    return {k: row[k] for k in row.keys()}


def parse_wordlist(lines):
    """Parse lines of a wordlist, yielding (term, category).

    Lines starting with '# SECTION' set category = section.lower().
    Blank lines and comments not starting with '# SECTION' are skipped.
    """
    section = "uncategorized"
    for line in lines:
        line = str(line or "").strip()
        if not line:
            continue
        if line.startswith("#"):
            m = re.match(r"#\s*([A-Za-z0-9_]+)", line)
            if m:
                section = m.group(1).lower()
            continue
        yield line, section


class IocStore:
    def __init__(self, database, settings):
        self.db = database
        self.settings = settings

    # -- seeds --------------------------------------------------------------

    def seed(self):
        """Import the read-only seed lists as active terms. Idempotent."""
        with self.db.connect() as conn:
            done = conn.execute(
                "SELECT 1 FROM cursors WHERE source = 'meta' AND key = 'seeded'"
            ).fetchone()
            if done:
                return 0
            stamp, added = db.now(), 0
            path = SEEDS_DIR / "wordlist-seed.txt"
            terms = [(term, cat, "seeds/wordlist-seed.txt")
                     for term, cat in parse_wordlist(path.read_text(encoding="utf-8").splitlines())]
            terms += [(t, c, "seeds/query-templates") for t, c in SEED_RULE_TERMS]
            for term, category, source in terms:
                cur = conn.execute(
                    "INSERT OR IGNORE INTO iocs(term, category, status, origin,"
                    " provenance, added_utc, updated_utc)"
                    " VALUES (?,?, 'active', 'seed', ?, ?, ?)",
                    (term, category, source, stamp, stamp))
                added += cur.rowcount
            conn.execute(
                "INSERT INTO cursors(source, key, value) VALUES ('meta','seeded',?)",
                (stamp,))
        return added

    # -- reads --------------------------------------------------------------

    def list(self, status=None, query=None, limit=500, offset=0):
        sql = ("SELECT i.*, (SELECT COUNT(*) FROM ioc_evidence x WHERE"
               " x.ioc_id = i.id) AS evidence_count FROM iocs i WHERE 1=1")
        args = []
        if status:
            if status not in STATUSES:
                raise IocError("bad status")
            sql += " AND i.status = ?"
            args.append(status)
        if query:
            sql += " AND i.term LIKE ?"
            args.append("%" + query.replace("%", "") + "%")
        sql += " ORDER BY i.updated_utc DESC, i.id DESC LIMIT ? OFFSET ?"
        args += [max(1, min(int(limit), 2000)), max(0, int(offset))]
        with self.db.connect() as conn:
            return [_ioc(r) for r in conn.execute(sql, args).fetchall()]

    def counts(self):
        with self.db.connect() as conn:
            rows = conn.execute(
                "SELECT status, COUNT(*) AS n FROM iocs GROUP BY status").fetchall()
        out = {s: 0 for s in STATUSES}
        out.update({r["status"]: r["n"] for r in rows})
        return out

    def active_terms(self):
        with self.db.connect() as conn:
            return [r["term"] for r in conn.execute(
                "SELECT term FROM iocs WHERE status = 'active' ORDER BY term")]

    def detail(self, ioc_id):
        with self.db.connect() as conn:
            row = conn.execute("SELECT * FROM iocs WHERE id = ?", (ioc_id,)).fetchone()
            if row is None:
                return None
            log = conn.execute(
                "SELECT ts, from_status, to_status, actor, reason FROM ioc_log"
                " WHERE ioc_id = ? ORDER BY id", (ioc_id,)).fetchall()
            evidence = conn.execute(
                "SELECT v.id, v.url, v.title, v.excerpt, v.claim_level, v.tainted,"
                " v.observed_utc FROM evidence v JOIN ioc_evidence x"
                " ON x.evidence_id = v.id WHERE x.ioc_id = ?"
                " ORDER BY v.observed_utc DESC LIMIT 50", (ioc_id,)).fetchall()
        out = _ioc(row)
        out["log"] = [dict(r) for r in log]
        out["evidence"] = [dict(r) for r in evidence]
        return out

    # -- proposals ----------------------------------------------------------

    def propose(self, term, category="proposed", provenance="", evidence_id=None,
                confidence=0.0, note="", actor="model"):
        """Propose a term. Returns (ioc_dict_or_None, reason).

        A term that is excluded, too broad, or already decided is
        recorded against existing rows only. A rejected term stays rejected.
        """
        term = str(term or "").strip()
        excluded = {t.lower() for t in self.settings.get("safety.exclusion_terms")}
        if term.lower() in excluded:
            return None, "excluded"
        if not term_is_specific(term):
            return None, "too broad"
        stamp = db.now()
        with self.db.connect() as conn:
            row = conn.execute("SELECT * FROM iocs WHERE term = ?", (term,)).fetchone()
            if row is None:
                cur = conn.execute(
                    "INSERT INTO iocs(term, category, status, origin, confidence,"
                    " provenance, note, added_utc, updated_utc)"
                    " VALUES (?,?, 'proposed', ?, ?, ?, ?, ?, ?)",
                    (term, category, actor, float(confidence), provenance[:500],
                     note[:500], stamp, stamp))
                ioc_id, reason = cur.lastrowid, "created"
                conn.execute(
                    "INSERT INTO ioc_log(ioc_id, ts, from_status, to_status, actor,"
                    " reason) VALUES (?,?,NULL,'proposed',?,?)",
                    (ioc_id, stamp, actor, note[:280] or "proposed"))
            else:
                ioc_id, reason = row["id"], "existing"
                conn.execute(
                    "UPDATE iocs SET confidence = MAX(confidence, ?), updated_utc = ?"
                    " WHERE id = ?", (float(confidence), stamp, ioc_id))
            if evidence_id is not None:
                conn.execute(
                    "INSERT OR IGNORE INTO ioc_evidence(ioc_id, evidence_id)"
                    " VALUES (?,?)", (ioc_id, evidence_id))
            out = _ioc(conn.execute(
                "SELECT * FROM iocs WHERE id = ?", (ioc_id,)).fetchone())
        return out, reason

    # -- decisions ----------------------------------------------------------

    def transition(self, ioc_id, to_status, actor, reason=""):
        allowed = _TRANSITIONS.get(actor)
        if allowed is None:
            raise IocError("unknown actor")
        with self.db.connect() as conn:
            row = conn.execute("SELECT * FROM iocs WHERE id = ?", (ioc_id,)).fetchone()
            if row is None:
                raise IocError("ioc not found")
            if to_status not in allowed.get(row["status"], ()):
                raise IocError("%s cannot move %s to %s"
                               % (actor, row["status"], to_status))
            stamp = db.now()
            conn.execute(
                "UPDATE iocs SET status = ?, updated_utc = ?, note = ? WHERE id = ?",
                (to_status, stamp, reason[:500], ioc_id))
            conn.execute(
                "INSERT INTO ioc_log(ioc_id, ts, from_status, to_status, actor,"
                " reason) VALUES (?,?,?,?,?,?)",
                (ioc_id, stamp, row["status"], to_status, actor, reason[:500]))
            return _ioc(conn.execute(
                "SELECT * FROM iocs WHERE id = ?", (ioc_id,)).fetchone())

    def decide(self, ioc_id, decision, reason="", narrower=None):
        """Human decision: accept, reject, narrow, deactivate, reactivate, reopen, benign."""
        if decision == "accept":
            return self.transition(ioc_id, "active", "human", reason)
        if decision == "reject":
            return self.transition(ioc_id, "rejected", "human", reason)
        if decision == "deactivate":
            return self.transition(ioc_id, "inactive", "human", reason)
        if decision == "reactivate":
            return self.transition(ioc_id, "active", "human", reason)
        if decision == "reopen":
            return self.transition(ioc_id, "proposed", "human", reason)
        if decision == "benign":
            return self.transition(ioc_id, "benign", "human", reason)
        if decision == "narrow":
            narrower = str(narrower or "").strip()
            if not term_is_specific(narrower):
                raise IocError("narrower term is missing or too broad")
            parent = self.detail(ioc_id)
            if parent is None:
                raise IocError("ioc not found")
            if narrower.lower() == parent["term"].lower():
                raise IocError("narrower term must differ")
            self.transition(ioc_id, "rejected", "human",
                            ("narrowed to %s. %s" % (narrower, reason)).strip())
            child, _ = self.propose(
                narrower, parent["category"],
                provenance="narrowed from %s" % parent["term"], actor="human",
                note="narrowed by operator")
            return self.transition(child["id"], "active", "human",
                                   "narrowed from %s" % parent["term"])
        raise IocError("unknown decision")

    # -- policy -------------------------------------------------------------

    def _stats(self, conn, ioc_id):
        rows = conn.execute(
            "SELECT v.id, v.url, v.claim_level FROM evidence v JOIN ioc_evidence x"
            " ON x.evidence_id = v.id WHERE x.ioc_id = ? AND v.tainted = 0",
            (ioc_id,)).fetchall()
        hosts = {host_of(r["url"]) for r in rows if host_of(r["url"])}
        level = max((CLAIM_LEVELS.index(r["claim_level"]) for r in rows
                     if r["claim_level"] in CLAIM_LEVELS), default=-1)
        return {"evidence": len(rows), "hosts": len(hosts), "level": level}

    def apply_policy(self):
        """Promote proposed terms that meet the operator's evidence rules.

        Returns the list of promoted terms. Does nothing in manual mode.
        Tainted evidence never counts. A daily cap bounds the damage if a
        rule is too loose.
        """
        cfg = self.settings.all()
        if cfg["iocs.promotion"] != "automatic":
            return []
        need = (cfg["iocs.auto_min_evidence"], cfg["iocs.auto_min_sources"],
                CLAIM_LEVELS.index(cfg["iocs.auto_min_claim_level"]))
        promoted = []
        with self.db.connect() as conn:
            today = db.now()[:10]
            used = conn.execute(
                "SELECT COUNT(*) FROM ioc_log WHERE actor = 'policy' AND"
                " to_status = 'active' AND ts LIKE ?", (today + "%",)).fetchone()[0]
            candidates = conn.execute(
                "SELECT id, term FROM iocs WHERE status = 'proposed'"
                " ORDER BY confidence DESC, id").fetchall()
            ready = []
            for row in candidates:
                s = self._stats(conn, row["id"])
                if (s["evidence"] >= need[0] and s["hosts"] >= need[1]
                        and s["level"] >= need[2]):
                    ready.append((row["id"], row["term"], s))
        for ioc_id, term, s in ready:
            if used >= cfg["iocs.auto_max_per_day"]:
                break
            reason = ("auto: %d evidence items, %d hosts, claim %s"
                      % (s["evidence"], s["hosts"], CLAIM_LEVELS[s["level"]]))
            self.transition(ioc_id, "active", "policy", reason)
            promoted.append(term)
            used += 1
        return promoted
