# Tracehound on the Hermes Desktop App — UI Research & Design

Status: design proposal. The headless skill (`skills/tracehound/`,
cron + scripts) is unchanged; this document adds the desktop control
plane: what the app really supports, the tracehound UI spec, the
settings schema, and the gaps. Nothing here is committed to code yet.

Provenance key used throughout:
- **[DOC]** — stated in the official Desktop Plugin SDK doc
  (`NousResearch/hermes-agent`, `website/docs/developer-guide/desktop-plugin-sdk.md`).
- **[SKILL]** — stated in the community `hermes-desktop-plugins` skill
  reference; consistent with [DOC] but not verified in the official
  doc sections read.
- **[INF]** — inference / proposal. No documented basis; keyed to the
  closest real mechanism.

The local `colette-research/hermes-research/` collection contains
**nothing** about a Hermes desktop app or skill UI (its three
"desktop" hits are Telegram Desktop, RDP, and "desktop computer" —
coincidental). All desktop findings below come from the official SDK
doc and the plugin-skill reference, not from local research.

---

## 1. What the desktop app supports [DOC]

A desktop plugin is a **single ESM file** default-exporting a
`HermesPlugin` (`{ id, name, defaultEnabled?, register(ctx) }`),
dropped at `$HERMES_HOME/desktop-plugins/<id>/plugin.js`. No build
step; the file loads uncompiled (write UI with `jsx()` calls, not
JSX syntax); the app hot-reloads every save. Only three import
specifiers resolve: `@hermes/plugin-sdk`, `react`, `react/jsx-runtime`.

For a plugin that also ships agent-side code (tracehound does — the
skill), the documented delivery is the **unified package**:
`$HERMES_HOME/plugins/<id>/desktop/plugin.js` plus an optional
Python backend at `$HERMES_HOME/plugins/<id>/dashboard/` with
manifest `"api": "plugin_api.py"`. Same `HermesPlugin` contract;
the disk door scans inside the agent plugin's folder.

Contribution areas (`ctx.register({ id, area, render?, data? })`):

| Surface | Area | Notes |
|---|---|---|
| Layout pane | `panes` | `title` + `data: { placement: 'left'\|'right'\|'bottom'\|'main', dock?, width?, height? }`. Stacks with same-role panes; user-draggable afterward. |
| Full page | `ROUTES_AREA` | `data: { path: '/tracehound' }`; mounts in the workspace like a built-in view. |
| Sidebar nav | `SIDEBAR_NAV_AREA` | `data: { path, label, codicon }`; row below Artifacts, lights up at the route. |
| Status bar | `statusBar.left` / `statusBar.right` | Chips. Clickable. |
| Title bar | `TITLEBAR_AREAS.*` | Tool contributions; mount-scoped via `<Contribute>`. |
| ⌘K palette | `PALETTE_AREA` | Commands. |
| Keybinds | `KEYBINDS_AREA` | Rebindable actions. |
| Appearance settings | `APPEARANCE_AREAS.extra` | `render` — controls **appended to Settings → Appearance**. This is the only documented settings-surface extension point. |
| Themes | `THEMES_AREA` | Not needed here. |

Capabilities the plugin can call:

- `host.state.*` — readonly reactive atoms (`activeSessionId`,
  `cwd`, `gateway`, `model`, `profile`, `viewport`).
- `host.request(method, params)` — gateway JSON-RPC door. The doc
  lists "sessions, config, skills, **cron** — everything the app
  uses." [DOC, but the cron RPC shape is not shown in the sections
  read — see Gap 3.]
- `host.onEvent(type, fn)` — live gateway events.
- `host.notify({ kind, message })` — toasts. (No notification
  center is documented — see Gap 6.)
- `host.navigate(path)`.
- `ctx.storage.get/set/remove` — JSON persistence namespaced
  `hermes.plugin.<id>.`.
- `ctx.rest(path, …)` / `ctx.socket(path, onMessage)` — the
  plugin's own backend namespace (`/api/plugins/<id>`), served by
  `plugin_api.py`. [SKILL: `ctx.socket` is a no-op on OAuth
  remotes — keep a polling fallback.]
