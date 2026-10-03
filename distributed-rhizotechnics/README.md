# distributed-rhizotechnics

Status: documented product direction; requirements interview active.
No application has been implemented by this session.

## Purpose

Make collective dependency structures inspectable through a provenance-sensitive, question-led rhizome.
Keep uncertainty, evidence classes, and source lineage visible.

Owner's pitch:

> This is not “chat with a dataset.”
> It is “watch a collective analysis accrete into an inspectable object.”

## Documentation map

| Document | Authority |
| --- | --- |
| [PROJECT_BRIEF.md](PROJECT_BRIEF.md) | Owner-stated direction, candidate details, and unresolved implementation boundaries. |
| [INTERVIEW.md](INTERVIEW.md) | Decision-area coverage, elicited owner answers, and milestone records. |
| [STATUS.md](STATUS.md) | Current checkpoint, verified state, and next interview question. |
| [AESTHETIC.md](AESTHETIC.md) | Owner-supplied visual, motion, accessibility, and consent-state scope. |
| [Parent AGENTS.md](../AGENTS.md) | Repository requirements and operational rules. |

Read the brief before proposing changes.
Read the interview and status before resuming elicitation.
Do not treat documented product direction as a completed implementation specification.

## Selected implementation direction

Use a Tauri shell with a Svelte/TypeScript frontend.
Keep graph rendering and ordinary interaction in the frontend.
Use Rust only where local capabilities justify it.
Keep the hackathon surface to one window.

Develop locally under `swarm-forensics/distributed-rhizotechnics` on Maria's own branch.
The owner renamed the existing documentation directory from `swarm-rhizomics`.
Do not export this application into FairyStack.
Do not scaffold the application at the repository root.
The current checkout is `colette-help-peer`; no branch switch or push occurred.

## Interview protocol

Ask one question per turn.
Adapt follow-up questions to the owner's actual answer.
Preserve uncertainty and deferred choices explicitly.

Track nine decision areas, not nine fixed questions.
Checkpoint after three completed areas and six completed areas.
Announce when all nine areas have been addressed.
Record any remaining blockers separately from interview coverage.

At each milestone, update the brief, interview record, and status together.
Do not begin implementation merely because the interview finishes.

## Re-entry

1. Read STATUS.md for the current area and checkpoint.
2. Read INTERVIEW.md for answers and unresolved follow-ups.
3. Continue with one highest-value owner question.
4. Preserve all unrelated working-tree changes.

No setup, build, or launch instructions exist yet.
Executable tooling remains an implementation-stage decision.
