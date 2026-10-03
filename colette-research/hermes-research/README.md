# AI swarms — research collection

Research cutoff: **2026-10-01**. Status: first-pass review and Stage 3 event discovery completed; Stage 2's named-seed integration remains deferred. Published-source research, not a live-network investigation or an accepted implementation plan.

## Mechanism synthesis — chapter 15

Read [Swarm dynamics: coupling, memory, governance, and adaptation](15-autonomous-swarm-mechanisms-and-detection.md).
Compare control organization with information lineage across the existing cases.
Use its hackathon perusal section for bounded reading and research questions.

Chapter 15 uses a separate citation namespace and [evidence map](_support/synthesis-15/source-evidence-map.json).
Its [verification report](_support/synthesis-15/verification.json) audits the chapter independently.
The earlier collection audits below do not cover this addition.
No new trace-reservoir findings are incorporated in this baseline synthesis.
Earlier stage labels describe this imported snapshot, not the newer original authoring collection.

## Current entry point — Stage 3

Read [Stage 3: event discovery by analogy](stage-3-event-discovery/README.md) for the additional 2025–2026 case shortlist: 14 seven-dimension cards, comprising eight primary event matches, three qualified/boundary comparators and three explicit simulation/testbed exceptions. These are not fourteen independently verified swarms.

The subcollection includes its own screening log, annotated source guide, stable citation namespace, durable evidence map and [passing verification report](stage-3-event-discovery/_support/verification.json).

The numbered chapters and totals below are the **first-pass snapshot**, not a description of all later findings. The existing [wiki chapter](11-wiki-collusion-and-external-memory-2026.md) and [open-world-agent chapter](14-autonomous-societies-and-open-world-agents.md) are retained earlier additions; completing Stage 3 does not silently complete deferred Stage 2 integration.

## The central finding — first-pass snapshot

“AI swarm” covers several different architectures. Classical swarm intelligence emphasizes local interaction and self-organization; modern LLM teams may instead be centrally orchestrated, and the stronger malicious-online-swarm definition specifies persistent identity, adaptation, coordinated goals, limited oversight, and cross-platform capability.[8][22][23]

The documented online cases reviewed here substantiate **AI-assisted coordinated operations**, but do not demonstrate that full autonomous, adaptive capability bundle. FOX8 explicitly describes rule-based bots using ChatGPT for content generation/dialogue.[28]

Physical robotic swarms and controlled digital-agent experiments provide stronger direct evidence of collective mechanisms—but they are not proof that equivalent autonomous communities have been discovered on social media.[51][53][54]

## First-pass reading map

1. [Definitions and characteristics](01-definitions-and-characteristics.md) — architecture boundaries, descriptive checklist, emergence, and stigmergy.
2. [Online cases I](02-online-cases-fox8-and-openai-may-2024.md) — FOX8, Bad Grammar, Doppelganger.
3. [Online cases II](03-online-cases-spamouflage-zero-zeno-storm2035.md) — Spamouflage, STOIC/Zero Zeno, Storm-2035.
4. [Physical swarms](04-physical-swarm-cases.md) — Kilobot self-assembly, forest-navigation drones, Perdix.
5. [Digital agent experiments](05-digital-agent-experiments.md) — Smallville/Generative Agents and emergent LLM naming conventions.
6. [Operational and evaluated detection](06-detection-current-and-evaluated.md) — provider investigations, behavioral graphs, historical deployed tools, content classifiers, watermark deployment, and base rates.
7. [Proposals and frontiers](07-detection-proposals-and-frontiers.md) — statistical nulls, multilayer evidence, theoretical limits, provenance, defensive simulation, and a clearly labeled synthesis workflow.
8. [Implications and research agenda](08-implications-and-research-agenda.md) — dependency structures, synthetic consensus, error propagation, privacy, and bounded next research questions.
9. [Annotated source guide](09-source-guide.md) — reading routes, source type/status, exact versions, overlap, and limitations.

For a short route, read **01 → 06 → 07**, then the cases relevant to your question. For evidence-first reading, begin with **02–05**, then compare the classification boundaries in **01**.

## Case inventory and why it is not a census

The first-pass chapters (01–09) break down **11 cases**:

| Evidence class | Cases | Important boundary |
|---|---|---|
| Published online investigations — 6 families | FOX8; Bad Grammar; Doppelganger; Spamouflage; STOIC/Zero Zeno; Storm-2035 | AI assistance and coordination do not automatically establish autonomous swarm agents. |
| Physical demonstrations — 3 | Kilobots; micro flying robots in the wild; Perdix | Hardware tests are distinguished from simulations, publicity, and operational deployment. |
| Controlled digital experiments — 2 | Generative Agents; LLM convention formation | Actual executed research, not organically discovered internet communities. |

