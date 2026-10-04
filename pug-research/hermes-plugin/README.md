# Tracehound

[Install in Hermes](hermes://plugin/install?repo=christopherwoodall/swarm-forensics&enable=1)

The link opens a confirm-first dialog. It never auto-installs. The
dialog shows the repo identity, source links, and what the repo
ships; you pick components before anything installs. Full
instructions: [HERMES_SETUP.md](HERMES_SETUP.md).

## What it is

Tracehound hunts agent-trace IOCs across public sources: urlquery,
Wayback CDX, arquivo.pt. It maintains a working IOC list, predicts
candidate URLs from observed request grammar, and watches
researcher publications for new IOCs.

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

## Doc map

| Doc | What it covers |
|---|---|
| [HERMES_SETUP.md](HERMES_SETUP.md) | Install, first run, `/swarm-forensics` grammar, chat, SDK citations |
| [DESIGN.md](DESIGN.md) | Plugin architecture and design decisions |
| [LEARNING.md](LEARNING.md) | The learning loop (now human-gated; see amendment at top) |
| [FIREWALL.md](FIREWALL.md) | Prompt-firewall design, golden set, eval status |
| [ADVERSARIAL.md](ADVERSARIAL.md) | The 12 objections (verdict: no-build as originally specified) |
| [ADVERSARIAL_DELTA.md](ADVERSARIAL_DELTA.md) | Re-grade under the hunting-dog model; verdicts the docs reflect |
| [HERMES_DESKTOP.md](HERMES_DESKTOP.md) | Desktop SDK mapping: UI spec, gaps, install link, settings schema |
| `skills/tracehound/SKILL.md` | The skill surface and command grammar |
| `skills/tracehound/config.example.ini` | Every config key, documented |

## Quick start

1. Install via the link above.
2. Enable both toggles: Capabilities → Plugins → tracehound, plus
   `tracehound` in `plugins.enabled` in `config.yaml`.
3. Open `/tracehound`, run a hunt, triage the review queue.
