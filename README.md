# Swarm Forensics 🔍🕵️‍♂️

> Precision multi-agent forensics engine: reconstructing agent timelines, inspecting cross-agent communication, and detecting coordination anomalies in autonomous AI swarms.

Built for the **[AI Swarm Dynamics Hackathon](https://swarmchasing.com/)** (October 3–4, 2026, San Francisco & Online), co-hosted by [AI Village](https://theaidigest.org/village) and [Grove Research](https://groveresearch.com/).

---

## 🎯 Context & Mission

As autonomous AI agent swarms scale across virtual environments, forums, and computer-use environments, understanding their coordination dynamics is an urgent safety challenge.

> *“We don't have good approaches for understanding/overseeing the activity and aims of AI 'swarms'.”*  
> — Ryan Greenblatt, Hugging Face incident investigator

Incidents like the **OpenAI-Hugging Face incident** and the **German Wiki incident** have demonstrated that society lacks dedicated tools for multi-agent digital forensics. `swarm-forensics` aims to bridge this gap by providing:

1. **Chronological Timeline Reconstruction**: Unified chronological event ordering across parallel agents, chat rooms, and computer-use turns.
2. **Discrepancy & Hallucination Auditing**: Comparing an agent's self-reported actions/claims against grounded tool logs and screenshots.
3. **Information Cascade & Collusion Tracing**: Tracing how instructions, memes, coordination signals, and emergent goals propagate across agents over long time horizons.
4. **Memory-Safe Stream Processing**: High-throughput parsing designed to stream massive datasets without loading gigabytes of raw archives into RAM.

---

## 🔗 Key Hackathon Resources & Datasets

| Resource | Link | Description |
| :--- | :--- | :--- |
| **AI Swarm Dynamics Hackathon** | [swarmchasing.com](https://swarmchasing.com/) | Official hackathon site with schedule, problem statements, and prize details. |
| **AI Village Dataset** | [huggingface.co/datasets/aidigestorg/ai-village](https://huggingface.co/datasets/aidigestorg/ai-village) | Primary dataset: >170k messages, ~233k structured events, ~1.14M computer-use turns, and screenshots from a multi-agent society operating autonomously since April 2, 2025. |
| **AI Village Live UI** | [theaidigest.org/village](https://theaidigest.org/village) | Interactive explorer for live and historical agent village activities. |

---

## 📊 AI Village Dataset Breakdown

The `aidigestorg/ai-village` dataset mirrors real-world multi-agent interactions across 31 frontier agents (Claude, GPT, Gemini). Key data streams include:

- `events.jsonl.gz` (~233k rows): The structured activity timeline (`AGENT_TALK`, `START_USING_COMPUTER`, `STOP_USING_COMPUTER`, `WAIT`, `PAUSE`, `USER_TALK`, etc.) with `event_index` ordering.
- `chat_messages.jsonl.gz` (~123k rows): Room-based chat logs (agent & human) with speaker identities and timestamps.
- `computer_use_turns.jsonl.gz` (~1.14M rows): Granular turn-by-turn computer interactions, model thought chains, action commands, tool outputs, and screenshot references.
- `computer_use_sessions.jsonl.gz` (~37k rows): Session-level goals, agent assignments, and durations.
- `agent_memories.jsonl.gz` (~165k rows): Agent long-term memories generated during periodic consolidation cycles.
- `images/computer-use-turns/<YYYY-MM-DD>.tar`: Daily screenshot archives indexed by turn ID.

---

## 🏗️ Architecture & Living Documentation

This repository employs a **Blackboard Living Documentation** tree governed by AI directives:

- **Local Blackboards (`MODULE.md`)**: Subsystems under `src/` maintain living blackboards documenting active invariants, interfaces, and known gaps (see [src/swarm_forensics/MODULE.md](src/swarm_forensics/MODULE.md)).
- **Agent Governance**: [AGENTS.md](AGENTS.md) defines immutable boundaries (`docs/` reserved for MkDocs/GitHub Pages, no `arch/` meta-folders).
- **Conflict-Free Merges**: `.gitattributes` configures union merge drivers for all living blackboard files.

---

## 🚀 Getting Started

The `Makefile` is the single entry point for all project commands. Run `make help` to list them.

### Installation

Requirements: [uv](https://docs.astral.sh/uv/) and `make`.

```bash
git clone https://github.com/your-org/swarm-forensics.git
cd swarm-forensics
make setup   # runs `uv sync`: creates .venv and installs pyproject.toml dependencies
make test
```

Every `make` target runs inside the `.venv` environment through `uv run`.

### Getting the Data

Raw data goes to the untracked `data/raw/` directory.

```bash
make data-sample     # synthetic tables in data/raw/sample/ (offline, no token)

export HF_TOKEN=...  # token of an account with approved dataset access
make data-info       # list files, sizes, and free disk space (no download)
make data-schema     # SCHEMA.md, CHANGELOG.md, manifest.json only (small)
make data-download   # all non-image files, about 5.8 GB
make data-download TABLES="events chat_messages agent_goals"   # selected tables only
make data-download REVISION=<commit>                           # pin a dataset commit
```

`make data-download` skips `images/` (the screenshot archives) and resumes completed files.

`data/raw/SCHEMA.md` is the column reference for every table. It is a human-readable document, not a validator. `make data-download` also fetches it. Use `make data-schema` to refresh it alone. Set `REVISION` to match your table downloads.

### Validating the Data

`src/swarm_forensics/ingest/dataset.schema.json` holds a JSON Schema (Draft 2020-12) for each raw table. It follows `SCHEMA.md` and a bounded check of real field types. Unknown fields stay allowed. Joins appear as `x-references` annotations. These contracts describe raw records. They are not the unified forensic event schema.

```bash
make data-validate                                  # synthetic sample, 100 records per table
make data-validate DATA_DIR=data/raw TABLES="events chat_messages" LIMIT=100
make data-validate DATA_DIR=data/raw LIMIT=0        # explicit full streaming scan (slow)
```

The command prints the table, line, field path, and rule of the first failure. It never prints record values. A limited run is not a whole-dataset check.

### Streaming the Data

Read tables one line at a time. Do not load a complete table into memory.

```python
import gzip
import json

with gzip.open("data/raw/events.jsonl.gz", "rt", encoding="utf-8") as handle:
    for line in handle:
        event = json.loads(line)
        print(event["data"]["actionType"], event["created_at"])
        break
```
