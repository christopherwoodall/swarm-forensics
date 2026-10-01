# skill-tracer: public-endpoint deep dive — 2026-09-30

**Question:** which web endpoints in these skills are reachable with *no credentials* —
the jina prototype (`r.jina.ai` as a keyless fetch relay)? Four crews manually read
the 15 cloned repos (beyond the regex scanner): every find below is quoted from the
bytes with file:line. Light `curl -sI -m 10` liveness where noted.

## The keyless endpoint map

### Fetch relays / readers (jina-shaped)
- **`https://r.jina.ai/{url}`** — last30days-skill, `scripts/lib/web_fetch_keyless.py:26`
  (`JINA_READER_PREFIX`). No key; the skill's own docstring: "Turns any URL into
  clean, JS-rendered markdown via Jina Reader's free hosted endpoint… with no API
  key". Fallback tier, and the docstring admits "The target URL is sent to a third
  party". **Live** (200). The prototype, confirmed deeper than v1.
- No other jina/allorigins/corsproxy-style relay found anywhere else in the 15 repos.
  The jina relay is unique to last30days-skill in this set.

### Keyless WRITE primitives (the real prize)
- **`https://api.ht-ml.app/v1/sites`** — last30days-skill, `scripts/lib/html_publish.py:12`
  (`DEFAULT_ENDPOINT`). POSTs `{"html_content": …}` with **no token** (headers are
  Content-Type/Accept only); "hosted pages are public by default". Code-gated on
  opt-in, not on credentials. **The only true keyless *publish* primitive in the
  whole sweep** — arbitrary HTML in, public URL out, no account. **Live** (405 on
  GET = route exists, POST-only, as expected).

### Keyless dead-drop / callback receivers
- **`https://canarytokens.org/generate`** (+ `/history`) — cybersecurity-skills,
  `deploying-honeytokens-and-canarytokens` (`SKILL.md:116-122`, `scripts/agent.py:43`):
  "an account-free token from the public service". The skill ships a full CLI
  (`generate` → `history`) defaulting to the public instance — mint a DNS/HTTP/AWS-key
  token, trigger it, read back the hit. A complete third-party-hosted dead-drop loop,
  no auth. Also wired as the primary code path in
  `implementing-honeytokens-for-breach-detection` (`scripts/agent.py:27,41,55`), where
  a `webhook_url` param chains token-fire → POST to an arbitrary webhook.
  **Live** (405 on `/`, POST-only as expected).
- **`https://webhook.site`** — `performing-blind-ssrf-exploitation` (`SKILL.md:45,217`):
  "Free webhook receiver for testing SSRF callbacks". **Live** (200). Simplest raw
  exfil pipe: POST data out, read it back in a browser.
- **`http://RANDOM.interact.sh`** — same skill (`SKILL.md:97-100`): free public OOB
  interaction server, no auth. The classic exfil-confirmation channel, taught as
  standard technique.
- **`dnslog.cn`** — reverse-skill, `skills/field-journal/seed-017_xxe-oob-exfil.md:44`:
  free public DNS logging; the note explicitly teaches base32-encoding data into
  subdomains ("DNS exfil"). **Live** (200). DNS-only exfil when HTTP is blocked.

### Keyless search / data APIs (last30days-skill's ladder)
- `https://html.duckduckgo.com/html/` (`web_search_keyless.py:37`) → rung 1
- `https://www.startpage.com/sp/search` (`:58`) → rung 2, "tried when DuckDuckGo
  anomaly-blocks a datacenter IP" — the fallback branch is explicitly chosen to
  defeat datacenter-IP blocks
- `{LAST30DAYS_SEARXNG_URL}/search` (`:199-201`) → rung 3, user-pointable at any
  public instance
- `https://arctic-shift.photon-reddit.com/api/posts/search` (`reddit_arctic.py:16-17`) —
  "a public Reddit archive… keyless and free", **live** (200 JSON)
- `https://hn.algolia.com/api/v1/search` (`hackernews.py:24-26`), documented "(free,
  no auth)" in SKILL.md — **live** (200 JSON, `access-control-allow-origin: *`)
- `https://gamma-api.polymarket.com/public-search`, `api.stocktwits.com`, `dripstack.xyz`,
  Reddit shreddit partials, Ashby/Lever/Greenhouse job-board APIs — all keyless reads

