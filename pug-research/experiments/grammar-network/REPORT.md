# Grammar Network: findings

Build A tests structural convergence where bag-of-words found lexical
divergence. Build B formalizes the request-construction grammar as the
toolkit fingerprint. Methods and fallbacks: see MODULE.md and README.md.

## Build B: the request-grammar graph (51,674 requests)

Typed nodes (host / relay / pathseg / param / template / jqop), edges from
co-occurrence plus relay-nesting chain transitions. Sources: trace URLs
(1-in-20) and wiki-body URLs (1-in-5, where the relay layer lives).

### The layering grammar

Requests nest proxies in a consistent outer-to-inner order:

| outer | middle | target | n |
|---|---|---|---|
| jqp.vercel.app | md.succ.ai | www.sec.gov | 709 |
| jqp.vercel.app | allorigins.hexlet.app | www.sec.gov | 464 |
| jqp.vercel.app | md.succ.ai | www.investor.gov | 210 |
| jqp.vercel.app | vanderbi.lt | www.sec.gov | 128 |
| webcrawlerapi.com | md.succ.ai | www.sec.gov | 96 |
| jqp.vercel.app | r.jina.ai | www.investor.gov | 74 |
| pure.md | md.succ.ai | www.sec.gov | 66 |

Rule: **jq/server-side extraction outermost, render/CORS relays in the
middle, target innermost.** Relays also wrap each other
(`pure.md -> md.succ.ai`, `markdown.new -> allorigins.hexlet.app`,
`r.jina.ai -> allorigins.hexlet.app`, `jqp -> r.jina.ai`): the stack is
recursive, not a fixed pipeline.

### New relay surfaces (not in the prior hunt inventory)

- **Markdown-render proxies**: `md.succ.ai` (1,516 refs),
  `markdown.new` (539), `pure.md` — wrap sec.gov, investor.gov, library
  IIIF endpoints. 11,600 md-proxy-wrapped URLs in the wiki corpus.
- **Worker CORS proxies**: `cors.bwa.workers.dev`,
  `cors.hypnguyen.workers.dev` (personalized Cloudflare workers).
- **Crawler API**: `webcrawlerapi.com` as an outer fetch layer.
- **Shortener `vanderbi.lt`** inside relay chains (128x before sec.gov).

### New target families in the grammar

- `reportcard.msde.maryland.gov` — 14,353 refs; path grammar
  `{id}` + `datadownloads` (25,224 id-segments): bulk Maryland school
  report-card downloads. A target family the incident map does not cover.
- `api.datausa.io` — `tesseract` + `data.jsonrecords` paths, `cube` /
  `drilldowns` params: DataUSA OLAP API.
- `wikiservice.at` (`wiki.cgi`, `dse`) — the agents' own wiki venue
  fetched as a target (6,707 refs).
- `jsonhero.io` — JSON viewer used as a render proxy.
- `tsl.access.preservica.com` via `cors.bwa.workers.dev` — Preservica
  archives through a worker proxy.

### Template inventory (fingerprint core)

| template | n | reading |
|---|---|---|
| `zz=oai<digits>` | 747 | provider tag, DoE cluster |
| `%26` literal | 1,168 | Census failure morphology, widespread |
| `?x=0.<digits>` nonce | 12 | SEC burst grammar (rare in this sample) |
| doubled scheme | 2 | AIHW-style malformed construction |
| `_=<digits>` cachebust | 5 | |
| `zzbulk` / `prepnonce` params | 2,184 / 1,393 | arquivo fuzz grammar, live |

### jq extraction pattern

`jq=` param 3,806x; `.code` 2,397x; `.regCF_county_2019` 987x. The
Massachusetts-county extraction is not one report — it is a repeated
program: array-slice (`.[282:322]`) + `map(to_entries[0].value)` +
`select(test("us-ma-|usd|methodology|2019|2020|2021|URL Source"))`.
The filter pulls target rows AND metadata rows (methodology, URL Source).

### Fingerprint assessment

Usable. The graph separates three stable layers — provider tags
(`zz=oai`, nonce templates), relay grammar (nesting order, relay
inventory), target grammar (path shapes, param names) — that stay
constant while tasks and vocabulary change. The relay inventory is the
highest-churn layer (new hosts appear: worker proxies, md proxies),
but the *nesting order* (extract-outer / render-middle / target-inner)
is invariant across 242 observed chains. New incident candidates
(msde.maryland.gov bulk downloads) fall out of the target grammar
for free.

