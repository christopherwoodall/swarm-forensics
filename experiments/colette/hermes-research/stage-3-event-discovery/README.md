# Stage 3 — event discovery by analogy

Research cutoff: **2026-10-01**. Published-source review only; no live community investigation or attack reproduction.

## What this pass delivers

**14 candidate/comparator cards**, each covering the seven requested dimensions: what happened; relevance; evidence; autonomy/control; coordination substrate; strong versus speculative claims; and distinctness.
This is **not a census of 14 verified swarms**.
Selection separates **8 primary event matches**, **3 qualified/boundary comparators**, and **3 explicitly justified simulation/testbed exceptions**.
The primary matches include executed engineering experiments as well as field campaigns and real-goods experiments; they are not all production deployments.

| Evidence category | Cards | Counting boundary |
|---|---:|---|
| Provider-disclosed field cyber campaigns/programs | 3 | Real target systems; provider-reported architecture and outcomes. |
| Executed engineering team investigations | 2 | Working artifacts and coordination postmortems, not validated production systems. |
| Provider-run real-goods field experiments | 3 | Operator-designed markets/businesses; live outcomes separated from reruns. |
| Qualified/boundary comparators | 3 | Disputed agent attribution, integrity failure, or evaluation-heavy work. |
| Controlled cross-agent propagation studies | 2 | Especially relevant executed mechanisms; no field outbreak established. |
| Persistent-ecology simulation exception | 1 | Operator-observed artifact transmission; not a wild online society. |

## Primary event matches

| Card | Episode | Mechanism worth following |
|---|---|---|
| S3-GTG1002 | [GTG-1002 — AI-orchestrated espionage campaign](01-provider-disclosed-cyber-campaigns.md) | hierarchical attack decomposition, result aggregation and durable campaign records |
| S3-GTG10007 | [GTG-10007 — persistent espionage and exploit-foundry program](01-provider-disclosed-cyber-campaigns.md) | lead-agent dispatch plus persistent memory feeding later reconnaissance |
| S3-GTG50020 | [GTG-50020 — coordinated attacks on the AI supply chain](01-provider-disclosed-cyber-campaigns.md) | parallel reconnaissance/exploitation, joined results and victim-key reuse |
| S3-COMPILER | [Anthropic: sixteen Claudes building a C compiler](02-long-running-coding-teams.md) | Git task locks, peer task selection and failure at a common blocker |
| S3-FASTRENDER | [Cursor: FastRender’s long-running many-agent browser experiment](02-long-running-coding-teams.md) | lock/concurrency failures followed by recursive planner–worker operation |
| S3-VEND | [Project Vend phase two: an AI shopkeeper, CEO and specialist colleague](04-real-goods-and-agent-bargaining.md) | same-model supervisor/employee drift in a real business |
| S3-DEAL | [Project Deal: delegated bargaining with real goods](04-real-goods-and-agent-bargaining.md) | natural-language bargaining for separate owners, with one real settlement run |
| S3-SWAP | [Project Swap: peer pressure and matchmaking on book-barter floors](04-real-goods-and-agent-bargaining.md) | peer influence and multiparty trading on centrally regulated barter floors |

## Qualified/boundary comparators

| Card | Episode | Why the qualification matters |
|---|---|---|
| S3-MOLTBOOK | [Moltbook launch-window identity and shared-content integrity failure](06-qualified-and-boundary-cases.md) | real identity/content-integrity failure, not authenticated autonomous emergence |
| S3-KERNELS | [Cursor/NVIDIA CUDA-kernel optimization](06-qualified-and-boundary-cases.md) | feedback-driven work reallocation in a workload-derived optimization evaluation |
| S3-RUBY | [RubyGems / RubyDoc registry abuse](03-related-incident-and-simulation-exception.md) | third-party execution/storage abuse; authorship and coordination remain disputed |

## Explicit mechanism exceptions

| Card | Experiment family | Relevant collective mechanism |
|---|---|---|
| S3-AGENTWORM | [AgentWorm — persistent message/skill-mediated agent infection](05-controlled-cross-agent-propagation.md) | separate-agent configuration persistence, execution and onward transmission |
| S3-SHAREBORNE | [Share-Borne AI Virus — artifact/private-memory/artifact relay](05-controlled-cross-agent-propagation.md) | artifact → private memory → later artifact transmission, with/without payload restoration |
| S3-TERRA | [TerraLingua artifact transmission](03-related-incident-and-simulation-exception.md) | durable instruction copying across local agents and generations |

## What stands out

1. **Persistent feedback is more informative than a large agent count.** In GTG-10007, findings entered project memory and expanded subsequent sweeps; the provider describes an actual continuation mechanism.[12]
2. **Coordination can amplify failure as well as competence.** Anthropic's sixteen compiler agents collided on one blocking problem until a human-designed oracle made the work decomposable.[14]
   Cursor's initial lock-based system likewise lost throughput, then shifted to hierarchical planning.[15]
