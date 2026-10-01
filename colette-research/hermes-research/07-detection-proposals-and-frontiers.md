# Detection proposals, theory, and a bounded workflow

Research date: 2026-10-01. This file separates published proposals, evaluated mechanisms, and this collection's own synthesis. Nothing here is a claim that an end-to-end universal AI-swarm detector has been validated or that new live investigations were performed.

## 1. Text-only detection has a conditional theoretical ceiling

Sadasivan and colleagues combine empirical detector stress tests with a theorem relating discrimination to the **total-variation distance between human and AI text distributions**. As those distributions become closer, the best achievable text-only AUROC decreases.[43]

The authors acknowledge that estimating the actual distance from finite text samples is difficult. The theorem does not prove all current classifiers useless, guarantee that every future model approaches human text, or invalidate provider logs, signed provenance, or behavioral evidence.[43]

Their experiments examine specified trained, zero-shot, watermark, and retrieval-based detectors. They support evaluating edited, mixed-origin, and out-of-distribution text, not a universal statement that every possible detector always fails.[43]

**Research implication:** improving surface fluency need not erase coordination traces. Content origin and relationships among actors are different evidence channels. Neither channel should be promised as foolproof.

## 2. Statistically calibrated coordination graphs

Pacheco et al. propose null models and Monte Carlo shuffling of the account–feature bipartite graph before projection, to test whether similarity edges exceed chance expectations. This is **future work in that paper**, not an evaluated component of its case studies.[37]

Nizzoli et al. actually implement backbone filtering and threshold sweeps, but their coordination index still does not distinguish authentic from inauthentic behavior.[38]

### An event-conditioned extension — proposed synthesis

A useful experiment would compare repeated co-actions with permutations preserving account activity, artifact popularity, and plausible event/time opportunities. This avoids a naive baseline in which every account has equal exposure to every artifact.

Required checks would include:

- Legitimate collective events: activist mobilization, fandoms, official campaigns, emergency response, news bursts, and share-button templates.
- Stability across time bins, similarity thresholds, minimum repeat support, and community-detection resolution.
- Multiple-comparison control over the actual search universe, not only a selected vivid cluster.
- Feature ablations: does a cluster survive removing one popular URL or copied template?
- Held-out time periods and entire campaigns, not random sibling posts from the same accounts.

This proposed extension was **not implemented or evaluated** for this collection. Even a statistically unusual edge would establish unusual dependence under a chosen null—not AI authorship, common ownership, or hostile intent. Organic coordination is an explicit false-positive concern in the foundational framework.[37]

## 3. Multilayer fusion: plausible, but easy to overstate

Published behavioral-graph methods motivate layers for shared URLs, images, repost targets, timing, and sequences. Provider investigations demonstrate output-to-publication matching and cross-platform linkage.[37][50]

**Proposed synthesis:** retain an account–artifact–time model, with separate evidence layers for exact reuse, semantic similarity, reciprocal interaction, infrastructure, and generation provenance. Only then evaluate combinations.

Every edge should say what produced it: “shared this rare URL twice within a defined window,” not merely “connected.” A projected similarity edge is not a verified private communications channel.[37]

Embedding similarity can prioritize review, but it is not an independent witness. A shared topic, language model, news source, or translation template can create resemblance without direct coordination. Preserve exact reuse and broader semantic similarity as different features.

A fusion score needs independent validation; several correlated features can otherwise count one observation several times. A strong public claim should depend on evidence that survives plausible benign explanations, not on the visual density of a graph.

## 4. Watermarks: evaluated mechanism, partial production evidence

Kirchenbauer et al.'s ICML 2023 watermark modifies generation-time token selection and detects statistical excesses using the compatible scheme, without running the underlying model during detection. It is implemented/tested research; that paper alone does not establish universal provider adoption.[46]

Length and entropy matter: low-entropy sequences require more text for detection. Compatible tokenization, rule/key access, and a participating generator constrain coverage.[46]