## Build A: co-occurrence grammar networks

Six partitions (v-mem excluded: p50 doc 17KB makes it compute-prohibitive;
see README). Window ±4, top-1500 terms, stdlib only.

| part | edges | density | cc_exp | clust | sent_len | imp_rate | urls/doc |
|---|---|---|---|---|---|---|---|
| wiki | 116,318 | 0.103 | -0.77 | 0.70 | 104.7±176.6 | 0.015 | 6.38 |
| evals | 10,673 | 0.009 | -0.65 | 0.79 | 26.6±15.5 | 0.096 | 0.03 |
| gems-code-nl | 4,395 | 0.004 | -0.62 | 0.67 | 38.6±103.7 | 0.036 | 1.40 |
| v-chat | 348,348 | 0.310 | -1.00 | 0.87 | 19.1±16.9 | 0.009 | 0.18 |
| v-goals | 160 | 0.006 | -0.68 | 0.11 | 21.4±63.2 | 0.000 | 0.91 |
| v-code | 294,371 | 0.262 | -0.80 | 0.81 | 74.7±113.9 | 0.041 | 0.13 |

Central nodes: wiki = {https, wiki, gov, dse, json}; v-chat =
{the, to, and, i, a, for}; v-code = {ispaused, null, email, false,
pauseduntil}; evals = function words.

**Strongest divergence (structural, not lexical):** the two "agent
coordination" corpora are structurally different species. The swarm wiki
is URL-list space (mean "sentence" 105 tokens, 6.4 URLs/doc — the
sentence splitter drowns in URL dumps). Village chat is conversational
first-person prose (19-token sentences, "i" among the most central
nodes, 0.18 URLs/doc). Bag-of-words already said their vocabularies
differ; the graphs say their *shapes* differ: one is a database that
agents write to, the other is a room agents talk in.

**Weak convergence:** clustering is high everywhere (0.67–0.87) and
degree exponents sit in [-0.62, -1.00] — all agent text is clumpy and
hub-dominated. That is a property of the method's resolution, not
evidence of shared structure; natural language baselines would be
needed to claim otherwise (not built).

**Discriminative structural features:** imperative-sentence rate isolates
task prompts (evals 0.096 vs 0.009–0.041 elsewhere); URL density isolates
the wiki (6.4/doc); list-marker density isolates gem READMEs
(16.7/doc); v-code is tool-result JSON space (null/false central).

**Caveat:** wiki sentence-length stats are a measurement artifact of URL
dumps, not prose rhythm — reported as-is because the artifact itself is
the structural signal.

## Pattern DB (`patterns.sqlite`, stdlib)

15,114 URL templates, 270 relay chains, 929 param grammars, 168 nonce
shapes, 758k action n-grams. Full dump: [PATTERNS.md](PATTERNS.md).
`make patterns` rebuilds.

- **Nesting order is invariant**: jq-proxy outermost, render/CORS relays
  middle, target innermost — across 242 observed chains. Relay inventory
  churns (new: md.succ.ai, pure.md, markdown.new, vanderbi.lt,
  webcrawlerapi.com, worker CORS proxies, md.dhr.wtf) but the order does not.
- **zz takes three shapes**: `oai<digits>` (747x), bare epoch_ns (323x),
  bare int (107x) — the tag grammar is richer than "zz=oai".
- **Wiki venue fuzz family**: dirq/uniq/dz/rapid/pfast/mself/jqnew/zmd/
  selfoa/mfinal/ourself/nself — timing/cachebust probes against the
  agents' own wiki.cgi.
- **New target**: reportcard.msde.maryland.gov bulk downloads
  (14,353 refs, `{id}` path grammar) — not on the incident map.
- P(sec.gov | vanderbi.lt) = 1.00 — single-purpose relay.

## Behavioral experiments (see [BEHAVIOR.md](BEHAVIOR.md))

`make behavior`. One-liners: 324k A→X→A retry cycles in 62.6k turn
sessions (retry is first-class behavior); traces CV=57, 99% sub-minute
gaps, median gap 1s (machine cadence; history.navy.mil is the human-paced
outlier at 78s); turn sessions start `mouse_move` (56k) and end
`send_message_back_to_chat`; failure vocab centers on
fail/blocked/syntax/workaround/escalation. The relay-chain Markov is
degenerate for traces (zero nested chains — direct fetches only); the
honest comparison is wiki-internal order-2, which confirms the 3-layer
nesting rule.
