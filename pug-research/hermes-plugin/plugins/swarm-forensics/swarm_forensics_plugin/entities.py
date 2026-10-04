"""Entity knowledge graph: agents, swarms, cases, traces, collections.

Each entity is a note, like an Obsidian page. Notes are Markdown and may
hold [[wikilinks]]. A wikilink to another entity becomes a `mentions`
edge, so backlinks and the graph stay in step with the text. Hunts write
here too, tagged with origin `model`, and never overwrite human notes.
"""

from . import db
from .extract import INDICATOR_KINDS, wikilinks
from .safety import (
    ENTITY_TYPES,
    HIERARCHY,
    LEGACY_LINKS,
    LEGACY_TYPES,
    LINK_KINDS,
)

ALL_LINK_KINDS = LINK_KINDS + ("mentions",)
MAX_GRAPH_NODES = 600


class EntityError(ValueError):
    pass


def _entity(row):
    tags = db.loads(row["tags"], []) if "tags" in row.keys() else []
    return {"id": row["id"], "type": row["type"], "name": row["name"],
            "summary": row["summary"], "notes": row["notes"],
            "attrs": db.loads(row["attrs"], {}), "origin": row["origin"],
            "tags": tags,
            "created_utc": row["created_utc"], "updated_utc": row["updated_utc"]}


def _check_type(kind):
    if kind in LEGACY_TYPES:
        kind = LEGACY_TYPES[kind]
    if kind not in ENTITY_TYPES:
        raise EntityError("type must be one of %s" % ", ".join(ENTITY_TYPES))


def _clean_name(name):
    name = " ".join(str(name or "").split())
    if not name or len(name) > 120:
        raise EntityError("name must be 1 to 120 characters")
    if any(c in name for c in "[]|#"):
        raise EntityError("name must not contain [ ] | #")
    return name


