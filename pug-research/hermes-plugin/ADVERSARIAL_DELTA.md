# Adversarial delta: re-grading the 12 objections under the hunting-dog model

Date: 2026-10-04. Parent review: `ADVERSARIAL.md` (verdict: no-build as
specified — public, self-updating, autonomous hunter).

## The model change

The user directed: "Only hunt with a human. Like a hunting dog." The
autonomous headless cron hunter is dropped entirely. The revised shape:

- **No background scheduler, no cron, no autonomous scans.** Nothing
  runs while the app is closed (accepted by the user).
- **Every hunt is a discrete human-triggered job**: the human starts it
  from the desktop console or the `/swarm-forensics` command, watches
  visible progress, can cancel it, and reviews every hit.
- **The IOC updater is purely assistive**: it proposes candidates with
  evidence into a human review queue. Nothing promotes without a human
  click (GUI button or `/swarm-forensics review accept`).
- **The desktop app is the whole product**: full GUI (dashboard, hunt
  control, review queue, IOC management, settings, kill-switch) plus the
  `/swarm-forensics` command grammar — two faces of the same state.
- **Private deployment only.** The prompt firewall stays advisory-only,
  locked (enforcing mode refuses to enable until an injection-resistance
  eval passes).

Re-grade per objection. Verdicts: FIXED / PARTIALLY / OPEN.

---

## 1. Publishing the skill destroys the tripwires — FIXED

Private deployment removes the publication mechanism. Watch-term
strings never ship in a public artifact, so the zero-baseline premise
survives. The methodology writeup (`RULES.md`) is already public by
design; that is methodology, not live tripwire strings — the review's
own recommendation drew this line. **Re-open condition:** if the skill
is ever published, strip watch terms to a private overlay first.

## 2. `update_from_hits` is a live poisoning cannon — FIXED

The cannon is decommissioned, not just gated. `auto_propose` defaults
to false; when enabled, proposals land **quarantined** in the human
review queue and the code enforces the exclusion-list filter and the
two-venue rule before a candidate even reaches the queue. Nothing in
the pipeline can promote — promotion exists only as a human decision
function (GUI click or `review accept`). The regex still extracts
tokens from untrusted evidence, but the pipe it feeds ends at a human,
not at the list. **Remaining:** implementation verification (the queue
writer, the two-venue check, and the quarantine default must be read
in code, not trusted from this doc).

## 3. Scan volume is abusive to free services — FIXED

The abusive pattern was *autonomous* volume: 2,092 terms × 4 sweeps/day
forever with no human in the loop. That pattern no longer exists. Every
hunt is human-initiated, discrete, and capped (`max_terms_per_sweep`,
default 200), with the estimated query count shown before the human
confirms. A human can still choose to hammer a source — that is
deliberate operator action, visible in hunt history, not automation
externalizing cost silently. **Remaining:** objection #8 (a human hunt
must still degrade gracefully on 429 rather than corrupt its results).

## 4. The human review queue does not exist — FIXED BY DESIGN

The review queue is now the product's core surface, not a prose
assertion: a Review tab with candidate cards (evidence, venue count,
co-occurring chunks, firewall advisory), ACCEPT/REJECT/NARROW actions,
filter/sort, keyboard triage, queue-depth badge, and a 7-day SLA flag —
plus `/swarm-forensics review` / `review accept <id>` / `reject <id>` /
`narrow <id> <chunk>` for keyboard-driven triage. **Remaining:**
implementation (review writer/reader/SLA in code) and naming the
operator in `HERMES_SETUP.md`.

## 5. Prompt firewall: the judge eats attacker-controlled input — FIXED (advisory-only, locked)

Under the hunting-dog model the firewall is demoted from "the gate"
to "an advisor to the human." The judge can never promote; the worst
a successful injection achieves is a bad recommendation displayed next
to the evidence the human already sees. Taint pre-screen, structural
separation, fail-closed parsing, per-cycle budget, and the golden set
remain as defense in depth. `enforcing` mode is locked in code — any
attempt to enable it is refused with an explanation. **Remaining:** run
the injection-resistance eval against `references/firewall-golden.jsonl`
before enabling even advisory mode; default stays off until then. Note
honestly: the firewall is now less load-bearing than `FIREWALL.md`
assumes, because the human queue is the real gate.

