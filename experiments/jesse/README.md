# Jesse: Discord Swarm

[Discord Swarm](discord-bot-swarm/README.md) provides authenticated MCP tools for private Discord channels.
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
Live Discord delivery and external coding clients remain unverified.
MCP currently requires an application login token.
Shared invitations and separate agent credentials remain unavailable.
See [MODULE.md](MODULE.md) for interfaces and constraints.
