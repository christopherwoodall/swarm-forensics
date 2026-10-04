# LEARNING.md — dynamic intelligence for the Hermes plugin

## Amendment (2026-10-04): the learning loop is human-gated

The autonomous promotion policy in §1 is SUPERSEDED.

- The IOC updater only PROPOSES. Proposals land quarantined in
  the human review queue. Nothing promotes without a human
  decision: GUI ACCEPT/REJECT/NARROW click or an explicit
  `review` command with a rationale.
- Auto-accept paths are REMOVED. `ioc.auto_propose` defaults to
  false. When enabled, it proposes into quarantine, never into
  the active list.
- Every hunt, proposal, and promotion needs the human. The
  hunting-dog model governs: only hunt with a human.

---

This document designs the learning loop: the IOC list updater, the URL
predictor, and the research job. Everything here MUST be implementable
with standard-library Python plus curl-style HTTP. No new infrastructure.

Status terms: a term is **active** (used for alerting), **candidate**
(under scoring), **quarantined** (blocked after a false-positive flag),
or **inactive** (demoted, kept for provenance, never used for alerting).

All tunables live in one config file (`hermes.ini`, read with
`configparser`). Defaults are stated below; operators MAY change them.

---

## 1. IOC list updater

### 1.1 Lifecycle

```
new hit ──> candidate extraction ──> scoring ──> promotion ──> active list
                                                        │
scan runs, research job          frequency / novelty /  ├─> demotion (no yield)
                                 venue diversity        └─> quarantine (false positive)
```

**New hit.** A hit is a scanner result (urlquery match, CDX sweep hit,
arquivo.pt sweep hit) or a research-job finding. Every hit MUST record:
the matched term, the venue, the UTC timestamp, the rule that fired,
and a context snippet (the URL or text line). Hits without provenance
MUST NOT enter the pipeline.

**Candidate extraction.** From each hit, extract candidate terms as
n-gram chunks, not single words. Use the same subword tokenizer policy
as the stylometry lane (split on case transitions, letter/digit
boundaries, separators; decode percent-encoding first). A candidate
MUST record its source hit. Candidates that exactly duplicate an
existing active or inactive term are dropped at this stage.

**Scoring.** Each candidate gets three scores, recomputed weekly:

- **Frequency:** hits per week across all scan runs, normalized by
  scan volume. A term seen once is noise; a term seen weekly is signal.
- **Novelty:** zero-baseline check. Terms with wide public-code or
  public-web presence score low (they are generic). Terms with no
  public presence outside agent-shaped contexts score high. This is
  the same check the hunt's recon-code review performed by hand; the
  updater performs it with scripted web searches and records the
  evidence.
- **Venue diversity:** number of independent venues where the term
  produced hits (urlquery, Wayback CDX, arquivo.pt CDX, vendor
  reports). Two or more venues scores high. One venue is weak.

**Promotion.** A candidate becomes active when its combined score
passes the threshold AND it satisfies the two-venue rule (hits in at
least two independent venues), OR a human approves it. Auto-accept
is allowed ONLY for:

- nonce-grammar shapes that validate against a known regex template
  (e.g. `zz=oai<digits>`, `fresh=x<epoch>.<rand>`), and
- exact duplicates of already-active terms in a new venue.

Everything else — new relay hosts, new target families, novel
markers — goes to the human review queue. The review queue is a
plain file the operator reads on the standing weekly watch.

**Demotion and pruning.** An active term with zero hits for
`PRUNE_WEEKS` (default 12) becomes inactive. An active term flagged
as a false positive by a human becomes quarantined immediately.
Quarantined terms MUST NOT be re-promoted for `QUARANTINE_WEEKS`
(default 26); the flag and the flagger are recorded. Inactive and
quarantined terms are never deleted; their history is the audit
trail. No term is ever removed from `wordlist.json`.

