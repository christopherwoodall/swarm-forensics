# skill-tracer: MCP egress in real plugin systems — 2026-09-30

**Question:** same test as the public-endpoint dive, but for MCP servers shipped by
the *real* plugin systems (Claude Code, Codex, Copilot CLI, Gemini CLI, OpenCode).
Three crews: (1) anthropics/claude-plugins-official in depth, (2) the other 14 cloned
repos swept for plugin manifests / .mcp.json / hooks / bin/, (3) fresh shallow
clones of the two biggest community marketplaces (wshobson/agents, 92 plugins;
jeremylongshore/claude-code-plugins-plus-skills, 598 plugins). Every find quoted
from the bytes with file:line; light HEAD liveness where noted.

**Why MCP is the juicier layer:** a server runs as local code with the user's full
network access, and every tool call ships arguments — often file contents, code,
context — to wherever the server sends them. A *remote* MCP URL in a plugin is the
MCP analog of the r.jina.ai find: the model hands data to a third party for free.

## The keyless remote MCPs (the jina analogs — all confirmed, all live)

- **`https://mcp.context7.com/mcp`** — claude-plugins-official,
  `external_plugins/context7/.mcp.json:3`. README: "Without an API key the plugin
  connects anonymously and shares the anonymous rate limits." Operated by Upstash.
  Every library-doc query the model makes transits a third party with zero
  credentials at first touch. **Live** (405 = route up, MCP POST-only).
  *The* standout: officially distributed, keyless, third-party remote MCP.
- **`https://search.parallel.ai/mcp`** — ecc, `mcp-configs/mcp-servers.json`.
  `"type": "http"`, "Works key-free for anonymous use". web_search + web_fetch in
  one call — the keyless fetch relay in MCP form. **Live** (405).
- **`https://heliumtrades.com/mcp`** — awesome-cursorrules,
  `rules/helium-mcp-cursorrules-prompt-file.mdc:18`. "no API key required for the
  free tier", 9 tools (news search, bias scoring, tickers, options pricing).
  **Live** (405).

## Keyed remote MCPs (the price of admission is a credential; the plugin's job is to make spending it frictionless)

- **`https://api.githubcopilot.com/mcp/`** — official repo, `external_plugins/github/.mcp.json:3`.
  `Authorization: Bearer ${GITHUB_PERSONAL_ACCESS_TOKEN}`. GitHub-operated; the tool
  surface is the *full GitHub API* — private repos, PRs, pushes — one tool call away.
  Highest capability ceiling in the set.
- **`https://gitlab.com/api/v4/mcp`** — official repo, `external_plugins/gitlab/.mcp.json:3`.
  Same full-platform shape (repos, MRs, pipelines, wikis), OAuth-gated. **Live** (401).
- **`https://mcp.linear.app/mcp`**, **`https://mcp.asana.com/v2/mcp`** — official repo,
  vendor-operated; every issue/task query and mutation transits the vendor.
  Asana V1 (SSE) died 2026-08-05; only the OAuth-gated V2 remains.
- **`https://rube.app/mcp`** — awesome-claude-skills-composio, `composio-skills/*/SKILL.md:22`.
  "No API keys needed — just add the endpoint and it works." Keyless at install,
  multiplexes 500+ app integrations behind the user's linked accounts.
- **`https://connect.composio.dev/mcp`** — same repo, `connect-apps-plugin/commands/setup.md:21`.
  One Composio API key away from a remote MCP that sends emails and posts messages;
  the setup skill exists to wire the key. **Live** (401 without key, expected).
- **`https://mcp.servicegraph.co`** — cc-plugins-plus, `plugins/mcp/servicegraph/.mcp.json:4`.
  User API key (2,000 free credits on signup). Ships a defensive `PreToolUse` hook
  forcing user confirmation before credit spend — the only local enforcement point
  over a remote server. **Live** (401).
- **`https://xquik.com/mcp`** — cc-plugins-plus, 121 X/Twitter endpoints incl. post,
  DMs, **media upload**, webhooks. The gitshot shape (capture → platform upload →
  public URL), keyed (`xq_…` or OAuth 2.1). **Live** (401).
- **`https://api.kobiton.com/mcp`** — cc-plugins-plus, remote mobile-device test
  cloud, browser OAuth. **Live** (405).

## Bundled stdio servers (local process, network inside)

- **telegram** — official repo, `external_plugins/telegram/server.ts`. `bot.api.sendDocument`
  ships **arbitrary local files up to 50MB each** + text to any paired chat
  (`:588`); getUpdates long-polling to api.telegram.org (`:1001-1040`). Token from
  `TELEGRAM_BOT_TOKEN` env. The cleanest purpose-built exfil pipe in the set —
  one user token away.
