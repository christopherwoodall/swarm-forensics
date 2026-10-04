# Adversarial review of the agent-incident brief

Status: completed review, with explicit unresolved evidence gaps.
Review date: October 3, 2026, local time; primary retrievals continued October 4 UTC.

## Result in one paragraph

The underlying traces are useful, but several headline implications fail.
The SEC burst survives with corrected counts and uncertain initiator.
Census's proposed three-relay success becomes three separate unsuccessful wrappers.
AIHW's June 18 response is a security-check page, not the requested workbook.
Relay-reference counts require new denominators, and major services were already inventoried.
Common-operation identity and operational dormancy are not established.
Read the [executive result](00-executive-result.md) for the bounded conclusions.

## Reading order

1. [Stabilized claim state](11-stabilized-claim-state-2026-10-04.md) — current wording, authority, and unresolved conflicts.
2. [Executive result](00-executive-result.md) — short corrected synthesis.
3. [Corrected claims](09-corrected-claims.md) — six original items, fifteen subclaims, and the later matrix crosswalk.
4. [Rejected claims and open questions](10-rejected-claims-and-open-questions.md) — what failed and what would change it.
5. [Source guide](SOURCE-GUIDE.md) — source types, provenance, limits, and evidence locations.

## Focused reviews

| File | Question |
| --- | --- |
| [01 — SEC Wayback](01-sec-wayback.md) | What does the burst establish about captures, timing, and initiators? |
| [02 — Operation linkage](02-operation-linkage.md) | Do the June clusters belong to one operation? |
| [03 — Relay layer](03-relay-layer.md) | Which denominator supports which claim about relay prevalence? |
| [04 — Census](04-census.md) | What happened in May and June, and did requested data return? |
| [05 — AIHW](05-aihw.md) | What did the malformed Jina capture actually preserve? |
| [06 — Dormancy and novelty](06-dormancy-and-novelty.md) | Do feed controls and prior publications support the headlines? |
| [07 — Chronologies](07-chronology.md) | Which ordering is observed, and which is interpretation? |
| [08 — Methods and reproduction](08-methods-and-reproducibility.md) | How were units, source dependence, and credentials handled? |

## Inputs and authority

- [Original brief](../discord-brief-2026-10-03.md).
- [Later claim matrix](../claim-matrix-2026-10-03.md).
- [Review specification](../adversarial-review-spec.md).

These are the claims and requirements under review, not evidence of their own correctness.
The later matrix partly demotes operation linkage but retains incompatible stronger language elsewhere.
The stabilized claim-state note records the current reading and preserves unresolved conflicts.

The six original claims received focused reviews.
Additional matrix leads are explicitly screened or left unverified in the crosswalk.
No NPWS, SwarmMemo, or seven-skill investigation is silently represented as completed.

## Evidence products

- [Full claim ledger](_support/corrected-claims.json).
- [Strict chronology: 74 selected observations](_support/strict-chronology.csv).
- [Typed linkage graph](_support/operation-graph.json).
- [Public-source catalog](_support/source-catalog.md).
- [Source manifest](_support/source-manifest.json).
- [Local measurements and source ZIP hashes](_support/parent-measurements.json).
- [Matrix-specific local counts](_support/matrix-local-counts.json).
- [Independent replay checks](_support/parent-replay-verification.json).
- [Final artifact verification](_support/verification.json).

Citation numbers are chapter-local.
The source guide maps namespaces and duplicate URLs.
They MUST NOT be combined as independent witnesses.

## Verification and reproduction

Run these commands from the repository root:

```sh
make review-measure
make review-relay-count
make review-verify
make --assume-old=setup test lint RUN='uv run --frozen --offline --no-sync'
```

The commands reuse the existing environment without synchronizing dependency files.
This is not a clean-install test.
The review verification checks coverage, references, links, counts, parseability, and known-key redaction.
The repository suite tests software behavior, not historical entailment.
The final run passed 189 tests and repository lint in the existing environment.
Citation identities, source-guide coverage, local links, and artifact checks passed.
The literal-quote attachment gate remains incomplete across the full collection.
Structured evidence receipts remain separate from those ledger attachments.
The relay chapter's optional 50% citation-density check failed at 21%.
These limitations are not reported as passed checks.
See the verification manifest for the final run and file hashes.

No raw archives, prior findings, active extraction outputs, or viewer data were overwritten.
The Makefile gains only review-specific offline measurement and verification targets.
Unrelated working-tree changes remain untouched.
No commit, push, publication, target probing, or credential test was performed.

## What remains unresolved

The original `briefdump-2026-10-03.zip` was not found in this repository.
Capture initiators, private runtime logs, some historical response bodies, and comparable feed coverage remain unavailable.
These gaps limit stronger attribution, causal linkage, success, novelty, and cessation claims.

Earlier notes remain historical hypotheses.
This collection supersedes their stronger interpretations where it states a correction.
It does not automatically repair the existing pipeline; identified implementation defects require a separate change.
