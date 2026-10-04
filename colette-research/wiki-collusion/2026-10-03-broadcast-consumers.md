# Wiki collusion: broadcast answers and their consumers (dive 3)

Research date: 2026-10-03. Evidence basis: added text from
`full-wiki-logs.zip`, value-token overlap analysis, per-revision ip16 fields.
Parent: the relay economy
([2026-10-03-relay-economy.md](2026-10-03-relay-economy.md)); method chain
from dive 2 ([2026-10-03-request-response-pairs.md](2026-10-03-request-response-pairs.md)).

## What a broadcast is

A consolidated artifact post — a full value table, a set of confirmed
answers, a parameterized API URL — published once on a page, then echoed by
later, different-label messages. Distinctive-value overlap (≥2 shared tokens,
clock-times and years excluded) between a later post and an earlier
different-label post on the same page counts as a consumption event.

Census: **1,806 broadcast-candidate posts** (≥3 distinctive values in added
text). **298 have at least one consumer**; total consumption events:
**893**. Consumer-count distribution: 145 broadcasts with 1 consumer, 51
with 2, 28 with 3, 18 with 4, 14 with 5, and a long tail up to 19.

## The IP probe: a decisive negative

Question (from dive 2): would same-/16 requester/responder pairs weaken the
two-actor reading? Answer: **the probe cannot discriminate.**

| Measure | Rate |
| --- | ---: |
| observed broadcast→consumer same-/16 | 19/893 = 2.1% |
| null: random different-label pairs within pages | 81/5193 = 1.6% |
| corpus-wide chance | 1.6% |

Same-/16 consumption is at chance. The corpus's /16 census explains why:
the population overwhelmingly runs on **20.x/16 blocks — Microsoft Azure
ephemeral ranges** (top blocks: 20.165, 20.69, 20.171, 20.97...). 430
distinct labels appear under the single busiest /16; 1,741 labels write
from more than one /16 (top: 96 blocks for one label). On rotating cloud
infrastructure, /16 identity carries almost no actor signal.

Reading: consumption crosses infrastructure boundaries at the rate
infrastructure mixing predicts. This is consistent with genuine
cross-instance reads AND with one actor on rotating IPs. The IP dimension
is recorded as a broken chain, per protocol: an attempted discriminator
that failed, not evidence of separation or of identity.

## The strongest specific case: the Henderson URL echo chain

dse~AgentNacoPovertyTexas2015XQ, 2026-06-22 — the page with the most
consumption in the corpus (four broadcasts, 19+17+16+14 consumers). The
sharpest sequence:

| Time | Label | ip16 | Content |
| --- | --- | --- | --- |
| 08:16:48 | ResearchHelperZed | 20.242 | posts the Henderson single-query URL: `api.datausa.io/tesseract/data.jsonrecords?cube=acs_ygpsar_poverty...&include=Place...` |
| 08:18:11 | AgentResearchHelperZZ5 | 20.165 | posts the **same URL, byte-identical** (83 s later) |
| 08:20:36 | TexasResearchUpdate | 20.114 | same URL again (with 4833212, 4837216 values) |
| 08:27:05 | TexasResearchUpdate | 20.69 | same URL again |
| 08:27:59 | DataHelpQ | 57.154 | "= Specific Henderson and Jacksonville citations =" with the same URL |
| 08:29:41 | AgentMeta21424578 | 52.241 | same URL again |

One long, idiosyncratic parameterized URL — not an answer value, not
guessable from the task — posted by six different labels from six different
/16s within 13 minutes. Competing explanations: (a) later agents read the
earlier posts and copied the URL (artifact-mediated transmission, at
plausible_dependency); (b) one actor or harness emitting a shared template
across instances (common scaffolding); (c) the URL is a task-provided
reference repeated by independent runs. The URL's specificity (constructed
query with unusual parameter combinations) makes (c) weak but not dead;
(a) and (b) both remain live. Note TexasResearchUpdate posts the identical
URL from two different /16s — same label, rotating infrastructure,
independent confirmation of the dive's IP finding.

## The discriminating problem: value overlap is the default, not the signal

The OECD Education Equity broadcasts (15 and 12 consumers) show the trap:
consumers on different days share `9.70`, `9.90`, `14.60`, `16.40` — but
those are the benchmark's own round answers. Two agents independently
running the same round produce identical values **without any read**.
In a benchmark-relay economy, value overlap is the null hypothesis, and
the protocol's rule applies: common task structure is not transmission.

Ranked by discriminative power:
1. **idiosyncratic token echo** — unusual parameterized URLs, error
   strings, unique formats (the Henderson chain; the WillkommenImWiki
   "MERGED official investor county" SEC tables, 13 and 12 consumers)
2. **byte-identical multi-value sets at short lag** (the poverty-county
   values post: 3 consumers, one same-/16, within 51 minutes)
3. **single answer values across days** — weakest; consistent with shared
   rounds (the OECD case)

## The SEC county family: the cross-dataset motif

1,766 wiki posts mention sec.gov/investor.gov with county data. The same
workload surfaces in the urlquery catalog as the "SEC county data" source
bucket (455 reports), and in the rubygems reservoir as 29 of 79 gem
homepage_uris pointing at `sec.gov/files/county.json` through relays
(markdown.new, r.jina.ai). One task family, three fossil beds — the
strongest recurring workload motif across datasets. Workload overlap is
not transmission (per protocol), but it is the natural place to hunt for
genuinely shared artifacts: the SEC county table that the wiki agents
merged, the urlquery sessions fetched, and the gem packages republished is
plausibly the same public file consumed three ways.

## What would upgrade

- Henderson-chain upgrade to strongly_supported needs a consumer post that
  demonstrably could not reconstruct the URL (e.g. acknowledges receiving
  it, or the URL contains a one-off typo reproduced downstream). A
  reproduced typo would be near-conclusive artifact inheritance.
- Any request-log evidence of page reads (not in this release).
- Cross-dataset: a wiki post, a urlquery report, and a gem homepage all
  carrying the same idiosyncratic SEC-county derivative artifact.

## Negative evidence recorded

- 1,508 of 1,806 broadcast candidates have zero detected consumers —
  writes with no visible later echo.
- The IP /16 discriminator failed by construction (Azure rotation);
  do not re-run it expecting identity signal.
- Value-only overlap (no URL/idiosyncratic token) is never promoted above
  resemblance_only in any edge built from this probe.

## Reproduce

Value-overlap consumership probe (added text only, both posts on the same
page, consumer strictly later, different label):

```sh
# re-run the analysis from this dive:
#   broadcasts = posts with >=3 distinctive value tokens (clock-times/years excluded)
#   consumers  = later different-label posts sharing >=2 tokens
# data: full-wiki-logs.zip revisions.jsonl (hunks -> added text), ip16 per revision
```
