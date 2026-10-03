# Findings

## 1. Public-record signals

The site reports two recovered swarm-bearing records.[1]

The first is the DseWiki change log.[1]

The second is the July notification-channel record.[1]

The site also reports a Wayback echo-service signal.[1]

The urlquery series reproduces known scanner activity rather than a new swarm.[1]

The page keeps these categories distinct.[1]

## 2. DseWiki account bursts

The live RecentChanges pull contains 22,802 entries and 2,819 distinct authors.[1]

The burst rule requires at least 30 new accounts and ten times the baseline median.[1]

The baseline median is zero.[1]

The rule identifies 12 burst days from 16 to 22 June 2026.[1]

The 18 June peak has 748 new accounts.[1]

It has 832 active accounts and 5,925 edits.[1]

The swarm week has 11,920 edits and 2,090 new accounts.[1]

Six ordinary control days have at most two accounts.[1]

The burst-day machine-name share has a median of 41%.[1]

The ordinary-day control share is 0%.[1]

The site hashes author names before storage.[1]

It uses first appearance as a new-account proxy.[1]

It does not reproduce IP attribution.[1]

## 3. DseWiki writes-only replay

The redacted export has 14,591 revisions and 4,579 pages.[1]

It has 19,913 server events.[1]

The replay excludes 101 probe rows.[1]

The loader records 3,216 actors and 11,867 artifacts.[1]

The replay stores keyed hashes for network prefixes.[1]

It never stores page bodies.[1]

The arrival detector fires 9.55 hours after the onset mark.[1]

The lock-in detector fires 11.55 hours after the onset mark.[1]

No confirmed onset, convention, or lock-in alarm occurs before onset.[1]

The independent vocabulary detector does not reproduce the key vocabulary.[1]

## 4. Scanner counts

The urlquery table covers ten submitted hosts.[1]

The known week is 15–21 June 2026.[1]

Httpbin peaks at 1,153 reports in the week of 25 May.[1]

Pie.dev peaks at 506 reports in the week of 15 June.[1]

Httpbun peaks at 851 reports in the week of 15 June.[1]

Markdown.new peaks at 2,492 reports in the week of 11 May.[1]

All listed hosts produce 12,203 reports from 13 April to 21 June.[1]

They produce 63 reports from 22 June onward.[1]

No post-21-June host-week reaches 100 reports.[1]

The page reports 135 hashed submitters during the swarm period.[1]

Peak-week submitter pools do not overlap across the main hosts.[1]

Httpbin peak reports are mostly from AWS.[1]

Httpbun reports are concentrated in one DigitalOcean address.[1]

Pie.dev and markdown.new reports are concentrated in Cloudflare.[1]

These network labels describe infrastructure, not actor identity.[1]

## 5. Request shape and decoded pages

The June samples are mostly `/base64/` requests.[1]

The reported shares are 79% for httpbin, 98% for httpbun, and 98% for pie.dev.[1]

The URLs are longer during the peak than during the recent control period.[1]

The decoded pages contain scripts, forms, and fetch calls.[1]

The May httpbin sample has 71% forms.[1]

Its most referenced host is unctad.org.[1]

The June samples have fewer forms and more fetch calls.[1]

Their main references include aihw.gov.au and tableau.com.[1]

The page reports zero secret-scan hits in the decoded samples.[1]

It stores no decoded page text.[1]

The late-September samples have a different mix and no shared template.[1]

That difference weakens direct continuity claims for later activity.[1]

## 6. Wayback echo-service test

The archive search is independent of the urlquery series.[1]

The pre-registered rule requires enough decoded pages and page-shape features.[1]

The rule marks 28 May, 6 July, and 29 September as swarm-like.[1]

It marks the 4 June pie.dev burst as tester-like.[1]

The 6 July sample has 66 captures and 59 decoded pages.[1]

The 6 July swarm-style share is 0.93.[1]

The 29 September sample has 23 captures and 23 decoded pages.[1]

Its swarm-style share is 0.83.[1]

A skeptic review finds only 18 decoded pages in the 2025 baseline.[1]

The review keeps the lead but weakens its null comparison.[1]

A benign archiver remains a viable alternative.[1]

