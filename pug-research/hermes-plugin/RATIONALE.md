# Case-management layer — RATIONALE

Date: 2026-10-04. Worker: 5.
Purpose: the reasoning a reviewer needs to trust the design. Each
decision names the objection or failure it answers, drawn from
`ADVERSARIAL.md` and `ADVERSARIAL_DELTA.md`.

## 1. Hunting-dog over autonomous (answers #1–#3)

The plugin never acts alone. Every hunt is a discrete job the human
starts; every mutation of the case DB is a GUI submit, palette
command, or CLI call. There is no scheduler, no watcher, no
background write.

The objection it answers: the original design was graded "no-build"
because an autonomous hunter was self-defeating (#1, #2) and abusive
(#3). Autonomy was the defect, not a feature. The re-grade closed
six objections the day the autonomous headless cron died. This
layer keeps that closure: nothing here can reintroduce a
self-running agent, because there is no code path that writes
without a human at the other end.

What is NOT claimed: this does not stop a human from hammering a
source. That is deliberate operator action, visible in hunt
history — not automation externalizing cost silently (#3 re-grade).

## 2. Private-only over public (answers #1, #11)

The case DB, the IOC working copy, and the tripwire strings never
leave the operator's machine. `cases.py` makes zero network calls.
The DB lives in untracked `state/`.

The objection it answers: publishing the skill destroys the
zero-baseline tripwires the hunt depends on (#1), and a public
artifact teaches the hunted the complete playbook (#11). A case
file is worse than a term list to leak: it contains the analyst's
conclusions. So the case layer is local-only by construction, not
by policy. There is no sync flag to misconfigure because there is
no sync code.

What is NOT claimed: local-only does not protect against the
operator's own backup, disk image, or screenshot habits. It
protects the deployment, not the operator.

## 3. Advisory-locked firewall over auto-promotion (answers #2, #5)

The firewall judges; it never gates. `enforcing` mode is locked in
code. The case layer extends the same principle one step further:
indicator extraction is not even advisory — it is clerical. It
files regex matches into the case DB and stops. It cannot propose,
promote, or demote an IOC.

The objection it answers: `update_from_hits` was a live poisoning
cannon (#2) because the pipe from untrusted evidence ended at the
list. Here the pipe from untrusted trace text ends at a private
notebook. The worst a poisoned trace achieves is a wrong note the
human wrote down themselves. The judge-eats-attacker-input problem
(#5) is demoted the same way: bad advice next to the evidence the
human already sees.

What is NOT claimed: extraction is not validated against
adversarial trace text. A trace crafted to produce misleading
indicators will produce them. The defense is the human reading
the note, not the regex.

## 4. Human-gated everything (answers #4)

The review queue is the product's core surface, and IOC promotion
exists only as a human decision function. The case layer adds a
second gate by omission: it has no promotion function at all. The
indicator table and the IOC list share no code, no schema, and no
reference. `delete_entity` cannot touch the IOC list because the
DB does not know it exists.

The objection it answers: the review queue "did not exist" (#4)
in the original design — it was prose. Now the queue is the only
door, and the case layer does not even have a door. Two
independent mechanisms would be worse than one; zero mechanisms
plus one human is the design.

What is NOT claimed: the UI cannot stop the human from copy-pasting
an indicator into the IOC term field. The gate is procedural, and
the procedure is the human's.

## 5. SQLite-local over server DB (answers #10)

One file, stdlib `sqlite3`, no server, no lock manager, no
credentials. The DB is created lazily and migrated on open.

The objection it answers: operational reality (#10) — no owner,
no locking, fragile state. The sharpest edges (run-locking,
overlapping cycles, dead-man's checks) died with the cron. What
remains is a single-user file on a single machine. A server DB
would reintroduce exactly the operational burden the re-grade
removed: something to run, to back up, to secure. SQLite is the
smallest thing that survives the operator closing the app.

What is NOT claimed: there is no backup story beyond the
operator's own disk. Cursor backups and log rotation are still
open residuals (#10).

## 6. No-cron over scheduler (answers #3, #10, #12)

Nothing in the case layer runs while the app is closed. There is
no refresh, no re-index, no nightly rollup. Stale data waits for
the human to return.

The objections it answers: autonomous volume abused free sources
(#3); scheduling created the locking and overlap hazards (#10);
and the old model-invoked scan path was a second threat model
(#12). A scheduled case-maintenance job would resurrect all
three in miniature. So there is none.

What is NOT claimed: the graph layout recomputes on load, which
costs O(n^2) per view. For a human-curated case file this is
trivial; it is not a design that scales to machine-sized graphs,
and it does not try to.

## 7. Single enforcement point over dual paths (answers #12)

The GUI and the `/swarm-forensics case …` grammar are two faces of
one state. Both call `plugin_api.py`; the backend calls `cases.py`.
The CLI calls `cases.py` through the same validation. There is no
second writer, no direct-DB GUI path, no model-invoked tool that
bypasses the backend.

The objection it answers: the old skill had two threat models —
the desktop path and the model-invoked `/tracehound scan` path with
raw shell (#12). One enforcement point means one audit surface.
Validation (entity types, rel kinds, indicator kinds) lives in
`cases.py` and is therefore identical for every caller.

What is NOT claimed: the CLI and the backend are separate
processes sharing a file. SQLite serializes this fine for one
human, but there is no cross-process transaction beyond what
SQLite gives for free.

## 8. Case DB as the consumer's workspace (answers #9)

The re-grade closed #9 — "false positives at scale have no
consumer" — by naming the consumer: the human hunter at the
console. The case DB is that consumer's desk. Hits arrive with
claim-ladder badges; the human files the ones that matter as
traces, links them to agents and swarms, and keeps the reasoning
in one place.

The failure this answers: without a workspace, triage output
evaporates. The review queue decides terms; the case DB remembers
why. A swarm hypothesis that took three hunts to build should not
live in chat scrollback.

What is NOT claimed: the case DB does not validate hypotheses.
It stores the analyst's conclusions with their provenance; it
does not check them. A wrong link is stored as faithfully as a
right one. The provenance field exists so the human — or a later
reviewer — can tell which is which.

## What this layer deliberately does not do

- It does not score, rank, or judge. No model, no heuristics.
- It does not deduplicate across hunts. The human curates.
- It does not back up, sync, or export. The operator owns the file.
- It does not enforce the two-venue rule or the exclusion list.
  Those belong to the IOC pipeline, which this layer cannot reach.
- It does not fix objection #8 (HTTP-status handling). That is
  still open and still the highest-priority code fix; this layer
  neither helps nor hinders it.
