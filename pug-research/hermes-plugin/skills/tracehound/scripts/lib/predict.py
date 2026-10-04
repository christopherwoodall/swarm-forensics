"""Pattern-based candidate URL generation.

Fills request-grammar templates with observed slots (relay hosts, nonce
shapes, basin targets, param grammars) to produce candidate URLs the
scanner sweeps for. Predictions are hypotheses: a candidate with no hit
is a recorded negative, not a silent drop.

Slot inventories are read programmatically from
pug-research/grammar-network/request_grammar.json. That file carries
node masses and nesting chains, not literal URLs; the observed-URL
validation corpus is the lane's published observed URL patterns
(grammar-network/REPORT.md, verbatim below). Every template MUST
produce at least one instance validated against that corpus before it
enters the candidate pool. Templates with zero validation hits are
dropped and logged. No network calls are made here.
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

from config import state_path

GRAMMAR_PATH = (Path(__file__).resolve().parents[5]
                / "grammar-network" / "request_grammar.json")

# Observed URL patterns, verbatim from grammar-network/REPORT.md (the
# grammar lane's published observations). Braces mark observed slots.
_OBSERVED_URL_PATTERNS = (
    "https://civilrightsdata.ed.gov/api/v1.0/getstateestimation"
    "?Measure_Id={int}&State_Id={int}&survey_Year_Key={int}",
    "https://civilrightsdata.ed.gov/api/v1.0/getstateestimation"
    "?Measure_Id={int}&State_Id={int}&survey_Year_Key={int}&zz={text}",
    "https://civilrightsdata.ed.gov/api/v1.0/getstateestimation"
    "?Measure_Id={int}&State_Id={int}&survey_Year_Key={int}&zzbulk={text}",
    "https://civilrightsdata.ed.gov/api/v1.0/getstateestimation"
    "?Measure_Id={int}&State_Id={int}&prepnonce={text}&survey_Year_Key={int}",
    "https://civilrightsdata.ed.gov/api/v1.0/getstateestimation"
    "?Measure_Id={text}&State_Id={int}&survey_Year_Key={int}&zzbulk={text}",
    "https://jqp.vercel.app/api/v0?jq={long}&url={url}",
    "https://www.sec.gov/files/county.json",
    "https://api.datausa.io/tesseract/data.jsonrecords"
    "?cube={text}&drilldowns={text}&include={long}&measures={text}",
    "https://www.kansasmemory.gov/item/{id}",
    "https://wikiservice.at/dse/wiki.cgi"
    "?action={text}&dirq={int}&id={text}&lang={int}",
    "https://reportcard.msde.maryland.gov/datadownloads/filedownload/{id}",
)

# Nonce probes: verbatim examples from grammar-network/PATTERNS.md.
_NONCE_PROBES = {
    "zz": ["oai17816846804506724"],        # 747x zz_oai
    "zzbulk": ["1781639035965977052"],     # hex16 in zz
    "prepnonce": ["a94a8fe5ccb19ba61"],    # hex16 shape
}

# jq probes: verbatim fragments from the grammar lane's jqop nodes.
_JQ_PROBES = [".code", ".regCF_county_2019", 'select(test("us-ma-"))']

# Extra basin targets from the seed list (RULES.md). The validator
# decides whether each survives; unobserved shapes are dropped.
_EXTRA_TARGETS = [
    "https://www.sec.gov/files/regcf.json",
]

# Fallback slot lists, used only when the grammar file is absent.
# A warning is logged; validation still runs against observed URLs.
_FALLBACK = {"relays": ["jqp.vercel.app", "allorigins.hexlet.app",
                        "r.jina.ai"],
             "nonce_params": ["zz", "zzbulk", "prepnonce"],
             "pairs": set()}


def _warn(msg):
    print(f"tracehound predict: WARNING: {msg}", file=sys.stderr)


def _load_grammar():
    try:
        return json.loads(GRAMMAR_PATH.read_text(encoding="utf-8"))
    except OSError as e:
        _warn(f"grammar file unreadable ({e}); using fallback slot lists")
    except json.JSONDecodeError as e:
        _warn(f"grammar file is not valid JSON ({e}); using fallback lists")
    return None


def _slots_from_grammar(g):
    """Derive slot inventories from the grammar JSON. No hand lists."""
    nodes = g["top_nodes_by_type"]
    relays = [h for h, _ in nodes.get("relay", [])]
    params = [p for p, _ in nodes.get("param", [])]
    nonce_params = [p for p in params if p in _NONCE_PROBES]
    pairs = {(a, b) for (a, b), _ in g.get("top_nesting_chains", [])}
    return {"relays": relays, "nonce_params": nonce_params, "pairs": pairs}


def _pattern_to_regex(pattern):
    out = []
    i = 0
    while i < len(pattern):
        if pattern[i] == "{":
            j = pattern.index("}", i)
            prev = pattern[i - 1] if i else ""
            out.append("[^/?&#]+" if prev == "/" else "[^&#]*")
            i = j + 1
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    return re.compile("^" + "".join(out) + "$")


_OBSERVED_RES = [_pattern_to_regex(p) for p in _OBSERVED_URL_PATTERNS]


def _match_observed(url):
    """Return the observed pattern a URL matches, or None."""
    for pat, rx in zip(_OBSERVED_URL_PATTERNS, _OBSERVED_RES):
        if rx.match(url):
            return pat
    return None


def _fill_pattern(pattern, probes):
    """Fill an observed pattern's placeholders with probe values."""
    def repl(m):
        sep, name, shape = m.group(1), m.group(2), m.group(3)
        value = probes.get(name, "1" if shape == "int" else "x")
        return f"{sep}{name}={value}"
    return re.sub(r"([?&])([^=&#?]+)=\{([^}]*)\}", repl, pattern)


