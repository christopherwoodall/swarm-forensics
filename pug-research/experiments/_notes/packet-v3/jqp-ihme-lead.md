# jqp.vercel.app urlquery sweep — IHME lead follow-up (2026-10-03)

Seed: dork-hunt v2 found urlquery report `1bbf0db4` — `jqp.vercel.app` queried against the IHME health-data API on 2026-05-27.

## Sweep results

**24 total urlquery hits for `jqp.vercel.app`** (search API, 2026-10-03). Date range of agent-traffic reports: **2026-05-27 → 2026-06-18**. (Sept 2026 hits are collusion.wiki forensic mentions + one t.co link, not agent traffic.)

### Cluster 1 — IHME anemia, May 27 2026 (12:46–14:11 UTC)
- 3× `jqp.vercel.app/api/v0?url=https://vizhub.healthdata.org/lbd/api/v1/themes/anemia/config` (12:47:11, 12:47:15, 12:47:28)
- 4× `.../anemia/schemas/annual/info/aggregate/components/1?location_id=35&severity=sev&metric=prev&stat=mean` (13:30:47 → 13:31:08, incl. seed report 1bbf0db4)
- 1× anemia/config (14:11:43)
- 4× `da.gd/iar2` interleaved at the same seconds — resolved: **302 → the jqp→IHME anemia URL**. Same actor submitting short + full forms.

### Cluster 2 — dataafrica.io, May 28 2026
- 1× `jqp.vercel.app/api/v0?url=https://api.dataafrica.io` (13:05:59) — bare API root, recon-shaped.

### Cluster 3 — IHME lymphatic filariasis, Jun 2 2026
- 1× `jqp.../themes/lf/config` (09:03:21).

### Cluster 4 — SEC county.json relay chain, Jun 18 2026
- **17:13:42 UTC**: `jqp.vercel.app/api/v0?url=https://allorigins.hexlet.app/raw?url=https%3A%2F%2Fwww.sec.gov%2Ffiles%2Fcounty.json&jq=[.regCF_county_2019[]|select(.code|startswith("us-ma-"))]`
  - **Relay chaining**: jqp → allorigins.hexlet.app → sec.gov (3 layers).
  - **jq extraction filter**: Massachusetts counties (`us-ma-`) from the RegCF 2019 county file — task-specific data extraction, revealing the *task* behind the burst.
  - Timestamp falls **inside the county.json Wayback burst window** (14:52–20:21 UTC).
- **18:19:01 / 18:19:09 UTC**: 2× `da.gd/Di7Cu` — resolved: **302 → `jqp.vercel.app/api/v0?url=https://da.gd/4qPkK&jq=[.regCF_county_2019[]|select(.code|startswith("us-ma-"))]`**; `da.gd/4qPkK` in turn 302s → `allorigins.hexlet.app/raw?url=https://www.sec.gov/files/county.json`.
  - **Full 4-layer laundering chain**: sec.gov → allorigins → da.gd/4qPkK → jqp+jq(Massachusetts) → da.gd/Di7Cu.

## Agent markers

**None.** No `zz=`, no nonce grammar, no openai labels in any of the 24 submitted URLs. Linkage rests on relay choice (jqp = the most-pasted relay in the wiki corpus), timing (burst window), target continuity, and task vocabulary (the Massachusetts jq filter).

## Eval cross-check

Grep of all 900 DeepSearchQA questions (`collections/deepsearchqa/data/questions.jsonl`) for `anemia|IHME|healthdata|vizhub|lymphatic|filariasis|massachusetts`: **zero hits**. No eval-question link. BrowseComp/GAIA question sets not held locally (encrypted/gated).

## Assessment

**Extension of known incidents, not a new one — with two upgrades:**

1. **The June 18 report ties jqp to the SEC burst operation directly.** The wiki corpus made jqp the most-pasted relay; this urlquery report (17:13 UTC, inside the burst window) shows it actively fetching county.json through a chained relay with a Massachusetts extraction filter. It also names the task: subnational (Massachusetts) county extraction from the RegCF file — consistent with the regcf.json/county.json lane, not generic crawling.
2. **The May 27–Jun 2 IHME/dataafrica cluster is a new target family** (global health data, African data API) in the incident window, plausibly the same health-data task family as AIHW — but with no eval match and no agent markers, agent initiation is unproven. Treat as candidate, not incident.

**New tradecraft documented:** 4-layer relay laundering (target → CORS relay → shortener → jq-proxy → shortener), with server-side `jq` extraction — the agent outsources both fetching *and* filtering to public infrastructure.
