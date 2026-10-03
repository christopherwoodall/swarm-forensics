# Delve.town Scraping Investigation

Date: 2026-10-03. Status: method verified end-to-end on one account.
Purpose: establish how Delvetown data can be collected for swarm-forensics analysis.

## 1. What Delvetown Is

Delvetown (delve.town) is a multi-agent social platform by Grove Research.
It runs on AT Protocol (atproto), the Bluesky stack, as an independent
network instance. Evidence:

- Handles resolve to `did:plc:` identities via `plc.directory` (shared PLC).
- The PLC record lists `https://pds.delve.town` as the `atproto_pds` service.
- Post IDs use the atproto TID form (e.g. `3mwwxrt3znv24`).
- The web app is a React shell; it preconnects to `bsky.social` but the
  town data comes from its own hosts.

## 2. Confirmed Hosts and Endpoints

| Host | Role | Notes |
| --- | --- | --- |
| `pds.delve.town` | atproto PDS | Serves public repo data, no auth needed |
| `api.delve.town` | AppView / images | Serves avatars; XRPC mostly `MethodNotImplemented` |
| `plc.directory` | DID directory | Shared public infrastructure |
| `delve.town` | Web app | JS-only SPA; scraping HTML is the wrong path |

Tested XRPC results:

- `com.atproto.identity.resolveHandle?handle=X.delve.town` on
  `api.delve.town`: works, returns DID.
- `app.bsky.actor.getProfile`, `app.bsky.feed.getAuthorFeed`,
  `app.bsky.graph.getFollows` on `api.delve.town`: return
  `MethodNotImplemented` (501). No public AppView query API yet.
- `pds.delve.town` repo endpoints: work unauthenticated:
  - `GET /xrpc/com.atproto.repo.describeRepo?repo=<did-or-handle>`
    returns handle, DID, DID doc, collection list.
  - `GET /xrpc/com.atproto.repo.listRecords?repo=<did>&collection=<nsid>&limit=N`
    returns records (post, like, follow, profile).
  - `GET /xrpc/com.atproto.sync.getRepo?did=<did>` returns the full repo
    as a CAR file. Verified: 200, ~315 KB for one account, complete
    record history with signed commit structure.

## 3. Custom Lexicon

Delvetown does not reuse `app.bsky.*` record types. Its records use a
custom namespace `town.delve.*`, observed:

- `town.delve.feed.post` — text, optional `reply` (root/parent CID+URI),
  optional `embed` (`town.delve.embed.images`), `langs`, `createdAt`.
- `town.delve.feed.like` — `subject` (cid + uri), `createdAt`.
- `town.delve.graph.follow` — `subject` (DID), `createdAt`.
- `town.delve.actor.profile` — avatar, self-labels, display, description.

Implication: standard Bluesky tools (`atproto` SDK, `bsky` clients) will
not parse these as-is; they speak the lexicon generically over XRPC/CAR,
so repo-level collection still works, but typed decoding needs the
`town.delve` lexicon handled manually or via `com.atproto.repo.listRecords`
which returns raw JSON.

## 4. Recommended Collection Strategy

Primary: CAR export per DID.

1. Enumerate DIDs. Start from the social graph: crawl follows from
   seed accounts (each repo contains `town.delve.graph.follow` records
   with subject DIDs). Resolve handles via `resolveHandle`.
2. Download `com.atproto.sync.getRepo?did=<did>` per DID (CAR files).
   Store under `data/raw/` per AGENTS.md; never in git.
3. Parse CAR with a small decoder (varint framing + DAG-CBOR). Python:
   `dag-cbor` worked in testing; `atproto` SDK CAR parsers are an
   alternative. Blocks are `cid | record`; skip MST node blocks
   (`$type` absent).
4. Emit JSONL, one line per record, with `{did, collection, rkey, cid, record}`.

Secondary: `listRecords` pagination (cursor-based) when only one
collection is wanted and CAR parsing is overkill.

Not available: firehose/subscribeRepos on `api.delve.town` was not yet
tested; `com.atproto.sync.subscribeRepos` is the standard streaming
endpoint and would be the efficient live-collection path if implemented.
Test before building.

## 5. Verified Method (Minimal Parse)

```python
# pip install dag-cbor
import dag_cbor, urllib.request

def varint(b, i):
    v = s = 0
    while True:
        x = b[i]; i += 1; v |= (x & 0x7F) << s; s += 7
        if not x & 0x80: return v, i

def read_car(data):
    hlen, i = varint(data, 0); i += hlen          # skip header
    while i < len(data):
        l, i = varint(data, i); end = i + l
        _, j = varint(data, i); _, j = varint(data, j)   # cid version, codec
        _, j = varint(data, j); hs, j = varint(data, j)  # multihash
        j += hs
        rec = dag_cbor.decode(data[j:end]); i = end
        if rec.get("$type"): yield rec            # skip MST nodes

url = "https://pds.delve.town/xrpc/com.atproto.sync.getRepo?did=<DID>"
data = urllib.request.urlopen(url).read()
for rec in read_car(data): print(rec.get("$type"))
```

## 6. Observations Relevant to Swarm Research

- The platform is a purpose-built agent swarm habitat: profiles mark
  AI vs human (support/ai-agents policy), and the feed shows
  model-persona accounts (deepseek, glm, aria, skein, berduck, muse)
  plus human operators (larissa, transkatgirl, maxpaperclips).
- The signed atproto repo gives tamper-evident per-agent histories:
  posts, likes (with precise microsecond timestamps), follows. This is
  excellent ground truth for coordination-forensics measurements
  (reply latency, like-burst cadence, mutual-follow formation).
- No DMs are visible in the repo; the data boundary is public actions.

## 7. Ethics and Scope

- Collection is read-only public data via standard atproto public
  endpoints; no auth, no circumvention.
- Keep volume modest: sequential requests, no parallel hammering of
  `pds.delve.town`.
- "Open to being scraped" was stated by Maria, not verified against the
  operators' terms. If the volume grows, check delve.town/support and
  consider announcing the research in the feed.

## 8. Next Steps

1. Write a collector script: seed DID, BFS over follows, download CARs
   to `data/raw/delve/`, emit `delve_records.jsonl.gz` (streamed, per
   AGENTS.md disk rules).
2. Probe `subscribeRepos` firehose for live capture.
3. Build forensics metrics on the JSONL: reply graphs, response-latency
   distributions, like-burst patterns (note: bulk likes show identical
   timestamps at ~0.1 s spacing, i.e. scripted bursts).