def _target_bases():
    """Observed target URL bases (patterns with queries stripped)."""
    bases = []
    for pat in _OBSERVED_URL_PATTERNS:
        base = pat.split("?", 1)[0]
        if "jqp.vercel.app" in base:
            continue  # a relay, not a target
        base = base.replace("{id}", "12345")
        if base not in bases:
            bases.append(base)
    for t in _EXTRA_TARGETS:
        if t not in bases:
            bases.append(t)
    return bases


def _relay_recipe(host):
    """Return (style, prefix) for a relay host, or None when unknown.

    Unknown relay hosts are skipped with a warning: the builder MUST
    NOT guess a relay's URL grammar.
    """
    if host == "jqp.vercel.app":
        return ("query", "https://jqp.vercel.app/api/v0")
    if host == "allorigins.hexlet.app":
        return ("query", "https://allorigins.hexlet.app/raw")
    if host == "r.jina.ai":
        return ("path", "https://r.jina.ai/")
    return None


def _wrap(relay_host, inner_url, jq_probe=None):
    """Wrap an inner URL through a relay. Returns None when unknown."""
    recipe = _relay_recipe(relay_host)
    if recipe is None:
        _warn(f"no URL recipe for relay host {relay_host!r}; skipping")
        return None
    style, prefix = recipe
    if style == "query":
        q = f"url={quote(inner_url, safe='')}"
        if jq_probe is not None:
            q = f"jq={quote(jq_probe, safe='')}&" + q
        return f"{prefix}?{q}"
    return prefix + inner_url


def _with_nonce(target, param, value):
    """Attach a nonce to the TARGET URL's query string. Never the relay's."""
    sep = "&" if "?" in target else "?"
    return f"{target}{sep}{param}={value}"


def _target_host(target):
    m = re.match(r"https?://([^/]+)", target)
    return m.group(1) if m else ""


