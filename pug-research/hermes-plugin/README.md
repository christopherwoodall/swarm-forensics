# Tracehound

**Install:** [one-click install
link](hermes://plugin/install?repo=christopherwoodall/swarm-forensics/pug-research/hermes-plugin/skills/tracehound&enable=1)
(confirm-first dialog; the subdirectory rides in the `repo`
parameter per the SDK installer source). The link resolves only
once the plugin is merged to the repo's default branch (`main`);
until then install manually — full instructions:
[HERMES_SETUP.md](HERMES_SETUP.md).

## What it is

Tracehound is a swarm-hunting app inside Hermes desktop. It hunts
agent-trace IOCs across public sources (urlquery, Wayback CDX,
arquivo.pt), maintains a working IOC list, and predicts candidate
URLs from observed request grammar.

The hunting dog. It hunts only with the human.

- Every hunt is a discrete job the human starts, watches, and
  can cancel. No cron, no background schedule, no autonomous
  scans. Nothing runs while the app is closed.
- The IOC updater only proposes candidates into a human review
  queue. Nothing promotes without a human decision.
- The prompt firewall is advisory-only and locked. It recommends;
  the human decides.
- Private deployment only. Watch-term strings never leave the
  operator's machine.

It is also a case-management and mapping interface:

- **Collections**: file a trace under an agent, agents under a
  swarm, swarms under a collection. Full CRUD in the GUI.
- **Graph view**: Obsidian-style node graph of traces, agents,
  swarms, collections, IOCs, and indicators. Pan, zoom, click
  for detail, filter by type.
- **Local database**: SQLite stores entities, relationships,
  extracted indicators, hunt history, and review decisions.
  Adding a trace auto-extracts its indicators into the DB.
- **Chat**: talk to the dog — ask it to hunt, ask what it found,
  ask why a candidate was flagged. Inline accept/reject/narrow
  on candidates wherever they appear.

## Doc map

| Doc | What it covers |
|---|---|
| [SPEC.md](SPEC.md) | Complete specification: architecture, entity model, DB schema, UI, commands |
| [RATIONALE.md](RATIONALE.md) | Why each major decision was made — the trust document |
| [HERMES_SETUP.md](HERMES_SETUP.md) | Install, first run, `/swarm-forensics` grammar, chat, SDK citations |
| [DESIGN.md](DESIGN.md) | Plugin architecture and design decisions |
| [LEARNING.md](LEARNING.md) | The learning loop (now human-gated; see amendment at top) |
| [FIREWALL.md](FIREWALL.md) | Prompt-firewall design, golden set, eval status |
| [ADVERSARIAL.md](ADVERSARIAL.md) | The 12 objections (verdict: no-build as originally specified) |
| [ADVERSARIAL_DELTA.md](ADVERSARIAL_DELTA.md) | Re-grade under the hunting-dog model |
| [HERMES_DESKTOP.md](HERMES_DESKTOP.md) | Desktop SDK mapping: UI spec, gaps, install link, settings schema |
| `skills/tracehound/SKILL.md` | The skill surface and command grammar |
| `skills/tracehound/config.example.ini` | Every config key, documented |

## Quick start

1. Install via [HERMES_SETUP.md](HERMES_SETUP.md) (manual path until the fixed link lands).
2. Open `/swarm-forensics`, run a hunt, triage the review queue.
3. File interesting traces into your collections; explore the graph.
