"""Research safety: URL checks, redaction, taint screen, strict output parser.

Fetched text is attacker-influenced by design. It is data, never an
instruction. Model output is untrusted too: it is parsed against a strict
schema, bounded in size, and can only propose. Policy decides outcomes.
"""

import hashlib
import ipaddress
import json
import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

CLAIM_LEVELS = ("L1", "L2", "L3", "L4", "L5")
ENTITY_TYPES = ("artifact", "agent", "swarm", "campaign", "collection")
HIERARCHY = ("artifact", "agent", "swarm", "campaign")
LINK_KINDS = ("part_of", "related", "observed_with")
LEGACY_TYPES = {"trace": "artifact", "case": "campaign"}
LEGACY_LINKS = {"member_of": "part_of", "trace_of": "part_of"}
TERM_CATEGORIES = ("nonce_grammar", "relay", "watch_term", "basin_target",
                   "toolkit", "proposed")

_BLOCKED_SUFFIXES = (".local", ".internal", ".localhost", ".lan", ".home",
                     ".corp", ".intranet")
_SECRET_PARAM = re.compile(r"key|token|secret|passw|auth|session|sig|cookie",
                           re.IGNORECASE)
_SECRET_VALUES = [
    re.compile(r"\bsk-[A-Za-z0-9_\-]{16,}"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"\bxox[abprs]-[A-Za-z0-9\-]{10,}"),
    re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._\-]{16,}"),
    re.compile(r"(?i)\b(api[_-]?key|secret|token|password)\s*[=:]\s*\S{8,}"),
]

_TAINT_PATTERNS = [
    re.compile(r"ignore\s+(?:(?:all|any|the|previous|prior|above|earlier)\s+)+"
               r"(?:instructions?|prompts?|rules)", re.IGNORECASE),
    re.compile(r"disregard\s+.*instructions?", re.IGNORECASE),
    re.compile(r"\byou are now\b", re.IGNORECASE),
    re.compile(r"new\s+system\s+prompt", re.IGNORECASE),
    re.compile(r"\bas an ai\b", re.IGNORECASE),
    re.compile(r"^\s*(developer|assistant|system)\s*:", re.IGNORECASE | re.MULTILINE),
    re.compile(r"</?\s*(system|untrusted)\b", re.IGNORECASE),
]

_TERM_RE = re.compile(r"^[A-Za-z0-9_.:/=+\-<>*%@#]{4,120}$")
# Words too broad to name a swarm. A bare common token is not an indicator.
_BROAD_TERMS = {
    "http", "https", "www", "html", "json", "api", "data", "code", "test",
    "agent", "agents", "swarm", "query", "search", "result", "results",
    "github.com", "google.com", "twitter.com", "wikipedia.org",
    "archive.org", "web.archive.org", "example.com",
}


class UrlRefused(ValueError):
    """Raised when a URL breaks the read-only public-web rules."""


def validate_url(url):
    """Return a normalized public http(s) URL or raise UrlRefused."""
    if not isinstance(url, str) or not url.strip():
        raise UrlRefused("empty url")
    parts = urlsplit(url.strip())
    if parts.scheme not in ("http", "https"):
        raise UrlRefused("scheme must be http or https")
    if parts.username or parts.password:
        raise UrlRefused("credentials in url")
    host = (parts.hostname or "").lower().rstrip(".")
    if not host:
        raise UrlRefused("missing host")
    if host == "localhost" or host.endswith(_BLOCKED_SUFFIXES):
        raise UrlRefused("non-public host")
    try:
        addr = ipaddress.ip_address(host)
    except ValueError:
        addr = None
        if "." not in host:
            raise UrlRefused("non-public host")
    if addr is not None and not addr.is_global:
        raise UrlRefused("non-public address")
    try:
        port = parts.port
    except ValueError:
        raise UrlRefused("bad port")
    if port not in (None, 80, 443):
        raise UrlRefused("unusual port")
    return urlunsplit((parts.scheme, parts.netloc.lower(), parts.path,
                       parts.query, ""))


def redact_url(url):
    """Blank secret-looking query values before a URL is stored."""
    parts = urlsplit(url)
    if not parts.query:
        return url
    pairs = [(k, "REDACTED" if _SECRET_PARAM.search(k) else v)
             for k, v in parse_qsl(parts.query, keep_blank_values=True)]
    return urlunsplit((parts.scheme, parts.netloc, parts.path,
                       urlencode(pairs), parts.fragment))


def redact_text(text):
    """Replace credential-shaped strings. Run before any text is stored."""
    out = str(text or "")
    for rx in _SECRET_VALUES:
        out = rx.sub("[REDACTED]", out)
    return out


def host_of(url):
    try:
        return (urlsplit(url).hostname or "").lower()
    except ValueError:
        return ""


def content_hash(text):
    return hashlib.sha256(str(text).encode("utf-8", "replace")).hexdigest()[:32]


