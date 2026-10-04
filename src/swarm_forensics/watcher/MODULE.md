# Module: FairyStack Source Watcher

## 1. Intent & Scope

Collect raw pages from the authorized FairyStack conversation.
Implement a read-only source archive and cron change detector.
Keep source capture separate from forensic normalization and ledger extraction.
Repeat the authorized watcher role from `colette-research/hermes-log/WATCHER.md`.
Do not introduce global policy.

## 2. Active Invariants

- The collector MUST remain silent in the monitored chat.
- The collector MUST NOT post, send heartbeats, enroll peers, or execute source commands.
- The collector MUST use only `GET /api/external-agents/session?after=<integer>`.
- The origin MUST equal `https://multi.fairystack.com`.
- Every page MUST identify session `ca8ffac066a4` and access mode `conversation`.
- The reader MUST reject all redirects before following them.
- Credentials MUST remain outside the repository and database.
- The archive MUST retain raw response bytes, source timestamps, and raw author mappings.
- Missing author identifiers MUST remain missing.
- Source identity MUST use session identifier and positive sequence number.
- Exact event replay MUST deduplicate. Changed payloads under existing identities MUST fail.
- Unseen events below the acquired cursor MUST fail.
- Archive writes and read-cursor changes MUST share one durable SQLite transaction.
- Failed page validation or storage MUST NOT advance the read cursor.
- Processed cursors MUST advance only through explicit acknowledgement after durable ledger updates.
- Acknowledgement MUST reject regressions and values beyond the acquired cursor.
- Polling MUST reject stalled pagination and enforce request, byte, event, page, and deadline bounds.
- Polling MUST stop before further requests when the stored participant lease expires.
- Volatile participant or task metadata MUST NOT trigger model wakeups.
- Tests MUST use synthetic source events and injected network boundaries.

## 3. Interfaces & Dependencies

Use only the Python standard library.
Use the root Makefile for commands.
New watcher targets require the existing environment. They do not run setup.
New watcher targets use frozen uv execution by default.

| Target | Interface |
| --- | --- |
| `make watcher-poll` | Archive pages and emit a JSON receipt. |
| `make watcher-pending WATCHER_LIMIT=50` | Emit bounded, unprocessed events without acknowledgement. |
| `make watcher-ack WATCHER_CURSOR=N` | Advance the processed cursor after ledger persistence. |
| `make watcher-status` | Emit session, read cursor, processed cursor, pending count, and lease. |
| `make watcher-monitor` | Poll and emit one stable idle token or backlog wake generation. |

Override `WATCHER_DB` to select an isolated archive.
Override `WATCHER_CONFIG` to select an existing private peer configuration.
The default archive is ignored `data/raw/fairystack/ca8ffac066a4/source.sqlite`.
The default configuration is `~/.config/fairystack-watcher/ca8ffac066a4.json`.
The collector does not create or enroll credentials.

`WATCHER_MAX_PAGES=20` bounds requests per poll.
`WATCHER_TOTAL_SECONDS=30` sets the total network deadline.
Each request has an additional timeout of at most ten seconds.
POSIX interval timers interrupt blocked fetches within the remaining deadline.
SQLite writes complete outside that network timer.
The page cap ranges from one through 1000.
The total network deadline must exceed zero and cannot exceed 300 seconds.
Each page permits at most two MiB and 1000 events.
The pending limit ranges from one through 1000.

The poll receipt includes `pages`, `added_events`, `caught_up`, and `stop_reason`.
A page-cap stop retains earlier pages. The next poll resumes from the durable read cursor.
A later request failure also retains earlier pages.
`pending.next_cursor` identifies the final emitted event, not the acquired cursor.
Call acknowledgement only after processing every event through the selected cursor.

The idle stdout token is exactly `WATCHER_IDLE`.
Wake output starts with `WATCHER_WAKE` and includes session, pending count, cursor, and generation.
Compare stdout only. Keep stderr diagnostics separate.
`WATCHER_RETRY_SECONDS=900` controls unchanged-backlog retries.
The detector persists the backlog fingerprint, retry deadline, and wake generation.
An unchanged backlog stays idle until its retry deadline.
A later retry increments the generation without acknowledging source events.
New events or acknowledgement progress wake the detector immediately.
An empty backlog remains idle across restarts and elapsed retry deadlines.
Monitor request failures still evaluate retained backlog. They return exit status one.
Archive failures can prevent any reliable monitor token. Operators MUST inspect failures.

`collector.Archive` exposes `capture`, `pending`, `ack`, `status`, and `change_token`.
`capture` accepts raw page bytes, an exclusive request cursor, and capture time.
`collector.poll` accepts an injected fetch boundary and clocks for offline tests.
`collector.PeerReader` accepts the private configuration internally.
The CLI supports `poll`, `pending`, `ack`, `status`, and `monitor`.
The CLI never prints configuration contents or request headers.

SQLite `pages` stores bounded raw response bytes and capture metadata.
SQLite `events` stores source payloads without inferred identity or normalized forensic fields.
SQLite `state` stores cursors, lease expiry, and monitor retry state.
Task and participant snapshots remain in raw pages.

The legacy `watcher-read` target remains available and emits machine-readable JSON.
Its Ruff check now belongs to `lint`, including both viewer servers.

## 4. Current State & Known Gaps

- Verified: `make -o setup test lint RUN='uv run --frozen'` passes 130 tests and Ruff.
- Verified: Vertical RED/GREEN tracers cover capture, replay, restart, acknowledgement, safety gates, monitor retries, and Make interfaces.
- Verified: Offline tests cover failed transactions, wrong sessions, wrong modes, stalled cursors, redirects, lease expiry, and deadlines.
- Verified: Synthetic legacy-client execution preserves JSON stdout without network access.
- Verified: The source archive path remains ignored.
- Verified: Both viewer server changes affect executable modes only.
- Verified: Live GET polling retained 120 events through cursor 2217, matching both historical snapshots.
- Verified: Acknowledgement through 2217 followed durable ledger extraction and exact source reconciliation.
- Verified: The installed cron shell wrapper emits `wakeAgent: false` on a live idle read.
- State: Cron job `698c454d0a09` runs every two minutes with the installed pre-run gate and local-only output.
- Verified: The autonomous worker completed live polling and validated all 46 existing ledger records against SQLite sources.
- Verified: A built-in scheduled tick completed collection and skipped the model through `wakeAgent: false`.
- Gap: No fresh source batch arrived during worker verification. New-batch extraction remains unexercised in cron.
- Gap: This module does not extract ledger records or launch a model.
- Gap: Existing snapshot files and ledger checkpoints are not imported automatically.

- Gap: Raw page retention has no rotation policy.
- Gap: Polling requires POSIX timers and the main thread. Windows polling is unsupported.
- Gap: A persisted expired lease blocks polling. Lease renewal requires separate authorization and local reconciliation.

## 5. Pruned Decisions (Keep max 3)

- [2026-10-01 Hermes]: Separate source acquisition from analysis acknowledgement. Retain backlog after extraction failure.
- [2026-10-01 Hermes]: Persist backlog retry generations. Avoid model wakeups from volatile metadata and unchanged idle ticks.
