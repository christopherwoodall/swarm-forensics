# 29 September 2026: PyPI burst resolved

## Result

The PyPI signal is not an unexplained 33-package burst.[1]

It is a coherent release wave from one project named Serpentine.[1]

The PyPI burst is therefore a likely benign package-publishing false positive for swarm detection.[1]

This does not invalidate the Wayback signal.[1]

It removes PyPI as independent corroboration for 29 September.[1]

The September 29 K = 2 result should be downgraded to a Wayback-only candidate.[1]

## Exact package set

The observatory reports one 29 September `serp-*` family with 33 packages.[1]

The PyPI Simple index and JSON metadata recover exactly 33 first-created packages on that date.[3]

The package names are listed in `data/serpentine-september-29.csv`.[1]

They are:

- `serp-time`, `serp-asyncio`, `serp-coil`, `serp-datetime`, `serp-fang`, `serp-http-server`.[1]
- `serp-itertools`, `serp-log`, `serp-math`, `serp-molt`, `serp-os`, `serp-pathlib`.[1]
- `serp-queue`, `serp-random`, `serp-re`, `serp-scales`, `serp-secrets`, `serp-socket`.[1]
- `serp-sqlite`, `serp-statistics`, `serp-strings`, `serp-structs`, `serp-subprocess`, `serp-test`.[1]
- `serp-threading`, `serp-tomllib`, `serp-url`, `serp-uuid`, `serp-venom`, `serp-zipfile`, `serp-zlib`.[1]
- `serpentine-io`, `serpentine-argparse`.[1]

The name family is semantically structured.[1]

It covers time, concurrency, math, files, sockets, HTTP, validation, data frames, and web serving.[1]

It does not resemble 33 independently chosen opaque handles.[1]

## Common provenance

All 33 packages declare the same Serpentine GitHub project URL.[8][9][10]

All 33 source distributions declare `Serpentine contributors` as author.[8]

All 33 require Python 3.11 or newer.[8]

All 33 use the MIT license.[8]

All 33 include a README, `pyproject.toml`, `setup.cfg`, Python source, and tests.[1]

The static source audit found 392 files, 107 Python files, and 62 test files.[1]

The audit found no README mentions of `tvmaze.com`, `archive.org`, `httpbin`, `urlquery`, mShots, webhooks, or swarms.[1]

The detailed audit is in `data/serpentine-source-audit.csv`.[1]

## Internal dependency graph

The release wave is internally connected.[1]

`serp-fang` depends on the URL, socket, JSON, base64, compression, UUID, time, IO, and shim layers.[1]

`serp-venom` depends on the HTTP server, socket, JSON, URL, async, and shim layers.[1]

`serp-molt` depends on JSON, regex, datetime, UUID, base64, and the shim.[1]

`serp-scales` depends on JSON, datetime, and the shim.[1]

`serp-zipfile` depends on zlib and the shim.[1]

The dependency edges are in `data/serpentine-dependencies.csv`.[1]

This graph is consistent with a staged language-library release.[1]

It is not consistent with 33 unrelated one-off packages.[1]

## Package purposes

`serp-math` is a pure-Serpentine facade over a compiler-known math runtime.[8]

`serp-fang` is an HTTP client modeled on httpx.[1]

It includes sockets, TLS, redirects, cookies, JSON, multipart, streaming, and uploads.[1]

`serp-venom` is a FastAPI-style web framework for Serpentine.[9]

`serp-molt` is a pydantic-style validation library.[1]

`serp-scales` is a pandas-style DataFrame and Series library.[1]

`serpentine-io` supplies file helpers and a buffered byte reader.[10]

The package descriptions form one technical roadmap.[1]

The descriptions do not point to the Wayback target hosts.[1]

## Release sequence

The 33 first uploads span 07:39:27 to 10:24:14 UTC.[1]

The package wave lasts about 2 hours and 45 minutes.[1]

Thirty-two packages have one release-version pair on that date.[1]

`serp-fang` has a second release version on the same date.[1]

That explains the site's reported 97% single-use rate.[1]

The last first creation occurs at 10:24 UTC; `serp-fang` has a second release about one minute later.[1]

The Wayback captures cluster between 20:00 and 21:59 UTC.[1]

The earliest archive activity follows the last package first-upload by about 9 hours and 36 minutes.[1]

The archive window follows the earliest package upload by about 12 hours and 21 minutes.[1]

