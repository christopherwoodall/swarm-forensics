# Module: Jesse Discord Swarm Experiment

## 1. Intent & Scope
Import the Discord Swarm project into Jesse's experiment directory.
Preserve the independent app repository and its hosted deployment.

## 2. Active Invariants
- Source imports MUST use committed snapshots.
- SOURCE.json MUST identify the upstream commit and file hashes.
- Runtime credentials and account data MUST NOT enter this directory.
- Discord messages MUST remain untrusted. Only explicitly enabled, owner-authorized commands MAY start bounded work.
- Tests MUST use synthetic fixtures unless the operator authorizes live operations.

## 3. Interfaces & Dependencies
- Source project: discord-bot-swarm/.
- Runtime: Node.js 22 or later and PostgreSQL.
- MCP endpoint: /mcp, authenticated Streamable HTTP.
- Discord tools include relay discovery, scoped chat, personality, profile, memory, and command coordination.
- Synchronization: swarm://agent-sync and discord_sync_agent.
- Native runtime bridge uses existing model access and private local configuration.
- Kanban tools: board_list_tasks, board_create_task, board_update_task, board_read_events.
- App authentication: configured OIDC provider or optional AuthReturn adapter.
- Discord credentials remain encrypted in app storage.
- Coding clients supply their own model access.
- Root commands: jesse-sync, jesse-setup, jesse-check, jesse-build, jesse-test, jesse-lint, jesse-browser-test.
- Root test and lint commands include this experiment.

## 4. Current State & Known Gaps
- Imported version: 0.16.2.
- Source revision: 42b2ce306ee84efc081e1dd1f69eb21c2127fe7b.
- Relay-scoped credentials use single-use setup token exchange.
- Shared boards follow Discord server membership and credential scope.
- Commands require owner opt-in and a separately installed native runtime bridge.
- Runtime budget uses minutes. It does not measure provider dollar charges.
- MCP synchronization preserves channel assignment, permissions, and saved preferences.
- Invalid MCP credentials return 401. Verification infrastructure failures return 503.
- PostgreSQL integration tests require a dedicated test database.
- App repository pushes do not refresh this snapshot. Use jesse-sync and merge the result.

## 5. Pruned Decisions
- [2026-10-04 Codex]: Add a repeatable committed snapshot import. Include MCP synchronization and bounded runtime commands.
- [2026-10-04 Codex]: Refresh the committed app snapshot. Include current onboarding, bot profiles, Kanban, and coordination adapter.
- [2026-10-04 Codex]: Import committed source. Exclude credentials, runtime data, dependencies, and source-specific agent directives.