Spamouflage's synthetic-anchor, provider-text, and voter-persona reports are **three slices of one family**, not three independent swarms. Source overlap and distinct units—accounts, provider customers, agents, videos, websites, views—are preserved throughout.

This is a selected comparative review, not an exhaustive global survey. Online case coverage is principally **2023–2024**; detection/theory reading extends through **2026**. No conclusion is made about the prevalence or absence of more sophisticated undisclosed operations.

## Detection conclusions worth carrying forward

- Detect **relationships and repeated behavior**, not just AI-like wording. Coordination graphs do not by themselves establish intent or authenticity.[37][38]
- Provenance-supported investigations can substantiate model use more strongly than blind text inference, but access and downstream visibility are partial.[50]
- Promising historical account-level AUC is not field precision or identification of campaign control; the June 2026 preprint explicitly rejects automatic bans.[48]
- Watermarking is not only hypothetical: SynthID-Text reports production deployment. It remains compatible-generator provenance, not a universal swarm test.[60]
- Keep false accusations, legitimate collective human action, multilingual bias, and privacy in the evaluation—not outside it.[44][23]

## Evidence and verification support

The first-pass inventory contains **38 cited source records**, including overlapping versions/reports; this is not a claim of 38 independent corroborating studies. Each substantive file has a generated Sources section. Stage 3 uses a separately audited ledger and its own totals.

- [Source metadata and preserved evidence map](_support/source-records.json).
- [Stable citation ledger and exact excerpts](_support/citation-ledger.json).
- [Case coverage manifest](_support/case-manifest.json).
- [Computed base-rate illustration](_support/base-rate-example.json).
- [Final verification report](_support/verification.json).

Retrieved body text is preserved under `_support/evidence/`, outside the disposable research scratch directory. These are private working evidence copies of published sources, not permission to republish copyrighted material.

Run the local, stdlib-only structural/evidence audit from this folder:

```sh
python3 _support/verify_research.py
```

The audit checks citation/URL mappings, saved excerpt matches, source and case coverage, local links, file inventory, and unresolved placeholders. A passing check **does not automatically validate every scientific claim or interpretation**. Experimental results remain the cited authors' results; this collection did not independently rerun their systems or inspect private provider logs.

## Scope kept

Only published reports, papers, official disclosures, and reference material were researched. No live suspect-account hunting, private-message access, social-network scraping, operational probing, or newly discovered swarms were part of this work. No repository code, credentials, or unrelated project documents were changed; nothing was committed or published.

## Sources

[8] https://iridia.ulb.ac.be/~mdorigo/Published_papers/All_Dorigo_papers/DorBir2007sch-si.pdf — [PDF] Swarm Intelligence - Scholarpedia - IRIDIA
[22] https://arxiv.org/html/2501.06322v1 — Multi-Agent Collaboration Mechanisms: A Survey of LLMs
[23] https://arxiv.org/html/2506.06299v4 — How malicious AI swarms can threaten democracy — Schroeder et al.
[28] https://arxiv.org/pdf/2307.16336 — Anatomy of an AI-powered malicious social botnet
[37] https://arxiv.org/pdf/2001.05658v2 — Uncovering Coordinated Networks on Social Media: Methods and Case Studies
[38] https://arxiv.org/pdf/2008.08370v2 — Coordinated Behavior on Social Media in 2019 UK General Election
[44] https://pmc.ncbi.nlm.nih.gov/articles/PMC10382961 — GPT detectors are biased against non-native English writers
[48] https://arxiv.org/html/2606.07219v1 — Adversarial Creation and Detection of AI-Generated Social Bot Content
[50] https://cdn.openai.com/threat-intelligence-reports/disrupting-malicious-uses-of-our-models-february-2025-update.pdf — Disrupting malicious uses of our models: an update February 2025
[51] https://zhepeiwang.github.io/pubs/sr_2022_swarm.pdf — Swarm of micro flying robots in the wild — Zhou et al., Science Robotics 7, eabm5954
[53] https://arxiv.org/html/2304.03442v2 — Generative Agents: Interactive Simulacra of Human Behavior — Park et al., arXiv:2304.03442v2 / UIST 2023
[54] https://openaccess.city.ac.uk/id/eprint/35211/1/sciadv.adu9368.pdf — Emergent social conventions and collective bias in LLM populations — Ashery, Aiello and Baronchelli, Science Advances 11(20), eadu9368
[60] https://www.nature.com/articles/s41586-024-08025-4 — Scalable watermarking for identifying large language model outputs
