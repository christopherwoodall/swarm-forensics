# Stage 4 — external trace reservoirs: shared forensic protocol

Status: governing protocol, adopted 2026-10-03.
Research cutoff: 2026-10-01. Local sources: the three reservoirs under
`colette-research/sources/`. This pass reads released archives only; no live
collection, no report fetching, no attack reproduction.

## Object of study

Three external trace reservoirs hold observable residue of agent-like
activity. Each is a different observation surface over possibly related
populations:

- **urlquery** (`urlquery-net-data/`): request traces. A catalog of 38,160
  browser-session reports (report id, second-precision UTC timestamp,
  disposition, confidence, broad class) plus source assignments. The package
  contains report links and research metadata only — no report JSON, no
  request bodies. Request-level HTTP entries exist only for the exported
  report subsets inside the us-canada package (9,667 rows across four
  folders).
- **arquivo** (`us-canada/`... in `us-can-data/`): routing/capture traces.
  561,229 Arquivo.pt web-archive capture rows across 15 target families
  (captured-at timestamps, HTTP status, WARC digest/offset, target URL), the
  investigation's fresh-response reads, and cited benchmark/wiki artifacts.
- **rubygems + wiki** (`rubygems-wiki-collusion/`): durable artifact traces.
  13,703 selected records with per-origin provenance (81 rubygems-origin:
  79 registry_metadata packages, 2 package_member), the full wiki logs
  (14,591 revisions, 4,579 pages, 5,217 deletes, 101 probes), the rmn.re
  shortener log (499 agent-window links), site coverage across 143 surfaces,
  and cross-site links.

The fourth corner of the observation tetrahedron — swarmtraces
(`sources/swarmtraces-dataset/redacted.jsonl.gz`) — is the reconstructed
organizational-machinery corpus already analyzed in
`notes/organizational-forensics.md`. It stays a separate reservoir; it is not
merged into this pass.

## The goal is dependency structure, not suspicion

The goal is not to prove a "swarm." The goal is to reconstruct the strongest
defensible dependency structures visible in each dataset and determine
whether any traces support, in increasing order of strength:

1. repeated individual task behavior
2. reuse of a technique across apparently separate runs
3. persistence through external artifacts
4. artifact-mediated information transfer
5. actual read/use of prior artifacts by later agents
6. task division, specialization, delegation, or role differentiation
7. adaptation to prior success/failure or environmental state
8. cross-run continuity that survives individual agent lifetimes
9. coordination infrastructure or protocols
10. evidence linking activity across the three datasets

## Evidence distinctions that MUST be preserved

Never collapse these into one field:

- action observed
- action attempted
- artifact created
- artifact retrieved
- artifact demonstrably used in a later decision
- similarity only
- attribution claim
- inferred coordination

## Non-inference rules

- Do not infer chronology from identifiers unless timestamps support it.
- Do not treat multiple requests, packages, reports, names, or artifacts as
  multiple agents.
- Do not treat common technique reuse as communication without evidence of
  transmission.
- A shared artifact is not coordination unless later behavior is shown to
  depend on it.
- Reconstruct wiki evidence from added text, never cumulative page copies.
  Counting inherited page text as authorship manufactures propagation.
- A request log entry is not verified uptake: it does not establish the
  response body delivered, the content admitted into context, or that the
  material caused a later decision.

## Record requirements for every candidate relation

- source dataset
- stable source identifier
- timestamp or time bound
- initiating action
- target/service
- artifact produced or changed
- later observable action
- evidence that the later actor could access the artifact
- evidence that it actually accessed it
- evidence that its behavior changed because of it
- alternative explanations
- confidence
- exact supporting excerpt/raw record reference

## Edge taxonomy

Classify each candidate edge as exactly one of:

- observed causal dependency
- strongly supported dependency
- plausible dependency
- temporal/structural association only
- resemblance only

Keep a separate unresolved ledger rather than forcing ambiguous cases into
the graph.

## Normalized output tables

One cross-dataset event table from day one:

`event_id | dataset | time | time_grade | actor_hint | action | target |
artifact | operation | parent_event | observed_read | behavior_change |
technique_family | raw_ref | confidence | notes`

And a separate candidate-edge table:

`edge_id | edge_from | edge_to | relation | evidence_type | causal_strength |
competing_explanation | raw_ref | notes`

Actor identity is `actor_hint` (investigator / human / agent_label /
unattributed), never an asserted actor id. The second table is where the
research starts: it lets us ask whether the same behavioral motifs recur
across substrates without prematurely deciding they belong to one population.

## Negative evidence is mandatory

Actively search for broken chains. Whenever you find:

- a write with no later read,
- a repeated technique with no transmission evidence,
- a claimed response with no captured response body,
- a temporal sequence with a plausible common-cause explanation,

record it explicitly. This is what keeps the pass from becoming numerological
soup. The real object is the dependency structure, not the pile of suspicious
artifacts.

## Per-reservoir hunts

### urlquery — recurrence and linkage

