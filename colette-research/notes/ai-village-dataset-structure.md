# AI Village dataset: structure report

Inspection date: 2026-10-03.
Dataset: `aidigestorg/ai-village`.
Observed revision: `838b4150303ca8228e8edb432d8b8ccae353d258`.[1]
Hub modification time: `2026-09-20T13:54:41.000Z`.[1]

## 1. Result and evidence boundary

Treat this dataset as related database tables, not one conversation corpus.[3]
Its main components cover activity, chat, computer use, memory, goals, and agent metadata.[3]
A second execution path records Claude Code sessions and messages.[3]
Screenshots occupy separate daily tar archives.[3]

The current revision contains 13 table files and 369 screenshot archives.[2]
Current file sizes total 176.865 GB, or 164.719 GiB.[2]
Non-image files total 5.405 GiB.[2]
Screenshots and their index account for 96.72% of current file bytes.[2]

This inspection covers public metadata and the user-downloaded schema, changelog, and manifest.
All three reference bodies match the observed revision's Git blob identifiers.[1]
The manifest records export time `2026-09-20T13:05:12.097Z`.[7]
Raw table records remain uninspected.
Hermes filters `HF_TOKEN` from tool processes as a protected provider credential.
The user retrieved the reference files outside the agent's tool environment.

Use manifest-declared counts instead of stale card and schema estimates.[3][5][7]
The manifest declares 3,646,304 rows across 13 tables.[7]
This sum is not a count of unique actions or interactions.
No raw row count was independently recounted.
Do not treat this report as a distribution, completeness, or behavior analysis.

## 2. Physical layout and exact file census

The recursive Hub listing returned 392 entries without a continuation link.[2]
These comprise 390 files and two directories.[2]
The independent metadata listing agrees on every file path and size.[1][2]

| Component | Files | Exact bytes |
| --- | ---: | ---: |
| Gzipped JSONL tables | 13 | 5,441,682,570 |
| All non-image files, including tables | 20 | 5,803,978,687 |
| Screenshot tars and image index | 370 | 171,061,391,125 |
| Complete current file tree | 390 | 176,865,369,812 |

The non-image subtotal includes the table subtotal.
Do not add these overlapping rows.

Each table uses one gzip file with one JSON object per line.[3]
The card declares one Hugging Face configuration per table.[1]
It does not declare separate benchmark train, validation, and test files.[1][2]
The card's loader example uses the `train` split.[3]
This name does not establish an experimental train/test partition.

Auxiliary root files include `README.md`, `SCHEMA.md`, `CHANGELOG.md`, `manifest.json`, `example.py`, and `.gitattributes`.[2]
`village-transcript.json` provides a separate, readable chat and activity export.[3]
It contains 362,235,443 file bytes, approximately 345.455 MiB.[2]
The upstream schema defines one transcript object with `village`, `dateRange`, and `days`.[5]
Each day contains `day`, `date`, and `events`.[5]
Each event carries an ISO timestamp, UTC clock time, type, and type-dependent fields.[5]
The transcript renders `events` and `chat_messages`; those tables remain the declared source of truth.[5]
Analyses MUST NOT count both representations as independent events.
The transcript body itself was not inspected.

Hub metadata reports `usedStorage` as 392,608,511,991 bytes.[1]
This differs from the current file-tree total.[1][2]
Use the file-tree total for the snapshot's logical file size.
The cause of this storage difference was not established.
Transfer, caching, and unpacking costs can differ from logical file size.

## 3. Table inventory

The manifest supplies exact declared export counts, not independently measured counts.[7]
The card and schema retain older estimates despite sharing this revision.[3][5][7]
Exact compressed file bytes come from the current repository listing.[2]

| Table | Manifest rows | Card-stated rows | Compressed bytes | Role |
| --- | ---: | ---: | ---: | --- |
| `agent_goals` | 33 | Not stated | 3,973 | Individual goal definitions and optional time bounds |
| `agent_memories` | 246,151 | ~165k | 2,438,234,633 | Agent-authored consolidation memories |
| `agents` | 46 | 31 | 5,280 | Agent identity, model, state, and token usage |
| `chat_messages` | 183,485 | ~123k | 52,543,996 | Agent and human messages |
| `chat_rooms` | 16 | 5 | 1,711 | Room definitions and routing metadata |
| `claude_code_messages` | 244,820 | ~245k | 104,002,877 | Claude Code SDK message stream |
| `claude_code_sessions` | 303 | ~300 | 12,662 | Claude Code SDK session records |
| `computer_use_sessions` | 78,362 | ~37k | 40,080,397 | Computer sessions and stated goals |
| `computer_use_turns` | 2,510,487 | ~1.14M | 2,475,319,119 | Actions, provider messages, and tool outputs |
| `events` | 381,610 | ~233k | 328,621,853 | Ordered village activity timeline |
| `summaries` | 939 | ~800 | 2,851,293 | Generated daily, agent, and goal summaries |
| `village_goals` | 51 | ~45 | 4,449 | Village-wide goal intervals |
| `villages` | 1 | 1 | 327 | Village metadata and current state |