The later SynthID-Text paper supplies actual production evidence and supports abstention when insufficient watermark evidence is present. It also discusses vulnerabilities to edits and the difficulty of imposing marking on separately deployed open models.[60]

Interpretation should remain narrow:

- **Detectable compatible mark:** evidence of the generation scheme, under its validated assumptions.
- **No detectable mark:** not a certificate of human authorship.
- **AI-generated text:** not a certificate of a bot account or coordinated campaign.
- **Generation provenance:** not a certificate of truth, independent judgment, or legitimate sponsorship.

These boundaries follow from the marking mechanisms and their coverage limits.[46][60]

## 5. Cryptographic identity and privacy-preserving provenance

Schroeder et al.'s Science Policy Forum proposes layered provenance and identity approaches, including cryptographic attestations, passkeys, federated reputation, and verified-but-anonymous participation. It also emphasizes privacy, account hijacking, and risks to vulnerable speakers.[23]

These are **defense proposals**, not experimental proof that one identity scheme stops adaptive swarms. A verified account can be compromised, coordinated by a common operator, or used to publish false material.[23]

**Design implication:** the question is not simply “is there a human name?” It is what the credential attests, who issues it, what it reveals, whether identities are linkable across contexts, and how revocation/correction work. Real-name enforcement and proof of independent control are not equivalent.

A signed artifact can establish a signer or producer under a trust model; it does not establish an honest belief or a true claim. Public accountability should not require exposing dissidents' identities by default.

## 6. Closed-world swarm simulation as a defensive laboratory

The Policy Forum proposes artificial environments modeling graph structure, posting cadence, and recommender behavior to stress-test defenses. These are research directions, not established field-performance guarantees.[23]

Smallville and the LLM naming-game study provide examples of actual controlled multi-agent execution and measured population behavior, but neither evaluates online swarm detection.[53][54]

The social-simulation critique matters here: an omniscient model scripting all participants can perform differently from agents with separate information. A realistic benchmark should disclose its scheduler, memories, observation limits, prompts, and control topology.[26]

**Proposed benchmark matrix:** central controller versus local adaptation; direct conversation versus shared-medium coordination; separate versus shared memories; homogeneous versus heterogeneous models; legitimate disclosed automation versus deceptive personas; and ordinary human collective events as negative controls.

Report what survives domain transfer. A detector that recognizes one synthetic generator's writing style may not recognize the underlying coordination process.

## 7. Trusted runtime traces: stronger observability, narrower jurisdiction

For an **owned or explicitly authorized** multi-agent runtime, inspection could collect authenticated participant IDs, state transitions, delegation/task records, inter-agent messages, observed artifact versions, tool-call events, and enacted outcomes.

This is a proposed observability design, not a detector tested in this review. It directly addresses the difference between public output resemblance and internal dependency evidence.

For stigmergic systems, capture which version of a shared medium was observed before a decision—not just what was written. This follows from the action–trace–subsequent-action definition; write-only logging can miss the coupling mechanism.[24]

Trace integrity, completeness, retention, and access control still matter. “A log exists” does not make it authentic, complete, or safe to publish; keep credentials and unnecessary private prompt content out of default traces.

## 8. Recommended end-to-end workflow — synthesis, not a validated product

### Phase A — establish the question and authorized evidence universe

Specify account, post, cluster, campaign, or operator as the unit. Fix platform, languages, time span, permitted dataset, sampling, and missingness. Define distinct thresholds for coordination, AI assistance, identity deception, common operation, and adaptive autonomy.

Do not silently expand a retrospective literature review into live monitoring, scraping, probes, or public allegations. That would require new authorization.

### Phase B — reconstruct observable relationships

Preserve source identifiers, timestamps, original artifacts, and exact edge-generating features. Keep URL originals alongside analysis variants; normalization must not erase meaningful paths or query values. Separate reposts from original writing.

Record the difference between follower/reply links and projected behavioral similarity. Downweight popular artifacts and require repeated support where suitable. The published frameworks justify these ingredients but do not validate this entire combined workflow.[37][38]

### Phase C — test alternative explanations and calibration

