# packet-v3 MANIFEST

Staging for the SwarmTracers Hackathon evidence packet v3.
Branch: `pug-scratch`. Status: STAGED ONLY — do not zip, do not commit
until the user says so. All files scanned for secrets (tokens, PATs,
Authorization headers, private keys, credential URLs) — none found.

## Finished documents (final, copied not moved)

| Staged file | Source | Description | Status |
|---|---|---|---|
| `stylometry-REPORT.md` | `pug-research/stylometry/REPORT.md` | 78-run multi-method lexical comparison of the four OpenAI-side partitions (gems/traces/wiki/evals); headline matrix, tradecraft-hub and provider-marker findings | final |
| `goal-inference-REPORT.md` | `pug-research/goal-inference/REPORT.md` | Degraded-stack fragment→goal matcher: LOO validation, anchored sanity checks, holdout inferences with confidence tiers, honest limits | final |
| `goal-inference-DESIGN.md` | `pug-research/goal-inference/DESIGN.md` | Experimental protocol: train/validate on village tasks, freeze, apply to the OpenAI holdout as hypotheses | final |
| `5w-operational-framework.md` | `~/workspace/silent-locus/collections/hunt-missed-surfaces/incident-discovery/5w-operational-framework.md` | Operational 5W detection/SOC framework; URL basins of attraction concept | final |
| `jqp-ihme-lead.md` | `~/workspace/silent-locus/collections/hunt-missed-surfaces/incident-discovery/jqp-ihme-lead.md` | June 18 17:13 UTC jqp/SEC Massachusetts county-extraction observation; relay-chain linkage | final |
| `seed-firehistory-sweep.md` | `~/workspace/silent-locus/collections/hunt-missed-surfaces/incident-discovery/seed-firehistory-sweep.md` | NSW Fire History negative result: service located, all June-2026 trace shapes clean; bounds the detection method | final |
| `CAVEATS.md` | written for this packet | All 19 documented limitations from the staged reports, collected in one place | final |

## Placeholders (pending lane outputs)

| Staged file | Will hold | Status |
|---|---|---|
| `placeholders/REPORT_V2.md` | Apples-to-apples stylometry re-partition (functional pairs) | placeholder-pending |
| `placeholders/PATTERNS.md` | Grammar-network pattern-database mining report | placeholder-pending |
| `placeholders/PROMPT_INVERSION.md` | Village prompt mining + holdout prompt inversion | placeholder-pending |
| `placeholders/REVIEW.md` | Final overclaim/adversarial review pass | placeholder-pending |
| `placeholders/RULES.md` | Detection rules derived from the 5W framework | placeholder-pending |
| `placeholders/JOURNAL.md` | Chronological hunt journal (steps + rationale) | placeholder-pending |

## Exclusions (deliberate)

- No raw data, no `data/raw/`, no gated AI Village content — docs and
  derived reports only.
- No `runs_log.jsonl`, no sqlite DBs, no intermediate JSONL — the packet
  carries findings, not working state.
- Secret scan: all six staged documents scanned for tokens, PATs,
  Authorization headers, private keys, and credential-bearing URLs.
  Nothing found; nothing excluded.

## Counts

- 7 finished documents (6 copied + CAVEATS.md)
- 6 placeholders
- Total staged: 13 files
