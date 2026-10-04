---
name: swarm-forensics
version: "0.2.0"
description: "Hunting-dog agent-trace IOC hunts across public sources. Every hunt is a discrete human-triggered job: the human starts it, watches it, and cancels it. No cron, no autonomous scans, no background schedule. IOC proposals wait in a human review queue; nothing promotes without an explicit human accept."
argument-hint: '/swarm-forensics [hunt <target> | stop | status | review | modify | research | predict-urls | update-iocs | diagnose]'
allowed-tools: Bash, Read
homepage: https://github.com/christopherwoodall/swarm-forensics
repository: https://github.com/christopherwoodall/swarm-forensics
author: swarm-forensics
license: MIT
user-invocable: true
metadata:
  swarm-forensics:
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

# Swarm Forensics

The hunting dog. It hunts only with the human.

Every hunt is a discrete job the human starts, watches, and can
cancel. Nothing here runs on its own: no cron, no background
schedule, no autonomous scans. The IOC updater only proposes
candidates into a human review queue. Nothing promotes without a
human click or an explicit human decision.

Scope: agents, agent systems, and public evidence only. A hit means
agent-shaped behavior was observed. It never identifies a human.

## Threat model (single)

human → command/UI → backend with guardrails.

The backend enforces allowlisted hosts, per-source budgets,
check-don't-fetch, and the paused state. The old model-invoked
`/swarm-forensics scan` path with `allowed-tools: Bash` is removed.
The command surface calls the backend, never raw shell.
(ADVERSARIAL_DELTA.md §12.)

## Command grammar

The skill's command is `/swarm-forensics`. The model translates the
human's intent into the CLI flags below. The model never invents
new verbs and never schedules work.

```
/swarm-forensics                              # dashboard  -> /swarm-forensics
/swarm-forensics hunt <target> [--sources urlquery,cdx,arquivo] [--cap N]
                                              # new hunt   -> /swarm-forensics/hunt
/swarm-forensics stop [job-id]                 # kill switch (stops active hunt)
/swarm-forensics modify <setting> <value>     # validated setting change
/swarm-forensics status                       # JSON summary -> /swarm-forensics
/swarm-forensics review                       # list queue -> /swarm-forensics/review
/swarm-forensics review accept <id>           # promote to active list
/swarm-forensics review reject <id>           # mark inactive, keep provenance
/swarm-forensics review narrow <id> <chunk>   # propose narrower term
/swarm-forensics case add <type> <label>    # new trace/agent/swarm/collection
/swarm-forensics case link <from> <to> <rel> # relate two entities
/swarm-forensics case list [--type T]       # list entities
/swarm-forensics case graph                 # open /swarm-forensics/graph
```

GUI deep links live as ⌘K palette entries in the desktop plugin
(`PALETTE_AREA`; HERMES_DESKTOP.md §1 [DOC]; command payload shape
[INF]): `swarm-forensics: Open dashboard`, `Start hunt...`,
`Stop hunt`, `Open review queue`, `Status`, `Pause / resume hunting`.

## CLI (what the skill actually runs)

```bash
python3 scripts/swarm_forensics.py hunt [--target T] [--sources urlquery,cdx,arquivo] [--cap N] [--resweep] [--mock]
python3 scripts/swarm_forensics.py stop [--job-id J]
python3 scripts/swarm_forensics.py modify <setting> <value>
python3 scripts/swarm_forensics.py status
python3 scripts/swarm_forensics.py review {accept,reject,narrow} <id> --rationale R [--reviewer X] [--chunk C]
python3 scripts/swarm_forensics.py case {add,link,list,graph} [...]  # case entities
python3 scripts/swarm_forensics.py update-iocs      # proposes only; no-op unless ioc.auto_propose=true
python3 scripts/swarm_forensics.py predict-urls     # candidate URLs from observed grammar (manual)
python3 scripts/swarm_forensics.py research         # checks research watchlist once (manual)
python3 scripts/swarm_forensics.py diagnose         # curl + config + source reachability
```

Notes:

- `hunt` prints the query plan first (terms, queries, per-source).
  It refuses to start when `safety.paused` is true.
- `stop` cancels the running hunt after its current query finishes.
- `modify` validates one setting against the schema. Unknown keys
  fail with the valid-key list. `firewall_mode` accepts `off` or
  `advisory` only; `enforcing` is refused in code (ADVERSARIAL.md
  objection #5).
- `review` REQUIRES `--rationale`. Decisions are audited and
  recorded on the entry (reviewer, timestamp, rationale).
- `update-iocs` is human-triggered by design. With
  `auto_propose=false` (default) it does nothing.

## What never happens

- No cron. No scheduling code exists in the plugin.
- No autonomous scans. The app closed means nothing runs.
- No auto-promotion. `accept_term` / `reject_term` / `narrow_term`
  are the only promotion functions, and they are human-gated.
- The chat responder never auto-accepts, auto-rejects, or
  auto-narrows. A "hunt ..." message counts as the human
  initiating that hunt.

## State layout (untracked)

- `state/iocs.json` — working IOC copy (seed is read-only; terms demote, never delete)
- `state/hits/YYYY-MM-DD.jsonl` — hunt hits with provenance
- `state/candidates/YYYY-MM-DD.jsonl` — predicted candidate URLs
- `state/cursors.json` — per-source `since` cursors (persist between hunts)
- `state/research_seen.json` — dedupe for the research check
- `state/review.json` — human review queue
- `state/throttles.jsonl` — throttle events (separate from results)

## Rules the skill follows

- Read-only public sources. No credentials, no authenticated APIs, no posting.
- Every hit records source, query, term, timestamp, evidence excerpt.
- Proposed IOC terms wait in the review queue until a human decides
  (`require_review_for_promote`, always true in practice).
- Candidate URLs are hypotheses. A candidate with no hit is a negative
  data point — record it, don't silently drop it.
- Interpret hits with the claim ladder in `references/claim-ladder.md`:
  L1 artifact → L5 operation. Never operator identity.
- Toasts fire only at or above `safety.alert_on_claim_level` (default L3).
