# Swarm Forensics (Hermes plugin)

An autonomous swarm hunter for Hermes desktop. An operator starts a hunt.
Hermes then searches the public web for agent traces until the operator
stops it. The plugin keeps what it finds in a local SQLite database:
events, evidence, IOCs, and an Obsidian-style graph of agents, swarms, and
cases.

## Install

From a checkout of this repository:

```
make hermes-install      # from the repository root
make install             # from pug-research/hermes-plugin
```

The target copies `plugins/swarm-forensics` into the Hermes home and runs
`hermes plugins enable swarm-forensics`. It picks the Hermes home in this
order: `HERMES_HOME`, the Windows desktop app (under WSL), then `~/.hermes`.
Restart the Hermes desktop app afterward so the backend routes mount.

```
HERMES_HOME=/path/to/hermes make hermes-install   # explicit target
make hermes-uninstall                             # keeps the database
```

One-click link (resolves only after the plugin is on the default branch):

```
hermes://plugin/install?repo=christopherwoodall/swarm-forensics/pug-research/hermes-plugin/plugins/swarm-forensics&enable=1
```

## Use

Open **Swarm Forensics** in the desktop app, or use the command:

| Command | Effect |
|---|---|
| `/swarm-forensics start [goal]` | Start a hunt. It runs until you stop it. |
| `/swarm-forensics pause`, `resume [id]`, `stop` | Control the hunt. |
| `/swarm-forensics status` | Show hunt state and totals. |
| `/swarm-forensics review` | List proposed IOC terms. |
| `/swarm-forensics accept\|reject <id>`, `narrow <id> <term>` | Decide an IOC. |
| `/swarm-forensics find <text>` | Search agents, swarms, and cases. |
| `/swarm-forensics settings [key [value]]` | Read or change a setting. |

Desktop pages: Hunt, Knowledge (graph and notes), Evidence, IOCs, Settings.

## How a hunt works

Each cycle runs these steps. The loop repeats until the operator stops it.

1. **Plan.** Hermes proposes search queries from past findings and open leads.
2. **Search.** The plugin runs the queries through Hermes `web_search` and the
   public indexes (urlquery, Wayback CDX, arquivo.pt).
3. **Read.** Hermes `web_extract` reads promising pages.
4. **Analyze.** The model proposes entities, links, IOC terms, and new leads.
5. **Record.** The plugin writes evidence, entities, and proposals to the
   database. New leads feed the next cycle.

## Safety model

- The model proposes. Policy and the operator decide.
- Fetched text is untrusted. The plugin fences it and screens it for
  injection phrasing. Tainted evidence never supports an IOC promotion.
- IOC promotion is `manual` by default. `automatic` mode needs minimum
  evidence, distinct hosts, claim level, and a daily cap. Every change is
  audited.
- Schedules are off. The operator arms each one. Scheduled hunts run only
  while the desktop app is open.
- A hunt stops when the app closes. After a restart a hunt is `paused`, and
  the operator resumes it.
- Index sources use a fixed host allowlist. Credentials are redacted before
  any write.
- Scope is agents and public evidence. No operator attribution.

## Data

The database lives at `<hermes home>/swarm-forensics/swarm-forensics.db`.
Override the folder with `SWARM_FORENSICS_STATE_DIR`. State from the first
(CLI) version is imported once, read-only.

## Develop

```
make hermes-test     # offline tests, synthetic data, no network or model
make hermes-lint
make hermes-check    # package structure, manifests, Python and JS syntax
```

Architecture, interfaces, and invariants are in [MODULE.md](MODULE.md).