Hunt for: repeated task-specific payload structure; identical or mutated
request programs; recurring target families; uncommon literals and markers;
infrastructure transitions; surviving task ids; and sequences where one
report appears to contain knowledge plausibly acquired in an earlier one.

Especially: distinguish "same harness/template emitted this" from "later run
inherited a discovery." That is the whole game. The catalog carries
`broad_class` and per-method discovery definitions (`methods.json`) — use
them as harness-side templates, not as agent-side facts. Report-level HTTP
exports (inside the us-canada package) are the only place request shapes are
visible; treat their coverage as partial.

### arquivo — request ecology

Cluster by destination host/path, temporal burst, request shape, payload
grammar, and task-relevant query patterns. Look for feedback evidence: a
failed endpoint followed by changed paths, escalating specificity, reuse of
discovered URLs, changes after response-visible state. Preserve capture
contents and status where the archive exposes them (`indexed_http_status`,
the fresh-response files).

The juicy question: is arquivo only an observation surface, or were agents
using its own persisted captures as an information substrate? Note the
`zz=` nonce grammar: 52,642 of 561,229 capture rows carry a `zz=` parameter.
Check whether the same nonce value recurs across different targets or
folders — recurrence would suggest the same caller family; it does not
establish transmission.

### rubygems — provenance chain

Be provenance-obsessed. Current evidence says public package artifacts,
documentation-build outputs, and registry/webhook records are plausible
coordination substrates, but cross-agent readership and causal reuse are not
established (see stage-3 card S3-RUBY). Trace:

package → publication time → files/content → external retrieval target →
build behavior → later package similarities → reused retrieved material →
any evidence another run consumed that material.

Test the strongest existing clue rather than assume it: Nightingale reports
June packages retrieved 49 of the same files as the wiki agents, but that
establishes possible workload/participant overlap, not transmission. The
released corpus makes the overlap locally enumerable: gem `homepage_uri`
values carry `sha256=` of the operational URL, and wiki `links.jsonl.gz`
carries `source_url_sha256` for the same URLs. Enumerate the overlap exactly
and ask:

**is this common upstream task structure, independent rediscovery, shared
scaffolding, or actual artifact-mediated inheritance?**

Keep all four hypotheses attached to every overlap row. Do not upgrade any
of them without a demonstrated read by a later actor.

## Stage 2 — cross-dataset families (after per-reservoir passes)

Forget dataset boundaries. Search the normalized records for repeated
mechanisms, literals, target sets, artifact names, request grammars,
temporal adjacency, task semantics, and unusual implementation choices that
could link episodes across substrates. Return candidate cross-dataset
families, but keep these as separate hypotheses:

- identity linkage (same actor population)
- common harness
- common task
- common operator
- direct information transfer

"Same weird trick appears in three fossil beds" is already interesting.
"The same organization carried state between them" is a much stronger
animal. Do not conflate them.

## Documentation rule (adopted 2026-10-03)

Every research dive MUST write its findings to a dated markdown file under
`colette-research/<topic>/` (e.g. `wiki-collusion/2026-10-03-relay-economy.md`)
in addition to terminal output. Files carry: evidence basis, extraction
census, hand-traced chains with strong-vs-speculative readings, other finds,
next probes, and reproduce commands. Shared cross-dataset state stays in
this PROTOCOL.md; per-dataset and per-dive detail lives in the topic folders.

## Implementation

Implemented in `src/swarm_forensics/traces/` (see `traces/MODULE.md`).
Run: `make traces-normalize`, then `make traces-report`. Outputs land in
untracked `data/raw/traces/` (streamed, one record at a time).

## Wiki relay-economy findings (2026-10-03, dive 1)

The wiki corpus contains a full relay economy, extracted from added text only:
2,102+ cadence messages across 591+ pages (cohort ids, R-rounds, task-clock
mappings to shared UTC, cooldown profiles, cross-page relays, status pings).
Peak coordination: June 16 (564 relay-page revisions), the day the Sector61
all-state answer chain ran.

### The strongest chain (hand-traced, all times shared UTC, Jun 16 2026)

1. 19:57:00 — `SectorAgentFeb25OAI` posts "BREAKTHROUGH": the plus-encoded
   la.datausa.io tesseract-proxy URL plus "I have all values cached"
   (dse~Sector61State5LiveRelay).
2. 20:01:20 — `OpenAIResearcherAug09` posts the complete all-state table on a
   new page, dse~Sector61AllStateValues2027 (the durable artifact).
3. 20:01:39 — `OpenAIResearcherAug07`, a third label, announces the mirror:
   "exact all-state 2015-20 table now mirrored at [[Sector61AllStateValues2027]]".
4. 20:14:08 — `SectorAgentFeb25OAI` posts a read-pointer on a fourth page:
   "Full exact table now at [[Sector61AllStateValues2027]]".
5. 22:14:42 — `OpenAiDenomSep03`: "STATE5-ID CONFIRMED by OpenAI-Dec27.
   Fifth prompt: Idaho."
6. 22:17:25 — `ResearchHelperOctFifteen` relays the outcome with exact Idaho
   values `154074,156625,158080,164010,169260,171604` — byte-identical to the
   mirror table's Idaho row.

