# Swarm Forensics

Investigate agent coordination through messages, tools, and persistent artifacts.

## Showcase

The [Hermes plugin](showcase/hermes-plugin/README.md) provides session-native and background investigations.
The morphology hunter discovers patterns from operator-selected raw datasets without a predefined mechanism list.
Discovery-generated cards preserve measurements and provenance, not source excerpts or model prose.
Candidates remain hypotheses until investigators verify them.

The showcase preserves chat narration, session bindings, corpus observations, text mirrors, and the desktop companion pane.
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

Restart Hermes after installation. Enable the plugin’s desktop half in Settings.
Source installation requests chat-injection consent through Hermes configuration.
Read the plugin README before authorizing excerpts or running investigations.

Survey an authorized dataset without sending excerpts to the model:

```bash
make hermes-hunter ARGS='/path/to/authorized.jsonl.gz --survey-only --max-records 1000'
```

Development dependencies and their lockfile live under `showcase/hermes-plugin/`.
The removed acquisition core is not restored by these command wrappers.

## Experiments and Research

- [Discord Swarm](experiments/jesse/README.md): Jesse’s imported coordination experiment and synchronization tooling.
- [Pug experiments](experiments/pug/): Stylometry, grammar, trajectory mining, and visualization research.
- [Colette research](colette-research/): Coordination mechanisms and documented source investigations.
- [Chris research](chris-research/): Project research and tools.

`make test` and `make lint` cover the maintained Hermes and Discord Swarm modules.
Historical research scripts and visualizations are not part of those regression suites.

## Data Boundaries

Use synthetic records for verification.
Raw downloads MUST remain under untracked `data/raw/`.
Stream dataset records. Full datasets MUST NOT be loaded into memory.
Authorize model excerpt exposure explicitly before discovery.
Do not treat sampled recurrence as proof of transmission, maliciousness, causality, or actor independence.

## Event

This project targets the [AI Swarm Dynamics Hackathon](https://swarmchasing.com/), October 3–4, 2026.
AI Village and Grove Research host the event.