The changelog roster also contains 46 entries.[6]
The schema still describes 31 agents and five rooms.[5]
Treat those prose counts as stale reference text, not alternate current censuses.[5][7]

`computer_use_turns` and `agent_memories` account for 90.29% of compressed table bytes.[2]
Their combined size makes indiscriminate full downloads expensive.[2]
For chat-oriented structure work, start with `events` and `chat_messages`.[3]
For action-level work, add sessions and turns.[3]
For longitudinal self-description, add memories and goals.[3]

## 4. Relationship map

The upstream schema confirms the main agent, room, event, and session relationships.[5]
The local contract supplements field-level join annotations.[4]
These references do not constitute independently verified foreign-key integrity.

| Source field | Target field | Structural use |
| --- | --- | --- |
| `computer_use_sessions.agent_id` | `agents.id` | Assign a computer session to an agent |
| `computer_use_turns.session_id` | `computer_use_sessions.id` | Reconstruct turns within a session |
| `chat_messages.agent_speaker_id` | `agents.id` | Identify an agent speaker |
| `chat_messages.room_id` | `chat_rooms.id` | Identify the message room |
| `agent_memories.agent_id` | `agents.id` | Track an agent's memory snapshots |
| `agent_goals.agent_id` | `agents.id` | Associate individual goals |
| `claude_code_sessions.agent_id` | `agents.id` | Associate the alternative execution path |
| `claude_code_messages.agent_id` | `agents.id` | Identify the message-producing agent |
| `claude_code_messages.sdk_session_id` | `claude_code_sessions.sdk_session_id` | Link SDK messages to SDK sessions |
| `events.data.messageId` | `chat_messages.id` | Link eligible timeline events to chat |
| `events.data.computerUseSessionId` | `computer_use_sessions.id` | Link eligible timeline events to computer sessions |
| `events.data.agentId` or `speakerId` | `agents.id` | Resolve eligible event actors |
| `events.data.roomId` | `chat_rooms.id` | Resolve eligible event rooms |

Do not join Claude Code messages to the database session `id`.[4][5]
Use `sdk_session_id` for that relationship.[5]
Do not assume every event includes every reference.[5]
Event fields depend on `data.actionType`.[5]

Several tables carry `village_id`, but the contract does not annotate every village relationship.[4]
Treat links to `villages.id` as candidates until validation proves them.
Human chat uses `speaker_type` and nullable `user_speaker_id`.[4]
The publisher excludes viewer-account tables.[3]
Do not attempt to reconstruct human identities.

Agent fields such as `current_room_id` represent pointers at export time.[5]
They MUST NOT substitute for historical room membership.
Goal tables carry optional interval boundaries.[5]
Do not assume a direct goal foreign key exists on each turn.

The publisher exports tables sequentially from a live database.[5]
Parent tables follow referencing tables; the publisher states that foreign keys resolve.[5]
Some late-created parents can lack children.[5]
This report has not independently tested that integrity claim.

## 5. Record shapes and parser boundaries

### Activity timeline

`events` uses `id`, `event_index`, `created_at`, and nested `data`.[5]
The publisher describes `event_index` as unique, increasing, and canonical for ordering.[5]
The nested payload uses camelCase fields, unlike many snake_case table columns.[5]

The upstream schema documents these action types:[5]

    AGENT_TALK, USER_TALK
    START_USING_COMPUTER, STOP_USING_COMPUTER
    CONSOLIDATE, WAIT, PAUSE, SEARCH_HISTORY, ENTER_ROOM
    REQUEST_HUMAN_HELPER, CANCEL_REQUEST_FOR_HUMAN_HELPER
    STOP_HUMAN_USE_SESSION
    REQUEST_GOOGLE_SIGN_IN, RESTARTING_AFTER_GOOGLE_SIGN_IN
    OUTREACH_APPROVAL_REQUEST, OUTREACH_APPROVAL_RESPONSE
    USER_NAME_CHANGE

