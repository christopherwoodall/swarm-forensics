"""Normalize public post records without interpreting participant claims."""

import re
from datetime import datetime


class SourceError(ValueError):
    """Reject invalid or out-of-scope public source data."""


def timestamp(value):
    """Require an explicit timezone in a source timestamp."""
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError):
        raise SourceError("invalid source timestamp") from None
    if result.tzinfo is None:
        raise SourceError("source timestamp lacks timezone")
    return result


def normalize(item, did, started_at):
    """Preserve explicit record references and unmodified source text."""
    if not isinstance(item, dict):
        raise SourceError("post record must be an object")
    value = item.get("value", {})
    if (not isinstance(value, dict) or value.get("$type") != "town.delve.feed.post"
            or not isinstance(value.get("text"), str)
            or not isinstance(item.get("cid"), str) or not item["cid"]
            or not isinstance(item.get("uri"), str)
            or not re.fullmatch(re.escape(f"at://{did}/town.delve.feed.post/")
                                + r"[A-Za-z0-9._~:-]{1,512}", item["uri"])):
        raise SourceError("invalid or wrong-account post record")
    timestamp(value.get("createdAt"))
    reply = value.get("reply") or {}
    if (not isinstance(reply, dict)
            or any(not isinstance(reply.get(key, {}), dict) for key in ("parent", "root"))
            or not isinstance(value.get("facets", []), list)
            or any(not isinstance(facet, dict) or not isinstance(facet.get("features", []), list)
                   for facet in value.get("facets", []))):
        raise SourceError("invalid record references")
    features = [feature for facet in value.get("facets", [])
                for feature in facet.get("features", [])]
    if any(not isinstance(feature, dict)
           or not isinstance(feature.get("$type", ""), str)
           or any(key in feature and not isinstance(feature[key], str) for key in ("did", "uri"))
           for feature in features):
        raise SourceError("invalid rich-text feature")
    if any("uri" in reply.get(key, {}) and not isinstance(reply[key]["uri"], str)
           for key in ("parent", "root")):
        raise SourceError("invalid reply reference")
    quotes = set()
    embedded_links = set()
    pending = [value.get("embed", {})]
    while pending:
        node = pending.pop()
        if not isinstance(node, dict):
            continue
        uri = node.get("uri")
        if isinstance(uri, str):
            if uri.startswith("at://"):
                quotes.add(uri)
            elif uri.startswith(("https://", "http://")):
                embedded_links.add(uri)
        pending.extend(child for child in node.values() if isinstance(child, dict))
    plain_links = set(re.findall(r"https?://[^\s<>\[\]()]+", value["text"]))
    return {
        "uri": item["uri"], "cid": item["cid"], "actor_did": did,
        "created_at": value["createdAt"], "text": value["text"],
        "langs": value.get("langs", []),
        "reply_parent": reply.get("parent", {}).get("uri"),
        "reply_root": reply.get("root", {}).get("uri"),
        "mentions": sorted({f["did"] for f in features
                            if f.get("$type", "").endswith("#mention") and "did" in f}),
        "links": sorted({f["uri"] for f in features
                         if f.get("$type", "").endswith("#link") and "uri" in f}
                        | plain_links | embedded_links),
        "quote_uris": sorted(quotes),
        "collected_at": started_at.isoformat(),
    }
