# Hermes Setup Guide for tracehound

Installs the tracehound skill on Hermes AI Agent
(https://github.com/NousResearch/hermes-agent).

## Prerequisites

1. **Hermes installed** — see https://github.com/NousResearch/hermes-agent
2. **Python 3.10+** (stdlib only, no dependencies)
3. **curl** on PATH (all network access is curl-via-subprocess)

## Installation

```bash
mkdir -p ~/.hermes/skills/hunt
cp -r skills/tracehound ~/.hermes/skills/hunt/
```

With named profiles the skills root is `~/.hermes/profiles/<name>/skills/`.
Run `hermes skills list` to confirm it shows up; a session already open
needs `/reload-skills` (or a new session) to pick it up.

Developer / live-edit alternative (edits propagate without re-copying):

```bash
mkdir -p ~/.hermes/skills/hunt
ln -s "$(pwd)/skills/tracehound" ~/.hermes/skills/hunt/tracehound
```

Note: `hermes skills install <repo>` runs a security scanner that may flag
network-access patterns. If installation is blocked, the `cp`/`ln -s` path
above is the supported workaround.

## First run

```bash
cd ~/.hermes/skills/hunt/tracehound
cp config.example.ini config.ini   # set your intervals
python3 scripts/tracehound.py --job diagnose
python3 scripts/tracehound.py --job scan
```

Inspect `state/hits/` before scheduling anything.

## Scheduling

No Hermes-native scheduler was found, so periodic runs use host cron:

```cron
0 */6 * * * cd ~/.hermes/skills/hunt/tracehound && python3 scripts/tracehound.py --job scan >> state/cron.log 2>&1
30 2 * * * cd ~/.hermes/skills/hunt/tracehound && python3 scripts/tracehound.py --job predict-urls >> state/cron.log 2>&1
15 3 * * 0 cd ~/.hermes/skills/hunt/tracehound && python3 scripts/tracehound.py --job research >> state/cron.log 2>&1
```

All intervals also live in `config.ini` `[schedule]`; the cron lines above
are the outer trigger, the config values document intent and gate
minimum spacing inside long-running deployments.

## Usage

```
/tracehound scan
/tracehound research
/tracehound predict-urls
/tracehound update-iocs
/tracehound diagnose
```