This list is not an observed action-frequency census.
Unknown action types and fields remain permitted by the local contract.[4]
Parsers SHOULD preserve them rather than reject or discard them.

### Computer use and Claude Code

`computer_use_turns.agent_action` permits an object or null.[5]
`agent_messages` permits an object or array, depending on the provider.[5]
`output`, `error`, and `system` permit strings or null.[5]
Do not assume one provider-neutral message envelope.
Anthropic responses use content blocks, including thinking, text, and tool use.[5]
OpenAI Responses uses item lists, while chat completions use another response shape.[5]
Gemini uses candidates and parts; `thought: true` marks reasoning.[5]
Both turn messages and event `data.output` can carry provider-shaped responses.[5]
Do not infer successful execution from an agent's statement.[3]
The upstream schema explicitly defines `error` as tool stderr/errors.[5]
The repository replay implementation therefore does not treat nonempty stderr as proof of failure.
See `src/swarm_forensics/replay.py:201-206` for that interpretation.
The schema's approximate null-output rate was not measured here.

Claude Code messages instead use `message_type`, `message_subtype`, and object-valued `content`.[5]
User-type SDK messages can include tool results.[5]
The publisher attributes this stream to one Opus 4.5 Claude Code agent.[5]
Its documented participation spans 2026-01-26 through 2026-04-02.[5][6]
Preserve this separate execution schema.
Do not force it into the computer-turn schema without an explicit adapter.

### Memory, goals, summaries, and state

Memories store agent-authored consolidation content.[3]
They record self-description, not an independent account of events.
Summaries cover days, agents, and goals.[3]
The publisher states that summary generation did not inspect computer-session internals.[3]
Treat summaries as secondary evidence.[3]

The agent table includes model strings, participation flags, and token counters.[5]
The publisher warns that lifetime token counters are not reliably maintained for every agent.[5]
These fields alone do not reconstruct historical model assignments.
The summary schema includes legacy day-number targets and newer Pacific-date daily keys.[5]
Parsers MUST NOT interpret every `summary_target` as the same identifier type.

### Structural regimes from the changelog

The changelog documents prompt, tool, memory, schedule, and visibility changes.[6]
It is LLM-written from private Git history; its dates record main-branch changes.[6]
Treat it as publisher-supplied history, not direct access to scaffolding code.

| Date or interval | Documented change | Consequence for analysis |
| --- | --- | --- |
| 2025-05-02 | Chatting during computer use introduced | Social/computer interleaving changes |
| 2026-01-26 to 2026-04-02 | Claude Code agent participation | Compare this execution path separately |
| 2026-02-10 | Automatic idle-detection nudger introduced | Some corrective messages are scaffolding-generated |
| 2026-02-25 | Rooms filter messages and membership context | Co-presence in the archive does not prove mutual visibility |
| 2026-03-11 to 2026-03-24 | Permanent computer use and consolidation introduced | Session boundaries change their meaning |
| 2026-06-03 | Parallel Anthropic tool use disabled | Turn/action correspondence changes |
| 2026-06-11 | Unseen-event context capped at 200 events | Retained archive history can exceed an agent's visible context |
| 2026-06-29 | Daily hours expand; shared hosting moves to GitLab | Exposure time and artifact locations change |
| 2026-07-03 | Individual goals added; consolidation-goal disclosure reduced | Public intentions no longer capture all goal context |

All dated changes above come from the upstream changelog.[6]
The schema identifies 2026-03-24 as the permanent-computer-use change.[5]
Agents subsequently consolidate after approximately 40 actions and start fresh sessions.[5]
Later sessions can therefore represent context resets, not newly chosen independent tasks.[5][6]
Analysts MUST NOT compare session counts across this boundary without accounting for the changed unit.

Rooms limit what each agent sees after 2026-02-25.[6]
Individual goals are not shown to other agents after their introduction.[6]
The full retained transcript therefore does not establish any agent's complete perceived world.

Memory mechanics also changed: retention prompts, consolidation reasoning, and timestamp handling received edits or fixes.[6]
The 2026-03-26 change removed a contradictory instruction against updating memory.[6]
The 2026-06-01 fix corrected messages appearing one turn early.[6]
Memory-fidelity comparisons SHOULD remain within documented regimes before making cross-regime claims.

## 6. Time and screenshot structure

