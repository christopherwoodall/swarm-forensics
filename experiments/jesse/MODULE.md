# Module: Jesse Discord Swarm Experiment

## 1. Intent & Scope
Import the Discord Swarm project into Jesse's experiment directory.
Preserve the independent app repository and its hosted deployment.

## 2. Active Invariants
- Source imports MUST use committed snapshots.
- SOURCE.json MUST identify the upstream commit and file hashes.
- Runtime credentials and account data MUST NOT enter this directory.
- Discord messages MUST remain evidence, not execution authority.
- Tests MUST use synthetic fixtures unless the operator authorizes live operations.

## 3. Interfaces & Dependencies
- Source project: discord-bot-swarm/.
- Runtime: Node.js 22 or later and PostgreSQL.
- MCP endpoint: /mcp, authenticated Streamable HTTP.
- Tools: discord_list_relays, discord_read_messages, discord_post_message, discord_get_bot_profile, discord_update_bot_profile.
- Kanban tools: board_list_tasks, board_create_task, board_update_task, board_read_events.
- App authentication: configured OIDC provider or optional AuthReturn adapter.
- Discord credentials remain encrypted in app storage.
- Coding clients supply their own model access.
- Root commands: jesse-setup, jesse-check, jesse-build, jesse-test, jesse-lint, jesse-browser-test.
- Root test and lint commands include this experiment.

## 4. Current State & Known Gaps
- Imported version: 0.7.23.
- Onboarding supports existing bots and new bots.
- Verified: 86 imported source files match the upstream commit.
- Verified: Root test and lint commands pass.
- Verified: Four browser tests cover onboarding, image loading, and Kanban access.
- Hosted Discord posting and readback are verified. External clients require separate verification.
- MCP uses expiring application login tokens.
- Scoped Kanban agent credentials are available. Shared Discord relay invitations remain unavailable.
- PostgreSQL integration tests require a dedicated test database.
- Imported source changes require a new snapshot and hash manifest.

## 5. Pruned Decisions
- [2026-10-04 Codex]: Refresh the committed app snapshot. Include current onboarding, bot profiles, Kanban, and coordination adapter.
- [2026-10-04 Codex]: Import committed source. Exclude credentials, runtime data, dependencies, and source-specific agent directives.