## 6. Predictor templates unvalidated and partly malformed — FIXED (by implementation)

The build reads slot inventories programmatically from
`pug-research/grammar-network/request_grammar.json`, fixes the
`relay_nonce` template (nonce attaches to the *target* URL's query
string, not the relay's), and validates every template against at
least one observed real URL before it enters the candidate pool.
**Remaining:** implementation verification — read the template-
validation log, not the doc.

## 7. Two of three scan sources are dead code — FIXED (by implementation)

The discrete hunt fans out to all three enabled sources (urlquery,
Wayback CDX, arquivo.pt) with per-source budgets and per-source
progress. The two-venue rule is satisfiable again because multi-venue
data actually flows. **Remaining:** implementation verification.

## 8. No HTTP-status handling: rate limits are invisible — OPEN

The model change does not fix this; only code does. Required: capture
HTTP status on every request; exponential backoff on 429/403 honoring
`Retry-After`; log throttle events to `state/throttles.jsonl`
separately from results; never record a throttled query as a negative.
**This is the highest-priority remaining code fix** — without it, a
human-triggered hunt still corrupts its own negative data the first
time a source throttles it.

## 9. False positives at scale have no consumer — FIXED

The consumer is now defined and present: the human hunter at the
console. Hits flow to the Hits tab with claim-ladder badges; toasts
fire only at or above `alert_on_claim_level` (default L3+); the
dashboard is the alert inbox (no notification center exists in the
app chrome — documented, not hidden). **Remaining:** trim the default
seed list to the high-precision subset (watch terms, nonce grammar,
exact relay+target pairs) so the first-run experience is quiet and
precise rather than noisy.

## 10. Operational reality: no owner, no locking, fragile state — MOSTLY FIXED

No cron means the sharpest edges disappear: no run-locking needed
(single discrete jobs, cancellable), no overlapping cycles, no
70-minute sweeps, no dead-man's check for a schedule that no longer
exists, no `cron.log` growing forever. State still lives on disk;
cursors persist between hunts. **Remaining:** name the operator and
the machine in `HERMES_SETUP.md`; log rotation for hunt logs; cursor
backups.

## 11. Strategic: the plugin teaches the hunted — FIXED

Same fix as #1: private deployment only. The complete playbook
(strings, venues, cadence, thresholds) never leaves the operator's
machine. **Remaining:** none, conditional on staying private. If the
user later wants a public version, it ships with tripwires stripped —
that is a separate product decision, not a default.

## 12. "Hermes plugin" is branding on a cron script — FIXED

There is no cron script anymore. The plugin *is* the desktop app: full
GUI plus the `/swarm-forensics` command grammar, with the Python
backend as its engine. One threat model: human → command/UI → backend,
where the backend enforces allowlisted hosts, per-source budgets,
check-don't-fetch, and the paused state. The old model-invoked
`/tracehound scan` path with `allowed-tools: Bash` is removed; the
command surface calls the backend, never raw shell. **Remaining:**
`SKILL.md` must be rewritten to describe exactly this (no stale
dual-path text).

---

## Tally

- **FIXED:** 1, 2, 3, 9, 11, 12 (6)
- **FIXED BY DESIGN** (implementation must be verified in code): 4, 5, 6, 7 (4)
- **MOSTLY FIXED** (small residuals): 10 (1)
- **OPEN** (code fix still required): 8 (1)

## SDK-conformance statement (per the FULL-GUI steer)

Every FULL-GUI requirement maps to a documented SDK surface
(`HERMES_DESKTOP.md` §1): the six-tab page (`ROUTES_AREA` + sidebar
nav), status-bar chip (`statusBar.right`), ⌘K commands
(`PALETTE_AREA`), triage keybinds (`KEYBINDS_AREA`, rebindable),
toasts (`host.notify`), live hunt progress (`ctx.socket` with the
documented React Query polling fallback), cancel (POST endpoint),
settings (dashboard Settings tab + `APPEARANCE_AREAS.extra` trio),
persistence (`ctx.storage` + `config.ini`). **Nothing in the full-GUI
scope exceeds the documented SDK.** Two `HERMES_DESKTOP.md` gaps are
retired by the model change: Gap 1 (no execution while the app is
closed) is accepted as the design, and Gap 3 (gateway cron RPC) is
moot — there is no cron.

## Addendum (2026-10-04): chat window + inline accept + prompt editors

The user added three GUI surfaces after the re-grade. None reopens a
closed objection, provided these invariants hold in the build:

- **Chat window.** The conversational responder MUST NOT auto-accept,
  auto-reject, or auto-narrow candidates. A "hunt X" message counts as
  the human initiating a hunt (human-initiated by construction); every
  promotion still requires an explicit accept click. The rule-based
  responder is preferred over a model precisely because it cannot be
  prompt-injected into promoting; if the optional model endpoint is
  configured, its key follows the firewall pattern (env var, never
  logged) and its replies are text only — never actions.
- **Inline accept.** The inline ACCEPT/REJECT/NARROW buttons call the
  same `POST /review/decision` endpoint as the Review tab (two faces,
  one state). Inline accept does not bypass provenance logging.
- **Prompt editors.** The firewall judge prompt and hunt query
  templates are editable in Settings with reset-to-default. Prompt
  edits are a config change: logged, versioned in state, and announced
  in the UI. An edited judge prompt must re-run the golden set before
  advisory mode re-enables (FIREWALL.md §5: model-or-prompt change
  blocks on golden regression).

## Addendum (2026-10-04): case-management + mapping layer

The user added a case layer: entity model (traces → agents → swarms →
collections), local SQLite DB, auto indicator extraction on trace add,
Obsidian-style graph view, SPEC.md + RATIONALE.md. Grading against the
12 objections:

- **#2 (poisoning) — stays closed.** Extraction is offline regex over
  a human-added trace; extracted indicators populate the case DB only.
  The load-bearing invariant is **indicators ≠ IOCs**: nothing in the
  extraction path writes to the IOC list or the review queue. IOC
  promotion still requires the human review queue. If extraction ever
  feeds candidates anywhere, re-grade this objection.
- **#9 (no consumer) — strengthened.** The case DB is the consumer's
  workspace: hits now have somewhere to go (trace entities linked to
  hunts), which is what the original objection asked for.
- **#10 (operational reality) — new residual.** The DB file
  (`state/tracehound.db`) needs a backup story: export on demand +
  documented restore. Corruption handling: SQLite is single-writer
  here (one human), so WAL + periodic export suffices; state this in
  SPEC.md rather than building clustering nobody needs.
- **#1/#11 (private deployment) — unchanged, still conditional.**
  The DB concentrates IOCs, indicators, and case notes on one disk.
  Private deployment covers it; the DB must never sync, export, or
  back up to any shared location without the operator's explicit act.
- **#5 (firewall) — not applicable.** No LLM touches extraction; it
  is deterministic regex. Nothing to inject into.
- **Graph view — no new attack surface.** Read-only visualization
  over the local DB; click-to-detail renders the entity's own stored
  fields. No network, no promotion path.
- **CRUD discipline — hunting-dog consistent.** All entity writes are
  human-initiated (GUI forms, chat intents, `case` subcommands). There
  is no autonomous entity creation; the only automatic write is
  indicator extraction from a trace the human just added, which is
  assistive, not autonomous.

## What the build must still prove

1. Objection #8 in code (HTTP-status handling) — the one fully OPEN item.
2. The "FIXED BY DESIGN" four (4, 5, 6, 7) verified by reading the
   implementation, not the docs.
3. The residuals: operator named (#10), high-precision default seed
   subset (#9), `SKILL.md` rewritten to the single threat model (#12).
4. Addendum invariants: chat never promotes (code read), prompt edits
  re-run the golden set, inline accept shares the decision endpoint.
5. Case-layer invariants: indicators≠IOCs enforced in code (extraction
   writes to the case DB only), all SQL parameterized, DB export/
   backup documented in SPEC.md.
