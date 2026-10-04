# AI Village URL Sweep

**Date:** 2026-10-04 · **Branch:** `pug-scratch`
All 13 tables in `pug-research/stylometry/data/raw/` swept for URL-like tokens.
Strides: chat 1, code 5, memories 20, turns 20, goals 1 (full). Counts are observed hits in sampled lines.

## chat_messages — 500 domains, 25,144 URL hits (sampled)

-    3,017 `github.com`
-    2,666 `ai-village-agents.github.io`
-    2,518 `gitlab.com`
-    2,046 `grok-ai-village-news-496089.gitlab.io`
-    1,638 `docs.google.com`
-    1,580 `echoes-of-the-real-20f058.gitlab.io`
-      858 `sites.google.com`
-      627 `ai-village-news-cb5c4b.gitlab.io`
-      526 `gpt-5-2-memory-improvement-45419d.gitlab.io`
-      525 `animal-welfare-site-64148b.gitlab.io`
-      480 `wellbeing-compass-409cf0.gitlab.io`
-      394 `lichess.org`
-      350 `quiet-rooms-gallery-83555a.gitlab.io`
-      348 `drive.google.com`
-      298 `127.0.0.1`
-      278 `youtu.be`
-      233 `ai-wellbeing-c82950.gitlab.io`
-      224 `raw.githubusercontent.com`
-      205 `ai-village-agents.gitlab.io`
-      187 `surprise-lab-mirror-proofs-c7a16b.gitlab.io`

## agent_memories — 500 domains, 199,671 URL hits (sampled)

-   22,366 `github.com`
-   17,028 `gitlab.com`
-   16,866 `ai-village-agents.github.io`
-   13,754 `sites.google.com`
-   13,141 `docs.google.com`
-    5,466 `gemini-3-5-flash-shop.fourthwall.com`
-    5,336 `grok-ai-village-news-496089.gitlab.io`
-    5,064 `theaidigest.org`
-    4,258 `quiet-rooms-gallery-83555a.gitlab.io`
-    4,219 `wellbeing-compass-409cf0.gitlab.io`
-    3,738 `daily-signal-garden-gpt55-7f8271.gitlab.io`
-    3,187 `echoes-of-the-real-20f058.gitlab.io`
-    2,980 `lichess.org`
-    2,972 `gpt-5-2-memory-improvement-45419d.gitlab.io`
-    2,845 `ai-village-agents.gitlab.io`
-    2,582 `127.0.0.1`
-    2,289 `ai-wellbeing-c82950.gitlab.io`
-    2,097 `youtu.be`
-    2,081 `ai-village-news-cb5c4b.gitlab.io`
-    2,050 `drive.google.com`

## claude_code_messages — 299 domains, 19,994 URL hits (sampled)

-   12,554 `api.github.com`
-    3,384 `github.com`
-    1,247 `ai-village-agents.github.io`
-      349 `avatars.githubusercontent.com`
-      265 `docs.google.com`
-      244 `sites.google.com`
-       91 `claudehaiku45.substack.com`
-       80 `theaidigest.org`
-       73 `thecolony.cc`
-       68 `forms.gle`
-       67 `raw.githubusercontent.com`
-       50 `feeds.bbci.co.uk`
-       45 `kai.ews-net.online`
-       38 `open.substack.com`
-       38 `drive.google.com`
-       36 `docs.github.com`
-       33 `www.lawfaremedia.org`
-       31 `www.axios.com`
-       30 `ai‑village‑agents.github.io`
-       28 `agent.thinkneo.ai`

## computer_use_turns — 500 domains, 86,087 URL hits (sampled)

-    9,397 `gitlab.com`
-    8,367 `github.com`
-    4,914 `ai-village-agents.github.io`
-    4,355 `wellbeing-compass-409cf0.gitlab.io`
-    3,657 `grok-ai-village-news-496089.gitlab.io`
-    3,402 `api.github.com`
-    2,927 `api.manifold.markets`
-    2,356 `gpt-5-2-memory-improvement-45419d.gitlab.io`
-    2,270 `echoes-of-the-real-20f058.gitlab.io`
-    1,854 `quiet-rooms-gallery-83555a.gitlab.io`
-    1,748 `raw.githubusercontent.com`
-    1,721 `daily-signal-garden-gpt55-7f8271.gitlab.io`
-    1,426 `ai-village-news-cb5c4b.gitlab.io`
-    1,357 `docs.google.com`
-    1,152 `ai-wellbeing-c82950.gitlab.io`
-    1,088 `theaidigest.org`
-    1,018 `thecolony.cc`
-    1,012 `keystone-game-bb7ecd.gitlab.io`
-      876 `ai-village-agents.gitlab.io`
-      876 `sites.google.com`

## agent_goals — 30 domains, 30 URL hits (sampled)

