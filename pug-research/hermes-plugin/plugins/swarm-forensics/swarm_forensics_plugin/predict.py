"""Candidate URL prediction from observed request grammar.

Candidates are hypotheses about infrastructure not yet seen. They are
checked against public indexes only. They are never fetched. A candidate
with no hit is stored as a negative data point.
"""

import re
from urllib.parse import quote

# Observed URL patterns. Braces mark observed slots.
OBSERVED_URL_PATTERNS = (
    "https://civilrightsdata.ed.gov/api/v1.0/getstateestimation"
    "?Measure_Id={int}&State_Id={int}&survey_Year_Key={int}",
    "https://civilrightsdata.ed.gov/api/v1.0/getstateestimation"
    "?Measure_Id={int}&State_Id={int}&survey_Year_Key={int}&zz={text}",
    "https://civilrightsdata.ed.gov/api/v1.0/getstateestimation"
    "?Measure_Id={int}&State_Id={int}&survey_Year_Key={int}&zzbulk={text}",
    "https://civilrightsdata.ed.gov/api/v1.0/getstateestimation"
    "?Measure_Id={int}&State_Id={int}&prepnonce={text}&survey_Year_Key={int}",
    "https://jqp.vercel.app/api/v0?jq={long}&url={url}",
    "https://www.sec.gov/files/county.json",
    "https://api.datausa.io/tesseract/data.jsonrecords"
    "?cube={text}&drilldowns={text}&include={long}&measures={text}",
)

NONCE_PROBES = {
    "zz": ["oai17816846804506724"],
    "zzbulk": ["1781639035965977052"],
    "prepnonce": ["a94a8fe5ccb19ba61"],
}
JQ_PROBES = [".code", ".regCF_county_2019", 'select(test("us-ma-"))']
EXTRA_TARGETS = ["https://www.sec.gov/files/regcf.json"]
# Relay host -> (style, prefix). Unknown relays are skipped, never guessed.
RELAYS = {
    "jqp.vercel.app": ("query", "https://jqp.vercel.app/api/v0"),
    "allorigins.hexlet.app": ("query", "https://allorigins.hexlet.app/raw"),
    "r.jina.ai": ("path", "https://r.jina.ai/"),
}


def _pattern_regex(pattern):
    out, i = [], 0
    while i < len(pattern):
        if pattern[i] == "{":
            j = pattern.index("}", i)
            out.append("[^/?&#]+" if i and pattern[i - 1] == "/" else "[^&#]*")
            i = j + 1
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    return re.compile("^" + "".join(out) + "$")


_OBSERVED_RES = [_pattern_regex(p) for p in OBSERVED_URL_PATTERNS]


def matches_observed(url, patterns=None):
    if patterns is None:
        return any(rx.match(url) for rx in _OBSERVED_RES)
    res = [_pattern_regex(p) for p in patterns]
    return any(rx.match(url) for rx in res)


def _targets(patterns=None, extra=None):
    patterns = patterns if patterns is not None else OBSERVED_URL_PATTERNS
    extra = extra if extra is not None else EXTRA_TARGETS
    out = []
    for pattern in patterns:
        base = pattern.split("?", 1)[0]
        if "jqp.vercel.app" not in base and base not in out:
            out.append(base)
    return out + [t for t in extra if t not in out]


def _wrap(relay_cfg, inner, jq=None):
    style, prefix = relay_cfg
    if style == "query":
        query = "url=" + quote(inner, safe="")
        if jq is not None:
            query = "jq=" + quote(jq, safe="") + "&" + query
        return prefix + "?" + query
    return prefix + inner


def _fill(pattern, param, value):
    def repl(m):
        name = m.group(2)
        return "%s%s=%s" % (m.group(1), name,
                            value if name == param else
                            ("1" if m.group(3) == "int" else "x"))
    return re.sub(r"([?&])([^=&#?]+)=\{([^}]*)\}", repl, pattern)


def generate_candidates(bundle=None):
    """Return a deduplicated list of (url, template) pairs.

    If bundle is provided, uses enabled items from the registry bundle:
    {"patterns": [...], "relays": {host: (style, prefix)}, "nonce_probes": {param: [probes]},
     "jq_probes": [...], "targets": [...]}
    """
    if bundle is not None:
        patterns = bundle.get("patterns", [])
        relays = bundle.get("relays", {})
        nonce_probes = bundle.get("nonce_probes", {})
        jq_probes = bundle.get("jq_probes", [])
        targets = bundle.get("targets", [])
    else:
        patterns = list(OBSERVED_URL_PATTERNS)
        relays = dict(RELAYS)
        nonce_probes = dict(NONCE_PROBES)
        jq_probes = list(JQ_PROBES)
        targets = list(EXTRA_TARGETS)

    seen, out = set(), []
    target_list = _targets(patterns, targets)

    def emit(template, url):
        # A candidate must match an observed shape. Others are dropped.
        if url not in seen and matches_observed(url, patterns):
            seen.add(url)
            out.append((url, template))

    for relay_host, relay_cfg in relays.items():
        for target in target_list:
            for jq in jq_probes:
                emit("relay_wrap", _wrap(relay_cfg, target, jq))
            for param, probes in nonce_probes.items():
                for probe in probes:
                    inner = "%s%s%s=%s" % (target, "&" if "?" in target else "?",
                                           param, probe)
                    for jq in jq_probes:
                        emit("relay_nonce", _wrap(relay_cfg, inner, jq))
    for pattern in patterns:
        names = re.findall(r"[?&]([^=&#?]+)=\{[^}]*\}", pattern)
        for param, probes in nonce_probes.items():
            if param in names:
                for probe in probes:
                    emit("nonce_direct", _fill(pattern, param, probe))
    return out
