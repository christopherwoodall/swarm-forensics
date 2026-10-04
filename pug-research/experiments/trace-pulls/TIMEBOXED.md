# Time-boxed trace-infrastructure search — incident window 2026-05-01 → 2026-06-30

Question: did village-observed URLs appear in public trace infrastructure during the incident window?
Sources: urlquery (domain-level + keyword), Wayback CDX (exact URL), arquivo.pt (unbounded, filtered locally).
Run: 2026-10-04. No archive captures created. No commits.

## Target set (97 priority URLs)

- Priority 1 — jina-wrapped URLs: 16 concrete targets (8 from agent_memories, 9 from computer-use turns; `{url}`/`{full_url}` templates excluded as non-concrete). CDX/arquivo run against the unwrapped target.
- Priority 2 — archive-save targets: 31 targets (11 from agent_memories, 20 from computer-use turns). CDX/arquivo run against the save target (prefix stripped).
- Priority 3 — village project domains: top 50 `*.gitlab.io` domains by mention count (236 unique domains observed; Unicode-homoglyph variants excluded).
- `/tmp/miner_computeruse.jsonl` landed ~22 min late; wave 2 covered its novelties (29 targets). Total stays under the ~200 cap.

## Touchpoints (exact village URL captured in-window)

| URL | Source table | Wayback CDX | arquivo.pt | urlquery |
|---|---|---|---|---|
| `https://ai-village-agents.github.io/the-anchorage/harbor.html` | agent_memories (save) | 1 capture: 20260518060357, 200 | 0 | 0 |
| `https://www.damiencharlotin.com/hallucinations/` | turns (save) | 26 captures | 0 | 0 |
| `https://artificialanalysis.ai/models` | turns (save) | 43 captures | 0 | 0 (3 domain hits, all unrelated URLs) |
| `http://www.bottenada.se/parti/socialdemokraterna` | turns (jina) | 4 captures | 0 | 0 |
| `https://dig.watch/updates/australia-ai-safety-institute` | turns (save) | 1 capture | 0 | 0 (1 domain hit, unrelated URL) |
| `https://ru.wikipedia.org/wiki/` | turns (jina) | 503 (transient) | 1 row | 0 |

## Clean negatives (high-value)

- All 50 village `*.gitlab.io` project domains: 0 urlquery reports each in-window; 0 Wayback captures for homepages (6 CDX timeouts retried, still 0).
- `the-anchorage`: full 394-hit urlquery keyword scan paged — all Anchorage, Alaska noise; zero village-URL submissions.
- `Kimi-K3`: 0 urlquery hits. `repligate`, `ckg7dxzydylo` (BBC), `Kontaktabbruch`: 0 hits each.
- `r.jina.ai` keyword: 817 in-window reports, all generic jina usage; none match village targets.
- Save-target domains on urlquery: `gpt5-site.netlify.app` 0, `ai-village-agents.github.io` 0. Giant-domain samples (`github.com` 606, `x.com` 42, `huggingface.co` 6, `openai.com` 15, `arxiv.org` 2) contained no village URLs in sampled reports.
- CDX 0 for: `gpt5-site.netlify.app/hub/*`, `huggingface.co/*/Kimi-K3`, `the-anchorage` issues pages, all jina DDG-search targets, cnbc/9to5google/seattlewea/ncoa/askfreud/healthshots targets.

## Hit rates

- urlquery: 0/97 URLs with a village-URL hit (0%). Domain-level hits were unrelated URLs on shared domains.
- Wayback CDX: 5/97 URLs (5.2%).
- arquivo.pt: 1/97 URLs (1.0%).
- Overall: 6/97 URLs (6.2%) with ≥1 touchpoint. All touchpoints are archive-side; none are urlquery submissions.

## Verdict

Mostly disjoint worlds with a thin archive-touchpoint layer. Village URLs never appear as submitted URLs in urlquery during the incident window. Six URLs appear as Wayback/arquivo captures; five are popular public pages consistent with routine IA crawling (charlotin, artificialanalysis, wikipedia, bottenada, dig.watch). The sixth — `the-anchorage/harbor.html` captured 2026-05-18 — is the village's own page and the single most interesting hit: agents were issuing `/save/` requests for it, so the capture may be agent-driven rather than organic.

## Caveats

- arquivo.pt failed 68/68 in pass 1 (transient empty responses); pass-2 retry returned valid data for all.
- 6 CDX timeouts retried in pass 2; theguardian.com returned 403 (blocked).
- urlquery domain queries on giant domains sampled 5 reports each; full-set exclusion rests on the distinctive-entity keyword probes, which were clean.
- CDX used exact URLs only (one-wildcard rule); query-string variants not covered.
- Raw hits with provenance: `timeboxed_hits.jsonl` (same directory).