class Graph:
    def __init__(self, database):
        self.db = database

    # -- entities -----------------------------------------------------------

    def upsert(self, kind, name, summary="", attrs=None, origin="model",
               evidence_id=None, tags=None):
        """Create an entity or enrich an existing one. Never erases text."""
        kind = LEGACY_TYPES.get(kind, kind)
        _check_type(kind)
        name = _clean_name(name)
        stamp = db.now()
        tags_list = [str(t).strip() for t in (tags or []) if str(t).strip()]
        with self.db.connect() as conn:
            row = conn.execute(
                "SELECT * FROM entities WHERE type = ? AND name = ?",
                (kind, name)).fetchone()
            if row is None:
                eid = db.new_id()
                conn.execute(
                    "INSERT INTO entities(id, type, name, summary, attrs, origin,"
                    " tags, created_utc, updated_utc) VALUES (?,?,?,?,?,?,?,?,?)",
                    (eid, kind, name, summary[:600], db.dumps(attrs or {}),
                     origin, db.dumps(tags_list), stamp, stamp))
            else:
                eid = row["id"]
                merged = db.loads(row["attrs"], {})
                merged.update(attrs or {})
                existing_tags = db.loads(row["tags"], []) if "tags" in row.keys() else []
                combined_tags = sorted(list(set(existing_tags + tags_list)))
                conn.execute(
                    "UPDATE entities SET summary = ?, attrs = ?, tags = ?, updated_utc = ?"
                    " WHERE id = ?",
                    (row["summary"] or summary[:600], db.dumps(merged),
                     db.dumps(combined_tags), stamp, eid))
            if evidence_id is not None:
                conn.execute(
                    "INSERT OR IGNORE INTO entity_evidence(entity_id, evidence_id)"
                    " VALUES (?,?)", (eid, evidence_id))
            return _entity(conn.execute(
                "SELECT * FROM entities WHERE id = ?", (eid,)).fetchone())

    def get(self, eid):
        with self.db.connect() as conn:
            row = conn.execute(
                "SELECT * FROM entities WHERE id = ?", (eid,)).fetchone()
        return _entity(row) if row else None

    def find(self, kind, name):
        kind = LEGACY_TYPES.get(kind, kind)
        with self.db.connect() as conn:
            row = conn.execute(
                "SELECT * FROM entities WHERE type = ? AND name = ?",
                (kind, name)).fetchone()
        return _entity(row) if row else None

    def list(self, kind=None, query=None, limit=200):
        sql = ("SELECT e.*, (SELECT COUNT(*) FROM links l WHERE l.src = e.id"
               " OR l.dst = e.id) AS degree,"
               " (SELECT COUNT(*) FROM entity_evidence x WHERE x.entity_id = e.id)"
               " AS evidence_count FROM entities e WHERE 1=1")
        args = []
        if kind:
            kind = LEGACY_TYPES.get(kind, kind)
            _check_type(kind)
            sql += " AND e.type = ?"
            args.append(kind)
        if query:
            sql += " AND (e.name LIKE ? OR e.summary LIKE ?)"
            like = "%" + query.replace("%", "") + "%"
            args += [like, like]
        sql += " ORDER BY e.updated_utc DESC LIMIT ?"
        args.append(max(1, min(int(limit), 1000)))
        with self.db.connect() as conn:
            rows = conn.execute(sql, args).fetchall()
        out = []
        for row in rows:
            item = _entity(row)
            item["degree"] = row["degree"]
            item["evidence_count"] = row["evidence_count"]
            del item["notes"]
            out.append(item)
        return out

    def update(self, eid, name=None, summary=None, notes=None, attrs=None,
               tags=None):
        with self.db.connect() as conn:
            row = conn.execute(
                "SELECT * FROM entities WHERE id = ?", (eid,)).fetchone()
            if row is None:
                raise EntityError("entity not found")
            new_name = _clean_name(name) if name is not None else row["name"]
            clash = conn.execute(
                "SELECT id FROM entities WHERE type = ? AND name = ? AND id != ?",
                (row["type"], new_name, eid)).fetchone()
            if clash:
                raise EntityError("an entity with that name already exists")
            tags_json = (row["tags"] if "tags" in row.keys() else "[]")
            if tags is not None:
                clean_tags = [str(t).strip() for t in tags if str(t).strip()]
                tags_json = db.dumps(clean_tags)
            conn.execute(
                "UPDATE entities SET name = ?, summary = ?, notes = ?, attrs = ?,"
                " tags = ?, origin = 'human', updated_utc = ? WHERE id = ?",
                (new_name,
                 row["summary"] if summary is None else str(summary)[:600],
                 row["notes"] if notes is None else str(notes)[:200000],
                 row["attrs"] if attrs is None else db.dumps(attrs),
                 tags_json,
                 db.now(), eid))
            if notes is not None:
                self._sync_mentions(conn, eid, str(notes))
        return self.get(eid)

    def delete(self, eid):
        with self.db.connect() as conn:
            cur = conn.execute("DELETE FROM entities WHERE id = ?", (eid,))
        return cur.rowcount > 0

    # -- links --------------------------------------------------------------

    def link(self, src, dst, kind, evidence_id=None):
        kind = LEGACY_LINKS.get(kind, kind)
        if kind not in ALL_LINK_KINDS:
            raise EntityError("kind must be one of %s" % ", ".join(ALL_LINK_KINDS))
        if src == dst:
            raise EntityError("an entity cannot link to itself")
        with self.db.connect() as conn:
            src_row = conn.execute("SELECT id, type FROM entities WHERE id = ?",
                                   (src,)).fetchone()
            dst_row = conn.execute("SELECT id, type FROM entities WHERE id = ?",
                                   (dst,)).fetchone()
            if src_row is None or dst_row is None:
                raise EntityError("entity not found")
            if kind == "part_of":
                st, dt = src_row["type"], dst_row["type"]
                if st in HIERARCHY and dt in HIERARCHY:
                    sr, dr = HIERARCHY.index(st), HIERARCHY.index(dt)
                    if sr == dr:
                        kind = "related"
                    elif sr > dr:
                        src, dst = dst, src
            conn.execute(
                "INSERT OR IGNORE INTO links(src, dst, kind, evidence_id,"
                " created_utc) VALUES (?,?,?,?,?)",
                (src, dst, kind, evidence_id, db.now()))
            row = conn.execute(
                "SELECT id FROM links WHERE src = ? AND dst = ? AND kind = ?",
                (src, dst, kind)).fetchone()
        return row["id"]

    def unlink(self, link_id):
        with self.db.connect() as conn:
            cur = conn.execute("DELETE FROM links WHERE id = ?", (link_id,))
        return cur.rowcount > 0

    def _sync_mentions(self, conn, eid, notes):
        """Make `mentions` edges match the [[wikilinks]] in a note."""
        wanted = set()
        for name in wikilinks(notes):
            row = conn.execute(
                "SELECT id FROM entities WHERE name = ? AND id != ?",
                (name, eid)).fetchone()
            if row:
                wanted.add(row["id"])
        existing = {r["dst"]: r["id"] for r in conn.execute(
            "SELECT id, dst FROM links WHERE src = ? AND kind = 'mentions'",
            (eid,))}
        for dst, link_id in existing.items():
            if dst not in wanted:
                conn.execute("DELETE FROM links WHERE id = ?", (link_id,))
        for dst in wanted - set(existing):
            conn.execute(
                "INSERT OR IGNORE INTO links(src, dst, kind, created_utc)"
                " VALUES (?,?, 'mentions', ?)", (eid, dst, db.now()))

    # -- indicators and evidence ---------------------------------------------

    def add_indicator(self, eid, kind, value, evidence_id=None):
        if kind not in INDICATOR_KINDS:
            raise EntityError("bad indicator kind")
        with self.db.connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO indicators(entity_id, kind, value,"
                " evidence_id, first_seen_utc) VALUES (?,?,?,?,?)",
                (eid, kind, str(value)[:600], evidence_id, db.now()))

    # -- views --------------------------------------------------------------

    def view(self, eid):
        """Everything one note page shows: edges, backlinks, evidence."""
        entity = self.get(eid)
        if entity is None:
            return None
        with self.db.connect() as conn:
            out = conn.execute(
                "SELECT l.id, l.kind, e.id AS other, e.type, e.name FROM links l"
                " JOIN entities e ON e.id = l.dst WHERE l.src = ? ORDER BY e.name",
                (eid,)).fetchall()
            back = conn.execute(
                "SELECT l.id, l.kind, e.id AS other, e.type, e.name FROM links l"
                " JOIN entities e ON e.id = l.src WHERE l.dst = ? ORDER BY e.name",
                (eid,)).fetchall()
            indicators = conn.execute(
                "SELECT kind, value, evidence_id, first_seen_utc FROM indicators"
                " WHERE entity_id = ? ORDER BY first_seen_utc DESC LIMIT 200",
                (eid,)).fetchall()
            evidence = conn.execute(
                "SELECT v.id, v.url, v.title, v.excerpt, v.claim_level, v.source,"
                " v.observed_utc FROM evidence v JOIN entity_evidence x"
                " ON x.evidence_id = v.id WHERE x.entity_id = ?"
                " ORDER BY v.observed_utc DESC LIMIT 100", (eid,)).fetchall()
        names = {m for m in wikilinks(entity["notes"])}
        resolved = {r["name"].lower() for r in out if r["kind"] == "mentions"}
        parents = {}
        children = {}
        for edge in out:
            if edge["kind"] == "part_of":
                parents.setdefault(edge["type"], []).append(dict(edge))
        for edge in back:
            if edge["kind"] == "part_of":
                children.setdefault(edge["type"], []).append(dict(edge))
        entity["outgoing"] = [dict(r) for r in out]
        entity["backlinks"] = [dict(r) for r in back]
        entity["parents"] = parents
        entity["children"] = children
        entity["indicators"] = [dict(r) for r in indicators]
        entity["evidence"] = [dict(r) for r in evidence]
        entity["unresolved"] = sorted(n for n in names if n.lower() not in resolved)
        return entity

    def graph(self, center=None, depth=2, types=None):
        """Return {nodes, edges}. A center id limits the view to its neighborhood."""
        with self.db.connect() as conn:
            if center:
                keep, frontier = {center}, {center}
                for _ in range(max(1, min(int(depth), 4))):
                    if not frontier or len(keep) >= MAX_GRAPH_NODES:
                        break
                    marks = ",".join("?" * len(frontier))
                    rows = conn.execute(
                        "SELECT src, dst FROM links WHERE src IN (%s) OR dst IN (%s)"
                        % (marks, marks), list(frontier) * 2).fetchall()
                    nxt = set()
                    for r in rows:
                        nxt.update((r["src"], r["dst"]))
                    frontier = nxt - keep
                    keep |= nxt
                ids = list(keep)[:MAX_GRAPH_NODES]
                marks = ",".join("?" * len(ids))
                nodes = conn.execute(
                    "SELECT id, type, name, summary FROM entities WHERE id IN (%s)"
                    % marks, ids).fetchall()
            else:
                nodes = conn.execute(
                    "SELECT id, type, name, summary FROM entities"
                    " ORDER BY updated_utc DESC LIMIT ?",
                    (MAX_GRAPH_NODES,)).fetchall()
            ids = [n["id"] for n in nodes]
            if types:
                nodes = [n for n in nodes if n["type"] in types]
                ids = [n["id"] for n in nodes]
            idset = set(ids)
            edges = [dict(r) for r in conn.execute(
                "SELECT id, src, dst, kind FROM links").fetchall()
                if r["src"] in idset and r["dst"] in idset]
        degree = {}
        for e in edges:
            degree[e["src"]] = degree.get(e["src"], 0) + 1
            degree[e["dst"]] = degree.get(e["dst"], 0) + 1
        return {"nodes": [dict(n, degree=degree.get(n["id"], 0),
                               rank=HIERARCHY.index(n["type"]) if n["type"] in HIERARCHY else None)
                          for n in nodes],
                "edges": edges, "center": center}