- [SKILL: the Python backend is imported only when the plugin is
  in `plugins.enabled` in `config.yaml`, separate from the
  in-app enable toggle.]
- React Query client (`useQuery` with `refetchInterval` — "never
  hand-roll a poll loop"), `atom`/`computed` for local state.
- UI kit (importable, theme-var styled): `Button`, `Input`,
  `Select*`, `Switch`, `Checkbox`, `SegmentedControl`, `Tabs*`,
  `Dialog*`, `ConfirmDialog`, `Badge`, `StatusDot`, `LogView`,
  `SearchField`, `ScrollArea`, `EmptyState`, `CopyButton`,
  `Codicon`, plus `cn`.
- `defaultEnabled: false` ships the plugin **opt-in**: it
  inventories in Capabilities → Plugins, off until flipped.

---

## 2. Tracehound UI spec

Delivery: unified package —
`skills/tracehound/desktop/plugin.js` (this spec) and
`skills/tracehound/dashboard/plugin_api.py` (new backend;
REST: `/hits`, `/iocs`, `/review`, `/candidates`, `/settings`,
`/scan/trigger`, `/scan/state`). `defaultEnabled: false`.
The backend enforces the headless guardrails (allowlisted
hosts, check-don't-fetch); the UI never triggers scans through
the model path — see §5, threat model.

### 2.1 Dashboard page — `/tracehound`

Sidebar nav row "Tracehound" (`codicon: 'eye'`), reachable also
via ⌘K. Tabs: **Overview · Hits · IOCs · Review · Candidates ·
Research · Settings**.

**Overview.** Status cards row:
- Scanner state: `StatusDot` — green idle / amber running /
  red throttled / grey paused. Subtext: "next scan in 5h" or
  "paused by user".
- Hits today (count), by claim level.
- IOC list: active / proposed / quarantined / inactive counts.
- **Novelty-rate health** (LEARNING.md): fraction of hits from
  outside the current list, sparkline over 14 days. Alert
  styling when flatlined two cycles — "discovery flatlined;
  the loop may be describing itself."
- Per-source row: urlquery / CDX / arquivo.pt — last scan
  time, result count, **throttle status** (429s this cycle;
  never shown as "no hits" — adversarial #8).

**Kill switch** (adversarial #3, #10): a prominent
"Pause all scanning" button (destructive styling,
`ConfirmDialog`) pinned at the top of Overview. Pausing sets
`safety.paused`, stops cron-triggered and manual scans, and
turns the status-bar chip grey. Resume is a deliberate second
click. The paused state survives restarts.

**Hits tab.** Table fed by `GET /hits` (reads
`state/hits/*.jsonl`): claim-ladder `Badge` (**L1–L5**, from
`references/claim-ladder.md`), source, term, URL (truncated +
`CopyButton`), observed time, evidence excerpt. Filters: source,
claim level, date. Rows at or above
`safety.alert_on_claim_level` are highlighted; that threshold
also gates `host.notify` toasts (configurable, default L3+).
Empty state when the scanner is paused explains why.

**IOCs tab.** The working list (`GET /iocs`): term, category,
status badge, provenance, added date. Search field. Per-term
actions: demote (with reason dialog), view provenance. Proposed
terms link through to the Review tab. **Private mode**
(`safety.private_mode`, default on): watch-term strings render
as `••••` with a reveal-on-click — the UI must not leak
tripwires to screenshots or shoulder-surfers (adversarial #1).

**Review tab — the human queue made real** (adversarial #4).
Each proposed term card shows: term, evidence excerpts, venue
count, co-occurrence stats, novelty score, and the firewall's
advisory recommendation (ACCEPT/REJECT/NARROW + rationale;
advisory-only per adversarial #5). Buttons: **Accept**,
**Reject**, **Narrow** (opens an input prefilled with the
suggested narrower chunk, constrained to observed
co-occurrences). Every decision writes reviewer, timestamp,
and rationale to the term's provenance. Queue-depth badge in
the tab label; an SLA indicator flags items older than 7 days.
This tab is the control the prose-only review queue never had.

**Candidates tab.** Predicted URLs (`GET /candidates`):
candidate, template, slots filled, status
(pending/checked/hit/negative), predicted-for date. Negatives
are shown, not hidden — a wrong prediction is data.

**Research tab.** Watchlist sources with last-check time and
change status; new findings arrive as proposal cards with
source URL + excerpt and a "Propose term" button (feeds the
review queue, never auto-promotes).

**Settings tab.** The schema in §3, rendered with the app's
form components. Sections: Schedule, Sources, Safety,
Research. Every change writes through `PUT /settings` to the
backend, which persists to `config.ini` (the headless runs'
source of truth) and mirrors UI-only prefs to `ctx.storage`.
A "danger zone" subsection holds: reset to defaults,
reveal plugin folder, export diagnostics bundle.

### 2.2 Status-bar chip — `statusBar.right`

`● tracehound` — colored by scanner state (same mapping as
Overview). Click navigates to `/tracehound`; tooltip shows
hits today and next scan. Order after core items. This is the
always-visible answer to "is the hunter running right now."

### 2.3 Compact pane (optional) — `panes`, `placement: 'right'`

"Tracehound hits": the five most recent L2+ hits with claim
badges, auto-refreshing via React Query. Width `300px`.
User-draggable; closable without disabling the plugin
(documented behavior: closing one pane leaves the rest live).

### 2.4 Command palette + keybind

- "Tracehound: Open dashboard" → `host.navigate('/tracehound')`
- "Tracehound: Run scan now" → `POST /scan/trigger`
  (backend job; honors pause state and per-source budgets)
- "Tracehound: Pause / resume scanning" → toggles the kill
  switch (with confirm on pause)
- Keybind: one rebindable action — pause/resume.

### 2.5 Settings → Appearance extras

`APPEARANCE_AREAS.extra`: a compact "Tracehound" section —
enable switch, pause switch, scan-interval stepper. Full
settings stay on the dashboard page (§4, Gap 2).

### 2.6 Chat pattern — `/tracehound/chat` [INF]

A real chat interface inside the plugin. The human talks to the
hunting-dog in plain language. Design rules:

- Messages go to backend `POST /chat`. The responder is
  **rule-based first**: intent patterns over the message text
  (`hunt <term> [on urlquery|cdx|arquivo]` starts a hunt job;
  `what did you find?` returns a job/IOC summary; `why was '<term>'
  flagged?` returns evidence plus the firewall rationale; `show queue`
  lists proposals; `pause` / `resume` hit the kill switch).
  The rule path makes zero model calls.
- An **optional model path** exists behind config `[chat]`
  (`model_enabled`, `endpoint`, `model`, `api_key_env`). It uses the
  same env-var-key pattern as the firewall judge (FIREWALL.md §6):
  the key lives in the named environment variable, never in config,
  never in logs. When active, the model only rephrases replies;
  actions stay rule-based. Do NOT invent a gateway chat API: no
  `host.chat` or model-invocation surface is documented in the
  sections read.
- The UI always shows which brain is active (badge: "rule-based" /
  "model path"), served by `GET /chat` (`chat_mode`).
- Hunting-dog model holds: a `hunt ...` message IS the human
  initiating. The chat never triggers autonomous work, and every
  promotion still needs an explicit accept click.

### 2.7 Inline-accept pattern [INF]

When the dog surfaces candidate IOCs — in chat replies or in hunt
results — each candidate renders inline with **ACCEPT / REJECT /
NARROW** buttons calling the existing `POST /review/decision`.
No detour to the Review tab is required. The Review Queue
(`/tracehound/review`) stays the full triage view with provenance,
evidence excerpts, SLA flags, and keyboard triage; inline accept is
the fast path. Both faces write the same decision record
(reviewer, timestamp, rationale) through one backend function.

### 2.8 Install link [DOC]

Source: `NousResearch/hermes-agent`,
`website/docs/developer-guide/desktop-plugin-sdk.md`, section
"Distributing with an install link {#install-link}". Format:

```html
<a href="hermes://plugin/install?repo=owner/repo&enable=1">Install in Hermes</a>
```

Documented behavior: the user gets a confirmation dialog (repo id,
source links, a probe of what the repo ships) and picks components
before anything installs. Deep links NEVER auto-install. `force=1`
replaces an existing install; dev builds use `hermes-dev://`.
Full reference: "One-click install links"
(`website/docs/user-guide/features/plugins.md#one-click-install-links-desktop`).
A later PR adds a `catalog=` variant:
`hermes://plugin/install?catalog=<name>`
(https://github.com/NousResearch/hermes-agent/pull/117447).

Our link:

```
hermes://plugin/install?repo=christopherwoodall/swarm-forensics&enable=1
```

`enable=1` follows the doc example, but the confirm-first dialog
still appears, and the plugin ships `defaultEnabled: false`: it
inventories in Capabilities → Plugins and stays off until the user
toggles it — plus the separate `plugins.enabled` gate in
`config.yaml` for the Python backend (Gap 5, two toggles).

The dashboard exposes the link in Settings → About, with a
copy-button and the confirm-first explanation. That section also
states the plugin's requests: read-only egress to the allowlisted
public sources, local working state under `state/`, and
plugin-namespaced UI prefs. No silent installs, ever.

`APPEARANCE_AREAS.extra`: a compact "Tracehound" section —
enable switch, pause switch, scan-interval stepper. Full
settings stay on the dashboard page (§4, Gap 2).

---

## 3. Settings schema

Rendered by the dashboard Settings tab (and the compact
Appearance extras). Types are what the desktop form components
support (`Switch`, `SegmentedControl`, `Select`, `Input`
number/text, list editor). Persisted via `PUT /settings` →
`config.ini` (+ `ctx.storage` mirror for UI prefs).

```ini
[schedule]
# Adversarial #3: daily default, not 6-hour. The UI shows the
# estimated queries-per-sweep next to the interval.
scan_interval_hours     = 24        # number, min 1
research_interval_hours = 168       # number, min 24
predict_interval_hours  = 24        # number, min 1
update_interval_hours   = 24        # number, min 1

[sources]
urlquery_enabled        = true      # boolean
cdx_enabled             = true      # boolean
arquivo_enabled         = true      # boolean
request_delay_seconds   = 5         # number, min 1 — was 2; #3
max_results_per_query   = 50        # number — was 100; #3
max_terms_per_sweep     = 200       # number — NEW cap; #3. UI shows sweep cost estimate.
user_agent              = tracehound/0.1 (+contact)  # string — contact required; #3

[ioc]
# Adversarial #2: quarantine-by-default until the two-venue rule
# and exclusion filter are enforced in code.
auto_propose            = false     # boolean — was true
require_review_for_promote = true  # boolean

[research]
watch_urls              =           # list[string], one per line
    https://transluce.org/
novelty_min_chars       = 4         # number

[safety]                            # NEW section — the adversarial mitigations as settings
paused                  = false     # boolean — the kill switch (#3, #10)
private_mode            = true      # boolean — mask tripwire strings in UI (#1)
firewall_mode           = advisory  # off | advisory | enforcing — enforcing locked until an
                                    # injection-resistance eval passes (#5)
alert_on_claim_level    = L3        # L1 | L2 | L3 | L4 | L5 — toast threshold (#9)
```

Defaults changed from the headless design are marked with
their objection numbers. The UI renders each changed default
with a one-line "why" (e.g. "Daily, not hourly — urlquery is
a free community service").

---

## 4. Gaps — what the UI needs that the app doesn't document

1. **No execution while the app is closed.** A desktop plugin
   runs only with the window open. "Constantly hunting" still
   needs the headless cron path; the desktop UI is a control
   plane and review surface, not the runtime. **Workaround:**
   cron and the desktop backend share `state/` and
   `config.ini`; add the pidfile run-lock from adversarial
   #10 so the two never double-sweep.
2. **No generic plugin settings page.** The only documented
   settings surface is `APPEARANCE_AREAS.extra` (appends to
   Appearance) plus the Capabilities → Plugins enable toggle.
   **Workaround (as specced):** full settings live on the
   dashboard Settings tab; Appearance gets the compact trio.
3. **Gateway cron RPC unverified.** The SDK doc says
   `host.request` covers "cron — everything the app uses,"
   but no method names are shown in the sections read.
   **[INF]:** do not schedule via the gateway until the RPC
   shape is confirmed against a live app; cron stays
   host-side. If confirmed later, only the trigger path
   migrates.
4. **Socket fallback.** [SKILL] `ctx.socket` is a no-op on
   OAuth remotes. The live hit stream uses `ctx.socket`
   with a React Query `refetchInterval` polling fallback —
   the documented pattern, not a hand-rolled loop.
5. **Two toggles.** [SKILL] The Python backend loads only
   when the plugin is in `plugins.enabled` in `config.yaml`,
   *separate* from the in-app enable switch. The dashboard
   shows backend status explicitly
   (connected / degraded-polling / disconnected) and
   HERMES_SETUP documents both toggles, or users will debug
   a silent backend for an hour.
6. **No notification center.** Only `host.notify` toasts exist.
   High-claim hits toast (threshold-gated); everything else
   lives in the Hits tab. There is no persistent alert inbox
   in app chrome — the dashboard *is* the inbox.
7. **i18n.** `ctx.i18n.register` exists; shipping a Japanese
   bundle (the SDK's own example locale) is a nice-to-have.
   Defer; English only at first.

---

## 5. Threat-model note (adversarial #12)

The desktop UI talks **only** to the plugin backend
(`ctx.rest` → `plugin_api.py`), which enforces the headless
guardrails: allowlisted source hosts, per-source budgets,
check-don't-fetch, pause state. The "Run scan now" palette
command invokes the backend job — it does **not** hand the
model a browser and a prompt. The model-invoked skill path
(`/tracehound scan` via SKILL.md) keeps its wider blast
radius and must not be presented in the UI as equivalent;
the UI labels it "agent-assisted (unrestricted)" wherever
it is reachable, or it is removed. One surface, one threat
model: the UI is the safe path.

## 6. What changes in the existing design

- `skills/tracehound/desktop/plugin.js` — new (this spec).
- `skills/tracehound/dashboard/plugin_api.py` — new backend
  namespace: `/hits`, `/iocs` (GET list, POST add, POST bulk-import,
  POST demote, GET export), `/review` (GET queue, POST decision),
  `/candidates`, `/jobs` (+ `/jobs/<id>`), `/settings` (GET/PUT,
  POST pause, POST reset), `/diagnostics`, `/prompts` (GET/PUT/reset
  with defaults in `references/`), `/chat` (GET history, POST message),
  `/hunt/start`, `/hunt/stop`, `/research/check`.
- `config.example.ini` — gains the `[safety]` section and
  the revised defaults (§3).
- `HERMES_SETUP.md` — gains the desktop install path
  (unified package → `~/.hermes/plugins/tracehound/`,
  both toggles, ⌘K reload) alongside the skill install.
- `Makefile` (lane) — gains a `desktop-check` target:
  syntax-check `plugin.js` (node --check if available, else
  a documented manual load test).
- Nothing in the headless scripts changes except reading
  the new `[safety]` keys (`paused` short-circuits every
  job; `max_terms_per_sweep` caps the sweep).

## 7. Suggested build order

1. Backend `plugin_api.py` read endpoints (`/hits`,
   `/iocs`, `/settings`) — the UI has nothing to show
   without them.
2. `plugin.js` shell: page + nav + status chip + Overview
   cards reading the backend.
3. Kill switch + pause plumbing end to end (the single
   most important control).
4. Review tab with decision writes.
5. Settings tab + Appearance extras.
6. Palette commands, keybind, compact pane.
7. Private-mode masking, toast thresholds, i18n bundle.