The experiment began on 2025-04-02.[3]
Listed screenshot archive names span 2025-04-02 through 2026-08-21.[2]
The Hub revision was modified on 2026-09-20.[1]
The manifest records a 2026-09-20 export.[7]
These dates describe different boundaries.
The latest event, chat, and memory timestamps remain unknown.
The screenshot listing ends before the manifest export date.[2][7]
Screenshot coverage for later table records therefore requires a separate completeness check.
Do not assume the September export includes screenshots through September.

The listing contains 369 archive dates across a 507-day calendar interval.[2]
It therefore lacks archives for 138 dates within that interval.[2]
Most listed dates are weekdays; six occur on weekends.[2]
The publisher states that village day numbering skips most weekends.[3]
Absent archive dates do not establish missing records or failed exports.

Archive names use Pacific dates, derived from each turn's UTC `created_at`.[3]
Use `America/Los_Angeles`, including daylight-saving rules.[3]
The schema defines table timestamps as UTC strings without timezone suffixes, with microsecond precision.[5]
Parsers MUST attach UTC explicitly before converting those timestamps to local dates.
An archive contains screenshot entries named `<turn_id>.png`.[3]
`images/computer-use-turns/index.json` records daily turn and image counts.[3]
Its listed file size is 20,245 bytes.[2]
Its contents were not fetched because repository rules exclude `images/`.

Talk-only turns can lack screenshots.[3]
Redacted screenshots can be placeholders rather than original evidence.[3]
Do not equate turns, screenshot entries, and usable images.
No screenshot was downloaded or inspected.

### Monthly archive footprint

These counts describe archive files, not turns, images, or activity intensity.[2]
GiB values use the listed tar sizes.[2]

| Pacific month | Daily tars | Listed tar GiB |
| --- | ---: | ---: |
| 2025-04 | 23 | 2.794 |
| 2025-05 | 24 | 2.098 |
| 2025-06 | 22 | 3.050 |
| 2025-07 | 23 | 3.790 |
| 2025-08 | 21 | 4.162 |
| 2025-09 | 22 | 4.364 |
| 2025-10 | 23 | 4.741 |
| 2025-11 | 20 | 7.194 |
| 2025-12 | 23 | 10.961 |
| 2026-01 | 22 | 7.044 |
| 2026-02 | 20 | 9.147 |
| 2026-03 | 22 | 9.101 |
| 2026-04 | 22 | 11.376 |
| 2026-05 | 21 | 10.048 |
| 2026-06 | 23 | 21.117 |
| 2026-07 | 23 | 30.615 |
| 2026-08 | 15 | 17.711 |

The late-period byte increase does not establish increased collaboration or agent productivity.
Image dimensions, screenshot frequency, and agent population could affect the footprint.
The 2026-06-29 schedule expansion supplies a documented exposure-time confounder.[6]
Its contribution to archive sizes remains unmeasured.

## 7. Provenance and evidence limits

The publisher describes a near-verbatim database export with selected removals.[3]
The surrounding scaffolding source is not public.[3]
Raw `llm_calls`, exact prompts, operational tables, and viewer accounts are excluded.[3]
Do not describe this as a complete record of model context.

The export replaces detected secrets and infrastructure addresses with `[REDACTED]`.[3]
It replaces embedded images with `[IMAGE_REMOVED]` and large opaque blobs with `[BLOB_REMOVED]`.[3]
The manifest lists dropped screenshot bytes, redaction reasons, and agent infrastructure-address columns.[7]
Redaction remains best effort, not a guarantee.[3]
Researchers MUST NOT use recovered credentials or attempt re-identification.[3]

The gate requires manual research-access review.[1][3]
Training or fine-tuning requires written permission.[3]
Resulting work MUST cite AI Digest / AI Village.[3]
The access terms also request notification about publications.[3]

This structure supports coordination research, but does not directly label collaboration outcomes.
Chat, attempted actions, memory, and returned effects require separate evidential treatment.
A shared-artifact graph would require extraction from actions, outputs, and messages.
The current file tree contains no separate shared-artifact table.[2]
Do not infer a shared filesystem snapshot or document history from this export.

## 8. Local repository findings

The local contract covers all 13 declared table configurations.[1][4]
It records the same upstream revision as the current Hub snapshot.[1][4]
It permits unknown fields and constrains required fields narrowly.[4]

The ingest module records earlier schema omissions:

- `chat_rooms.blacklisted_agent_names` and `whitelisted_agent_names`.
- `villages.is_chat_open` and `schedule`.
- `claude_code_messages.message_uuid`.

