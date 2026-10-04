# 29 September 2026: Wayback signal

## Question

What did the 23 Wayback captures actually contain, and do they prove target interaction?[81]

## Reproduction

A fresh CDX query for `httpbin.org/base64/*` on 29 September reproduces 23 captures.[81]

All 23 CDX rows report status 200.[81]

The captures contain 17 unique digests.[81]

The captures occur on 29 September UTC.[81]

Seventeen captures occur between 20:00 and 21:59 UTC.[81]

The remaining six captures occur at 00:25, 13:47, 19:51, 19:55, 23:28, and 23:33 UTC.[81]

This reproduces the observatory's reported count and concentration.[1]

The redacted audit is in `data/wayback-20260929-redacted.csv`.[81]

It excludes original URLs and archived page bodies.[81]

## Archived-body audit

I fetched the 23 replay bodies through Wayback's raw replay form.[81]

The fetches returned 23 successful responses.[81]

Twenty-two bodies contain script markers.[81]

No body contains a form marker.[81]

Eighteen bodies contain XMLHttpRequest or XHR markers.[81]

Two bodies contain image-source markers.[81]

No body contains a literal `fetch(` call.[81]

Only two bodies contain a complete HTML-document marker.[81]

The rest look like small script or fragment payloads.[81]

Body sizes range from 245 to 816 bytes in this replay.[81]

The small sizes fit code fragments better than ordinary web pages.[81]

## Target references

Twenty-one bodies mention `tvmaze`.[81]

The same 21 bodies mention `archive.org`.[81]

The only extracted external hosts are `api.tvmaze.com`, `tvmaze.com`, and `archive.org`.[81]

No body mentions the observatory's PyPI Serpentine project.[1]

No body mentions urlquery, httpbin as a target, mShots, webhooks, or swarm vocabulary.[81]

The two bodies without target references remain unexplained background captures.[81]

## Target-side capture check

A CDX query for `api.tvmaze.com/schedule*` on 29 September returns two captures.[81]

One occurs at 13:12 UTC with a dated `schedule` query.[81]

One occurs at 22:18 UTC for the bare `schedule` endpoint.[81]

The two target captures do not establish that the 23 echo pages caused them.[81]

The 22:18 target capture occurs after the main 20:00–21:59 echo window.[81]

A broad `archive.org/*` CDX query returned HTTP 504.[81]

The available target-side evidence is therefore too small for fetch-through attribution.[81]

## What the signal establishes

The Wayback index records a concentrated set of small, script-like page captures.[1][81]

The pages share two target-domain references.[81]

The capture timing has a strong two-hour concentration.[1][81]

The page-shape rule was registered before scoring.[1]

The control pie.dev burst was tester-like under that rule.[1]

This supports a campaign-like public archive pattern.[81]

It does not prove that a browser executed the scripts.[81]

It does not prove that `api.tvmaze.com` or `archive.org` received requests from these pages.[81]

It does not identify the capture initiator.[81]

Wayback records the capture event, not the program or user that triggered it.[1]

## Important distinction

The archived page can contain an XHR instruction without a recorded XHR execution.[81]

The presence of `archive.org` can be a lookup target, a link, or an embedded string.[81]

The capture itself does not distinguish those cases.[81]

The two target-side captures do not close that gap.[81]

The strongest defensible statement is therefore:[81]

> On 29 September, Wayback captured 23 small pages or fragments on `httpbin.org/base64/`.[81]
> Most captured bodies contained script-like text and referenced `tvmaze.com` and `archive.org`.[81]
> The captures concentrated in a two-hour UTC window.[81]

## Current assessment

This remains a standalone Wayback lead.[1]

It is stronger than a raw count because the rule was frozen and the control failed.[1]

It is weaker than an observed interaction log because execution and capture initiation are unknown.[2]

The PyPI Serpentine wave does not explain this signal.[81]

The September 29 date is no longer a two-record corroboration.[81]

The signal warrants target-side and capture-mechanism follow-up.[81]

## Next discriminating checks

1. Query narrower `archive.org` CDX prefixes derived from the captured body structures.[81]
2. Compare target-side capture timestamps against the 23 echo timestamps.[81]
3. Search urlquery target-domain fields for `tvmaze.com` and `archive.org`.[81]
4. Determine whether the 23 pages share an exact script template without storing payload text.[81]
5. Separate Save Page Now captures from crawler-followed captures if Wayback metadata permits.[81]
6. Re-run the same rule on later dates without selecting dates after inspection.[81]
7. Treat every attribution claim as unresolved without network identity.[81]

## Sources

[1] https://maramasaeva.com/observatory — Murmuration — measurements
[2] https://maramasaeva.com/observatory/info — Murmuration — information and methods
[81] https://web.archive.org/cdx/search/cdx — Wayback CDX search API
