"""Offline indicator extraction. Pure regex, no network, no model."""

import re
from urllib.parse import urlparse

INDICATOR_KINDS = ("url", "domain", "nonce", "relay", "hash")

RELAY_HOSTS = ("jqp.vercel.app", "allorigins.hexlet.app", "r.jina.ai", "da.gd")

_URL_RE = re.compile(r"https?://[^\s<>\"'`]+")
_NONCE_RES = [
    re.compile(r"\bzz=oai\d+"),
    re.compile(r"\bzzbulk=[0-9A-Za-z]{4,}"),
    re.compile(r"\bprepnonce=[0-9A-Fa-f]{4,}"),
    re.compile(r"\bfresh=x\d+\.\d+"),
]
_HASH_RES = [re.compile(r"\b[0-9a-fA-F]{%d}\b" % n) for n in (64, 40, 32)]
_WIKILINK_RE = re.compile(r"\[\[([^\[\]\n|#]{1,120})(?:\|[^\]\n]*)?\]\]")


def _clean_url(url):
    return url.rstrip(".,;:!?)]}'\"")


def extract_indicators(text):
    """Return unique (kind, value) pairs in order of first appearance."""
    text = text or ""
    found = []
    for m in _URL_RE.finditer(text):
        url = _clean_url(m.group(0))
        if not url:
            continue
        found.append((m.start(), "url", url))
        try:
            host = urlparse(url).hostname
        except ValueError:
            host = None
        if host:
            found.append((m.start(), "domain", host.lower()))
    for rx in _NONCE_RES:
        for m in rx.finditer(text):
            found.append((m.start(), "nonce", m.group(0)))
    for host in RELAY_HOSTS:
        pos = text.find(host)
        while pos >= 0:
            found.append((pos, "relay", host))
            pos = text.find(host, pos + len(host))
    for rx in _HASH_RES:
        for m in rx.finditer(text):
            found.append((m.start(), "hash", m.group(0).lower()))
    found.sort(key=lambda item: item[0])
    seen, out = set(), []
    for _, kind, value in found:
        if (kind, value) not in seen:
            seen.add((kind, value))
            out.append((kind, value))
    return out


def wikilinks(markdown):
    """Return the unique [[Name]] targets in a note, in order."""
    out = []
    for m in _WIKILINK_RE.finditer(markdown or ""):
        name = m.group(1).strip()
        if name and name not in out:
            out.append(name)
    return out
