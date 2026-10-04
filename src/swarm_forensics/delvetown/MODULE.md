# Module: Delvetown Public-Record Pilot

## 1. Intent & Scope

Collect the user-approved, private 72-hour public-record cohort.
Keep acquisition separate from stage-4 forensic timelines and publication.

## 2. Active Invariants

- Requests MUST use public GET routes without credentials.
- Requests MUST reject redirects and nonpublic network destinations.
- The collector MUST freeze the supplied cohort. It MUST NOT expand through social references.
- PDS collection MUST request only `town.delve.feed.post`.
- Collection MUST stop at 10,000 unique posts, 100 MB, 500 requests, or 1,800 seconds.
- Requests MUST use one worker and at least one second between request starts.
- Persisted posts MUST fall within the fixed 72-hour collection window.
- Raw records and derived outputs MUST remain under ignored `data/raw/delvetown/`.
- Private directories MUST use mode 0700. Private files MUST use mode 0600.
- Existing runs MUST NOT be overwritten.
- Tests MUST use synthetic records and injected network boundaries.
- Record references MUST NOT establish causal use or verified runtime identity.
- Publication, media downloads, unrelated collections, training, and participant experiments MUST remain excluded.

## 3. Interfaces & Dependencies

Use the Python standard library and the root Makefile.

- `make delvetown-test`: run the synthetic collector suite.
- `make delvetown-pilot DELVE_COHORT=<json> DELVE_DIR=<new-directory>`: collect one bounded snapshot.
- `make delvetown-audit DELVE_DIR=<directory>`: verify the retained snapshot without network requests.
- `make delvetown-inspect DELVE_DIR=<directory>`: inspect bounded private thread excerpts without network requests.
- `make delvetown-record DELVE_URI=<uri> DELVE_DIR=<directory>`: read one complete retained post without network requests.
- The cohort JSON MUST contain an `actors` list with unique DID and handle fields.
- Optional cohort labels remain self-reported source metadata.
- Outputs include a raw-record SQLite archive, normalized JSONL, structural edges, and a private coverage report.
- `records.normalize`: preserve text, timestamps, rich-text references, quote references, and source identifiers.
- `transport.Reader`: enforce fixed GET routes, public-address pinning, verified TLS, rate spacing, and network budgets.
- `collector.collect`: filter the fixed time window while scanning collection pages through exhaustion or a safety limit.
- `report.audit`: compare every exported post and edge against the retained record JSON and request metadata.
- `report.inspect`: return at most 20 discussion samples with bounded excerpts.
- `report.record_view`: return one exact post with its source handle and request provenance. Preserve complete text.
- The CLI requires output paths under ignored `data/raw/delvetown/`.
- The archive retains selected record JSON, not complete transport response bodies.
- Request metadata preserves response hashes, byte counts, statuses, headers, and receipt timestamps.
- Repository key order MUST NOT establish authored chronology. Filter source timestamps locally.
- Commands reuse the existing frozen environment. Tests and lint cover this package through the root targets.

## 4. Current State & Known Gaps

- Verified: Fifteen synthetic tests cover normalization, scope gates, budgets, retry delays, partial coverage, provenance, inspection, and complete-text lookup.
- Verified: The current tree passes 190 tests and Ruff using the existing frozen environment.
- Verified: The private pilot scanned all 45 approved accounts and retained 1,529 posts from 36 posting accounts.
- Verified: The pilot completed within 182 GET attempts and 2,495,340 downloaded response bytes.
- Verified: Offline audit checks raw projections, time bounds, structural references, request counts, and private permissions.
- State: Private coverage and initial readings live under ignored `data/raw/delvetown/pilot/`.
- State: Source files remain mode 0600. The pilot directory remains mode 0700.
- State: Private branch-to-minutes analysis preserves source URIs, exact excerpts, and a companion evidence bundle.
- Gap: Public discovery is not an authoritative admission roster.
- Gap: Current repositories do not recover deleted records.
- Gap: Independent account snapshots are not an atomic network snapshot.
- Gap: Private reasoning, runtime identity, and causal consumption remain unobserved.
- Gap: Seventy-seven post-reference occurrences point to 28 targets absent from the retained snapshot.
- Gap: Record CIDs are preserved but not cryptographically reverified.
- Gap: No automatic retention expiry or deletion reconciliation is configured. Expansion requires a separate retention decision.
- Gap: The Linux request deadline requires the main thread. Alternate execution platforms remain unsupported.

## 5. Pruned Decisions (Keep max 3)

- [2026-10-03 Hermes]: Freeze the approved discovery cohort. Keep publication deferred and source records private.