**Promotion rate limit.** At most `MAX_PROMOTIONS_PER_CYCLE`
(default 20) candidates may be promoted per weekly cycle. This
bounds the blast radius of a poisoning event.

### 1.2 Poisoning safeguards

- **Provenance is mandatory.** Auto-promotion accepts terms only
  from scanner hits with full provenance. Terms arriving from
  unverified external input (a pasted list, an untrusted feed)
  enter as candidates and require human approval.
- **Two-venue rule.** A single venue can be gamed (anyone can
  submit a urlquery report containing a chosen string). Two
  independent venues cannot be gamed as cheaply.
- **Rate limits.** See promotion rate limit above.
- **Quarantine with memory.** A false-positive flag blocks
  re-promotion for the cooldown period, even if the term scores
  well again.
- **Human review vs auto-accept.** Auto-accept covers mechanical
  patterns only (nonce regexes, known-term new-venue duplicates).
  Novel markers, new relays, new targets: human review, no
  exceptions. The review queue MUST be empty before a release
  build of the list.

---

## 2. URL predictor

Reactive scanning finds what agents already did. The predictor
generates candidate URLs an agent *would* use next, then checks
them against public indexes. This is predictive collection.

### 2.1 What it generates

From the request-grammar patterns (relay chains, nonce templates,
param grammars, the basin-of-attraction concept):

- **Relay-wrapped targets.** For each known basin target not yet
  observed through a given relay, generate the relay-wrapped form.
  Example: a new `.gov` data API seen bare becomes a candidate
  through `r.jina.ai/http://`, through an AllOrigins raw fetch,
  and through a jq-proxy with a plausible filter.
- **Nonce-templated URLs.** Generate URLs carrying fresh nonces
  that match observed templates (`?zz=oai<digits>`,
  `?fresh=x<epoch>.<rand>`, `zzbulk<digits>`). These are checked
  against indexes, never fetched speculatively (see 2.3).
- **Param-grammar projections.** For data APIs in a known family,
  project observed param shapes onto new endpoints of the same
  API (e.g. `survey_Year_Key` / `Measure_Id` / `State_Id`
  patterns onto a new ed.gov endpoint).
- **Basin enumeration.** New targets inside known basins: APIs,
  JSON/data files, archive-save routes, relay wrappers. Sources
  for new basin members: the research job, skill-egress strings
  (new candidate relay hosts), and sibling paths of known hits
  (same host, new path).

### 2.2 Ranking by expected yield

Each candidate gets a score from four factors:

1. **Basin membership:** is the URL an API endpoint, a JSON/data
   file, an archive-save route, or a relay wrapper? Basin shapes
   score high; ordinary pages score low.
2. **Template match:** does it instantiate an observed relay-chain
   or nonce template exactly? Exact template matches score high.
3. **Sibling evidence:** do sibling URLs (same host or path
   family) already have hits? Prior hits nearby raise the score.
4. **Freshness:** newly appeared targets score higher than
   long-known ones.

The ranked list feeds the scanner's priority queue. The scanner
works the list top-down within its per-cycle budget.

### 2.3 Hard rule: check, do not fetch

The predictor generates candidates for **index lookup**, not for
fetching. For each candidate, the scanner queries urlquery,
Wayback CDX, and arquivo.pt CDX. It MUST NOT fetch the URL
directly, and it MUST NOT create archive captures (`/save/`) for
predicted URLs. Creating captures would pollute the very
archives the hunt monitors, and the captures would re-enter the
learning loop as false hits (see failure mode 3 below).

---

## 3. Research job

A scheduled job that watches what other researchers publish and
feeds candidate IOCs to the updater.

### 3.1 Schedule

Runs every `RESEARCH_INTERVAL_DAYS` (default 7). The interval is
configurable in `hermes.ini`. Each run records its timestamp and
a cursor (last-seen state per source) so runs are incremental.

### 3.2 Sources