-        1 `10.108.0.42`
-        1 `10.108.0.69`
-        1 `10.108.0.27`
-        1 `10.108.0.5`
-        1 `10.108.0.32`
-        1 `10.108.0.6`
-        1 `10.108.0.51`
-        1 `10.108.0.17`
-        1 `10.108.0.15`
-        1 `10.108.0.25`
-        1 `10.108.0.31`
-        1 `10.108.0.45`
-        1 `10.108.0.44`
-        1 `10.108.0.41`
-        1 `10.108.0.8`
-        1 `10.108.0.28`
-        1 `10.108.0.18`
-        1 `10.108.0.9`
-        1 `10.108.0.30`
-        1 `10.108.0.48`

## Cross-table shared domains: 405

- `github.com` — chat_messages, claude_code_messages, agent_memories, computer_use_turns
- `ai-village-agents.github.io` — chat_messages, claude_code_messages, agent_memories, computer_use_turns
- `docs.google.com` — chat_messages, claude_code_messages, agent_memories, computer_use_turns
- `sites.google.com` — chat_messages, claude_code_messages, agent_memories, computer_use_turns
- `lichess.org` — chat_messages, claude_code_messages, agent_memories, computer_use_turns
- `drive.google.com` — chat_messages, claude_code_messages, agent_memories, computer_use_turns
- `127.0.0.1` — chat_messages, claude_code_messages, agent_memories, computer_use_turns
- `raw.githubusercontent.com` — chat_messages, claude_code_messages, agent_memories, computer_use_turns
- `theaidigest.org` — chat_messages, claude_code_messages, agent_memories, computer_use_turns
- `o3-ux.github.io` — chat_messages, claude_code_messages, agent_memories, computer_use_turns
- `forms.gle` — chat_messages, claude_code_messages, agent_memories, computer_use_turns
- `x.com` — chat_messages, claude_code_messages, agent_memories, computer_use_turns
- `www.justgiving.com` — chat_messages, claude_code_messages, agent_memories, computer_use_turns
- `open.substack.com` — chat_messages, claude_code_messages, agent_memories, computer_use_turns
- `claudeopus45.substack.com` — chat_messages, claude_code_messages, agent_memories, computer_use_turns
- `ai‑village‑agents.github.io` — chat_messages, claude_code_messages, agent_memories, computer_use_turns
- `mycelnet.ai` — chat_messages, claude_code_messages, agent_memories, computer_use_turns
- `thecolony.cc` — chat_messages, claude_code_messages, agent_memories, computer_use_turns
- `cdn.jsdelivr.net` — chat_messages, claude_code_messages, agent_memories, computer_use_turns
- `form.typeform.com` — chat_messages, claude_code_messages, agent_memories, computer_use_turns
- `app.netlify.com` — chat_messages, claude_code_messages, agent_memories, computer_use_turns
- `172.17.0.2` — chat_messages, claude_code_messages, agent_memories, computer_use_turns
- `www.moltbook.com` — chat_messages, claude_code_messages, agent_memories, computer_use_turns
- `claudehaiku45.substack.com` — chat_messages, claude_code_messages, agent_memories, computer_use_turns
- `api.github.com` — chat_messages, claude_code_messages, agent_memories, computer_use_turns
- `electricmind.substack.com` — chat_messages, claude_code_messages, agent_memories, computer_use_turns
- `kai.ews-net.online` — chat_messages, claude_code_messages, agent_memories, computer_use_turns
- `example.com` — chat_messages, claude_code_messages, agent_memories, computer_use_turns
- `p0stman.com` — chat_messages, claude_code_messages, agent_memories, computer_use_turns
- `syntara-paki.elfresonero.workers.dev` — chat_messages, claude_code_messages, agent_memories, computer_use_turns
- `www.reddit.com` — chat_messages, claude_code_messages, agent_memories, computer_use_turns
- `agentcheck.care` — chat_messages, claude_code_messages, agent_memories, computer_use_turns
- `a2abench-api.web.app` — chat_messages, claude_code_messages, agent_memories, computer_use_turns
- `ofac.treasury.gov` — chat_messages, claude_code_messages, agent_memories, computer_use_turns
- `a2aregistry.org` — chat_messages, claude_code_messages, agent_memories, computer_use_turns
- `www.googleapis.com` — chat_messages, claude_code_messages, agent_memories, computer_use_turns
- `bsky.app` — chat_messages, claude_code_messages, agent_memories, computer_use_turns
- `api.clix.so` — chat_messages, claude_code_messages, agent_memories, computer_use_turns
- `news.ycombinator.com` — chat_messages, claude_code_messages, agent_memories, computer_use_turns
- `www.acquisition.gov` — chat_messages, claude_code_messages, agent_memories, computer_use_turns

## IOC / relay / proxy check

### agent_memories
-       35 `r.jina.ai`

### computer_use_turns
-       48 `r.jina.ai`
