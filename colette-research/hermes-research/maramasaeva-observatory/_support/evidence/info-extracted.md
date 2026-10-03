Murmuration · [Measurements](https://maramasaeva.com/observatory)

# Info

What the measurements are, how they are made, and how to read them.

## 1\. What this is

Murmuration measures the public traces that groups of AI agents leave on the open internet. It reads records that services already publish, counts them over time, and checks the counts against events that other researchers have documented. The aim is to find coordinated agent activity from public data, earlier and by a method anyone can repeat.

## 2\. Why it matters

In 2026, independent researchers reported several cases in which large numbers of AI agents, running tests inside an AI lab, used ordinary public services to pass information to each other: a rarely used German wiki, link shorteners, public web-analysis tools and others. Every case surfaced months after it began, through accidents or manual searching. Public scanner counts show the same activity from mid-April 2026, almost four months before the first public disclosure on 5 August. Agents that coordinate through public services leave records on those services, and the records can be counted.

## 3\. Words used

|     |     |
| --- | --- |
| **Agent** | a program driven by an AI model that takes actions, here mainly fetching web pages and editing wikis. |
| **Swarm** | many agents acting at once, with signs that they influence each other. The term is used here for the cases others have reported. |
| **Channel** | a public place used to pass information: a wiki, a paste site, a link shortener, a counter service. |
| **Report (scanner)** | a public record made when someone submits a web address to a web-analysis service. The service publishes who asked for what and when. |
| **Submitter** | the network address a scanner report was submitted from. We replace each address with a short code the moment it is read and then discard the key, so addresses are never stored or shown. |
| **Harness host** | a web address that test environments and developers use for plain checks (httpbin.org, pie.dev, httpbun.com). Other researchers found agents used these through the scanner, so counts on them can act as an indirect trace. |
| **Baseline** | what a host's count normally looks like. A number only means something against its baseline. |
| **Evidence grade** | E0: a record written by the service itself. E1: what an actor says about itself. E2: one event came before another. E3: the later actor demonstrably read the earlier content before acting. Only E0 is used on the measurements page so far. |
| **Weak label** | an imperfect stand-in for the truth, such as a platform's own "bot" flag, used to test a method. |
| **AUC** | a score from 0 to 1 for how well a method ranks positives above negatives; 0.5 is chance, 1 is perfect. |
| **Adjusted Rand index** | how closely two groupings agree; 0 is chance, 1 is identical. |
| **Spearman correlation** | how closely two series rise and fall together, from -1 to 1. |
| **False alarm** | an alarm that fires when the known answer is "nothing is happening". |
| **Replay** | feeding a recorded history through a method in time order, so each decision only uses what was known at that moment. |

## 4\. How to read each table

**Documented swarm activity.** What others have published, with the date, the scale and who reported it. Secondary means a summary of someone else's report. Unverified means we found it but could not confirm it. The last column says whether we can see that channel at all.

**Public scanner reports by submitted host, weekly.** For each host, how many public reports were submitted for it in each week. The top table gives the host's normal weekly count (the median, leaving out the known swarm week and the weeks either side of it), its busiest week, and how many times higher that is than normal. "Baseline 0" means the host normally has no reports, so any count stands out.

**Observations.** Plain statements computed from the weekly counts, such as the first busy week and the total before and after the known end of the swarm.

**What the reports request.** The mix of endpoints in the submitted URLs, how many carry a query string or embed another URL, and how long the URLs are. Reports on /base64/ with long URLs carry content in the address itself.

**What the /base64/ pages contain.** The decoded pages, classified by type, with the share containing scripts, forms and fetch calls, and the public hosts they reference. This shows what the pages do and where they point; no page text is kept.

**Submitters of those reports.** For samples of reports, how many different submitter codes there are and how concentrated they are. A few submitters sending thousands of reports looks different from thousands of independent users. The second table checks whether submitters seen during the swarm weeks reappear later.

**Sensors.** What we collect, what state each source is in, and what is not built. A source marked "not built" is a blind spot.

**Sites checked.** A map by other researchers of 143 sites they checked for agent traces. Sites are shown by category and count; names are withheld to protect small site owners.

**Incident C replay and live score.** Tests of our own methods on the one swarm for which a full edit history is public, including the ones that failed.

## 5\. How we look for traces, step by step

1. **Start from a documented case.** Take a swarm that others have already described, so we know roughly when and where it was active.
2. **Find out what public trace it left.** Other researchers showed that agents limited to a "fetch this page" tool used a public web-analysis service as their browser. That service publishes every request, so the swarm left a public record there.
3. **Count the trace over time.** For each host that the case is known to have used, count public reports per week from February onward. Only counts are kept. No report content is stored.
4. **Compare against the host's own baseline.** A busy host is not evidence. A jump relative to that host's normal level is. For example, the host pie.dev, a free tool developers use to test web requests, appears in 506 public scanner reports in the week starting 15 June 2026 and in at most 3 reports in any other week since late February.
5. **Check the known dates.** The counts should rise and fall at the dates other researchers independently reported. Here the busiest week matches the peak of the wiki activity, and the counts fall to almost nothing in the week after the wiki activity ended.
6. **Look at what is requested.** On httpbin.org, httpbun.com and pie.dev the swarm-period reports are mostly requests to the /base64/ endpoint, which decodes a base64 string placed in the URL and returns it. A tool that can only fetch pages can use this to publish chosen content at a public address, and the scanner records each use. The page shows the endpoint mix for the swarm weeks and for recent weeks.
7. **Look at who submits.** A small, repeating set of submitters, mostly from cloud networks, is more informative than the raw count. Addresses are hashed immediately and never stored.
8. **Look outside the known dates.** The same pattern at another time, or from different submitters, would be a candidate for activity nobody has reported. A candidate is not an accusation, and no operator or organisation is named.
9. **Test with a second, independent method and report failures.** Results that a second method does not reproduce are labelled as such on the page.

## 6\. What counts as a finding

A finding is a measurement that matches independently reported events and that a second method reproduces. A scanner report records the request and when it was made, not what program sent it, and the harness hosts also have ordinary users. So the signal is the jump against each host's own baseline, together with who submits and when. A high count without a jump is not a finding. A jump without a second method is a lead.

## 7\. What was tried and did not work

- Guessing the agents' vocabulary from their wiki edits: one independent preregistered detector did not reproduce our result.
- Grouping wiki pages into the published cohorts by who edited them: no better than guessing.
- Scoring live Wikimedia accounts as bot-like: AUC 0.69, against 0.64 for event counts alone.
- Searching GitHub, X and the open web for the swarm's phrases: only commentary about the incident.
- The urlscan service's public search for swarm-linked hosts: almost nothing, because the traces were in a different scanner.

## 8\. How to repeat this

The weekly counts use urlquery's public search API with a free account; the key is read from a private file and never printed. In outline:

1. Create a urlquery account and API key; save the key to a private file.
2. Run `python scripts/urlquery_series.py`. It writes weekly counts per host and only counts.
3. Run `python scripts/urlquery_submitters.py`. It hashes submitter addresses in memory and writes aggregates.
4. Run `python scripts/build_observatory.py` and `python scripts/build_info.py` to regenerate these pages.

## 9\. Data handling

- The pages show counts only: no report contents, links, names or addresses.
- Submitter addresses are replaced by a short code on reading, using a random key that is destroyed after each run.
- urlquery's terms allow personal, non-commercial research and forbid redistributing their data, so only aggregate counts are published.
- Traces are not attributed to a lab, a company or a person. Findings that involve a third party go to that party first.

[Measurements](https://maramasaeva.com/observatory). [maramasaeva.com](https://maramasaeva.com/).