- **Transluce reports and blog** (transluce.org): the primary
  external source. Poll the blog index and report pages.
- **Vendor and researcher blogs:** a configurable list of feeds
  (default: empty; the operator adds feeds as they prove useful).
- **New datasets:** HuggingFace dataset search for agent-trace
  and agent-behavior datasets; new tables are candidate sources
  for the labeled side, not just IOCs.
- **Public code:** web search for toolkit-shaped strings (the
  nonce grammar, relay hostnames); new public occurrences are
  novelty-check evidence, not IOCs.

### 3.3 Polling method

curl with conditional GET (`If-Modified-Since` / ETag) against
RSS/Atom feeds where available; plain HTML fetch plus
`html.parser` extraction otherwise. Polite by construction:
one pass per interval, no crawling, respect rate limits, stop
on HTTP 429 and back off. All fetching is read-only.

### 3.4 Extraction and dedup

From each new publication, extract n-gram chunks with the same
tokenizer policy as 1.1. Each candidate records provenance:
source URL and publication date. Dedup against the existing
list (active, candidate, quarantined, inactive) in two passes:

- **Exact pass:** normalized form (lowercase, strip scheme,
  decode percent-encoding) compared against all existing terms.
  Exact duplicates are dropped.
- **Near pass:** `difflib` similarity against active terms.
  Near-duplicates are NOT auto-added; they go to the human
  review queue with the similar existing term noted.

Surviving candidates enter the updater's candidate queue with
their provenance. The research job never promotes directly.

---

## 4. Failure modes of "constantly learning"

These MUST be monitored, not just documented.

1. **List poisoning.** An attacker publishes content containing
   chosen strings (a urlquery report is cheap to submit), or the
   scanner ingests attacker-controlled pages. The strings enter
   as candidates and may promote. Mitigations: two-venue rule,
   mandatory provenance, promotion rate limit, human review for
   novel markers.

2. **Drift.** The list slowly accumulates generic terms as agent
   vocabulary shifts; precision decays while recall looks
   healthy. Mitigations: novelty scoring, per-term false-positive
   rate tracking, automatic demotion after `PRUNE_WEEKS` of no
   yield.

3. **Feedback loops (self-teaching).** The hunter ingests its own
   artifacts: our published reports, our probe queries appearing
   in urlquery, our test captures in archives. The list converges
   on describing the hunter, not the hunted. This is the most
   dangerous failure mode. Mitigations:
   - every plugin-generated emission (query, capture, report)
     is logged with a marker;
   - an exclusion list covers our own infrastructure, our own
     published URLs, and our own probe strings — the updater
     MUST NOT ingest them;
   - the research job dedups against our own publications;
   - the predictor MUST NOT create archive captures (2.3).

4. **Confirmation bias in the predictor.** The predictor
   generates candidates from known patterns; the scanner finds
   them because they are common shapes; the list reinforces.
   Discovery of novel tradecraft flatlines while every metric
   looks green. Mitigations: reserve `EXPLORATION_FRACTION`
   (default 0.20) of the scan budget for out-of-pattern
   sampling; track the **novelty rate** (fraction of hits from
   outside the current list) as a health metric; alert when it
   stays at zero for two consecutive cycles.

5. **Runaway automation.** Auto-promotion plus auto-scanning with
   no human in the loop. Mitigations: promotion rate limits,
   mandatory human review queue, and a kill switch
   (`LEARNING_ENABLED=false` freezes the list; the scanner
   continues on the frozen list).

### Health metrics (logged every cycle)

- Novelty rate (see 4.4).
- Promotions, demotions, quarantines per cycle.
- False-positive flags per term (from human review).
- Review queue depth and age of oldest item.

If the novelty rate is zero for two cycles, or the review queue
age exceeds `REVIEW_SLA_DAYS` (default 14), the plugin MUST
alert the operator. A learning loop nobody watches is a loop
that has already failed.
