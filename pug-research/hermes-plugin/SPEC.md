# Swarm Forensics case-management layer — SPEC

Date: 2026-10-04. Worker: 5 (case management + mapping layer).
Scope: the analyst workspace for SWARM hunting. Read `MODULE.md`
first for the invariants this spec must not break.

Language: Simplified Technical English. RFC 2119 keywords state
requirements.

## 1. Architecture

The case layer sits BESIDE the hunt pipeline, not inside it. The
pipeline (hunts, hits, IOC working list, review queue) is unchanged:
its stores stay JSONL (`state/jobs/`, `state/hits/`, `state/iocs.json`,
`state/review.json`). The case layer is a SQLite DB
(`state/swarm-forensics.db`) that records what the HUMAN concludes: which
traces belong to which agents, which agents form a swarm, and what
indicators each trace contains.

Data flows one way: hunt output -> human -> case DB. The case DB
never writes back into the pipeline. A trace entity MAY store its
hunt job id in `data_json`; this is a link, not a join. The backend
(`dashboard/plugin_api.py`) is the single enforcement point for
both the GUI and the CLI, as before.

Nothing in the case layer runs on its own. Every write is a human
action: a GUI form submit, a palette command, or a CLI invocation.
There is no scheduler, no cron, no watcher. The DB file is created
lazily on first write.

## 2. Entity model

Four entity types:

- `trace` — one observed agent trace (a report, a URL set, a text
  excerpt). Holds extracted indicators.
- `agent` — a hypothesized agent instance.
- `swarm` — a group of agents acting together.
- `collection` — a bucket for a hunt, an incident, or a dataset.

Four relationship kinds: `trace_of` (trace -> agent),
`member_of` (agent -> swarm), `part_of` (anything -> collection),
`related` (anything -> anything).

Five indicator kinds: `url`, `domain`, `nonce`, `relay`, `hash`.
Indicators attach to trace entities only.

INVARIANT (adversarial #2 stays closed): extracted indicators are
NOT IOCs. Extraction populates the case DB only. No path in this
layer promotes, demotes, or edits the IOC list. IOC promotion still
requires a human decision in the review queue (`iocs.py`). This
invariant is enforced in code (`cases.py` module docstring and
`delete_entity`) and stated in the GUI.

## 3. Database DDL and migration policy

File: `state/swarm-forensics.db`. Library: stdlib `sqlite3` only.

```sql
CREATE TABLE entities(
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL CHECK(type IN ('trace','agent','swarm','collection')),
    label TEXT NOT NULL,
    data_json TEXT,
    provenance TEXT,
    created_utc TEXT NOT NULL);

CREATE TABLE relationships(
    id TEXT PRIMARY KEY,
    from_id TEXT NOT NULL,
    to_id TEXT NOT NULL,
    rel TEXT NOT NULL
        CHECK(rel IN ('trace_of','member_of','part_of','related')),
    created_utc TEXT NOT NULL);
CREATE INDEX idx_rel_from ON relationships(from_id);
CREATE INDEX idx_rel_to ON relationships(to_id);

CREATE TABLE indicators(
    id TEXT PRIMARY KEY,
    trace_id TEXT NOT NULL,
    kind TEXT NOT NULL
        CHECK(kind IN ('url','domain','nonce','relay','hash')),
    value TEXT NOT NULL,
    created_utc TEXT NOT NULL);
CREATE INDEX idx_ind_trace ON indicators(trace_id);

CREATE TABLE schema_version(version INT NOT NULL);
```

Migration policy:

- `SCHEMA_VERSION = 1` in `cases.py`. The module is authoritative;
  this spec mirrors it.
- `migrate(conn)` reads `schema_version`. A DB without the version
  table is version 0. Migrations apply in order, each idempotent.
- Migration 0->1 builds the full schema above. A pre-migration
  `entities(id, type, label)` table keeps its rows; missing columns
  are added with `ALTER TABLE`, never rebuilt.
- `connect()` always runs `migrate()`. Callers never see an old schema.

Safety invariant: every SQL statement uses `?` placeholders. No
string interpolation into SQL, ever. Trace text is untrusted input
and enters only as bound parameters.

Module: `skills/swarm-forensics/scripts/lib/cases.py`. Functions:

- `connect(path=None, cfg=None)` — open + migrate. With `cfg`,
  the path resolves via `config.state_path(cfg, "swarm-forensics.db")`.
- `add_entity`, `get_entity`, `list_entities(type?)`,
  `update_entity`, `delete_entity`.
- `link(from_id, to_id, rel)`, `unlink(id)`, `neighbors(id)`,
  `graph()`.
- `extract_indicators(trace_text)` -> list of `(kind, value)`.
  Pure regex. Offline. No network, no model.
- `add_trace(label, trace_text, provenance, job_id)` — inserts the
  trace and runs extraction automatically.
- `add_indicator`, `list_indicators`.

`delete_entity` removes the entity, its relationships (both
directions), and its indicators. It never touches the IOC list:
the DB holds no reference to it, so deletion cannot affect it.

## 4. Indicator extraction

`extract_indicators` finds, in first-appearance order, duplicates
collapsed:

- `url` — `https?://` tokens (trailing punctuation stripped).
- `domain` — the host of each found URL (lowercased).
- `nonce` — `zz=oai<digits>`, `zzbulk=<alnum>`,
  `prepnonce=<hex>`, `fresh=x<epoch>.<rand>`.
- `relay` — known relay hosts, matched against the relay inventory
  from `predict.py`'s grammar slots (fallback:
  `jqp.vercel.app`, `allorigins.hexlet.app`, `r.jina.ai`).
