"""Research job: watch what other researchers publish, extract new IOCs.

Fetches the configured watchlist, dedupes by URL + content hash, mines
novel n-gram terms against the working IOC copy, and proposes candidates
with provenance. Read-only public pages.
"""

import hashlib
import json
import re
import subprocess
import time
from datetime import datetime, timezone

from config import state_path
from iocs import propose_term

MIN_CHARS_DEFAULT = 4


def _fetch(url, cfg):
    ua = cfg["sources"].get("user_agent", "swarm-forensics/0.1")
    cmd = ["curl", "-sL", "--max-time", "60", "-A", ua, url]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    time.sleep(float(cfg["sources"].get("request_delay_seconds", 2)))
    if r.returncode != 0:
        return None
    return r.stdout


def _novel_terms(text, known, min_chars):
    """Naive n-gram novelty: 1-3 grams absent from the working copy."""
    words = re.findall(r"[A-Za-z0-9_.\-/]{%d,64}" % min_chars, text)
    cands = set()
    for n in (1, 2, 3):
        for i in range(len(words) - n + 1):
            gram = " ".join(words[i:i + n])
            if gram not in known and len(gram) >= min_chars:
                cands.add(gram)
    # Keep it conservative: prefer technical-looking tokens.
    return sorted(c for c in cands
                  if re.search(r"[./=_-]|https?|[A-Z]{2,}", c))[:50]


def check_watchlist(cfg):
    """Fetch watchlist, propose novel terms. Returns proposal count."""
    watch = [u.strip() for u in
             cfg["research"].get("watch_urls", "").splitlines() if u.strip()]
    min_chars = int(cfg["research"].get("novelty_min_chars", MIN_CHARS_DEFAULT))
    seen_path = state_path(cfg, "research_seen.json")
    seen = json.loads(seen_path.read_text(encoding="utf-8"))
    from iocs import _load  # working copy for novelty check
    known = {r["term"] for r in _load(cfg)}
    n = 0
    for url in watch:
        body = _fetch(url, cfg)
        if not body:
            continue
        digest = hashlib.sha256(body.encode("utf-8", "replace")).hexdigest()
        if seen.get(url) == digest:
            continue
        seen[url] = digest
        # Strip tags crudely; this is a stub extractor.
        text = re.sub(r"<[^>]+>", " ", body)
        for term in _novel_terms(text, known, min_chars):
            if propose_term(cfg, term, provenance=url,
                             category="research", note=text[:120]):
                known.add(term)
                n += 1
    seen_path.write_text(json.dumps(seen, indent=1) + "\n", encoding="utf-8")
    return n