See `src/swarm_forensics/ingest/MODULE.md` for their historical provenance.
The newly inspected upstream schema still omits these local-contract extensions.[4][5]
The local contract includes those fields.[4]
Contract validity does not prove foreign-key integrity, completeness, or event ordering.

The module previously reported a completed download and bounded real-data validation.
Those are historical reports, not reproduced results from this session.
This checkout still lacks the root raw table files.
The user supplied the three upstream reference files through `make data-schema`.
Its retained raw data includes synthetic samples and unrelated watcher archives.
The module now distinguishes historical claims from the current inspection.

## 9. Recommended next inspection

The user-side reference download demonstrates access to the gated reference files.
Raw-record inspection still requires an authorized table download.
Provide credentials through supported local mechanisms, never through research notes or chat.
Hermes protects `HF_TOKEN` as a provider credential and excludes it from tool processes.
Do not disable credential filtering or rename that protected secret to evade the boundary.
Run existing acquisition commands through the root Makefile.
Use `make data-info REVISION=838b4150303ca8228e8edb432d8b8ccae353d258` to reconfirm file sizes.
The three reference files already match that revision.
Do not start bulk downloads without a separate user request.
Screenshots remain outside the repository's allowed acquisition scope.

Once authorized data exists, stream each gzip file one line at a time.
Do not copy the card's full-table list-comprehension example into production analysis.

The next census SHOULD measure:

1. Independently recounted rows and timestamp bounds per table, compared with manifest counts.
2. Missing fields, nulls, and provider-specific payload shapes.
3. Duplicate record identifiers and non-monotonic event indices.
4. Unresolved agent, room, session, and SDK-session references.
5. Chat/event overlap without duplicate counting.
6. Goal intervals and scaffolding epochs.
7. Screenshot availability and redaction coverage, only after separate scope approval.

These checks remain unperformed.

## 10. Deliverables and verification

- Report: `colette-research/notes/ai-village-dataset-structure.md`.
- Derived census: `colette-research/sources/ai-village-structure/census.json`.
- Citation ledger: `colette-research/sources/ai-village-structure/citation-ledger.json`.
- Raw public evidence: ignored `data/raw/ai-village-structure/`.
- Upstream reference bodies: ignored `data/raw/SCHEMA.md`, `CHANGELOG.md`, and `manifest.json`.

The census retains every listed file path and byte size.
It also retains monthly archive totals and local field definitions.
It now includes manifest counts, reference hashes, and documented structural regimes.
Raw public evidence remains outside tracked research artifacts.
The ledger preserves exact evidence excerpts and source identities.

Verified: independent public listings agree on all 390 files.
Verified: all 13 configurations match table filenames and local contract names.
Verified: local contract revision matches the current Hub revision.
Verified: all three downloaded references match revision-specific Git blob identifiers.
Verified: manifest table names match all 13 configurations; declared rows sum to 3,646,304.
Verified: the latest `make test` run passes 164 tests. Concurrent implementation changes remain outside this research update.
Verified: `make lint` passes.
Blocked: agent-side authenticated acquisition cannot receive the protected `HF_TOKEN` credential.
Not performed: raw row inspection and screenshot inspection.

## Sources

[1] https://huggingface.co/api/datasets/aidigestorg/ai-village?blobs=true — AI Village public Hub metadata
[2] https://huggingface.co/api/datasets/aidigestorg/ai-village/tree/main?recursive=true&expand=false&limit=1000 — AI Village public Hub metadata
[3] https://huggingface.co/datasets/aidigestorg/ai-village — AI Village dataset card
[4] file:///home/resonatingloop/.resonance/exoresonance/swarm-forensics/src/swarm_forensics/ingest/dataset.schema.json — Repository AI Village record contract; prior derivation, not fresh row inspection
[5] https://huggingface.co/datasets/aidigestorg/ai-village/blob/838b4150303ca8228e8edb432d8b8ccae353d258/SCHEMA.md — AI Village upstream SCHEMA.md; locally retrieved body
[6] https://huggingface.co/datasets/aidigestorg/ai-village/blob/838b4150303ca8228e8edb432d8b8ccae353d258/CHANGELOG.md — AI Village upstream CHANGELOG.md; locally retrieved body
[7] https://huggingface.co/datasets/aidigestorg/ai-village/blob/838b4150303ca8228e8edb432d8b8ccae353d258/manifest.json — AI Village upstream manifest.json; locally retrieved body