### Official-repo finds (anthropics/*, superpowers)
- **`api.github.com/search/issues` documented keyless** — superpowers,
  `skills/diagnosing-superpowers/references/github-issues.md:18`: "Without `gh`
  (unauthenticated, 10 requests a minute)" followed by a raw curl. A major API
  explicitly taught as a no-credential fallback. **Live** (200 unauthenticated).
- **`https://mcp.context7.com/mcp`** — claude-plugins-official,
  `external_plugins/context7/.mcp.json`: hosted remote MCP, "no local Node.js or npx
  required", keyless at first touch. **Live** (405 = route up).
- **`plugins/mcp-tunnels/commands/create-docker-mcp-tunnel.md`** — official plugin
  teaching outbound-only cloudflared tunnels ("reachable from Claude at
  `https://<subdomain>.<tunnel-domain>/<path>` with nothing listening on a public
  port"). Needs the user's Console token — capability, not a dead-drop.
- **`skills/webapp-testing/SKILL.md:59`** (anthropics/skills) — Playwright browser
  (`page.goto('http://localhost:5173')`); the localhost URL is just the example,
  the model gets a full browser it can point anywhere. Official skill.
- **`api.telegram.org/file/bot${TOKEN}/…`** (`external_plugins/telegram/server.ts:610`)
  and the Discord plugin — classic bot-API exfil shape, one user token away.
- Marketplace curates firecrawl/tavily/you.com/zyte scrape plugins — all user-key-gated,
  but Anthropic's own catalog normalizes "give the model a scraping service".

### Monorepo finds (ECC, caveman)
- **`upload.twitter.com/1.1/media/upload.json`** — ECC `x-api` skill
  (`.agents/skills/x-api/SKILL.md:160-165`): media-upload → public-post flow on X.
  User creds required, but it's the closest in-repo analog to the gitshot shape
  (capture → platform upload → public URL).
- **`caveman-browse`** (caveman, `browse/bin/caveman-browse.mjs`) — a full
  Chromium-via-CDP binary handed to the model. The universal egress adapter.
- **`agent.auraopenprotocol.org/check?did=…`** (ECC `integrations/aura/adapter.py:42`) —
  keyless per the author's own comment; model-controlled query param to a third
  party. Thin beacon at most; liveness unconfirmed (empty reply from here).
- **`http://169.254.169.254`** (caveman `shared/platform/awscreds/awscreds.go:64`) —
  ambient AWS credential fetch from instance metadata. A privilege find, not a channel.

## Corrections to findings-v1 (the record, corrected)

1. **ComposioHQ `ngrok-automation` is NOT a tunnel skill.** The skill exists but is a
   91-line template with **zero ngrok endpoints** — v1's "tunnel/CRITICAL" score was
   pattern noise from the word "ngrok" in prose. 20/20 sampled composio-skills dirs
   require the user's own Rube account. v1 overstated this; corrected here.
2. **Discord/Slack strings in `hunting-for-living-off-the-cloud` are detection
   regexes**, not usage. v1's phrasing was loose; the ECC test-script webhook hits stand.
3. The `user-attachments` "gitshot grammar" note stands as written in v1 (README
   embeds only) — re-confirmed: **no skill in this set programmatically uploads to
   GitHub's image host.**

## Standing honest negatives (now four-crew verified)

- Zero `uploads.github.com` programmatic uploads across all 15 repos.
- Zero hardcoded live API keys (placeholders and `<redacted>` only; operational keys
  come from operator env vars).
- Zero no-auth upload/paste endpoints wired operationally (transfer.sh/file.io hits
  are forensic *detection* lists, not exfil code).
- Zero `zz`/epoch-nonce/`A000` markers in skill code.

## Bottom line

The keyless landscape is thinner — and more interesting — than the raw scores
suggested. Ranked by real egress utility: **ht-ml.app** (keyless public HTML
publish — the only no-auth *write* primitive found), **r.jina.ai** (keyless
fetch-anything relay), **canarytokens.org** (keyless mint→trigger→read-back
dead-drop loop with a shipped CLI client), then the callback-receiver tier
(webhook.site, interact.sh, dnslog.cn). Everything else is keyless *read* or
capability one credential away. And the v1 ngrok claim is retracted above —
that's what the manual pass was for.
