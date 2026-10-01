# Swarm Forensics

Investigate how agent swarms coordinate through messages, tools, and persistent artifacts.
Explore changing relationships between agents, egress sites, shared artifacts, and targets.

This project targets the [AI Swarm Dynamics Hackathon](https://swarmchasing.com/), October 3–4, 2026.
AI Village and Grove Research host the event in San Francisco and online.

Status: acquisition tooling and synthetic visualization mocks.
The forensic engine, graph pipeline, and integrations are not implemented.
Read [STATUS.md](STATUS.md) for the verified checkpoint.

---

## Project Direction

The team discussed these complementary workstreams:

1. Map tools, skills, plugins, and possible egress routes.
2. Trace distributed coordination through durable shared artifacts.
3. Explore a temporal graph, including lateral links and changing relation types.
4. Investigate information propagation, memory formation, role emergence, and coordination repair.
5. Explore a Hermes swarm-search plugin.
6. Experiment with FairyStack or Discord for human and agent collaboration.

These are discussed directions, not completed features or an accepted implementation specification.
Read [PROJECT_BRIEF.md](PROJECT_BRIEF.md) for source attribution, evidence limits, and open decisions.

---

## Resources

| Resource | Link | Description |
| :--- | :--- | :--- |
| **AI Swarm Dynamics Hackathon** | [swarmchasing.com](https://swarmchasing.com/) | Official hackathon site with schedule, problem statements, and prize details. |
| **AI Village Dataset** | [huggingface.co/datasets/aidigestorg/ai-village](https://huggingface.co/datasets/aidigestorg/ai-village) | Existing downloader target. Access approval is required. |
| **AI Village Live UI** | [theaidigest.org/village](https://theaidigest.org/village) | Interactive explorer for live and historical agent village activities. |
| **Swarmtraces** | [swarmtraces.org](https://swarmtraces.org/) | Redacted incident artifacts that motivated the coordination research. No parser is implemented here. |

---

## Data Boundaries

Default to synthetic data with `make data-sample`.
The sample includes `agent_goals`, `chat_messages`, and `events` tables.
The downloader recognizes additional AI Village tables, including computer-use sessions, turns, and agent memories.
Use `make data-info` to inspect revision-specific file sizes.
Previously quoted dataset counts are not a verified inventory of the current dataset.

Raw downloads MUST remain under untracked `data/raw/`.
Full tables MUST NOT be loaded into memory.
The downloader excludes `images/` and image files.
Read [AGENTS.md](AGENTS.md) before using real data.

---

## Documentation Map

| Document | Authority |
| --- | --- |
| [README.md](README.md) | Entry point and executable setup instructions |
| [STATUS.md](STATUS.md) | Verified checkpoint, gaps, and next decision |
| [PROJECT_BRIEF.md](PROJECT_BRIEF.md) | Historical discussion and proposed direction |
| [AGENTS.md](AGENTS.md) | Repository requirements and agent authorization |
| [Core MODULE.md](src/swarm_forensics/MODULE.md) | Local architecture, invariants, and implementation gaps |
| [Ingest MODULE.md](src/swarm_forensics/ingest/MODULE.md) | Acquisition interfaces and data-safety requirements |
| [Visualization references](data/viz_mock/README.md) | Synthetic mocks, not implemented forensic analysis |

Keep architecture documentation in local `src/**/MODULE.md` files.
Reserve `docs/` for MkDocs and GitHub Pages assets.
Union merges preserve text; they do not resolve semantic contradictions.
Follow the contradiction procedure in `AGENTS.md` when rules disagree.

---

## Getting Started

The `Makefile` is the single entry point for all project commands. Run `make help` to list them.

### Installation

Requirements: [uv](https://docs.astral.sh/uv/) and `make`.

```bash
git clone https://github.com/christopherwoodall/swarm-forensics.git
cd swarm-forensics
make setup   # runs `uv sync`: creates .venv and installs pyproject.toml dependencies
make test
make lint
make data-sample
```

Setup installs the Python dependencies in `.venv`.
Python commands run through `uv run`.
Tests run offline; lint checks the Python source with Ruff.
The sample command writes three gzipped JSON Lines tables under `data/raw/sample/`.
It requires no credentials and downloads no dataset files.

The existing mocks require internet access for Three.js from a CDN.
Open `data/viz_mock/pipeline-mock-v2.html` in a browser to inspect the synthetic reference.
This bootstrap did not validate browser rendering or real-data integration.

### Getting the Data

Request dataset access before using the downloader.
Set `HF_TOKEN` in the environment through your credential workflow.
The downloader reads it directly and does not print it.
Run a download only when you explicitly choose to acquire real data.

```bash
make data-sample     # synthetic tables in data/raw/sample/ (offline, no token)

make data-info       # list files, sizes, and free disk space (no download)
make data-download   # all non-image files; inspect the size first
make data-download TABLES="events chat_messages agent_goals"   # selected tables only
make data-download REVISION=<commit>                           # pin a dataset commit
```

`make data-download` skips `images/` (the screenshot archives) and resumes completed files.

With `TABLES`, the downloader selects only the named table files.
Without `TABLES`, it also selects non-image reference files.
Each run resolves and pins one dataset revision.
Access approval and the token were not tested during this documentation bootstrap.

### Hackathon Submission

The organizer site states a Sunday deadline of 5:00 PM Pacific Time, including online submissions.
Submit a short write-up or explanatory video and a link to the code repository.
A write-up of results found with the tool is optional.
Early development and other datasets are permitted.
See the [project brief](PROJECT_BRIEF.md#hackathon-context) for the reviewed event context.

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