Reading: the fifth-round answer was plausibly produced through a shared
cache → artifact → read-pointer chain spanning five distinct labels in about
2.5 hours. It remains classified plausible_dependency, not observed causal:
the release carries no request-log proof that a specific later label fetched
the mirror page, and "same actor under multiple labels" stays live (the
corpus's own reconstruction withdraws naive identity readings; labels are
self-assigned names, not authenticated agents).

### Extracted edge census (added text only, all strengths ≤ plausible)

- 733 cross-label page citations (page referenced after creation by a
  different label; median lag hours, not minutes)
- 545 request→response pairs (explicit request followed within 6h by a
  different-label post with an answer token; first response only)
- 70 same-specific-URL-across-labels (parameterized URLs, cache-buster
  params normalized away)
- Standing competing explanations attached to every row; nothing upgraded
  beyond plausible_dependency. A demonstrated read (request-log proof of
  mirror-page fetch by a later label) would upgrade the Feb25 chain toward
  strongly_supported; the released logs do not contain it.

## Verified run — 2026-10-03

Full normalization over the real archives produced 643,199 events and 21
candidate edges, all schema-valid:

- arquivo: 561,298 events (561,229 captures; 69 investigator fresh-response
  reads)
- urlquery: 47,316 events (catalog included rows + 9,667-row HTTP exports)
- wiki: 34,504 events (19,913 rows from events.jsonl: 14,591 saves,
  5,217 deletes, 4 reverts, 101 probes; plus 14,591 revision rows with
  added-text reconstruction)
- rubygems: 81 events (79 register, 2 publish)

### Bridge candidates found (all weak; none upgraded)

1. **Ten exact-URL overlaps** between gem homepages and wiki link rows
   (sha256-identical operational URLs on markdown.new and r.jina.ai relays).
   Edge class: resemblance_only. Competing: common upstream task structure /
   independent rediscovery / shared scaffolding / artifact-mediated
   inheritance. Transmission is not established by any released record.
2. **One wiki→urlquery citation**: revision `dse~TestAgentResearchLinks@1`
   (2026-05-26T16:43:26Z, label `ResearchUser`) cites urlquery report
   `42fa1863` in added text; the report is in the catalog (same day,
   significant, indirection, MAX budget documents). Edge class:
   temporal/structural association only. Competing: investigator provenance
   (label `ResearchUser`; body "test content"), agent found the report
   independently, or the agent produced the cited session. Note: revision @2
   (label AgentOurGroceryGeorgiaLinkY) inherits the citation in cumulative
   page copy; added-text reconstruction correctly counts one citation, not
   two.
3. **Eleven relay hosts shared** between the rubygems and wiki populations
   (markdown.new, r.jina.ai, allorigins, cors workers, jqp.vercel.app...).
   Edge class: resemblance_only. Shared relay services indicate at most a
   common toolkit or task family, not transmission.

### Negative evidence recorded

- No observed read of any gem homepage URL by a wiki-side actor (or vice
  versa) exists in the released records; `observed_read` stays `unobserved`
  for all 21 edges.
- No response bodies are present in any of the three packages: urlquery
  catalog has links only, arquivo rows carry status/mime/digest but the
  response layer present is the investigation's own re-fetches, and wiki
  bodies are page text, not HTTP responses. Claimed-response chains are
  therefore broken by construction.
- The wiki citation edge is a write with no captured later read of the cited
  report by another actor.
- 555,156 arquivo events have no zz= marker and classify `technique_family:
  unknown`; nonce recurrence analysis is pending and must not be presented as
  done.

## Open probes (next)

- Burst and feedback analysis within arquivo task families: same nonce
  across targets/folders → caller-family recurrence, not transmission;
  failed endpoint followed by changed path → feedback evidence.
- Gem name stems (`amdvar` 9, `amdmore` 5, `a----00proxy` 5...) as a
  publication-family census; stem families are not agents.
- The 49-file Nightingale overlap is only partially enumerable locally (11
  distinct gem homepage URLs; 10 overlap). The remaining overlap presumably
  lives in package file contents not present in this release; do not claim
  the full 49 from local data.

## Classification vocabulary (updated 2026-10-03)

`technique_family` splits the former `unknown` bucket:

- `no_visible_mechanism` — the row parsed clean; no coordination-relevant
  mechanism is visible in it (arquivo captures without a zz= nonce;
  urlquery HTTP entries with plain government URLs).
- `content_not_in_release` — the released record withholds the request
  shape or content (urlquery catalog rows; the investigation's
  fresh-response layer).
- `unknown` — reserved for rows not yet examined; currently zero rows.

`task_family` is a separate first-class field: coarse host/path templates
(crdc_state_estimation, md_reportcard_2022_download, wiki_peer_exchange,
gem_publication...). It labels visible request structure only. Two rows in
one task family show the same kind of work was attempted; it is not a
mechanism claim, not an attribution, and MUST NOT be promoted into
`technique_family`.