- `hash` — md5 / sha1 / sha256 hex strings (32 / 40 / 64).

The relay inventory is read from the same grammar file the
predictor uses, so extraction and prediction agree on what a
relay is.

## 5. Backend endpoints

Namespace: `/api/plugins/swarm-forensics`. All follow the existing
conventions (`_send`, `_body`, `_path`; 400 on bad input, 404 on
unknown id, 500 never leaks a traceback).

- `GET /cases/entities?type=` — list, newest first.
- `POST /cases/entities` — body `{type, label, data?, provenance?,
  trace_text?, job_id?}`. A `trace` with `trace_text` runs
  extraction on save. Returns 201.
- `GET /cases/entities/<id>` — entity + indicators + links +
  adjacent entities.
- `PUT /cases/entities/<id>` — body `{label?, data?, provenance?}`.
- `DELETE /cases/entities/<id>` — cascade delete (see §3).
- `POST /cases/link` — body `{from_id, to_id, rel}`. Both entities
  must exist. Returns 201.
- `DELETE /cases/link/<id>`.
- `GET /cases/graph` — `{nodes:[{id,type,label}],
  edges:[{id,from,to,rel}]}`.
- `POST /cases/extract` — body `{trace_text}`. Returns indicator
  preview. Read-only: nothing is saved.

The case layer is an optional import. When `cases.py` is absent,
every `/cases` endpoint returns 404 with "case layer unavailable".
`/diagnostics` reports `worker5_cases: present|missing`.

## 6. UI structure

Routes (after Review Queue, before IOC List):

- `/swarm-forensics/cases` — entity CRUD. List with type filter and
  label search. "New entity" dialog: type, label, provenance; for
  traces, a text area, an optional hunt job id, and a "Preview
  indicators" button that calls `POST /cases/extract` before
  saving. Per-entity detail: rename, provenance, hunt job link,
  indicator list (with the indicators-are-not-IOCs note), links
  with unlink buttons, link adder (target select + rel select),
  delete with inline confirm.
- `/swarm-forensics/graph` — the Obsidian-style view. SVG rendered with
  `jsx()`. No imports beyond `react`, `react/jsx-runtime`,
  `@hermes/plugin-sdk`.

Graph interactions:

- Pan: drag the background (pointer events).
- Zoom: wheel around the cursor (0.3x–3x). The wheel listener is
  added with `{ passive: false }` so the page does not scroll.
- Click a node (drag threshold 6 px distinguishes click from pan):
  opens the detail panel.
- Filter: per-type checkboxes hide node types (edges follow).
- "Reset view" restores pan/zoom/selection.

Layout (force-lite, documented in code):

1. Seed: nodes on a circle. Node order is stable, so the layout
   is deterministic across reloads.
2. 90 iterations: pairwise Coulomb-style repulsion (O(n^2); the
   case DB is human-curated, so n stays small), Hooke springs
   along edges toward a 150 px rest length, weak gravity to the
   center. The step cap shrinks linearly per iteration.
3. Freeze. No animation loop, no physics engine.

SDK conformance: the graph needs no documented gesture surface.
Routes, sidebar rows, and palette commands use `ROUTES_AREA`,
`SIDEBAR_NAV_AREA`, and `PALETTE_AREA` per HERMES_DESKTOP.md §1.
No required interaction lacks a documented SDK path, so no
`[INF]` gap is marked for the graph.

Palette commands:

- `swarm-forensics: Open case graph` -> `/swarm-forensics/graph`.
- `swarm-forensics: New case entity…` -> sets a store flag, then
  navigates to `/swarm-forensics/cases`, which opens the dialog.

## 7. Command grammar

`swarm_forensics.py case …` backs the `/swarm-forensics case …`
grammar. Added without touching existing subcommands.

- `case add <type> <label> [--text T] [--job J] [--provenance P]`
  — `--text` on a trace runs extraction; `--job` stores the hunt
  job id in `data_json`.
- `case link <from_id> <to_id> <rel>` — rel in
  `trace_of|member_of|part_of|related`.
- `case list [--type T]`.
- `case graph` — prints `open /swarm-forensics/graph in the desktop app`.

Deep links: `case add/list/link` -> `/swarm-forensics/cases`;
`case graph` -> `/swarm-forensics/graph`.

## 8. Hunting-dog interaction model

| Step | Human | Plugin |
|---|---|---|
| Start work | Opens the app; decides what to hunt. | Shows dashboard, hunts only when told. |
| Build a case | Creates entities, writes labels and provenance. | Stores them; extracts indicators from trace text. |
| Connect evidence | Draws links between entities. | Records links; renders the graph. |
| Promote an IOC | Clicks accept in the review queue, or `review accept`. | Never promotes on its own. Extraction cannot promote. |
| Stop | Cancels a hunt; deletes entities. | Stops after the current query; cascade-deletes. |

The plugin points, fetches, and files. The human decides.

## 9. Security posture

- Local-only DB. `state/swarm-forensics.db` lives under `state/`
  (untracked). Nothing syncs it anywhere.
- Parameterized SQL everywhere (§3 safety invariant). No string
  interpolation into SQL.
- Indicators ≠ IOCs (§2 invariant). Extraction writes to the case
  DB only; the review queue is the only promotion path, and it is
  human-gated.
- Private deployment only. Case data (trace text, labels,
  provenance) never leaves the operator's machine through this
  layer: no network calls exist in `cases.py`.
- No autonomous writes. Every mutation is a human-initiated GUI,
  palette, or CLI action. No cron, no watcher, no background job.
- Input validation at the boundary: entity types, rel kinds, and
  indicator kinds are CHECK-constrained in SQL and re-validated
  in Python; bad values return 400, never a traceback.
