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

(Results below when the run completes.)
