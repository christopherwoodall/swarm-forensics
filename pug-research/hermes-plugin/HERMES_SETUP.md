# Tracehound — Hermes setup

The hunting dog. It hunts only with the human.

Every hunt is a discrete job the human starts, watches, and can
cancel. There is no cron, no background schedule, and no autonomous
scanning. The IOC updater only proposes candidates into a human
review queue. Nothing promotes without a human decision.

## Prerequisites

1. Hermes AI Agent — https://github.com/NousResearch/hermes-agent
2. Python 3.10+ (stdlib only, no dependencies)
3. curl on PATH (all network access is curl-via-subprocess)

## Install path 1: install link (recommended)

[Install tracehound in Hermes](hermes://plugin/install?repo=christopherwoodall/swarm-forensics/pug-research/hermes-plugin/skills/tracehound&enable=1)

The plugin subdirectory rides inside the `repo` parameter as path
segments. That is the documented mechanism:
`apps/desktop/electron/desktop-plugin-install.ts`
(`resolvePluginGitUrl`) splits `owner/repo/<subdir…>` into a git
URL plus a subdirectory and sparse-checkouts only that folder.
There are no `path=` or `ref=` parameters — do not add them. The
installer probes the subdirectory for `<dir>/plugin.js` or
`<dir>/desktop/plugin.js`; tracehound ships `desktop/plugin.js`,
so the desktop component is detected.

The app shows a confirm-first dialog: repo identity, source links,
and the probe result. You pick components before anything installs.
Deep links NEVER auto-install.

REQUIREMENT: the installer clones `--depth 1` of the repo's
DEFAULT branch only (`main`). The plugin is on `pug-scratch`
until merged — the link resolves only after the merge.
Pick both components: the agent skill (Python backend at
`dashboard/plugin_api.py`) and the desktop UI (`desktop/plugin.js`).

Repo-id caveat: the build notes flag this repo id for confirmation
before publishing the link. Confirm the id is current, then share.

## Install path 2: desktop unified package

The documented delivery for a plugin with agent-side code is the
unified package: `$HERMES_HOME/plugins/<id>/desktop/plugin.js` plus
the Python backend at `$HERMES_HOME/plugins/<id>/dashboard/` with
manifest `"api": "plugin_api.py"` (HERMES_DESKTOP.md §1 [DOC]).

Two toggles gate the plugin. Enable BOTH, or the backend stays
silent and the UI shows "disconnected".

1. In-app switch: Capabilities → Plugins → tracehound. The plugin
   ships `defaultEnabled: false`: it inventories there but stays
   off until you flip it.
2. Backend gate: add `tracehound` to `plugins.enabled` in
   `config.yaml`. The Python backend loads only under this gate
   ([SKILL], HERMES_DESKTOP.md §1; the doc tags this behavior
   SKILL, not DOC).

A session already open needs `/reload-skills` (or a new session)
to pick up the skill.

## Why there is no scheduling

Scheduling was removed under the hunting-dog model. Adversarial
objection #3 found autonomous volume abusive to free services.
Objection #10 found no owner, no locking, and fragile state. The
fix is the model itself: no cron, no background schedule, no
scans while the app is closed (accepted design). If you want a
repeat hunt, you start it again.

## The operator

The operator is the human hunter: the person at the console who
starts hunts, reads hits, and decides the review queue. This is a
private single-operator deployment.

Weekly cadence:

1. Run at least one hunt per watch term.
2. Triage the review queue to zero (accept, reject, or narrow).
3. Read `state/throttles.jsonl` for source health.
4. Re-run the firewall golden set if the judge prompt changed.

## First-run flow

1. Install via the link above.
2. Flip both toggles (in-app switch + `plugins.enabled`).
3. Open the dashboard: route `/tracehound`.
4. Run a first hunt (see grammar below).
5. Triage the review queue at `/tracehound/review`.

```bash
cd <skill dir>/skills/tracehound
cp config.example.ini config.ini
python3 scripts/tracehound.py diagnose
python3 scripts/tracehound.py hunt --target <term> --mock
```

Use `--mock` first: synthetic hits, no network. Inspect
`state/hits/` before any live hunt.

## `/swarm-forensics` command grammar

| Command | What it does | GUI deep link |
|---|---|---|
| `/swarm-forensics` | Open the dashboard | `/tracehound` |
| `/swarm-forensics hunt <target> [--sources urlquery,cdx,arquivo] [--cap N]` | Start a discrete hunt job | `/tracehound/hunt` |
| `/swarm-forensics stop [job-id]` | Cancel the running hunt | kill switch |
| `/swarm-forensics modify <setting> <value>` | Change one setting (validated) | `/tracehound/settings` |
| `/swarm-forensics status` | JSON summary: jobs, IOCs, pause state | `/tracehound` |
| `/swarm-forensics review` | List the review queue | `/tracehound/review` |
| `/swarm-forensics review accept <id>` | Promote term to active | `/tracehound/review` |
| `/swarm-forensics review reject <id>` | Mark inactive, keep provenance | `/tracehound/review` |
| `/swarm-forensics review narrow <id> <chunk>` | Propose a narrower term | `/tracehound/review` |

Notes:

- `review` decisions REQUIRE a rationale (`--rationale`). The CLI
  rejects rationale-less decisions. The GUI asks for it too.
- `modify` validates against the schema. Unknown keys fail with
  the valid-key list.
- `firewall_mode` is LOCKED: `modify safety.firewall_mode
  enforcing` is refused in code. Use `advisory` (the judge
  recommends; you decide) or `off`. Advisory mode exists because
  the judge has not passed the injection-resistance eval
  (ADVERSARIAL.md objection #5).
- `paused = true` refuses every hunt with "hunting is paused".
  The kill switch sets this.

The same verbs also live as ⌘K palette entries (`swarm-forensics:
Open dashboard`, `Start hunt...`, `Stop hunt`, `Open review
queue`, `Status`, `Pause / resume hunting`).

## Chat

The Chat tab (`/tracehound/chat`) is a rule-based responder
([INF], HERMES_DESKTOP.md §2.6). It understands:

- `hunt <term> [on urlquery|cdx|arquivo]` — starts a hunt job.
  This message IS the human initiating. No autonomous work.
- `what did you find?` / `status` — job and hit summary.
- `why was '<term>' flagged?` — evidence plus firewall rationale.
- `show queue` — review-queue candidates.
- `pause` / `resume` — the kill switch.
- `help` — lists the intents above.

The chat never auto-accepts, auto-rejects, or auto-narrows.
Every promotion needs an explicit accept.

Optional model path: `[chat] model_enabled=true` with `endpoint`
and `api_key_env` set. The key lives in the named environment
variable, never in config, never in logs. The model only
rephrases replies; actions stay rule-based. The UI always shows
which brain is active ("rule-based" / "model path").

## Desktop pages

- `/tracehound` — Dashboard: status cards, hits, IOCs, review,
  candidates, research, settings.
- `/tracehound/hunt` — Hunt control: target, sources, cap,
  live progress, cancel.
- `/tracehound/chat` — Chat ([INF]).
- `/tracehound/review` — Review queue: candidate cards with
  evidence, venue count, firewall advisory, ACCEPT / REJECT /
  NARROW, 7-day SLA flag.
- `/tracehound/iocs` — IOC list management.
- `/tracehound/research` — Research watchlist (manual check).
- `/tracehound/settings` — Settings incl. the install link
  (Settings → About) and prompt editors.

## SDK capability citations

Every Hermes SDK capability the build relies on, with its doc
citation. [INF] marks inferences carried through honestly
(per HERMES_DESKTOP.md's own marking).

| Capability | Citation |
|---|---|
| Install link scheme, confirm-first dialog, no auto-install | SDK `website/docs/developer-guide/desktop-plugin-sdk.md` § "Distributing with an install link"; also `website/docs/user-guide/features/plugins.md` § "One-click install links" [DOC] |
| Unified package layout (`desktop/plugin.js` + `dashboard/plugin_api.py`) | SDK desktop-plugin-sdk.md, via HERMES_DESKTOP.md §1 [DOC] |
| Single ESM file plugin, `jsx()`, hot reload | SDK desktop-plugin-sdk.md, via HERMES_DESKTOP.md §1 [DOC] |
| Full pages (`ROUTES_AREA`, `data: { path }`) | SDK, via HERMES_DESKTOP.md §1 [DOC] |
| Sidebar nav (`SIDEBAR_NAV_AREA`, `data: { path, label, codicon }`) | SDK, via HERMES_DESKTOP.md §1 [DOC] |
| Sidebar grouping hints (`group`, `indent`) | [INF] — HERMES_DESKTOP.md marks these inferred |
| Status-bar chip (`statusBar.right`) | SDK, via HERMES_DESKTOP.md §1 [DOC] |
| ⌘K commands (`PALETTE_AREA`) | SDK, via HERMES_DESKTOP.md §1 [DOC] |
| Palette payload shape `{ command, run }` | [INF] — HERMES_DESKTOP.md marks this inferred |
| Keybinds (`KEYBINDS_AREA`, rebindable) | SDK, via HERMES_DESKTOP.md §1 [DOC] |
| Keybind payload shape `{ id, title, run }` | [INF] — HERMES_DESKTOP.md marks this inferred |
| Appearance extras (`APPEARANCE_AREAS.extra`) | SDK, via HERMES_DESKTOP.md §1 [DOC] |
| `ctx.storage` (JSON persistence) | SDK, via HERMES_DESKTOP.md §1 [DOC] |
| `ctx.rest` (backend namespace `/api/plugins/<id>`) | SDK, via HERMES_DESKTOP.md §1 [DOC] |
| `ctx.socket` | SDK, via HERMES_DESKTOP.md §1 [DOC]; UNUSED — the build polls via `refetchInterval` (documented pattern, Gap 4) |
| `host.notify` toasts (no notification center documented) | SDK, via HERMES_DESKTOP.md §1 [DOC] |
| `host.navigate` | SDK, via HERMES_DESKTOP.md §1 [DOC] |
| `defaultEnabled: false` opt-in inventory | SDK, via HERMES_DESKTOP.md §1 [DOC] |
| `plugins.enabled` in `config.yaml` (backend gate) | [SKILL] — HERMES_DESKTOP.md tags this SKILL, not DOC |
| Chat surface (`/tracehound/chat`, rule-based intents) | [INF] — HERMES_DESKTOP.md §2.6 |
| Inline ACCEPT/REJECT/NARROW buttons | [INF] — HERMES_DESKTOP.md §2.7 |

Could not cite (no SDK surface found in the sections read):

- A desktop slash-command surface for `/swarm-forensics`. The
  command grammar is skill-level (SKILL.md); the desktop exposes
  the same verbs as palette commands. No chat slash-command
  registration area is documented.