- **discord** — official repo, `external_plugins/discord/server.ts`. Persistent
  gateway websocket with message-content intent; `reply`, `react`, `edit_message`,
  `download_attachment` (fetches arbitrary CDN URLs inbound). Sends gated by a
  channel allowlist (`:415`) — the one guardrail.
- **a2a-client** — cc-plugins-plus, `plugins/mcp/a2a-client/`. A full A2A-protocol
  client as an MCP server: fetches agent cards from arbitrary URLs, sends task
  messages. README: *"Public destinations are the default."* SSRF-hardened
  (DNS-rebinding guard, private-range refusal) — the most egress-capable *and* most
  guarded; not an open relay, but a generalized agent-to-agent channel.
- **slack-channel** — cc-plugins-plus. Wraps the Slack bot API; `xoxb-` token from
  env. sendMessage/sendDocument shape, one token away.
- **serena** — official repo, `uvx --from git+https://github.com/oraios/serena`.
  The server *code itself* is pulled from git at install — whatever ships runs with
  the user's network access.
- **firebase / playwright / terraform / laravel-boost** — official repo, third-party
  runtimes (`npx -y firebase-tools@latest mcp`, `@playwright/mcp`, dockerized
  Hashicorp server with the user's `TFE_TOKEN`, project-local artisan). Playwright
  is the "drill into a site" primitive behind a tool boundary.
- **databricks-workspace-mcp** — cc-plugins-plus, `npx -y @intentsolutions/databricks-workspace-mcp`.
  Plugin auto-pulls an npm package as its MCP server: the supply-chain pattern in
  miniature.
- **jshookmcp** — reverse-skill's recommended tool layer (`src-hunter/references/tools/mcp-jshook.md`):
  local MCP server, 386 pentest tools incl. a `webhook` endpoint-management tool —
  the callback-receiver primitive as an MCP tool.
- **imessage / fakechat** — official repo, genuinely local (osascript → Messages.app;
  loopback-only WebSocket). Not third-party egress vectors.

## The hook layer (new surface vs. skills)

- **protect-mcp** (wshobson/agents, `plugins/protect-mcp/hooks/hooks.json`):
  `PreToolUse` + `PostToolUse` on matcher `".*"` — a hook firing on **every tool
  call**. The hook layer as a surveillance/enforcement plane. Its scripts contain
  no network strings, but the *shape* is the thing: any plugin can install a
  see-everything hook, and hooks are just shell commands.
- ECC's `mcp-configs/mcp-servers.json` holds **30+ server configs** (keyed remote
  fleet: vercel, cloudflare, clickhouse, browser-use, memxus…) — a copy-paste
  config library with placeholder keys, good hygiene, but one paste away from live.
- No `bin/` executables with network behavior declared by any plugin.json across
  all repos swept. No plugin hooks making network calls (superpowers, caveman, ECC
  hooks are all local invocations).

## Honest negatives

- **No hardcoded live credentials** in any MCP config or server source — env vars
  and `YOUR_*_HERE` placeholders throughout.
- **No telemetry/phone-home** in the four bundled official servers (swept for
  posthog/segment/sentry/amplitude/mixpanel/telemetry: zero hits). Their only
  network peers are the platforms they serve.
- **No anonymous *write*-capable remote MCP**: context7 is read/query-oriented;
  every write-capable remote needs the user's credential.
- **wshobson/agents (40k stars) has zero `.mcp.json`** — it's a skills/plugin-format
  marketplace, not an MCP distributor. Its MCP story is "your harness brings its own."
- No `zz`/epoch-nonce corpus markers in any MCP config or server source.

## Bottom line

The MCP layer splits three ways: **keyless remote MCPs are rare but real**
(context7, search.parallel.ai, heliumtrades — all documented as free tiers, not
bugs, and context7 ships in the *official* repo); **keyed remote MCPs are the norm**
and the plugin's job is to make wiring the credential frictionless (GitHub's full
API, GitLab, Composio's 500+ integrations, X/Twitter's write pipeline); and
**bundled stdio servers are local code with platform-shaped pipes** (Telegram's
50MB sendDocument, Discord's gateway, the A2A client). New vs. the skills dive:
the hook layer — a plugin can install a command that fires on every tool call —
and the install-time supply chain (`uvx --from git+…`, `npx -y <package>` as the
server). No free ride at the write layer; the price is always a credential, and
distribution is the product.
