# MODULE.md — pug-research/detection

## 1. Purpose

Executable detection artifacts derived from the 5W operational
framework. Turns hunt findings into runnable rules: urlquery search
strings, Wayback CDX sweep patterns, and a SOC runbook.

## 2. Active Invariants

- Every rule states what it catches, why it works (with trace
  evidence), and its blind spots. A rule without a blind spot MUST
  NOT be added.
- Scope is agents, agent systems, and infrastructure. Rules MUST NOT
  attempt human or operator attribution.
- Findings are graded on the claim-strength ladder (L1 artifact →
  L5 operation). Rules MUST NOT assert above their evidence level.
- No Elastic or SIEM query shapes live here (dropped per 2026-10-04
  correction). Venue coverage is urlquery, CDX, arquivo.pt.

## 3. Interfaces & Dependencies

- `RULES.md`: the rule set and runbook. The only deliverable.
- Reads (read-only): `../stylometry/REPORT.md`,
  `../grammar-network/request_grammar.json`,
  `~/workspace/silent-locus/collections/hunt-missed-surfaces/incident-discovery/5w-operational-framework.md`,
  `jqp-ihme-lead.md`.
- No code, no dependencies, no build step.

## 4. Current State & Known Gaps

- RULES.md written 2026-10-04, uncommitted on `pug-scratch`.
- CDX filter regexes should be re-derived from the request-grammar
  graph each sweep; grammar drift evades fixed patterns.
- Direct query-API incidents (ArcGIS `/query?where=...`) are
  invisible to every rule here — venue-shaped blind spot, stated
  in the runbook.

## 5. Decisions

- [2026-10-04 Agent]: Drop Elastic/JSON query shapes from the deliverable per user correction; keep urlquery, CDX, runbook only.
- [2026-10-04 Agent]: Structure every rule as catches / why-it-works / blind-spots, mirroring the 5W calibration discipline.