Use matched organic controls, temporal holdouts, feature ablations, language/topic tests, and review below as well as above threshold. Do not measure precision using only a hand-picked set of obvious detections.

Where ground truth exists, report campaign-level precision/recall, false-positive rates, PR curves, calibration, review workload, and subgroup performance. Where a complete census is unavailable, mark recall unknown rather than manufacturing it.[40]

### Phase D — add corroboration, not substitute scores for evidence

Provider output matching, legitimate platform-internal records, and compatible watermarks can corroborate specific claims. They are different from blind text classification.[50][60]

Account-level content aggregates may be useful after local validation, but their promising historical benchmark result does not justify automatic bans or infer common controllers.[48]

Include benign AI writing assistance and mixed manual/automated activity in evaluation. Subgroup false positives and short-text limitations are substantive constraints, not cosmetic caveats.[44][45]

### Phase E — issue a bounded finding

Produce an evidence dossier with supporting observations, plausible alternatives, data gaps, analyst uncertainty, and the exact claim supported. Keep “unusual similarity,” “likely coordination,” “common operation,” “AI-assisted,” and “adaptive autonomous swarm” as separate conclusions.

Prefer proportionate review and correction paths to punitive automatic labeling. The 2026 content-detection authors expressly recommend human review before punishment; the Policy Forum warns that false bot accusations can suppress legitimate speech.[48][23]

## Bottom line

The strongest near-term approach supported by this reading is **relationship analysis plus provenance-supported investigation and human review**, not a single stylistic “AI detector.” The proposed frontier is measuring adaptive coordination without collapsing human collective action into artificial threat.

This is a literature-based judgment, not a proven optimum. Read the [implications/research agenda](08-implications-and-research-agenda.md) and the [source guide](09-source-guide.md) for evidence boundaries.

## Sources

[23] https://arxiv.org/html/2506.06299v4 — How malicious AI swarms can threaten democracy — Schroeder et al.
[24] https://pespmc1.vub.ac.be/Papers/StigmergyICognSystems.pdf — Stigmergy as a universal coordination mechanism I: Definition and components — Heylighen
[26] https://aclanthology.org/2024.emnlp-main.1208.pdf — Is this the real life? Is this just fantasy? The Misleading Success of Simulating Social Interactions With LLMs — Zhou et al.
[37] https://arxiv.org/pdf/2001.05658v2 — Uncovering Coordinated Networks on Social Media: Methods and Case Studies
[38] https://arxiv.org/pdf/2008.08370v2 — Coordinated Behavior on Social Media in 2019 UK General Election
[40] https://www.cs.unm.edu/~chavoshi/debot/SocInfo.pdf — Identifying Correlated Bots in Twitter
[43] https://arxiv.org/pdf/2303.11156v4 — Can AI-Generated Text be Reliably Detected?
[44] https://pmc.ncbi.nlm.nih.gov/articles/PMC10382961 — GPT detectors are biased against non-native English writers
[45] https://openai.com/index/new-ai-classifier-for-indicating-ai-written-text — New AI classifier for indicating AI-written text
[46] https://proceedings.mlr.press/v202/kirchenbauer23a/kirchenbauer23a.pdf — A Watermark for Large Language Models
[48] https://arxiv.org/html/2606.07219v1 — Adversarial Creation and Detection of AI-Generated Social Bot Content
[50] https://cdn.openai.com/threat-intelligence-reports/disrupting-malicious-uses-of-our-models-february-2025-update.pdf — Disrupting malicious uses of our models: an update February 2025
[53] https://arxiv.org/html/2304.03442v2 — Generative Agents: Interactive Simulacra of Human Behavior — Park et al., arXiv:2304.03442v2 / UIST 2023
[54] https://openaccess.city.ac.uk/id/eprint/35211/1/sciadv.adu9368.pdf — Emergent social conventions and collective bias in LLM populations — Ashery, Aiello and Baronchelli, Science Advances 11(20), eadu9368
[60] https://www.nature.com/articles/s41586-024-08025-4 — Scalable watermarking for identifying large language model outputs
