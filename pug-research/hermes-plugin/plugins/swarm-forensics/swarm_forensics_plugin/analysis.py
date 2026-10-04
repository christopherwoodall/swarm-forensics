"""Deterministic corpus and TTP analysis for observed traces.

Normalizes URLs, extracts relays, detects nonces, and grades findings.
Distinguishes verified traces from inferred hypotheses.
"""

import re
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qsl, unquote, urlsplit, urlunsplit

from .safety import redact_text, redact_url

RELAY_HOSTS = {
    "jqp.vercel.app": "query",
    "allorigins.hexlet.app": "query",
    "r.jina.ai": "path",
    "da.gd": "path",
}

NONCE_PATTERNS = [
    ("zz_oai", re.compile(r"\bzz=oai\d+\b")),
    ("zzbulk", re.compile(r"\bzzbulk=[0-9A-Za-z]+\b")),
    ("prepnonce", re.compile(r"\bprepnonce=[0-9a-fA-F]+\b")),
    ("fresh_x", re.compile(r"\bfresh=x\d+\.\d+\b")),
]

TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "fbclid", "gclid", "ref", "source",
}


def normalize_url(url: str) -> str:
    """Normalize a URL for exact and domain comparison."""
    if not url:
        return ""
    try:
        parts = urlsplit(str(url).strip())
    except ValueError:
        return ""
    scheme = (parts.scheme or "http").lower()
    netloc = (parts.netloc or "").lower().rstrip(".")
    path = parts.path or "/"
    if not path.startswith("/"):
        path = "/" + path
    pairs = [
        (k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
        if k.lower() not in TRACKING_PARAMS
    ]
    pairs.sort(key=lambda item: item[0])
    query = "&".join(f"{k}={v}" if v else k for k, v in pairs)
    return urlunsplit((scheme, netloc, path, query, ""))


def parse_relay(url: str) -> Dict[str, Any]:
    """Extract destination URL from nested relay wrappers."""
    norm = normalize_url(url)
    parts = urlsplit(norm)
    host = (parts.hostname or "").lower()
    style = RELAY_HOSTS.get(host)
    if not style:
        return {"is_relay": False, "relay_host": None, "target_url": norm}

    target = None
    if style == "query":
        for k, v in parse_qsl(parts.query):
            if k.lower() in ("url", "src", "target") and v:
                target = unquote(v)
                break
    elif style == "path":
        raw_path = parts.path.lstrip("/")
        if raw_path.startswith("http://") or raw_path.startswith("https://"):
            target = raw_path

    if target:
        sub_relay = parse_relay(target)
        final_target = sub_relay.get("target_url") or target
        return {
            "is_relay": True,
            "relay_host": host,
            "intermediate_url": target,
            "target_url": final_target,
        }
    return {"is_relay": True, "relay_host": host, "target_url": norm}


def classify_archive_url(url: str) -> str:
    """Classify archive URLs as create, read, index, or non-archive."""
    norm = normalize_url(url).lower()
    if "web.archive.org/save/" in norm:
        return "archive_create"
    if "/cdx/search" in norm or "wayback/cdx" in norm:
        return "archive_index"
    if "web.archive.org/web/" in norm or "arquivo.pt/wayback/" in norm:
        return "archive_read"
    return "direct_web"


def extract_nonces(text: str) -> List[Dict[str, str]]:
    """Extract nonces and request grammar shapes from text."""
    results = []
    text_str = str(text or "")
    for name, pattern in NONCE_PATTERNS:
        for match in pattern.finditer(text_str):
            results.append({"name": name, "value": match.group(0)})
    return results


def grade_match(target: str, candidate: str) -> str:
    """Grade match precision between two URLs."""
    t_norm = normalize_url(target)
    c_norm = normalize_url(candidate)
    if t_norm == c_norm:
        return "exact_url"

    t_relay = parse_relay(t_norm)
    c_relay = parse_relay(c_norm)
    t_target = t_relay.get("target_url", t_norm)
    c_target = c_relay.get("target_url", c_norm)
    if t_target == c_target:
        return "target_url"

    t_parts = urlsplit(t_target)
    c_parts = urlsplit(c_target)
    if t_parts.netloc == c_parts.netloc:
        if t_parts.path == c_parts.path:
            return "domain_path"
        return "target_host"

    if t_relay.get("is_relay") and c_relay.get("is_relay"):
        if t_relay.get("relay_host") == c_relay.get("relay_host"):
            return "relay_service"

    return "no_match"


def analyze_corpus(
    observations: List[Dict[str, Any]],
    evidence: List[Dict[str, Any]],
    urls: List[Dict[str, Any]],
    query: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute deterministic TTP analysis across observed corpus traces."""
    classified_urls = []
    observed_relays = []
    detected_nonces = []
    exact_matches = []
    domain_matches = []

    q_norm = normalize_url(query) if query else ""

    all_url_strings = set()
    for row in observations or []:
        u = row.get("query_or_url") or ""
        if u.startswith("http"):
            all_url_strings.add(u)
    for row in evidence or []:
        u = row.get("url") or ""
        if u.startswith("http"):
            all_url_strings.add(u)
    for row in urls or []:
        u = row.get("url") or ""
        if u.startswith("http"):
            all_url_strings.add(u)

    for raw_u in sorted(all_url_strings):
        norm = normalize_url(raw_u)
        relay_info = parse_relay(norm)
        archive_kind = classify_archive_url(norm)
        nonces = extract_nonces(norm)

        item = {
            "url": redact_url(norm),
            "archive_kind": archive_kind,
            "relay": relay_info,
            "nonces": nonces,
            "status": "verified",
        }
        classified_urls.append(item)

        if relay_info.get("is_relay"):
            observed_relays.append({
                "relay_host": relay_info.get("relay_host"),
                "target_url": redact_url(relay_info.get("target_url") or ""),
            })

        for n in nonces:
            detected_nonces.append(n)

        if q_norm:
            grade = grade_match(q_norm, norm)
            if grade == "exact_url":
                exact_matches.append(norm)
            elif grade in ("domain_path", "target_host"):
                domain_matches.append(norm)

    absence_report = None
    if query:
        if not exact_matches and not domain_matches:
            absence_report = {
                "query": redact_text(query),
                "status": "ABSENT_IN_SCOPE",
                "scope_note": "Term is absent within recorded search scope, not globally absent.",
            }

    return {
        "ok": True,
        "total_corpus_urls": len(classified_urls),
        "classified_urls": classified_urls[:100],
        "observed_relays": observed_relays[:50],
        "detected_nonces": detected_nonces[:50],
        "exact_matches": exact_matches,
        "domain_matches": domain_matches,
        "absence_report": absence_report,
    }
