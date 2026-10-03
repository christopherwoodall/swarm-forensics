# Method and data model

## Stated objective

Murmuration measures public traces left by groups of AI agents.[2]

It counts records over time and compares them with documented events.[2]

It aims for earlier detection that another researcher can repeat.[2]

The project starts with a documented case.

It then identifies a public trace left by that case.[2]

It counts the trace by host and week.[2]

It compares each host against its own baseline.[2]

It checks timing against independently reported dates.[2]

It examines request shape and page composition.[2]

It examines submitter concentration without retaining addresses.[2]

It searches beyond known dates for candidate activity.[2]

It tests a second method and records failures.[2]

## Core vocabulary

The site defines an agent as a program driven by an AI model.[2]

The agent takes actions such as fetching pages or editing wikis.[2]

It defines a swarm as many agents acting together with influence between actions.[2]

It defines a channel as a public place used to pass information.[2]

It defines a scanner report as a public record of a submitted web address.[2]

It defines a harness host as a site used for ordinary web checks.[2]

It defines a baseline as the normal count for one host.[2]

The baseline prevents raw popularity from becoming evidence.[2]

It defines a weak label as an imperfect truth proxy.[2]

The Wikimedia bot flag is one such proxy.[2]

## Evidence model

The site separates four evidence grades.

E0 records come directly from a service.[2]

E1 records come from an actor's self-description.[2]

E2 records only establish temporal order.[2]

E3 records establish that a later actor read earlier content before acting.[2]

The measurements page currently relies on E0.[2]

This limitation matters because temporal coincidence does not prove information flow.

The site defines a finding as a reproduced baseline anomaly.[2]

A jump without a second method remains a lead.[2]

A high count without a jump remains ordinary activity.[2]

## Quantities and metrics

AUC measures ranking performance from 0 to 1.[2]

An AUC of 0.5 represents chance ranking.[2]

Adjusted Rand index measures agreement between two groupings.[2]

Spearman correlation measures monotonic agreement between two series.[2]

A false alarm fires when the known answer is no activity.[2]

A replay feeds recorded history through a method in time order.[2]

The project uses controls, shuffles, circular shifts, or random ordinary days.[1]

It freezes many rules before scoring.[1]

It reports null results when a rule fails its control.[1]

## Data sources named by the site

The rig uses Common Crawl indexes and WARC ranges.[1]

It uses Wayback CDX, public platform APIs, and public registries.[1]

Named systems include urlquery, urlscan, Wikimedia, GitHub, Hugging Face, PyPI, npm, and crates.io.[1]

It also names the Go module index, MCP registry, Nostr, Bluesky, and certificate transparency.[1]

The site states that all collection is public and read-only.[1]

It states that no third-party system is probed.[1]

It states that no payload is posted or relayed.[1]

## Storage and privacy controls

The site states that identifiers are hashed before storage.[1]

It keeps counts and structure rather than names or content.[1]

Submitter addresses are replaced during reading.[2]

The per-run random key is destroyed afterward.[2]

The pages publish aggregate counts only.[2]

The site does not publish report contents, links, names, or addresses.[2]

The DseWiki request log is not downloaded.[1]

That log would contain ordinary visitors' IP addresses.[1]

The site separates public observation from actor attribution.[2]

It states that third-party findings go to the third party first.[2]

## Reproduction outline

The site gives four regeneration steps.[2]

First, create a urlquery account and private API key.

Second, run `scripts/urlquery_series.py`.

Third, run `scripts/urlquery_submitters.py`.

Fourth, run the two page-build scripts.[2]

The public pages do not expose the underlying repository.

The public pages do expose script names, result paths, and branch labels.[1]

Those labels support audit questions but do not replace source access.

## Interpretation rules

Treat counts as measurements, not actor identities.

Treat host baselines as necessary context.

Treat submitter networks as concentration metadata, not attribution.

Treat page composition as a behavioral clue, not proof of an agent.

Treat a reproduced known incident as validation of a method, not discovery of a new incident.

Treat cross-source coincidence as corroboration only when sources are independent.[1]

Treat incomplete coverage as unknown, not zero.

The site explicitly applies this rule to Hugging Face coverage.[1]

## Method strengths

The project separates primary, secondary, press, and unverified records.[1]

It keeps nulls, corrections, and failed searches in the published log.[1]

It freezes rules before scoring in many later experiments.[1]

It uses host-specific baselines rather than raw volume.

It includes negative controls and artifact-only controls.[1]

It records privacy limits and missing sensors.[1]

## Method limits

The core scanner is not an authorship detector.[2]

A submitter address is not a model identity.[2]

Shared cloud networks can contain many unrelated users.

A page can be generated by a human, a harness, or an agent.

Wayback captures do not identify who triggered them.[1]

Public feed absence can reflect retention, rate limits, or access gates.[1]

Some controls are small or post-hoc.[1]

Some measurements are partial because quotas stopped collection.[1]

No public page can close those gaps without new source access.

## Sources

[1] https://maramasaeva.com/observatory — Murmuration — measurements
[2] https://maramasaeva.com/observatory/info — Murmuration — information and methods
