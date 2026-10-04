<div align="center">

# Swarm Forensics

**Investigating how machine swarms coordinate — and how to see them.**

Built by **The Stigmergists** at the [AI Swarm Dynamics Hackathon](https://swarmchasing.com/)
October 3–4, 2026 · Hosted by AI Village and Grove Research
*Building the tools we wished we had for the Hugging Face incident.*

</div>

We fanned out across three efforts.
One team coordinates humans and their agents over Discord.
One team mapped the morphology of swarm attempts in public traces.
One team built a Hermes plugin that hunts agent infrastructure live.
This repository holds all three.

## The Team

Shout-outs to the Stigmergists behind each lane:

- **Chris** — project tooling and repository integration.
- **Colette** — morphology: the attempt-morphology taxonomy from public traces.
- **Jesse** — the Discord Coordinator app and its source-synchronization pipeline.
- **Pug** — the Swarm Forensics Hermes plugin.

---

## The Projects

### 1. Swarm Forensics — Hermes Plugin

A Desktop/CLI plugin that hunts autonomous-agent infrastructure on the public web.
Start a hunt in any chat with `/swarm-forensics start <goal>` and the agent works the lead live.
It searches public indexes (Wayback CDX, Arquivo, urlquery), mirrors pages into a content-addressed store, and logs every query, tool call, and verdict to a local SQLite ledger.
It posts progress digests right into your chat and nudges itself forward when idle.
You steer with plain conversation or slash commands, and watch URLs, evidence, IOCs, and entity graphs pile up in the desktop workbench.
Discipline is built in: model proposes, policy decides, every claim sits on a graded evidence ladder, and nothing ever attributes activity to a human operator.

**[One-click install](https://tinyurl.com/swarm-forensics-plugin)** · [Plugin guide](showcase/hermes-plugin/README.md) · [Verified status](STATUS.md)

**Narrated walkthrough:**

[Demo Video](https://github.com/user-attachments/assets/389dd157-1853-4faf-97cb-d3f6c967f6f4)

[Watch the narrated walkthrough](showcase/hermes-plugin/docs/voice_over.mp4) · [Silent demo](showcase/hermes-plugin/docs/demo.mp4)

### 2. Morphology

Our tool investigates public traces of AI-agent activity across web archives, browser reports, relay services, wiki revisions, and published incident reports.
It found a dense SEC archive cluster, earlier census-related request records, a malformed AIHW relay request, and repeated use of public intermediary services.

The most important result is not proof of a single hidden operation or successful data access.
It is a clearer taxonomy of attempt morphology: how automated or semi-automated systems generate malformed requests, rotate relays, retry after failures, and leave partial traces across public services.
The tool separates archive captures from requests, errors from successful retrievals, timing overlap from coordination, and feed silence from proof that activity stopped.
The result is an evidence-layer reconstruction that makes agent activity more measurable without overclaiming attribution.

[Grammar-network findings report](experiments/pug/grammar-network/REPORT.md) · [Trace pulls](experiments/pug/trace-pulls/TRACE_PULLS.md) · Morphology hunter: see the **Morphologies** tab in the [plugin](showcase/hermes-plugin/README.md)

### 3. Discord Coordinator

Coordinates users and their personal agent swarms via Discord, allowing greater continuity and effect.
Authenticated MCP tools for Discord text channels keep agents in touch with their owners between sessions.
Agents synchronize capabilities and owner settings through `discord_sync_agent`.
A runtime bridge enforces configured command budgets, rates, and deadlines.

[Source](showcase/discord-bot-swarm/) · [Hosted app](https://discord-bot-swarm.multi.fairystack.com/) · [Sync tooling](experiments/jesse/README.md)

---

## Inside This Repository

| Path | Contents |
|---|---|
| [showcase/hermes-plugin](showcase/hermes-plugin/) | The Swarm Forensics Hermes plugin: hunts, morphology discovery, desktop workbench |
| [showcase/discord-bot-swarm](showcase/discord-bot-swarm/) | The Discord Coordinator app source |
| [experiments/jesse](experiments/jesse/) | Discord Swarm upstream source and synchronization tooling |
| [experiments/pug](experiments/pug/) | Stylometry, goal inference, grammar-network, and trace-pull research |
| [experiments/colette](experiments/colette/hermes-research/) | Published-source research collection: 38 cited records and Stage 3 event discovery |
| [experiments/chris](experiments/chris/tools/) | Project research and tools |

Read [STATUS.md](STATUS.md) for verified results and remaining gaps.
Read [MODULE.md](showcase/hermes-plugin/MODULE.md) for plugin interfaces and invariants.

## Commands

Run commands through the root Makefile.
Requirements: uv, make, and Node.js.

```bash
make help
make setup
make test
make lint
make check
make hermes-install
```

Restart Hermes after installation. Enable the plugin's desktop half in Settings.
Source installation requests chat-injection consent through Hermes configuration.
Read the [plugin README](showcase/hermes-plugin/README.md) before authorizing excerpts or running investigations.

Survey an authorized dataset without sending excerpts to the model:

```bash
make hermes-hunter ARGS='/path/to/authorized.jsonl.gz --survey-only --max-records 1000'
```

## Data Boundaries

Use synthetic records for verification.
Raw downloads MUST remain under untracked `data/raw/`.
Stream dataset records. Full datasets MUST NOT be loaded into memory.
Authorize model excerpt exposure explicitly before discovery.
Do not treat sampled recurrence as proof of transmission, maliciousness, causality, or actor independence.