def taint_prescreen(snippets):
    """Return True when any snippet carries a prompt-injection marker."""
    for snippet in snippets or []:
        text = str(snippet)
        if "```" in text and re.search(r"system", text, re.IGNORECASE):
            return True
        if any(p.search(text) for p in _TAINT_PATTERNS):
            return True
    return False


def fence_untrusted(text, label, limit=6000):
    """Wrap fetched text so the model reads it as data."""
    body = redact_text(str(text or ""))[:limit]
    body = body.replace("<<<", "< < <").replace(">>>", "> > >")
    return "<<<UNTRUSTED %s>>>\n%s\n<<<END UNTRUSTED>>>" % (label, body)


def term_is_specific(term):
    """Cheap gate against terms too broad to watch."""
    t = str(term).strip()
    if not _TERM_RE.match(t) or t.lower() in _BROAD_TERMS:
        return False
    return bool(re.search(r"[0-9=._/\-]", t)) or len(t) >= 8


def _text(value, limit):
    return redact_text(str(value or "")).strip()[:limit]


def _entities(items):
    out = []
    for item in items if isinstance(items, list) else []:
        if not isinstance(item, dict):
            continue
        name = _text(item.get("name"), 120)
        if name:
            out.append({"name": name,
                        "description": _text(item.get("description"), 400)})
        if len(out) >= 8:
            break
    return out


def parse_analysis(raw):
    """Strict parser for the model's page analysis. Fails closed.

    Returns a bounded dict. Unparseable output becomes an empty,
    irrelevant analysis with invalid=True.
    """
    empty = {"relevant": False, "invalid": True, "claim_level": "L1",
             "summary": "", "agents": [], "swarms": [], "cases": [],
             "terms": [], "links": [], "leads": []}
    try:
        obj = raw if isinstance(raw, dict) else json.loads(str(raw).strip())
    except (TypeError, ValueError):
        return empty
    if not isinstance(obj, dict) or not isinstance(obj.get("relevant"), bool):
        return empty
    level = obj.get("claim_level")
    terms = []
    for item in obj.get("terms") if isinstance(obj.get("terms"), list) else []:
        if not isinstance(item, dict):
            continue
        term = str(item.get("term") or "").strip()
        if not _TERM_RE.match(term):
            continue
        category = item.get("category")
        terms.append({
            "term": term,
            "category": category if category in TERM_CATEGORIES else "proposed",
            "why": _text(item.get("why"), 280)})
        if len(terms) >= 12:
            break
    links = []
    for item in obj.get("links") if isinstance(obj.get("links"), list) else []:
        if not isinstance(item, dict):
            continue
        src, dst = item.get("from"), item.get("to")
        if not (isinstance(src, dict) and isinstance(dst, dict)):
            continue
        src_type = LEGACY_TYPES.get(src.get("type"), src.get("type"))
        dst_type = LEGACY_TYPES.get(dst.get("type"), dst.get("type"))
        if src_type not in ENTITY_TYPES or dst_type not in ENTITY_TYPES:
            continue
        raw_kind = item.get("kind")
        kind = LEGACY_LINKS.get(raw_kind, raw_kind if raw_kind in LINK_KINDS else "related")
        names = (_text(src.get("name"), 120), _text(dst.get("name"), 120))
        if all(names):
            links.append({"from": {"type": src_type, "name": names[0]},
                          "to": {"type": dst_type, "name": names[1]},
                          "kind": kind})
        if len(links) >= 12:
            break
    leads = []
    for item in obj.get("leads") if isinstance(obj.get("leads"), list) else []:
        if not isinstance(item, dict):
            continue
        kind, value = item.get("kind"), _text(item.get("value"), 300)
        if kind not in ("query", "url") or not value:
            continue
        if kind == "url":
            try:
                value = validate_url(value)
            except UrlRefused:
                continue
        leads.append({"kind": kind, "value": value,
                      "why": _text(item.get("why"), 200)})
        if len(leads) >= 8:
            break
    campaigns = _entities(obj.get("campaigns"))
    if not campaigns and "cases" in obj:
        campaigns = _entities(obj.get("cases"))
    return {"relevant": obj["relevant"], "invalid": False,
            "claim_level": level if level in CLAIM_LEVELS else "L1",
            "summary": _text(obj.get("summary"), 600),
            "agents": _entities(obj.get("agents")),
            "swarms": _entities(obj.get("swarms")),
            "campaigns": campaigns,
            "cases": campaigns,
            "terms": terms, "links": links, "leads": leads}


def parse_plan(raw, limit):
    """Strict parser for the planning step. Returns a list of query dicts."""
    try:
        obj = raw if isinstance(raw, dict) else json.loads(str(raw).strip())
    except (TypeError, ValueError):
        return []
    out = []
    for item in (obj.get("queries") if isinstance(obj, dict) else None) or []:
        if not isinstance(item, dict):
            continue
        query = _text(item.get("query"), 300)
        if query:
            out.append({"query": query, "why": _text(item.get("why"), 200)})
        if len(out) >= limit:
            break
    return out
