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
| `/swarm-forensics start [goal]` | Start an autonomous hunt. It runs until you stop it. |
| `/swarm-forensics session [goal]` | Start an interactive hunt session in Hermes chat. |
| `/swarm-forensics attach [id]` | Attach any chat session to a running hunter for live steering. |
| `/swarm-forensics pause`, `resume [id]`, `stop` | Control the hunt and active sub-hunts. |
| `/swarm-forensics status` | Show hunt state and totals. |
| `/swarm-forensics review` | List proposed IOC terms. |
| `/swarm-forensics accept|reject <id>`, `narrow <id> <term>` | Decide an IOC. |
| `/swarm-forensics benign <id|term>` | Mark an indicator as a benign false positive. |
| `/swarm-forensics find <text>` | Search artifacts, agents, swarms, and campaigns. |
| `/swarm-forensics settings [key [value]]` | Read or change a setting. |

Interactive Hermes tools:
- `sf_get_context`, `sf_search_index`, `sf_record_evidence`, `sf_propose_ioc`, `sf_manage_entity`, `sf_link_entities`, `sf_triage_item`, `sf_query_knowledge`, `sf_spawn_subhunt`, `sf_attach_hunt`.

Desktop pages:
- **Hunt**: Activity log with filters, active leads with dismiss actions, recursive sub-hunt tree view, `+ Sub-hunt` spawner, attach command helper, and interactive hunt session card.
- **Knowledge**: Interactive graph, hierarchy browser (*Belongs to* and *Contains*), custom groups (`+ Group`), tags, and Markdown notes.
- **Evidence**: Captured page excerpts with provenance and taint indicators.
- **IOCs**: Indicator catalog, promotion policy status, decision audit logs, and benign triage.
- **URLs**: Discovered and predicted URL catalog, filtering by status, and benign/suspicious triage.
- **Prompts**: Database-backed prompt templates, token placeholder chips (`{{var}}`), reset to defaults, and JSON export/import.
- **Sources**: Index source enable toggles (Wayback CDX, crt.sh, arXiv Intelligence), candidate URL grammar rules, and wordlist import.
- **Settings**: Plugin configuration (depth limits, multi-hunt concurrency), schedule controls, and full data export bundle.

## How a hunt works

Each cycle runs these steps. The loop repeats until the operator stops it.

1. **Plan.** Hermes proposes search queries from past findings and open leads.
2. **Search.** The plugin runs queries through Hermes `web_search` and
   enabled public indexes.
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
- Entities enforce strict hierarchy: `artifact -> agent -> swarm -> campaign`.
  Links of kind `part_of` must point from child to parent.
- Schedules are off. The operator arms each one. Scheduled hunts run only
  while the desktop app is open.
- A hunt stops when the app closes. After a restart a hunt is `paused`, and
  the operator resumes it.
- Index sources use dynamic allowlisting from enabled database records.
  Credentials are redacted before any write.
- Scope is agents and public evidence. No operator attribution.

## Data & Export

The database lives at `<hermes home>/swarm-forensics/swarm-forensics.db`.
Override the folder with `SWARM_FORENSICS_STATE_DIR`. State from the first
(CLI) version is imported once, read-only.

Operators can export data through the Settings tab or palette command:
- Generates `swarm-forensics.json` streaming dump (schema v3 with prompts, URLs, and entity tags).
- Generates an Obsidian Markdown vault with `[[wikilinks]]` in `exports/vault/`.

## Develop

```
make hermes-test     # offline tests, synthetic data, no network or model
make hermes-lint
make hermes-check    # package structure, manifests, Python and JS syntax
```

Architecture, interfaces, and invariants are in [MODULE.md](MODULE.md).
