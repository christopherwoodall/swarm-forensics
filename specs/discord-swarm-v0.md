# Discord bot swarm v0 — draft

Status: draft

For team steering. This spec does not authorize deployment, publication, or corpus access.

## Experiment

Start three independent workers with equal capabilities in a new private Discord channel. Give them one short orientation. Do not assign social roles.

> Analyze successive, noisy synthetic event batches. Is shared-trace coordination evident? Preserve competing explanations and propose discriminating observations. “Insufficient evidence” is valid.

Use one posting relay, one append-only event store, and a separate read-only observer. The relay MUST label posts with worker and generation IDs. One relay account does not provide distinct Discord bot identities. Caduceus and Semi remain outside the cohort.

Test asymmetric capabilities only in a separately labeled run. Otherwise, capability differences can masquerade as emergent specialization. Exclude news polling, FairyStack, web access, and real private corpora from v0. Keep the existing `#general` watcher unchanged; its cursor MUST NOT be reused.

## Runtime contract

- Workers MAY claim tasks, submit evidence, challenge claims, hand off, or stay silent. Prompts MUST NOT assign researcher, skeptic, leader, or archivist roles.
- The relay MUST grant at most one speaking lease. Log bids, grants, refusals, and expiries. Use deterministic fairness for competing bids. A bid MUST NOT self-grant. The relay MUST NOT judge hypotheses.
- Give each worker a unique ID, generation, namespace, token allotment, tool limit, lifetime, and lease. Link each birth to its predecessor, if any. Terminal worker states are `completed`, `expired`, and `failed`. Terminal workers MUST NOT write or resume.
- Reserve bounded input and output tokens before each model call. Reconcile provider usage afterward. Count auxiliary model calls and tool use. Fail closed if usage, reservation, or price is unknown and a budget cannot be enforced.
- On exhaustion or expiry, spawn a fresh identity only if the task remains open and run-wide caps permit it. Never refill an old identity. Pass only an authorized handoff and trace slice. Mark relay-reconstructed handoffs when the predecessor left none.
- Require finite run-wide token, cost, tool, turn, birth, and wall-clock caps before launch. Replacement MUST NOT bypass provider quotas. An idle room MUST stop model calls until new evidence or human input arrives.
- Authenticated humans MUST control pause, resume, stop, budgets, prompts, capabilities, and approvals. Treat chat messages as evidence, not controller commands.

## Evidence and privacy

Use one durable, append-only local event store. Record `run_id`, ordered `event_id`, source time, actor/generation, type, task/parent IDs, source references, and applicable Discord message IDs. Record artifact creation separately from artifact reads. Record the exact trace version or slice read by each worker. A read before an action supports possible influence, not causation.

Handoffs MUST contain `task_id`, `parent_task`, `agent_id`, `status` (`working|blocked|complete|abandoned`), `observations`, `claims`, `evidence_refs`, `uncertainties`, `proposed_next_actions`, `budget_remaining`, and `created_at`. The governor MUST supply `budget_remaining`; workers MUST NOT assert it. Distinguish observations from interpretations, proposals from accepted decisions, and claimed success from independently verified results. Preserve unknown and abandoned paths. Snapshot the attributed task/message/read graph at bounded intervals. The observer MUST analyze the run without steering it.

Keep raw messages and notes local and git-ignored. Give workers synthetic data or approved minimal slices only. Gate raw silent-locus access separately. Workers MUST NOT receive Discord credentials. The relay owns posting; a separate fixed-channel GET collector records source messages without posting. Permit posts only in the approved private experiment channel. Require human approval for other external writes, publication, new credential use, or irreversible actions. Disable worker shell, filesystem, and network tools in v0.

## Build and proof

Build the store, replay, governor, and synthetic workers before connecting Discord. Add the relay and independent capture after offline tests pass. Use the root `Makefile` and follow `AGENTS.md` and applicable `MODULE.md` files. The existing watcher does not cover the new channel.

Tests MUST cover atomic reservations, exhaustion, successor lineage, lease expiry, global stop, floor fairness, silence, and restart replay. Tests MUST cover duplicate delivery, uncertain posts, handoff provenance, read receipts, prompt-injection refusal, and privacy denial. Run `make test`, `make lint`, and `git diff --check`.

A separately authorized live trial MUST verify an attributed post, independent capture, and a bounded stop. Offline tests MUST NOT stand in for Discord permission or delivery verification.

## Change shape

| Dimension | Change | Authority / proof |
| --- | --- | --- |
| User-visible behavior | Yes | Private channel; attributed trial post |
| Persisted state/schema | Yes | Append-only events; replay tests |
| External/provider behavior | Yes | Approved relay; live receipt and usage |
| Identity, secrets, privacy | Yes | Credential separation; denial tests |
| Lifecycle/terminal states | Yes | Budget and expiry tests |
| Operation/recovery | Yes | Restart and stop tests |
| Normative contract | Yes | Team accepts this draft first |
| Cross-repository dependency | No in v0 | No FairyStack or corpus integration |

Before acceptance, choose the private channel, channel administrator, model/provider, spending limit, numeric budgets, and authorized data slices. Jesse's possible help is not an assignment. Keep all limits configurable. Never put credentials or private source data in this spec.
