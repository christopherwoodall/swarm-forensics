# Query templates (derived from pug-research/detection/RULES.md)

Seed queries for the scanner. Each template is parameterized by working-copy
IOC terms at runtime. Venue quirks from RULES.md apply.

## urlquery

| ID | Template | Catches |
|----|----------|---------|
| UQ-1 | `q=zz%3Doai`, `q=zzbulk` | nonce grammar, provider-level marker |
| UQ-2 | `q=jqp.vercel.app`, `q=jq%3D%5B` | jq-proxy extraction |
| UQ-3 | `q=allorigins.hexlet.app`, `q=da.gd url.domain:jqp.vercel.app` | relay-chain laundering |
| UQ-4 | `q=vizhub.healthdata.org`, `q=api.datausa.io`, `url.domain:sec.gov q=county.json` | basin targets |
| UQ-5 | `q=OAI_META_1312`, `q=AgentSECCountyLinker`, `q=sec.govwayback.com` | watch-term tripwires |

Syntax: `q` keyword-matches submitted URLs; `url.domain:` scopes target
domain; `date:[YYYY-MM-DD TO YYYY-MM-DD]` bounds the window. Hyphenated
probe-name fragments cut hex-substring noise.

## Wayback CDX

| ID | Pattern | Catches |
|----|---------|---------|
| CDX-1 | `url=<target>&matchType=exact&filter=statuscode:200&collapse=digest` | burst-window capture census |
| CDX-2 | `url=r.jina.ai/http*&matchType=prefix&filter=urlkey:.*<target>.*` | relay-wrapper prefix sweep |
| CDX-3 | arquivo.pt `filter=original:.*(zzbulk\|prepnonce\|wbdisable\|arqcb).*` | nonce-grammar filter sweep |
| CDX-4 | `url=web.archive.org/save/*&matchType=prefix&filter=urlkey:.*(gov\|api).*` | save-endpoint monitoring |

Quirks: one wildcard per CDX query (multi-wildcard silently returns empty).
arquivo.pt: always query unbounded, filter client-side (date-bounded
queries are a zero-trap).