def _build_instances(slots):
    """Yield (template_name, url, slotinfo) for every template."""
    relays = slots["relays"]
    pairs = slots["pairs"]
    targets = _target_bases()

    def pair_ok(relay_host, target):
        if not pairs:
            return True  # fallback mode: grammar absent
        return (relay_host, _target_host(target)) in pairs

    known_relays = []
    for relay in relays:
        if _relay_recipe(relay) is None:
            _warn(f"no URL recipe for relay host {relay!r}; skipping")
            continue
        known_relays.append(relay)

    # relay_wrap: relay-wrapped basin targets.
    for relay in known_relays:
        for target in targets:
            if not pair_ok(relay, target):
                continue
            for jq in _JQ_PROBES:
                url = _wrap(relay, target, jq_probe=jq)
                yield ("relay_wrap", url,
                       {"relay": relay, "target": target, "jq": jq})

    # relay_nonce: nonce on the TARGET query string, then relay-wrapped.
    # The old form appended the nonce to the relay's query string and
    # broke the relay's own ?url= parameter. This form is well-formed.
    # The jq probe is included: the observed jqp shape carries jq.
    for relay in known_relays:
        for target in targets:
            if not pair_ok(relay, target):
                continue
            for param in slots["nonce_params"]:
                for probe in _NONCE_PROBES[param]:
                    inner = _with_nonce(target, param, probe)
                    for jq in _JQ_PROBES:
                        url = _wrap(relay, inner, jq_probe=jq)
                        yield ("relay_nonce", url,
                               {"relay": relay, "target": target,
                                "p": param, "probe": probe, "jq": jq})

    # nonce_direct: observed URL shapes carrying observed nonce params,
    # with fresh nonce probes. Built from the observed patterns, so the
    # structural match is exact; survival depends on the grammar still
    # containing such patterns.
    for pat in _OBSERVED_URL_PATTERNS:
        pnames = re.findall(r"[?&]([^=&#?]+)=\{[^}]*\}", pat)
        for param in slots["nonce_params"]:
            if param not in pnames:
                continue
            for probe in _NONCE_PROBES[param]:
                url = _fill_pattern(pat, {param: probe})
                yield ("nonce_direct", url,
                       {"p": param, "probe": probe, "pattern": pat})


def _validate(template, url, slotinfo, slots):
    """Return the observed URL pattern when valid, else None.

    Rules: the URL MUST match an observed pattern; relay templates
    MUST use an observed relay->target nesting pair; nonce params
    MUST be observed grammar params.
    """
    pat = _match_observed(url)
    if pat is None:
        return None
    if template in ("relay_wrap", "relay_nonce"):
        pairs = slots["pairs"]
        if pairs and (slotinfo["relay"],
                      _target_host(slotinfo["target"])) not in pairs:
            return None
    if template in ("relay_nonce", "nonce_direct"):
        if slotinfo["p"] not in slots["nonce_params"]:
            return None
    return pat


def generate_candidates(cfg):
    """Write validated candidates to state/candidates/YYYY-MM-DD.jsonl.

    Every template MUST match >= 1 observed URL. Templates with zero
    validation hits are dropped and logged. Returns the count written.
    """
    g = _load_grammar()
    slots = _slots_from_grammar(g) if g is not None else dict(_FALLBACK)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out = state_path(cfg, "candidates", f"{today}.jsonl")
    template_hits = {}
    rows = []
    for template, url, slotinfo in _build_instances(slots):
        pat = _validate(template, url, slotinfo, slots)
        if pat is None:
            continue
        template_hits[template] = template_hits.get(template, 0) + 1
        rows.append({"candidate_url": url, "template": template,
                     "slots": slotinfo, "validated_against": pat,
                     "predicted_for": today, "status": "unprobed"})
    for template in ("relay_wrap", "relay_nonce", "nonce_direct"):
        if template_hits.get(template, 0) == 0:
            _warn(f"template {template!r} had zero validation hits; "
                  "dropped from the candidate pool")
    seen = set()
    n = 0
    with out.open("a", encoding="utf-8") as f:
        for row in rows:
            if row["candidate_url"] in seen:
                continue
            seen.add(row["candidate_url"])
            f.write(json.dumps(row) + "\n")
            n += 1
    return n
