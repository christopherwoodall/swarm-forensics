# The SEC county artifact: one file, three fossil beds (dive 4)

Research date: 2026-10-03. Evidence basis: added text from `full-wiki-logs.zip`;
urlquery-http exports inside the us-canada package; registry_metadata records
in `records.jsonl.gz`. All queries local. Parent: the relay economy
([2026-10-03-relay-economy.md](2026-10-03-relay-economy.md)).

## The artifact

`https://www.sec.gov/files/county.json` (mirror:
`investor.gov/sites/default/files/county.json`) — a public SEC county-code
file. Three beds hold it:

| Bed | First touch (UTC) | Last touch | Events |
| --- | --- | --- | ---: |
| urlquery-http | 2026-06-18 04:23 | 2026-06-18 23:27 | 568 fetches |
| wiki added text | 2026-06-18 14:54 | 2026-06-19 21:38 | 960 revisions |
| rubygems homepages | (no dates in release; Nightingale: June) | — | 79 packages |

All 79 gem packages wrap this one file — no other artifact appears in any
homepage. Wrapper families used by the gems: direct+z= nonce (22), r.jina.ai
(19), direct (12), google-translate proxy (9), markdown.new (8), allorigins
(5), w3c-validator (4).

## What resolved and what didn't

The 10 gem↔wiki sha256-overlap URLs (dive 1) are withheld in the release, but
3 of 10 resolved by hashing wiki-body URL variants:

- `m--00cfproxy47` → `https://r.jina.ai/https://www.sec.gov/files/county.json`
  (wiki: dse~AI@2, DataResearchHelperX, 2026-06-18T21:02:27Z)
- `g----00prx15127` → `https://r.jina.ai/http://www.sec.gov/files/county.json`
  (wiki: dse~Agent0MdDirectPlainJuly777@1, OpenAI, 21:02:32Z)
- `z----00prx58090` → `https://r.jina.ai/http://r.jina.ai/https://www.sec.gov/files/county.json`
  (wiki: dse~AgentCountyTransformNextJulyZ@1, AgentNewNameXYZ123, 17:46:19Z —
  a jina-of-jina double relay)

The remaining 7 overlap URLs did not resolve to any literal in the release
(they include markdown.new variants and at least one allorigins URL whose
exact normalized form is not recoverable). The resolution confirms the
earlier finding at URL level: **the gems point at the exact relay URLs the
wiki agents used** — not merely the same file.

## The nonce grammar across beds

Cache-buster nonces (`?z=` / `?x=` / `?_=`) on county.json:

- **urlquery**: 12 distinct values, mostly toy-like (`abcdef12`, `abc999`,
  `fresh987`, `100001`, `33`). First nonce 04:23, cluster 17:37–20:10.
- **wiki**: 345 nonce-bearing posts; values range from `1`, `2`, `123` to
  `1781809999` and names like `pretty`, `newcache17181`, `mdsecfresh*`.
- **gems**: 22 distinct z= values, all 8-digit numbers (`25122817`...
  `98889760`). Zero of them are epoch-like.

**Cross-bed nonce value overlap: effectively zero.** urlquery∩wiki = {33}
(the trivial value 33, likely coincidence); urlquery∩gems = ∅; wiki∩gems = ∅.
Same grammar, disjoint values. Shared scaffolding, not shared strings.

## The 156991212 echo chain (wiki-internal)

Nine posts on dse~StartSeite between 19:42:44 and 20:13:40 (Jun 18) carry the
identical section header `===DirectInvestorCountyXYZ992===` and the same
investor.gov mirror URL with nonce `z=156991212` — 8 distinct labels, 7
distinct /16s (20.80, 20.3, 20.225 ×3, 20.165, 172.173, 74.249, 104.45),
31 minutes. One constructed URL echoed by eight labels across
infrastructure. Same competing explanations as the Henderson chain (dive 3):
read-and-copy vs shared harness template vs task-provided reference. The
section name `DirectInvestorCountyXYZ992` is agent-invented (not a standard
name), which leans toward read-and-copy or shared-harness, not
task-provided.

## The three-bed chronology (Jun 18, UTC)

- 04:23 — urlquery sessions start fetching county.json (corsfix
  `?x=abcdef12`, allorigins raw/get, noroffcors; failures 400/502 then 200s)
- 12:57 — direct sec.gov fetches begin succeeding
- 14:54 — first wiki page (dse~AgentSECBridgeJun18X) touches the file
- 17:46–21:02 — wiki wrapper bloom: jqp.vercel (1022 mentions), md.succ.ai
  (618), allorigins (335), r.jina.ai (202), markdown.new (146), pure.md
  (77), translate.goog (26)
- 23:27 — last urlquery county.json fetch
- Jun 19–later — gems publish (release has no dates; Nightingale's window)

## Readings

**Strong (directly in evidence):** one public file fetched by all three
populations within a single day; identical relay services (allorigins,
r.jina.ai, markdown.new, translate proxies) in all three; three gem
homepage URLs sha256-identical to wiki-posted relay URLs; the wiki
population's wrapper bloom follows the urlquery failures (400/502 → 200)
by hours, consistent with relay discovery diffusing.

**Speculative (not established):** that any gem package was created by an
actor that read the wiki pages (the sha256 identity is consistent with
shared task structure OR shared scaffolding OR read-and-copy; the release
cannot separate them); that the June packages are temporally downstream of
the Jun 18 wiki bloom (no gem dates in release).

Classification: the gem↔wiki URL overlaps remain
`resemblance_only`→`plausible_dependency` (technique identity is exact;
transmission unproven). The cross-bed chain — urlquery failures → wiki
wrapper bloom → gem republishing — is `temporal_structural_association`
with a coherent mechanism story but no captured handoff.

## What would upgrade

- A gem package whose homepage nonce value matches a wiki-posted nonce value
  (none found: disjoint sets).
- RubyGems publication timestamps (not in release; the live registry is out
  of scope for this pass).
- A wiki post acknowledging a rubygems package (none found in this dive;
  the Nightingale overlap claim remains the only reader link, and it is a
  report, not a released record).

## Reproduce

```sh
# all queries in this dive stream the three source packages:
#  full-wiki-logs.zip revisions.jsonl (added text, hunks)
#  us-canada...v3/14-sec/urlquery-http.csv (+ other folders)
#  records.jsonl.gz registry_metadata origins
# sha256-variant resolution: hash {url, url.rstrip('/'), +'/'} against the
# 10 overlap sha256 values from links.jsonl.gz
```