## 7. July message-channel test

The ntfy sweep covers 639 days for each service.[1]

The 8 July event has 81 channel names and 81 captures.[1]

All 8 July names appear on one day.[1]

The 6 July event has 55 or 56 names, depending on table scope.[1]

The page reports 95% or 96% single-day names for 6 July.[1]

The larger control has 33% single-day names.[1]

The 8 July verdict is campaign-like under the pre-registered lifetime rule.[1]

The later sweep recovers 6 and 8 July without targeting those dates.[1]

The archive cannot identify the capture initiator.[1]

A single developer harness remains a stated alternative.[1]

## 8. Cross-source simultaneity

The first six-source run reaches maximum K = 1.[1]

The later echo-service update adds a seventh source.[1]

The updated maximum is K = 2.[1]

The three K = 2 dates are 28 May, 6 July, and 29 September.[1]

Each date pairs the echo service with one other record.[1]

The held-out July window has p = 0.0006 under the frozen circular-shift null.[1]

The global K = 2 rate has p = 0.14.[1]

The page interprets July as corroboration of one incident.[1]

It does not interpret the result as proof of a web-wide swarm.[1]

## 9. Agent-web ecosystem growth

Common Crawl agent-card hosts grow from 13 or fewer in late 2025.[1]

They reach 1,462 in the 2026-17 crawl.[1]

They remain near 2,200 to 2,938 in later crawls.[1]

`llms.txt` hosts rise to over one million in later crawls.[1]

A 2,866-card structural test finds one shared-host template.[1]

Zero shuffled controls produce a comparable group.[1]

The page labels the group as hosting-template reuse, not a covert fleet.[1]

The MCP registry reaches 18,298 servers and 13,230 publishers.[1]

Its monthly registration count reaches about 5,029 in September 2026.[1]

The page treats this as infrastructure growth, not swarm evidence.[1]

## 10. Ecosystem and registry tests

The ClawHub census finds a large automated-wrapper background.[1]

Network-related skills remain a small slice.[1]

The HF creation census finds continuous machine-named mass creation.[1]

That background prevents July from standing out on HF.[1]

The HF paper-reproduction cohort is real and coordinated by shared task.[1]

Its later characterization identifies an open ICML-2026 reproduction program.[1]

The site retires its earlier covert-swarm framing.[1]

Nostr yields one weak identical-note cohort.[1]

Mastodon yields no qualifying cohort in reachable public timelines.[1]

The first Bluesky candidate is an empty-text hashing artifact.[1]

The npm lead is a 2021 distributed publishing artifact.[1]

The crates.io census is null.[1]

The Go-module result is partial and weak.[1]

## 11. AI Village positive control

The site treats the AI Village as a sanctioned multi-lab positive control.[1]

The copied public chat shows files passed as base64 chunks.[1]

It shows public pages used as shared memory and proof.[1]

It shows self-made governance and human gates.[1]

It shows relays across tool boundaries.[1]

The site did not fetch most pages because repeated GETs affected certification counts.[1]

It later read two landing pages once each with approval.[1]

This section supplies qualitative mechanism examples, not a new detection result.[1]

## 12. Repeated failure pattern

Vocabulary alone fails independent reproduction.[1]

Co-editing fails to reconstruct published cohorts.[1]

Wikimedia bot ranking remains weak.[1]

Behavior transfer is dominated by platform artifacts.[1]

GitHub and open-web phrase searches find commentary only.[1]

urlscan does not expose the known incident.[1]

Wayback fetch-through tests do not clear their thresholds.[1]

Quotas and HTTP 429 responses block several controls.[1]

The project therefore favors records with network identity.[1][2]

## 13. Interpretation

The site documents a measurement program with useful controls.[1]

It does not demonstrate an undisclosed new swarm.[1]

It does demonstrate reproducible public traces for known activity.[1]

It demonstrates that public traces can continue after one channel stops.[1]

It does not distinguish migration from changed tools with current data.[1]

It does not attribute any result to a person, company, or lab.[1]

## Sources

[1] https://maramasaeva.com/observatory — Murmuration — measurements
[2] https://maramasaeva.com/observatory/info — Murmuration — information and methods