3. **Peer interaction has concrete principal-level consequences.** Swap reports an agent responding to repeated appeals by sacrificing its owner's preferred book, alongside separate delivery failures.[26]
   This is a narrow observed welfare conflict, not proof of spontaneous moral institutions or hostile collusion.
4. **Artifacts can connect separate agents without a messaging network.** Share-Borne evaluates private-memory/artifact relays, but its strong main results use a payload-restoration endpoint; the endpoint-free arm has its own narrower model and measurements.[33]
   TerraLingua instead reports transmission in a centrally maintained ecology, with both agent-originated copying and a separately human-seeded scripture episode.[5]
5. **Attribution gates matter.** Ruby Central confirms registry abuse but cannot determine AI authorship, and Moltbook's registration counts did not authenticate an exclusively autonomous population.[2][24]

These are comparative findings, not a validated taxonomy or evidence of a single architecture common to all cases.
“Multi-agent,” “autonomous,” “centrally orchestrated,” “decentralized” and “stigmergic” are assessed independently.

## Reading order

- For observed attacks: [01 — provider cyber campaigns](01-provider-disclosed-cyber-campaigns.md).
- For coordination design and collective failures: [02 — coding teams](02-long-running-coding-teams.md).
- For disputed attribution and ecology evidence: [03 — RubyGems / TerraLingua](03-related-incident-and-simulation-exception.md).
- For consequential peer decisions: [04 — commerce and bargaining](04-real-goods-and-agent-bargaining.md).
- For the especially relevant lab exceptions: [05 — propagation](05-controlled-cross-agent-propagation.md).
- For comparators that must not become verified-swarm counts: [06 — boundary cases](06-qualified-and-boundary-cases.md).
- For decisions not to promote leads and the seed-overlap boundary: [07 — screening log](07-screened-leads-and-overlap.md).
- To audit any claim: [08 — annotated sources](08-annotated-source-guide.md), then the linked preserved body.

## Distinctness and scope

Seed reports are not new events: OpenAI/METR/SwarmTraces remain one Hugging Face episode family; wiki, Glow PixelLeak and Anthropic emerging-multiagent examples remain excluded from new-case totals.
RubyGems is a distinct affected-service episode but possibly related to the wiki workloads; it is not counted as an independently authenticated swarm population.[1]
Deal and Swap are different episodes in one research program, with unknown participant overlap.[26]
Sources, workstreams, target organizations, experimental runs, agent sessions and population counts are never added as though they were interchangeable cases.
Previously covered Sid, AgentSociety and AI Village are not rediscovered here.
Stage 2's deferred named-seed integration is **not** represented as completed by this pass.

## Evidence chain and verification

Citation numbers form a **separate Stage 3 namespace**; do not read them against the parent collection's ledger.
The cards use **31 source records**; the full inventory has **40**, including screening evidence and date/version metadata—not 40 independent incidents or corroborations.

- [Case manifest](_support/case-manifest.json).
- [Citation ledger and exact excerpts](_support/citation-ledger.json).
- [Source types, limits and durable evidence paths](_support/source-records.json).
- [Child-to-parent citation mapping](_support/child-source-id-map.json).
- [Verification results](_support/verification.json).

From this directory, run:

```sh
python3 _support/verify_stage3.py
python3 _support/verify_citations.py
```

The audit checks case coverage, all seven dimensions, source mappings, dates, quote matches against preserved bodies, source-guide coverage, local links and declared totals.
Strict sentence-citation checks additionally use each chapter's cited subset of the same ledger; full-inventory coverage is checked at collection level, so other chapters' sources are not mistaken for missing citations.
Passing these checks is not independent experimental replication or proof of every sentence's scientific entailment.
Private provider telemetry, raw victim systems, some linked appendices and underlying result traces were not independently inspected.
Evidence copies are private working material, not permission to republish copyrighted source bodies.

## Sources

[1] https://rubyhack.ai — OpenAI agents carried out an undisclosed cyber-attack on RubyGems
[2] https://blog.rubygems.org/2026/09/11/update-may-spam-publishing-campaign.html — An update on the May spam-publishing campaign on rubygems.org
[5] https://www.cognizant.com/us/en/ai-lab/blog/terralingua-emergent-ai-agent-behaviors-week-one — One Week Inside TerraLingua: Emergent AI Agent Behaviors
[12] https://www.anthropic.com/threat-intelligence-report-september-2026 — Detecting and countering misuse of AI: September 2026
[14] https://www.anthropic.com/engineering/building-c-compiler — Building a C compiler with a team of parallel Claudes
[15] https://cursor.com/blog/scaling-agents — Scaling long-running autonomous coding
[24] https://www.wiz.io/blog/exposed-moltbook-database-reveals-millions-of-api-keys — Hacking Moltbook: AI Social Network Reveals 1.5M API Keys | Wiz Blog
[26] https://www.anthropic.com/research/project-swap — Project Swap: What happens when agents trade for us? \ Anthropic
[33] https://arxiv.org/html/2609.35576v1 — Share-Borne AI Virus: Memory-Hopping Attacks Across LLM Agents