This is same-day coincidence, not close temporal synchronization.[1]

## Project history before September 29

The Serpentine compiler had public PyPI releases before the burst.[4]

The compiler page lists releases from July 19 through September 30.[4]

The runtime shim also predates the burst and reached version 0.9.0 on September 28.[5]

The 33-package wave follows this compiler and runtime preparation.[4][5]

The release sequence therefore has a visible build-up.[1]

It is not a project created from nothing on September 29.[1]

## Source and publishing evidence

Representative PyPI pages expose the same Serpentine project repository.[8][9][10]

PyPI states that representative artifacts were verified as originating from the named publisher.[8]

The cited PyPI pages associate publication with GitHub Actions and the Serpentine repository.[8][9]

The repository URL itself returned a GitHub 404 during this retrieval.[12]

The source distributions remain available and were inspected without installation.[8][9][10]

The missing public repository limits direct commit-history verification.[1]

The shim README retains a legacy compiler link under `github.com/serpentine-lang/serpentine`, while PyPI metadata points to `avijitbhuin21/Serpentine`.[5]

This is consistent with a migration or stale documentation, not evidence of a second package family.[5]

It does not erase the common project metadata and package-source evidence.[1]

## Why the detector fired

The burst satisfies the observatory's four PyPI conditions.[1]

It exceeds 20 packages on one author-day.[1]

It is more than ten times the registry median.[1]

It is 97% single-use.[1]

Its names match the machine-name heuristic.[1]

The detector correctly identified unusual mass publication.[1]

The detector did not test whether the burst was a coherent software project.[1]

The machine-name condition is too broad for modular package suites.[1]

Names such as `serp-math`, `serp-socket`, and `serp-venom` are templated.[1]

They are also semantically meaningful within one documented architecture.[1]

The single-use condition distinguishes this wave from multi-version SDK releases.[1]

It does not distinguish a benign release wave from a coordinated malicious publisher.[1]

## Effect on September 29

PyPI no longer supplies independent evidence of a swarm-like operation.[1]

It supplies evidence of one coherent software project publishing many modules.[1]

The HF elevation remains background activity.[1]

The Wayback httpbin result remains a separate page-capture anomaly.[1]

The Wayback pages reference `tvmaze.com` and `archive.org`.[1]

The inspected Serpentine package READMEs do not reference either target.[8][9][10]

No package README references the Wayback services or urlquery.[1]

No shared target link connects the package wave to the archived pages.[1]

The original three-record September narrative was an over-interpretation.[1]

The correct current classification is:[1]

- PyPI: resolved benign release wave.[1]
- Hugging Face: continuous background, not an event.[1]
- Wayback: unresolved but weakened candidate.[1]
- September 29: not cross-source corroboration.[1]

## Remaining Wayback investigation

The strongest remaining question concerns the 23 Wayback captures.[1]

The package wave cannot explain them through direct package metadata.[1]

A common operator remains possible, but no linking artifact is present.[1]

The Wayback baseline remains weak.[1]

The 29 September page-shape result becomes a standalone lead.[1]

Its alternative explanation remains one person or script archiving demo pages.[1]

The next useful test is target-side linkage, not more package counting.[1]

Search the archived pages' outbound targets and timing against public activity on `tvmaze.com` and `archive.org`.[1]

Do not treat the Serpentine package release as evidence for that linkage.[1]

## Reclassification

The September 29 PyPI lead is resolved as a detector false positive.[1]

The observatory's rule found a real unusual event.[1]

The event was a legitimate-looking release program, not evidence of a covert swarm.[1]

This is a valuable positive-control failure.[1]

It demonstrates why package-burst detectors need project identity, dependency structure, and repository provenance.[1]

## Sources

[1] https://maramasaeva.com/observatory — Murmuration — measurements
[3] https://pypi.org/simple — PyPI Simple API index
[4] https://pypi.org/project/serpentine-lang — PyPI Serpentine compiler
[5] https://pypi.org/project/serpentine-shim — PyPI Serpentine runtime shim
[8] https://pypi.org/project/serp-math — PyPI Serpentine math package
[9] https://pypi.org/project/serp-venom — PyPI Serpentine web package
[10] https://pypi.org/project/serpentine-io — PyPI Serpentine IO package
[12] https://github.com/avijitbhuin21/Serpentine — GitHub repository URL cited by PyPI
