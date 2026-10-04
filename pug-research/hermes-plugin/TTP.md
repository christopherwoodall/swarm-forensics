# Technical Playbook: Swarm Forensics TTP Replication

## 1. Overview & Role

This document defines technical tactics, techniques, and procedures (TTPs) for swarm threat intelligence.
Forensics analysts use this playbook to investigate agent infrastructure and behavioral patterns.
Techniques focus on relay infrastructure, nonce grammars, archive patterns, and shared target basins.

## 2. Methodology & TTP Catalog

### TTP-1: Stratified URL Mining
Stream large dataset files line by line using standard streaming readers.
Never load entire datasets into memory.
Extract URLs using regular expressions.
Normalize each URL to its registrable domain.
Count occurrences per corpus layer with recorded sampling strides.
Intersect domain sets across populations to identify shared infrastructure.

### TTP-2: Relay-Chain Grammar
Decompose nested proxy and relay chains for each URL.
Observe nesting order: jq proxies outermost, CORS relays middle, target innermost.
Extract the host of each nesting layer and query parameter names.
Identify known relays including `r.jina.ai`, `allorigins`, `corsproxy.io`, `da.gd`, and `jqp.vercel.app`.
Capture markdown proxies such as `md.succ.ai`, `pure.md`, and `markdown.new`.

### TTP-3: Nonce Grammar
Match query parameter structures rather than specific values.
Detect parameter families such as `zz=oai<digits>`, `zzbulk`, and `prepnonce`.
Detect bare epoch integers and `oai*` tags.
Count occurrences per corpus layer.
Note whether a nonce grammar appears exclusively in one population.

### TTP-4: Archive-First Behavior
Search for capture creation endpoints including `web.archive.org/save/` and `arquivo.pt`.
Identify retry and delay loops surrounding archive requests.
Distinguish creating archive captures from reading existing captures.
Capture creation serves as a stronger behavioral signal.

### TTP-5: Basin Grading
Grade shared domains and URLs across five distinct categories:
1. **Exact URL**: Identical scheme, host, path, and normalized query parameters.
2. **Domain and Path**: Matching host and stable path with differing queries.
3. **Target Host**: Matching destination service.
4. **Service Basin**: Related hosts within public organizational domains.
5. **Temporal**: Observed hits bounded within the incident time window.

### TTP-6: Trace Pulling & Verification
Retrieve corroborating traces time-boxed to the target activity window.
Query public Wayback CDX indexes and Arquivo endpoints.
Record verdicts for every queried URL.
Log zero-hit queries as verified clean negatives.

### TTP-7: Tokenization Hygiene
Use n-grams and character chunks rather than word splits.
Normalize camel case, digit-letter boundaries, and percent encoding before comparison.
Quarantine contaminated partitions with documented reasons.
Never drop data partitions silently.

### TTP-8: Functional Matching
Compare equivalent communication channels: chat to chat, code to code, traces to traces.
Never compare conversational text against raw URL dumps.
Document the match rationale for every compared pair.

## 3. Report-Driven Analysis

When reviewing external incident reports:

1. **Extract Claimed Indicators**:
   Extract all URLs, domains, URL patterns, nonce shapes, and relay hosts.
   Record the exact quotation for each indicator.

2. **Verify Indicators Locally**:
   Run TTP-1 through TTP-5 against the local corpus.
   Assign one explicit verdict to each indicator:
   - `CONFIRMED`: Present with matching structure, cite counts, and timestamps.
   - `COMMODITY`: Present but generic infrastructure common to multiple services.
   - `QUOTATION`: Present only inside agents discussing public incident reports.
   - `ABSENT`: Clean negative result within the searched scope.

3. **Surface Novel Findings**:
   Identify patterns that the external report omitted.
   Look for unlisted relay hosts and novel parameter nonce families.

4. **Grade Analytical Claims**:
   Apply the claim ladder before publishing conclusions.

## 4. Epistemic Rules

- Sharing does not equal linkage.
- Linkage does not equal correlation.
- Shared destinations on public data portals are gravity wells, not linkage.
- Commodity relays indicate shared tooling, not shared operators.
- Mark every claim as verified or inferred.
- Record clean negatives with the same care as positive hits.
- Never pursue human operator attribution.
