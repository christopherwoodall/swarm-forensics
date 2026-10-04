# 29 September 2026: first analysis

Update: The PyPI component is resolved as a coherent Serpentine release wave. Read [the resolution](08-september-29-pypi-resolution.md).[1]

## Executive reading

29 September is the strongest new date in the observatory.[1]

It is not a confirmed new swarm.[1]

The formal result is a K = 2 coincidence between the Wayback echo-service record and PyPI.[1]

Hugging Face adds a third elevated record, but its own background is too active for strong discrimination.[1]

The correct current label is: promising cross-source lead, without attribution.[1]

## The three signals

### 1. Wayback httpbin record

The pre-registered page-shape rule marks 29 September as swarm-like.[1]

The date has 23 captures and 23 decoded pages.[1]

The swarm-style share is 0.83.[1]

The tester-style share is 0.09.[1]

The unchanged rule reproduces the 29 September verdict.[1]

The capture pattern has 17 unique digests among 23 captures.[1]

Seventeen captures occur between 20:00 and 21:59 UTC.[1]

All 23 captures return status 200.[1]

The 17 unique digests represent about 74% of captures.[1]

This is not one identical page copied 23 times.

It is also not 23 independent contents with no repetition.[1]

The decoded pages reference `tvmaze.com` and `archive.org`.[1]

Those references differ from the June targets, which centered on AIHW and Tableau.[1]

The date therefore has a distinct content signature from the confirmed June period.[1]

### 2. PyPI author-day burst

The PyPI rule requires at least 20 distinct packages first-created by one author-hash on one UTC day.[1]

It also requires at least ten times the registry median, at least 80% single-use, and at least 50% machine-named.[1]

The control contains 10,559 author-days.[1]

Its median is one package and its p99 is four.[1]

Only 0.09% of control author-days reach 20 packages.[1]

One 29 September author-day passes all four conditions.[1]

The burst contains 33 packages.[1]

The page reports 97% single-use and 100% machine-named packages.[1]

The packages use a `serp-*` family and are create-once.[1]

Nine other high-count author-days fail because they publish multiple versions.[1]

The site treats single-use as the important discriminator.[1]

The site does not publish the package names, publisher identity, code, or exact release times.[1]

Therefore the PyPI result is a strong anomaly, but not an attribution.

### 3. Hugging Face background elevation

The September HF scan covers 49,517 model owner-days.[1]

It finds 429 owner-days with at least 20 creations.[1]

It finds 22 single-owner bursts after excluding the reproduction program.[1]

The September background averages about 14 mass-creator owner-days per day.[1]

On 29 September, 19 distinct owners each create at least 20 models.[1]

That exceeds the daily average by about 36%.[1]

It remains inside the platform's continuous heavy-tailed background.[1]

The observatory explicitly rejects a distinct September HF swarm event.[1]

HF therefore strengthens the date as a coincidence, but weakens it as an isolated anomaly.

## What the conjunction means

The formal K = 2 result combines PyPI and Wayback.[1]

The Wayback date coincides with the only PyPI author-day passing its rule.[1]

HF also elevates on that date, but the formal detector does not treat it as an equally strong source.[1]

The three sources measure different mechanisms.

Wayback measures archived page captures.

PyPI measures package creation events.

Hugging Face measures model creation by owner-day.

Their independence is useful, but their units are not equivalent.

The evidence does not show that the same actor caused all three signals.

It does not show a shared IP address, account, package dependency, page payload, or model artifact.[1]

It does not show that any participant read another source before acting.[2]

The conjunction is therefore temporal corroboration, not causal linkage.

## Why 29 September matters

The date is not merely a large count on one popular platform.[1]

It combines one rare package burst with one rare page-shape day.[1]

The site reports no comparable crates.io burst on 29 September.[1]

The site reports no third source strong enough to raise the date to K = 3.[1]

The date is later than the June and July incidents.

It may represent a later recurrence, a different workload, or coincidence.

The page itself calls 28 May and 29 September dates worth pursuing.[1]

## Main alternative explanations

### A. One legitimate automated publisher

One release process could create 33 machine-named packages in one day.

The single-use rule makes ordinary SDK publishing less likely, but it does not make it impossible.[1]

A package family named `serp-*` could support search or scraping software.

That interpretation is only a semantic clue, not evidence of intent.

The site did not inspect the package code in this public report.[1]

### B. One operator using multiple public services

A person or script could publish packages and archive demonstration pages on the same day.

The Wayback skeptic review names this as the strongest alternative.[1]

The archive cannot distinguish Save Page Now from a crawler following links.[1]

The PyPI result does not identify the publisher in the public page.[1]

### C. Independent background coincidence

HF already contains frequent machine-named mass creation.[1]

Wayback contains a weak baseline and broad page-shape criteria.[1]

PyPI has a low but nonzero rate of large author-days.[1]

The three marginal signals could align without a common operation.

The global K = 2 result is not rare by itself.[1]

The page reports a global p-value of 0.14 for K = 2 somewhere.[1]

The July p = 0.0006 cannot be transferred to September.[1]

September has no equivalent held-out significance claim.

## Evidence grading

Wayback evidence is strong as a public-record observation.

Its interpretation as swarm-like is moderate because the rule was frozen in advance.[1]

Its specificity is limited because the 2025 baseline has only 18 decoded pages.[1]

Its 29 September verdict holds in 14 of 17 sensitivity variants.[1]

It becomes mixed when the size bound increases by 30% or the two referenced hosts are excluded.[1]

PyPI evidence is strong as a distributional anomaly under the stated rule.[1]

Its actor interpretation is weak because the publisher and package contents are withheld.[1]

HF evidence is weak for a September event because the background is continuous.[1]

The combined date is a moderate research lead, not a discovery claim.

## Best next tests

1. Resolve whether the 33 PyPI packages belong to one coherent software release.
2. Compare their exact creation timestamps with the Wayback 20:00–22:00 UTC window.
3. Inspect package metadata, dependencies, source links, and README templates.
4. Check whether package metadata references `tvmaze.com`, `archive.org`, or related services.
5. Compare the September 29 package burst with rejected multi-version publishers.
6. Re-run the Wayback rule on later dates without changing its thresholds.
7. Build a control set of unrelated PyPI burst days and Wayback page-shape days.
8. Test whether package and archive events share a stable time-of-day signature.
9. Treat HF owner-days as background unless shared templates or artifacts emerge.
10. Search for a third independent source with a pre-registered September test.

## Working conclusion

For now, treat 29 September as a reproducible two-record coincidence.[1]

The PyPI component is the sharpest anomaly.

The Wayback component supplies independent timing and page-shape support.[1]

The HF component is contextual and weak.[1]

The date deserves deeper source-level investigation.

It does not justify calling a new swarm.

## Sources

[1] https://maramasaeva.com/observatory — Murmuration — measurements
[2] https://maramasaeva.com/observatory/info — Murmuration — information and methods
