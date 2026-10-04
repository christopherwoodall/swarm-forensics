# Swarm Forensics — Hermes plugin design

A Hermes-agent skill that runs the swarm-forensics hunt methodology on a loop:
scan public sources for agent-trace IOCs, maintain the IOC list, predict
candidate URLs from observed patterns, and watch what other researchers publish.
All intervals configurable. Stdlib only. Read-only public web.

## Extension point

Hermes (NousResearch hermes-agent) installs **skills** as directories under
`~/.hermes/skills/<category>/<name>/`, each with a `SKILL.md` manifest
(frontmatter: `name`, `version`, `description`, `argument-hint`,
`allowed-tools`, `homepage`, `repository`, `author`, `license`,
`user-invocable`). Install via `hermes skills install <repo>` (security
scanned) or `git clone` + `cp`/`ln -s` into the skills dir, then
`hermes skills list` and `/reload-skills`. This plugin ships as
`skills/swarm-forensics/` → `~/.hermes/skills/hunt/swarm-forensics`.

Two invocation paths:
- **Model-invoked:** `/swarm-forensics scan`, `/swarm-forensics research`, etc. The
  model reads SKILL.md and runs the scripts.
- **Headless:** host cron calls `python3 scripts/swarm_forensics.py --job <name>`.
  No Hermes-native scheduler was found in the surveyed material, so periodic
  execution is cron-driven. If hermes-agent documents scheduling later, the
  cron wrapper migrates without changing the jobs.

## Components

### 1. IOC scanner (`--job scan`)

Periodic hunts across three public sources, driven by query templates derived
from `pug-research/detection/RULES.md`:

- **urlquery:** `UQ-1` nonce-grammar sweep (`zz=oai`, `zzbulk`), `UQ-2`
  jq-proxy extraction (`jqp.vercel.app`, `jq=[`), `UQ-3` relay-chain
  laundering (`allorigins`, `da.gd` nesting), `UQ-4` basin targets
  (data APIs, `county.json` family), `UQ-5` watch-term tripwires.
- **Wayback CDX:** `CDX-1` burst-window census, `CDX-2` relay-wrapper
  prefix sweep (`r.jina.ai/http*`), `CDX-3` nonce-grammar filter sweep,
  `CDX-4` save-endpoint monitoring.
- **arquivo.pt CDX:** unbounded sweep, client-side filter (the venue is a
  zero-trap for date-bounded queries — see RULES.md venue quirks).

Each source keeps a `since` cursor in `state/cursors.json`; scans fetch only
new results. Hits append to `state/hits/YYYY-MM-DD.jsonl` as
`{source, query_id, term, url, observed_utc, evidence}`. Per-source rate
limits and delays are configurable. Transport is curl-via-subprocess
(the VM's Python HTTP stack cannot parse the egress proxy env).

### 2. IOC list updater (`--job update-iocs`)

The seed set (`pug-research/detection/wordlist.txt` + terms mined from
`RULES.md`) is read-only. The plugin keeps a working copy at
`state/iocs.json`: `[{term, category, status, provenance, added_utc, note}]`.

- `propose_term(term, provenance)`: adds with `status: proposed`.
- Promotion `proposed → active` and demotion `active → inactive` record
  reason + timestamp. Terms are never deleted.
- Scan hits whose evidence is strong (exact watch-term match, burst
  co-signal) auto-propose the novel co-occurring terms they contain;
  promotion policy (thresholds, review gate) is defined in `LEARNING.md`.
- `state/iocs.json` is untracked working state, not a publication artifact.

### 3. URL predictor (`--job predict-urls`)

Generates candidate URLs from the observed request grammar, so the scanner
can sweep for infrastructure that has not been seen yet:

- **Templates:** `{relay}/{target_url}`, `{relay}/http://{target}{path}?{nonce}={shape}`,
  `{shortener}/{id}` chains, `{target}{path}?{param_grammar}`.
- **Slots** filled from the working IOC list and the grammar tables:
  relay hosts (`jqp.vercel.app`, `allorigins.hexlet.app`, `r.jina.ai`,
  `da.gd`), nonce shapes (`zz=oai<digits>`, `zzbulk<digits>`,
  `prepnonce`, `fresh=x<epoch>.<rand>`), basin targets (data APIs,
  `county.json`/`regcf.json` family), param grammars
  (`survey_Year_Key`, `jq=[...]`).
- Output `state/candidates/YYYY-MM-DD.jsonl`: `{candidate_url, template,
  slots, predicted_for}`. Candidates feed back into CDX prefix sweeps
  and urlquery probes on the next scan cycle. Predictions are hypotheses;
  a candidate with no hit is a negative data point, recorded as such.

### 4. Research job (`--job research`)

Watches what other researchers publish, on a configurable interval:

- **Watchlist** (`config.ini [research]`, stub list to be curated):
  Transluce report index, vendor threat-intel feeds, relevant arXiv
  listings. Pure HTTP fetch of public pages/feeds.
- For each new or changed item: extract candidate IOC terms via n-gram
  novelty against the working copy (terms not present, or present but
  inactive). Each candidate is proposed with `provenance: <url>` and an
  excerpt.
- Dedupe by URL + content hash in `state/research_seen.json`. Never
  re-propose the same finding twice.

### 5. Config schema (`config.ini`, `configparser`)

```ini
[schedule]
scan_interval_hours = 6
research_interval_hours = 168
predict_interval_hours = 24
update_interval_hours = 24

[sources]
urlquery_enabled = true
cdx_enabled = true
arquivo_enabled = true
request_delay_seconds = 2
max_results_per_query = 100
user_agent = swarm-forensics/0.1 (+https://github.com/christopherwoodall/swarm-forensics)

[ioc]
auto_propose = true
require_review_for_promote = true

[research]
watch_urls =
    https://transluce.org/
novelty_min_chars = 4

[paths]
state_dir = state
```

Every interval lives here. Nothing periodic is hardcoded. `config.example.ini`
ships the defaults; the live file is `skills/swarm-forensics/config.ini`
(untracked, created on first run from the example).

## Data flow

```
config.ini → scan ──→ state/hits/*.jsonl ──→ update-iocs ──→ state/iocs.json
                         │                                     │
research ──→ proposals ──┘                                     │
                                                               ▼
predict-urls ← grammar tables + iocs.json ──→ state/candidates/*.jsonl
       │                                                │
       └──────── next scan cycle sweeps candidates ─────┘
```

## What this module does not do

- No authenticated sources, no private APIs, no credentials of any kind.
- No posting, no alerting integrations, no operator attribution.
- No claim stronger than the evidence: a hit means agent-shaped behavior
  was observed at a public source. The SOC runbook's claim ladder
  (`pug-research/detection/RULES.md` §3) governs interpretation.
- Learning policy (when a proposed term promotes, how novelty is scored,
  feedback from confirmed hits) is specified in `LEARNING.md`, written
  separately. This document specifies the machinery.

## Security posture

- Read-only egress to public HTTP endpoints. `curl` with a fixed allowlist
  of source hosts; redirects followed only within the allowlist.
- `hermes skills install` may flag network-access patterns (precedent:
  last30days's `dangerous` verdict on env-var reads + subprocess). The
  documented fallback is `git clone` + `cp`/`ln -s`; see `HERMES_SETUP.md`.
- State dir holds no secrets by construction. If a fetched page ever
  contains credential-shaped strings, the scanner redacts before writing
  (keys matching `*key*`, `*token*`, `*secret*`, `*password*`).
