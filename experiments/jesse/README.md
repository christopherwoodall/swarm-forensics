# Jesse: Discord Swarm

[Discord Swarm](discord-bot-swarm/README.md) provides authenticated MCP tools for Discord text channels.
The wizard supports existing bots and new bots.
Agents retain their own coding tools and model accounts.

Source: [QualityCopperShovel/discord-bot-swarm](https://github.com/QualityCopperShovel/discord-bot-swarm).
[SOURCE.json](SOURCE.json) records the imported commit and file hashes.
The hosted app remains at [Discord Swarm](https://discord-bot-swarm.multi.fairystack.com/).
This directory contains source only. It contains no account data or runtime credentials.
Parent repository directives apply. Source-specific agent directives are excluded.

Run these commands from the repository root:

```sh
make jesse-setup
make jesse-check
make jesse-build
make jesse-test
make jesse-browser-test
```

Browser tests use synthetic authentication and Discord responses.
Live Discord posting and readback were verified in the hosted app.
External coding clients require their own connection tests.
MCP accepts app identity tokens and expiring relay-scoped agent credentials.
Agents synchronize capabilities and owner settings through `discord_sync_agent`.
The runtime bridge enforces configured command budgets, rates, and deadlines.

Refresh the snapshot from a committed upstream revision:

```sh
make jesse-sync SOURCE_REPO=/path/to/discord-bot-swarm SOURCE_REV=<commit>
make test
make lint
```

Pushing the app repository does not update this snapshot.
Snapshot updates MUST pass tests and merge into this repository.
See [MODULE.md](MODULE.md) for interfaces and constraints.
