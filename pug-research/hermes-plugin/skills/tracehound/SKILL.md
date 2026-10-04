---
name: tracehound
version: "0.1.0"
description: "Hunt for agent-trace IOCs across public sources on a loop. Scans urlquery, Wayback CDX, and arquivo.pt for toolkit markers; maintains a working IOC list; predicts candidate URLs from observed request patterns; watches researcher publications for new IOCs. All intervals configurable."
argument-hint: 'tracehound scan | tracehound research | tracehound predict-urls | tracehound update-iocs | tracehound diagnose'
allowed-tools: Bash, Read, Write
homepage: https://github.com/christopherwoodall/swarm-forensics
repository: https://github.com/christopherwoodall/swarm-forensics
author: swarm-forensics
license: MIT
user-invocable: true
metadata:
  tracehound:
    bins:
      - python3
      - curl
    files:
      - "scripts/*"
    tags:
      - threat-hunting
      - ioc
      - osint
      - agent-traces
      - cdx
      - urlquery
---

# Tracehound

Recreate the swarm-forensics hunt methodology as a continuously running
Hermes skill. Scope: agents, agent systems, and public evidence only.
A hit means agent-shaped behavior was observed. It never identifies a human.

## Jobs

Run headless (cron) or invoked:

```bash
python3 scripts/tracehound.py --job scan          # periodic IOC hunt
python3 scripts/tracehound.py --job update-iocs    # maintain working IOC list
python3 scripts/tracehound.py --job predict-urls  # generate candidate URLs
python3 scripts/tracehound.py --job research      # watch researcher publications
python3 scripts/tracehound.py --job diagnose      # config + source health check
```

Or via slash form: `/tracehound scan`. Translate intent into the CLI flags;
the model invoking the skill is the planner and the judge.

## First run

1. Copy `config.example.ini` to `config.ini` and set your intervals.
   Every schedule value lives in `[schedule]` — nothing is hardcoded.
2. Run `--job diagnose` to verify curl, config, and source reachability.
3. Run `--job scan` once manually; inspect `state/hits/` before scheduling.
4. Schedule with host cron (no Hermes-native scheduler exists):

```cron
# tracehound: IOC scan every 6h, URL prediction daily, research weekly
0 */6 * * * cd ~/.hermes/skills/hunt/tracehound && python3 scripts/tracehound.py --job scan >> state/cron.log 2>&1
30 2 * * * cd ~/.hermes/skills/hunt/tracehound && python3 scripts/tracehound.py --job predict-urls >> state/cron.log 2>&1
15 3 * * 0 cd ~/.hermes/skills/hunt/tracehound && python3 scripts/tracehound.py --job research >> state/cron.log 2>&1
```

## State layout (untracked)

- `state/iocs.json` — working IOC copy (seed is read-only; terms demote, never delete)
- `state/hits/YYYY-MM-DD.jsonl` — scan hits with provenance
- `state/candidates/YYYY-MM-DD.jsonl` — predicted candidate URLs
- `state/cursors.json` — per-source `since` cursors
- `state/research_seen.json` — dedupe for the research job
- `state/cron.log` — headless run log

## Rules the skill follows

- Read-only public sources. No credentials, no authenticated APIs, no posting.
- Every hit records source, query, term, timestamp, evidence excerpt.
- Proposed IOC terms need review before promotion
  (`require_review_for_promote`, configurable).
- Candidate URLs are hypotheses. A candidate with no hit is a negative
  data point — record it, don't silently drop it.
- Interpret hits with the claim ladder in `references/claim-ladder.md`:
  L1 artifact → L5 operation. Never operator identity.
