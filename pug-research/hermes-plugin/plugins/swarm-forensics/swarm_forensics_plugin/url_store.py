"""URL store: discovery catalog, triage status, and benign exclusion.

Maintains discovered and candidate URLs. Operators can examine URLs,
mark false-positive hosts as benign, and filter noisy infrastructure.
"""

from urllib.parse import urlsplit

from . import db

URL_STATUSES = ("discovered", "examined", "benign", "suspicious")


class UrlError(ValueError):
    """Raised when URL store operations fail validation."""


def _url_row(row):
    return {
        "url": row["url"],
        "host": row["host"],
        "source": row["source"],
        "status": row["status"],
        "reason": row["reason"],
        "discovered_utc": row["discovered_utc"],
        "updated_utc": row["updated_utc"],
    }


class UrlStore:
    """Manages discovered URLs and analyst triage in SQLite."""

    def __init__(self, database):
        self.db = database

    def add(self, url, host=None, source="evidence", status="discovered", reason=""):
        """Add or update a URL record. Preserves prior benign/suspicious triage."""
        url = str(url or "").strip()
        if not url:
            raise UrlError("url must not be empty")
        if status not in URL_STATUSES:
            raise UrlError("invalid status: %s" % status)
        if not host:
            parsed = urlsplit(url)
            host = (parsed.hostname or "").lower()
        else:
            host = host.lower().strip()
        stamp = db.now()
        with self.db.connect() as conn:
            existing = conn.execute(
                "SELECT status FROM urls WHERE url = ?", (url,)).fetchone()
            if existing is None:
                conn.execute(
                    "INSERT INTO urls(url, host, source, status, reason,"
                    " discovered_utc, updated_utc) VALUES (?,?,?,?,?,?,?)",
                    (url, host, source[:100], status, reason[:500], stamp, stamp))
            else:
                # Keep prior triage unless caller explicitly marks benign/suspicious
                new_status = existing["status"]
                if status in ("benign", "suspicious"):
                    new_status = status
                conn.execute(
                    "UPDATE urls SET source = ?, status = ?, reason = ?,"
                    " updated_utc = ? WHERE url = ?",
                    (source[:100], new_status, reason[:500], stamp, url))
            row = conn.execute("SELECT * FROM urls WHERE url = ?", (url,)).fetchone()
        return _url_row(row)

    def get(self, url):
        """Get URL record by URL string, or None if absent."""
        url = str(url or "").strip()
        with self.db.connect() as conn:
            row = conn.execute("SELECT * FROM urls WHERE url = ?", (url,)).fetchone()
        return _url_row(row) if row else None

    def triage(self, url, status, reason=""):
        """Set triage verdict on a URL (e.g. mark benign or suspicious)."""
        url = str(url or "").strip()
        if status not in URL_STATUSES:
            raise UrlError("status must be one of %s" % ", ".join(URL_STATUSES))
        stamp = db.now()
        with self.db.connect() as conn:
            cur = conn.execute(
                "UPDATE urls SET status = ?, reason = ?, updated_utc = ? WHERE url = ?",
                (status, reason[:500], stamp, url))
            if cur.rowcount == 0:
                # Insert if not present
                parsed = urlsplit(url)
                host = (parsed.hostname or "").lower()
                conn.execute(
                    "INSERT INTO urls(url, host, source, status, reason,"
                    " discovered_utc, updated_utc) VALUES (?,?,?,?,?,?,?)",
                    (url, host, "manual", status, reason[:500], stamp, stamp))
            row = conn.execute("SELECT * FROM urls WHERE url = ?", (url,)).fetchone()
        return _url_row(row)

    def is_benign(self, url_or_host):
        """Return True if URL or host is marked benign."""
        target = str(url_or_host or "").strip().lower()
        if not target:
            return False
        with self.db.connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM urls WHERE (url = ? OR host = ?) AND status = 'benign' LIMIT 1",
                (target, target)).fetchone()
        return row is not None

    def list(self, status=None, query=None, limit=200, offset=0):
        """List URL records with optional filtering."""
        sql = "SELECT * FROM urls WHERE 1=1"
        args = []
        if status:
            if status not in URL_STATUSES:
                raise UrlError("invalid status: %s" % status)
            sql += " AND status = ?"
            args.append(status)
        if query:
            sql += " AND (url LIKE ? OR host LIKE ?)"
            like = "%" + str(query).replace("%", "") + "%"
            args += [like, like]
        sql += " ORDER BY updated_utc DESC, url ASC LIMIT ? OFFSET ?"
        args += [max(1, min(int(limit), 1000)), max(0, int(offset))]
        with self.db.connect() as conn:
            rows = conn.execute(sql, args).fetchall()
        return [_url_row(r) for r in rows]

    def counts(self):
        """Return total count grouped by status."""
        with self.db.connect() as conn:
            rows = conn.execute(
                "SELECT status, COUNT(*) AS n FROM urls GROUP BY status").fetchall()
        out = {s: 0 for s in URL_STATUSES}
        out.update({r["status"]: r["n"] for r in rows})
        return out
