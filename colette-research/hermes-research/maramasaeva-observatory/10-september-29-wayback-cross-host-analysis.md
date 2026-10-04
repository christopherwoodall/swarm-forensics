# 29 September 2026: cross-host Wayback analysis

## Question

Does the 29 September pattern occur only on `httpbin.org`, or across related echo services?[81]

## Host sweep

I queried ten echo-service hosts for `/base64/*` captures on 29 September.[81]

The sweep found 23 captures on `httpbin.org`.[81]

It found 10 on `httpbin.dev`.[81]

It found 2 on `httpbin.io`.[81]

It found 1 on `httpbingo.org`.[81]

It found zero on `httpbun.com`, `pie.dev`, `eu.httpbin.org`, `postman-echo.com`, `httpstat.us`, and `mockbin.io`.[81]

The sweep therefore found 36 captures across four hosts.[81]

Thirty-five replay requests succeeded.[81]

One `httpbingo.org` replay refused the connection.[81]

The redacted rows are in `data/wayback-20260929-cross-host-redacted.csv`.[81]

## Timing

The secondary hosts align with the main `httpbin.org` window.[81]

Eight `httpbin.dev` captures occur at 20:00 UTC.[81]

One `httpbin.dev` capture occurs at 21:00 UTC.[81]

One `httpbin.dev` capture occurs at 22:00 UTC.[81]

`httpbin.io` has one capture at 20:00 UTC and one at 21:00 UTC.[81]

The `httpbingo.org` capture occurs at 20:00 UTC.[81]

This is a same-hour, cross-host concentration.[81]

It is stronger than a single-host archive anomaly.[81]

## Body similarity

All ten replayed `httpbin.dev` bodies mention both `tvmaze` and `archive.org`.[81]

Both replayed `httpbin.io` bodies mention both target domains.[81]

The main `httpbin.org` set has 21 target-referencing bodies out of 23.[81]

The bodies use script-like content rather than HTML forms.[81]

The shared target-domain pair appears across three echo-service hosts.[81]

This is the first result that materially strengthens the Wayback lead.[81]

The signal is not confined to one host's archive behavior.[81]

## Threshold limitation

The observatory's classifier evaluates a day only when one host has at least 20 decoded pages.[1]

Only `httpbin.org` reaches that threshold.[81]

The `httpbin.dev` and `httpbin.io` counts remain supporting evidence, not independent classifier positives.[81]

The cross-host result therefore strengthens pattern continuity without raising the formal K value.[81]

It does not create a third independent source.[81]

## What this supports

The 29 September event likely involved a common payload family, common workflow, or common operator session across echo hosts.[81]

The shared target references make an incidental single-host crawl less likely.[81]

The aligned hours make an unrelated multi-day coincidence less likely.[81]

The capture records still do not show runtime execution.[81]

They do not show who triggered the captures.[81]

They do not show whether the target domains received requests.[81]

A single developer test harness could still produce the same cross-host pattern.[81]

A scripted archival session could also produce it.[81]

The result does not identify a swarm.[81]

## Updated assessment

The Wayback signal now has two layers.[81]

Layer one is a pre-registered `httpbin.org` page-shape anomaly.[1]

Layer two is a same-hour extension across `httpbin.dev` and `httpbin.io`.[81]

Together, these make the date a stronger campaign-like public-record lead.[81]

They still do not establish agent execution, common authorship, or target-side activity.[2]

The PyPI Serpentine release remains unrelated evidence.[81]

September 29 remains a Wayback-centered lead, not cross-source corroboration.[81]

## Next checks

1. Re-run the same host sweep for September 28, 30, and October 1.[81]
2. Compare body fingerprints across the three active hosts.[81]
3. Query target-side CDX paths at matching hours.[81]
4. Separate shared payload templates from shared target references.[81]
5. Check whether the secondary hosts' page sizes cross the classifier threshold on nearby dates.[81]
6. Preserve only structural metadata and hashes.[81]

## Sources

[1] https://maramasaeva.com/observatory — Murmuration — measurements
[2] https://maramasaeva.com/observatory/info — Murmuration — information and methods
[81] https://web.archive.org/cdx/search/cdx — Wayback CDX search API
