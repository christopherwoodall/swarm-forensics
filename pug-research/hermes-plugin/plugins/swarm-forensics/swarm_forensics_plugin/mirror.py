"""Local text mirror for observed web artifacts.

Stores extracted text from web pages locally.
All content MUST come from Hermes web_extract.
Content is fenced as untrusted data.
Tainted content is flagged and quarantined.
"""

import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import db
from .safety import redact_text, screen_content


class MirrorStore:
    """Manages local mirrored text artifacts in SQLite and the file system."""

    def __init__(self, database, state_dir: Path):
        self.db = database
        self.state_dir = Path(state_dir)
        self.mirror_dir = self.state_dir / "mirror"
        self.mirror_dir.mkdir(parents=True, exist_ok=True)

    def save_extract(
        self,
        url: str,
        content: str,
        hunt_id: Optional[str] = None,
        session_id: Optional[str] = None,
        max_bytes: int = 500_000,
    ) -> Optional[Dict[str, Any]]:
        """Save extracted text to disk and record metadata in SQLite."""
        url = str(url or "").strip()
        content = str(content or "").strip()
        if not url or not content:
            return None

        # Truncate content to maximum byte limit
        encoded = content.encode("utf-8", errors="replace")
        if len(encoded) > max_bytes:
            encoded = encoded[:max_bytes]
            content = encoded.decode("utf-8", errors="replace")

        sha = hashlib.sha256(encoded).hexdigest()
        screen = screen_content(content)
        tainted = 1 if screen.get("tainted") else 0
        clean_text = redact_text(content)

        file_path = self.mirror_dir / f"{sha}.md"
        try:
            file_path.write_text(clean_text, encoding="utf-8")
        except OSError:
            return None

        now_ts = db.now()
        with self.db.connect() as conn:
            conn.execute(
                "INSERT INTO mirrors("
                "url, sha256, path, byte_count, tainted, hunt_id, session_id, fetched_utc)"
                " VALUES (?,?,?,?,?,?,?,?)"
                " ON CONFLICT(url) DO UPDATE SET"
                " sha256=excluded.sha256,"
                " path=excluded.path,"
                " byte_count=excluded.byte_count,"
                " tainted=excluded.tainted,"
                " hunt_id=COALESCE(excluded.hunt_id, mirrors.hunt_id),"
                " session_id=COALESCE(excluded.session_id, mirrors.session_id),"
                " fetched_utc=excluded.fetched_utc",
                (url, sha, str(file_path), len(encoded), tainted, hunt_id, session_id, now_ts),
            )

        return {
            "url": url,
            "sha256": sha,
            "path": str(file_path),
            "byte_count": len(encoded),
            "tainted": bool(tainted),
            "fetched_utc": now_ts,
        }

    def get_mirror(self, target: str) -> Optional[Dict[str, Any]]:
        """Retrieve mirror metadata by URL or sha256."""
        target = str(target or "").strip()
        if not target:
            return None
        with self.db.connect() as conn:
            row = conn.execute(
                "SELECT * FROM mirrors WHERE url = ? OR sha256 = ? LIMIT 1",
                (target, target),
            ).fetchone()
        if not row:
            return None
        return dict(row)

    def read_text(self, target: str) -> Optional[str]:
        """Read mirrored text from disk for an artifact."""
        meta = self.get_mirror(target)
        if not meta or not meta.get("path"):
            return None
        path = Path(meta["path"])
        if not path.is_file():
            return None
        try:
            return path.read_text(encoding="utf-8")
        except OSError:
            return None

    def list_mirrors(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Return list of recent mirrored artifacts."""
        with self.db.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM mirrors ORDER BY id DESC LIMIT ?",
                (max(1, min(int(limit), 200)),),
            ).fetchall()
        return [dict(r) for r in rows]

    def count(self) -> int:
        """Return count of mirrored artifacts."""
        with self.db.connect() as conn:
            row = conn.execute("SELECT COUNT(*) FROM mirrors").fetchone()
        return int(row[0]) if row else 0

    def clear(self) -> None:
        """Wipe all mirror files and database records."""
        with self.db.connect() as conn:
            conn.execute("DELETE FROM mirrors")
        if self.mirror_dir.is_dir():
            for child in self.mirror_dir.glob("*.md"):
                try:
                    child.unlink()
                except OSError:
                    pass
