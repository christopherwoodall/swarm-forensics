"""Public index adapters: urlquery, Wayback CDX, arquivo.pt CDX.

Read-only GETs through curl against a fixed host allowlist. A throttled
or failed query is reported as such and never as "no hits".
"""

import json
import os
import re
import subprocess
import tempfile
import urllib.parse

ALLOWLIST = ("urlquery.net", "web.archive.org", "arquivo.pt", "commoncrawl.org")
URLQUERY_SEARCH = "https://urlquery.net/api/v1/search"
CDX_SEARCH = "https://web.archive.org/cdx/search/cdx"
ARQUIVO_CDX = "https://arquivo.pt/wayback/cdx"
INDEX_SOURCES = ("urlquery", "cdx", "arquivo")
NONCE_BATCH_SIZE = 6


def host_allowed(url, allowed_hosts=None):
    host = (urllib.parse.urlsplit(url).hostname or "").lower()
    if not host:
        return False
    targets = allowed_hosts if allowed_hosts is not None else ALLOWLIST
    return any(host == a or host.endswith("." + a) for a in targets)


def _split_status(stdout):
    m = re.search(r"(\d{3})\s*$", stdout or "")
    if not m:
        return 0, stdout or ""
    return int(m.group(1)), stdout[:m.start()].rstrip()


def curl_get(url, user_agent, params=None, allowed_hosts=None):
    """Run one GET. Returns (http_status, headers_text, body_bytes)."""
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    if not host_allowed(url, allowed_hosts):
        raise ValueError("host not allowlisted: %s" % url)
    fd, body_path = tempfile.mkstemp(prefix="sf-", suffix=".body")
    os.close(fd)
    try:
        cmd = ["curl", "-s", "-D", "-", "-o", body_path, "-w", "%{http_code}",
               "--max-time", "60", "-A", user_agent, url]
        try:
            run = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        except (OSError, subprocess.TimeoutExpired):
            return 0, "", b""
        status, headers = _split_status(run.stdout)
        try:
            with open(body_path, "rb") as handle:
                body = handle.read()
        except OSError:
            body = b""
        return status, headers, body
    finally:
        try:
            os.remove(body_path)
        except OSError:
            pass


def _retry_after(headers):
    m = re.search(r"(?im)^retry-after:\s*(\d+)", headers or "")
    return int(m.group(1)) if m else None


def _is_hostname_term(term):
    return "." in term and not re.search(r"[=\s/]", term)


class IndexSources:
    """Runs index queries with backoff. `wait(seconds)` returns True to abort."""

    def __init__(self, user_agent, delay, limit, wait, getter=curl_get, allowed_hosts=None):
        self.user_agent = user_agent
        self.delay = delay
        self.limit = limit
        self.wait = wait
        self.getter = getter
        self.allowed_hosts = allowed_hosts

    def queries_for(self, source, terms, cursor=None):
        """Build the query list for one source. No network happens here."""
        if isinstance(source, dict):
            kind = source.get("kind", "cdx")
            endpoint = source.get("endpoint", CDX_SEARCH)
            cfg = source.get("config") or {}
            field = cfg.get("filter_field", "urlkey" if "web.archive.org" in endpoint else "original")
            nonce_prefix = cfg.get("nonce_prefix", "r.jina.ai/http*")
            source_id = str(source.get("id", source.get("name", kind)))
        else:
            kind = source
            endpoint = CDX_SEARCH if source == "cdx" else (ARQUIVO_CDX if source == "arquivo" else URLQUERY_SEARCH)
            field = "urlkey" if source == "cdx" else "original"
            nonce_prefix = "r.jina.ai/http*"
            source_id = source

        since = self._since(kind, cursor)
        queries = []
        if kind == "urlquery":
            for term in terms:
                params = {"q": term, "format": "json"}
                params.update(since)
                queries.append({"id": "uq:" + term, "label": term, "terms": [term],
                                "url": endpoint, "params": params})
            return queries

        for term in terms:
            if _is_hostname_term(term):
                params = {"url": term + "/*", "matchType": "prefix",
                          "output": "json", "limit": self.limit}
                params.update(since)
                queries.append({"id": "%s:host:%s" % (source_id, term), "label": term,
                                "terms": [term], "url": endpoint, "params": params})
        loose = [t for t in terms if not _is_hostname_term(t)]
        for i in range(0, len(loose), NONCE_BATCH_SIZE):
            batch = loose[i:i + NONCE_BATCH_SIZE]
            alt = "|".join(re.escape(t) for t in batch)
            params = {"url": nonce_prefix, "matchType": "prefix",
                      "output": "json", "limit": self.limit,
                      "filter": "%s:.*(%s).*" % (field, alt)}
            params.update(since)
            queries.append({"id": "%s:nonce:%s" % (source_id, "|".join(batch)),
                            "label": "nonce-batch", "terms": batch,
                            "url": endpoint, "params": params})
        return queries

    def candidate_query(self, url, source=None):
        """Exact-match index check for one predicted URL. Never fetches it."""
        if isinstance(source, dict):
            endpoint = source.get("endpoint", CDX_SEARCH)
        elif source == "arquivo":
            endpoint = ARQUIVO_CDX
        else:
            endpoint = CDX_SEARCH
        params = {"url": url, "matchType": "exact", "output": "json",
                  "limit": 5}
        return {"id": "cand:" + url, "label": url, "terms": [url],
                "url": endpoint, "params": params}

    @staticmethod
    def _since(kind, cursor):
        if not cursor:
            return {}
        day = cursor[:10]
        if not re.match(r"\d{4}-\d{2}-\d{2}$", day):
            return {}
        if kind == "urlquery":
            return {"date": "[%s TO *]" % day}
        return {"from": day.replace("-", "") + "000000"}

    def run(self, source, query):
        """Run one query. Returns (outcome, http_status, hits)."""
        outcome, status, data = self._get_json(query)
        hits = []
        if outcome != "ok":
            return outcome, status, hits
        kind = source.get("kind") if isinstance(source, dict) else source
        if kind == "urlquery":
            for row in data if isinstance(data, list) else []:
                if isinstance(row, dict):
                    url = row.get("url") or row.get("report_url") or ""
                    hits.append({"url": url, "title": query["label"],
                                 "excerpt": json.dumps(row, sort_keys=True)[:500]})
        elif isinstance(data, list) and len(data) >= 2:
            header = data[0]
            for item in data[1:]:
                rec = dict(zip(header, item)) if isinstance(item, list) else {}
                hits.append({
                    "url": rec.get("original", ""), "title": query["label"],
                    "excerpt": "timestamp=%s status=%s digest=%s" % (
                        rec.get("timestamp"), rec.get("statuscode"),
                        rec.get("digest", ""))})
        return outcome, status, [h for h in hits if h["url"]]

    def _get_json(self, query):
        attempts = 3
        for attempt in range(attempts):
            if self.wait(0):
                return "aborted", 0, None
            status, headers, body = self.getter(
                query["url"], self.user_agent, query["params"])
            if self.wait(self.delay):
                return "aborted", status, None
            if status == 200:
                try:
                    return "ok", status, json.loads(
                        body.decode("utf-8", "replace") or "null")
                except ValueError:
                    return "error", status, None
            if status in (429, 403):
                if attempt < attempts - 1:
                    pause = _retry_after(headers)
                    if pause is None:
                        pause = min(120.0, max(self.delay, 5.0) * (2 ** attempt))
                    if self.wait(pause):
                        return "aborted", status, None
                    continue
                return "throttled", status, None
            if 500 <= status <= 599 and attempt == 0:
                continue
            return "error", status, None
        return "throttled", 0, None
