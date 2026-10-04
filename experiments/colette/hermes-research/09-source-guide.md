# Annotated source guide

Research date: 2026-10-01. This guide explains what each source can support, its evidence type, and important limits. Citation numbers are shared across the collection; gaps reflect retrieved candidates that were not used. The mechanically generated Sources section supplies exact URLs.

## How to use the evidence

- **Primary experimental paper:** evidence of the authors' executed experiment, not independent replication by this review.
- **Provider investigation:** privileged evidence of service use and account/output relationships, with partial downstream visibility and generally non-public raw data.
- **Independent threat-intelligence report:** analyst attribution and public-artifact investigation; confidence remains the reporting organization's assessment.
- **Official announcement:** evidence that an institution reported a demonstration; less inspectable than open methods and telemetry.
- **Conceptual paper / survey / policy proposal:** definitions, synthesis, or possible capabilities—not automatically a documented occurrence.
- **Preprint:** results may be informative, but review/publication status and the exact version matter.

Sources describing the same campaign or experiment are not independent occurrences. In particular, the FOX8 preprint/journal paper overlap; OpenAI's May overview overlaps its case reprints; and three Spamouflage reporting slices belong to one campaign family.

## Suggested reading routes

**Architecture and definitions:** Dorigo/Birattari, then Heylighen and the collaboration survey.[8][24][22]

The Policy Forum adds the modern online threat definition.[23]

**Observed online AI assistance:** start with FOX8, OpenAI's May disclosure/reprints, and Graphika's synthetic-anchor investigation.[28][34][35]

The voter-persona and Storm-2035 reports add different audience and provenance limits.[36][33]

**Detection mechanics:** Pacheco for account–artifact graphs, Nizzoli for coordination strength, and SynchroTrap for historical deployment.[37][38][39]

OpenAI's February report illustrates the provider vantage point.[50]

**Do not skip the limitations:** Botometer validation, the FOX8 field test, and subgroup false positives.[42][47][44]

The distribution-overlap theory is conditional rather than universal impossibility.[43]

## A. Foundations, architecture, and conceptual limits

### [8] Dorigo and Birattari — Swarm intelligence, Scholarpedia (2007)

Expert-authored foundational reference, read through the author-hosted PDF. The strongest narrow definition emphasizes coordinated action without a coordinator/external controller, local interaction, and self-organization. It provides classical algorithms and robotic context; it is not an online influence investigation. Typical simple-rule/homogeneity properties should not become rigid requirements for every modern multi-agent system.[8]

### [55] Bonabeau, Dorigo, and Theraulaz — Swarm Intelligence (1999)

Canonical book, accessed only through a displayed **page-7 excerpt** on its bibliographic preview. The excerpt supports the bio-inspired distributed-problem-solving definition. The whole book was not obtained or read, so no unviewed chapter is treated as evidence. This is historical terminology, not a case count or empirical modern-agent result.[55]

### [24] Heylighen — Stigmergy as a universal coordination mechanism I (2016; online 2015)

Conceptual paper defining indirect coordination through an action's trace stimulating subsequent action. Useful for repository/task-board/shared-medium architectures and for distinguishing trace-as-evidence from trace-as-mechanism. It applies to human activity too: stigmergy is neither an AI fingerprint nor proof of malicious control.[24]

### [22] Tran et al. — Multi-Agent Collaboration Mechanisms (2025; arXiv v1)

Survey taxonomy covering actors, collaboration types, control structures, strategies, and protocols. Useful for describing centralized, distributed, and peer-to-peer teams without calling all of them swarms. This review pins **2501.06322v1**; a survey is not independent replication of its cited systems.[22]

### [23] Schroeder et al. — How malicious AI swarms can threaten democracy (2026; v4)

Science Policy Forum, read in author-accepted **2506.06299v4**, dated January 22, 2026. Specifies persistent synthetic identities, coordinated objectives, adaptation, low oversight, and cross-platform capability; proposes technical/policy defenses. Threat analysis and proposed capabilities must not be counted as forensic proof of a fully autonomous online swarm.[23]

### [26] Zhou et al. — The Misleading Success of Simulating Social Interactions With LLMs (EMNLP 2024)

Empirical critique distinguishing an omniscient model scripting interlocutors from separate agents acting under information asymmetry. Read as the full ACL paper. Useful counterweight to plausible-looking social simulations; findings remain bounded by its models and tasks, not a verdict that all later simulations fail.[26]

### [27] Cemri et al. — Why Do Multi-Agent LLM Systems Fail? (2025; v3)

Empirical failure taxonomy and trace analysis, pinned to **2503.13657v3**. Identifies 14 modes across design, inter-agent misalignment, and verification. Useful for failure propagation and stopping/verification questions. Selected frameworks, tasks, and partly model-assisted annotation do not supply a universal failure rate for all swarms.[27]

## B. Online investigations

**Breakout terminology:** OpenAI uses Brookings' scale from 1 (lowest) to 6 (highest); its overview describes Category 2 as activity on multiple platforms without breakout into authentic communities. This is an uptake category, not a direct measure of causal persuasion.[34]

### [28] and [47] Yang and Menczer — Anatomy of an AI-powered malicious social botnet

The **2023 preprint** and **May 2024 journal paper** describe the same 1,140-account FOX8 network. Native PDF prose was used where reconstructed chart tables were unreliable. Strong evidence for an LLM-assisted botnet and benchmark-to-field detector gaps; refusal leakage is not provider-log proof, and not every post is confirmed AI-generated. Neither paper establishes fully autonomous decentralized agents or causal persuasion.[28][47]

The preprint was retrieved at an unversioned PDF URL, with first-posting/native-PDF metadata supporting the 2023 reading. The preserved evidence copy fixes what was actually read; do not assume the unversioned URL will remain identical.

### [34] OpenAI — Disrupting deceptive uses of AI by covert influence operations (May 30, 2024)

Provider overview of five disruptions during the preceding three months. Supports mixed AI/traditional workflows and low observed breakout in the inspected activity. Overlaps the detailed reprints and includes IUVM, which is not separately broken down here. Selection of detected/disrupted activity and partial distribution visibility prevent prevalence or universal-impact conclusions.[34]

### [29] Bad Grammar — case-study reprint

Provider evidence of coding assistance, Russian/English comment generation, and at least a dozen Telegram posting accounts. Supports a managed commenting pipeline and fabricated persona plurality. Exact total scale, scheduler, and unattended autonomy are undisclosed. Original May 30 report timing is used; the current reprint's May 1 label is not promoted into an earlier discovery date.[29][34]

### [30] Doppelganger — case-study reprint

Provider/public-output matching across **four model-service account clusters**, with task specialization and synthetic reply/amplification evidence. The clusters are not four independent campaigns or a social-account census. The engagement/Breakout assessment concerns the inspected AI-associated activity, not every historical Doppelganger asset.[30]

### [31] Spamouflage — case-study reprint

Provider evidence for generated harassment-related text and coding help within a much older network. Explicitly says AI was a **minority of output**; some website content was not generated with OpenAI models. Does not establish AI use throughout the entire campaign family or a decentralized controller. Overlaps the Graphika family-level cases.[31]

### [32] STOIC / Zero Zeno — case-study reprint

Provider attribution to a commercial campaign operator, with generated personas/articles/comments, recycled portraits, and self-engagement. Distinguish operator **STOIC** from campaign name **Zero Zeno**, and do not infer a commissioning state. Deleted social accounts limit historical engagement measurement; India activity's rapid disruption does not describe the entire operation's lifetime.[32]

### [33] OpenAI — Storm-2035 (August 16, 2024)

Provider investigation informed by published Microsoft reporting. Observed five websites, twelve X accounts, and one Instagram account; long-article and short-comment workstreams. Counts are public assets, not provider accounts or independent agents. Low observed circulation does not establish zero readership, and image non-attribution to OpenAI does not establish human origin.[33]

### [35] Graphika — Deepfake It Till You Make It (February 7, 2023)

Full public report PDF, used instead of the now-gated landing page. Links two Wolf News videos to commercial synthetic avatars using reverse-image search and catalog matching. Strong synthetic-video assessment, without disclosed generator logs or proof the scripts were LLM-written. The videos belong to Spamouflage; their observed sub-300-view reach is a time-bounded result.[35]

### [36] Graphika — The #Americans (September 3, 2024)

Full PDF investigating a Spamouflage voter-persona subset, with high-confidence Chinese state-linked attribution by Graphika. Combines inconsistent/recycled identities, reciprocal amplification, and historical relationships. A Harlan Report TikTok video reached 1.5 million views, but its AI provenance and causal influence are not established. Do not add overlapping personas/platform accounts into an invented full-network total.[36]

## C. Detection systems and empirical cautions

### [37] Pacheco et al. — Uncovering Coordinated Networks (ICWSM 2021; v2)

Full **2001.05658v2** paper. Account–feature bipartite projection, weighted similarity graphs, and five case studies. Supports latent coordination analysis but explicitly not intent, authenticity, or underlying control. Manual validation is recommended. Null-model/Monte Carlo significance testing is proposed future work in this paper, not one of its evaluated results.[37]

### [38] Nizzoli et al. — Coordinated Behavior in the 2019 UK General Election (ICWSM 2021; v2)

TF-IDF co-retweets, multiscale backbone, iterative community detection, and relative coordination index. Useful for rare-feature weighting and threshold sensitivity. A selected active-user population in one political event is not ground truth for hostile AI swarms; authentic/inauthentic coordination remains unresolved. Citation identifies **2008.08370v2**, as recorded by retrieved PDF metadata.[38]

### [39] SynchroTrap — Uncovering Large Groups of Active Malicious Accounts (CCS 2014)

Full production-system paper documenting Facebook/Instagram deployment and August 2013 evaluation. Strong historical evidence for scalable constrained-action coordination detection. Reported over-99% precision is sampled security-team review on privileged data; complete recall and present-day use of the exact implementation are not established. It predates LLM-assisted swarms.[39]

### [40] DeBot — Identifying Correlated Bots in Twitter (2016 companion)

Implemented activity-correlation detector with historical daily reports, not documented Twitter-internal deployment. Companion omits full algorithm details. The body contextualizes “94% botness” through sampled account-pair content similarity; it is not a universal bot-identity precision measure. A missing complete census prevents exact recall.[40]

### [41] Botometer-v4 — Ensembles of Specialized Classifiers (CIKM 2020; v2)

Full **2006.06867v2**, describing deployment and a maximum-rule ensemble. Useful for known/new bot-class generalization and why high benchmark AUC need not transfer. Current service/model/platform access was not checked. Preserve its methodological disagreement with the separate v3 validation study.[41]

### [42] Rauchfleisch and Kaiser — The false positive problem (PLOS ONE, 2020)

Selected Botometer-v3 validation datasets, thresholds, languages, and repeated measurements. Supports base-rate and cross-domain warnings. Its assumed 15% bot prevalence is a thought-experiment input, not a census; ground-truth choices are contested by Botometer authors. Not a universal verdict on every later version.[42]

### [44] Liang et al. — GPT detectors are biased against non-native English writers (Patterns, 2023)

Seven detectors evaluated on 91 TOEFL essays and 88 U.S. school essays. Concrete **61.3% average false-positive rate** for the TOEFL sample. Useful for subgroup harm and fluency-based enforcement caution, not representative bot-account accuracy or an estimate for every non-native speaker and later detector.[44]

### [45] OpenAI — New AI classifier (January 2023; July retirement update)

Official notice is definitive about withdrawal on **July 20, 2023**. Includes historical challenge-set TPR/FPR and short-text/non-English limitations. Useful status evidence; neither an available current tool nor proof that every other detector fails.[45]

### [48] Trokhymovych et al. — Adversarial Creation and Detection of AI-Generated Social Bot Content (June 5, 2026; v1)

Evaluated **2606.07219v1** preprint with context/persona-conditioned training and account-level averaging. Strong FOX8 ranking results are not calibrated field precision, campaign detection, or 98.9% accuracy. Historical self-revealing-bot selection, text-only scope, and baseline contamination are acknowledged. No verified production or peer-review claim; authors oppose automatic bans.[48]

### [49] OpenAI — Disrupting malicious uses of AI (live operational page)

Retrieved October 1, 2026. Current public description of automated detection, expert contextual review, investigation, and disruption. Useful deployment-practice anchor, but vendor self-report without a representative public confusion matrix or full internal architecture. A live index may change; use the preserved evidence copy for this review's reading.[49]

### [50] OpenAI — February 2025 threat update

Full provider report showing output-to-publication matching, semantic rewrite analysis, partner leads, and possible operator overlap. Stronger AI provenance than blind public-text inference. Raw service data are not independently reproduced here, output generation is not automatically deployment, and operator overlap does not prove universal common command.[50]

## D. Theory and cooperative provenance

### [43] Sadasivan et al. — Can AI-Generated Text be Reliably Detected? (v4, January 17, 2025)

Read **2303.11156v4**, with TMLR publication noted in metadata. Combines detector stress tests with distribution-overlap theory. The ceiling is conditional on human/AI distributions becoming closer; actual total variation is difficult to estimate. It does not invalidate logs, signatures, or all present content classifiers. Retrieval-based provenance also raises conversation-storage privacy risks.[43]

### [46] Kirchenbauer et al. — A Watermark for Large Language Models (ICML 2023)

Full PMLR paper, with implemented generation-time marking and statistical detection. Requires participating generation and compatible scheme/key/tokenizer; length and entropy constrain evidence. Tested robustness is not universal adversarial resistance. This paper itself is not a claim of industry-wide deployment, and a mark identifies generation provenance—not truth or a swarm.[46]

### [60] Dathathri et al. — Scalable watermarking / SynthID-Text (Nature, October 23, 2024)

Full accessible article body, including evaluation, limitations, and methods. Reports Gemini/Gemini Advanced production use and a roughly **20-million-response quality study**. This supplies real deployment evidence missing from a proposal-only account of watermarks. Requires participating generators; edits, low entropy, and attacks constrain detection. No present-endpoint test or independent rerun was performed.[60]

## E. Physical and digital swarm experiments

### [58], [59], and [56] Kilobot self-assembly (August 2014)

Science journal abstract/metadata **[58]**, full supplementary methods/results **[59]**, and Harvard hardware announcement **[56]**. The gated main paper was not obtained. The supplement supports four seeds, local coordination, trial counts/timings, camera/state measurements, and idealized-proof limits. Two trials started with 1,024 robots; final membership differences do not imply robot deaths. Institutional publicity is not independent replication.[58][59][56]

### [51] Zhou et al. — Swarm of micro flying robots in the wild (Science Robotics, May 4, 2022)

Author-hosted full paper describing onboard perception/planning/control and broadcast trajectories. Ten-drone forest/avoidance hardware, four-drone tracking, and a separate 40-drone software example. No disaster-response deployment claim. Unlabeled extracted plot values were not used as precise results; network assumptions and field conditions bound generalization.[51]

### [52] Perdix official demonstration announcement (January 9, 2017)

PACOM mirror of Defense press release **NR-008-17**. Reports 103 drones launched from three aircraft in October 2016, with leaderless/adaptive behavior described by the program director. No open telemetry or controller details are supplied. Not battlefield deployment; a prospective 1,000-unit production batch is not the tested population.[52]

### [53] Park et al. — Generative Agents (UIST 2023; arXiv v2)

Full **2304.03442v2**. Twenty-five agents, separate memory/reflection/planning, a centrally maintained sandbox, and seeded-event diffusion across two game days. Replays and memory checks are stronger evidence than believability alone. Constructed identities/goals, hallucinations, cost, and sequential infrastructure limit “autonomous society” readings.[53]

### [54] Ashery, Aiello, and Baronchelli — Emergent social conventions and collective bias (Science Advances, 2025)

University-hosted full journal PDF. Naming-game populations demonstrate locally incentivized convention formation, collective bias, and convention-dependent tipping. Default 24 agents/five-interaction memories differ from scaling and some tipping conditions. “Unbiased” means an initial statistical test did not detect a preference. Neither a universal tipping fraction nor an uncontrolled internet community is established; code/data were not rerun.[54]

## Preserved support and audit boundaries

[_support/source-records.json](_support/source-records.json) links cited IDs to publication metadata, read scope/limits, and preserved evidence files. [_support/citation-ledger.json](_support/citation-ledger.json) supplies the stable URL mapping and exact supporting excerpts. Evidence copies are saved locally for reproducible reading, not relicensed for redistribution.

Citation checks confirm ID/URL consistency and that attached excerpts occur in the saved body text. They do **not** automatically prove that every interpretation or sentence is correct. Numerical/context checks and explicit scope qualifications remain necessary. This research reads published investigations and papers; it does not independently reproduce private logs, rerun every experiment, or estimate present global swarm prevalence.

## Sources

[8] https://iridia.ulb.ac.be/~mdorigo/Published_papers/All_Dorigo_papers/DorBir2007sch-si.pdf — [PDF] Swarm Intelligence - Scholarpedia - IRIDIA
[22] https://arxiv.org/html/2501.06322v1 — Multi-Agent Collaboration Mechanisms: A Survey of LLMs
[23] https://arxiv.org/html/2506.06299v4 — How malicious AI swarms can threaten democracy — Schroeder et al.
[24] https://pespmc1.vub.ac.be/Papers/StigmergyICognSystems.pdf — Stigmergy as a universal coordination mechanism I: Definition and components — Heylighen
[26] https://aclanthology.org/2024.emnlp-main.1208.pdf — Is this the real life? Is this just fantasy? The Misleading Success of Simulating Social Interactions With LLMs — Zhou et al.
[27] https://arxiv.org/html/2503.13657v3 — Why Do Multi-Agent LLM Systems Fail? — Cemri et al.
[28] https://arxiv.org/pdf/2307.16336 — Anatomy of an AI-powered malicious social botnet
[29] https://openai.com/index/disrupting-malicious-uses-of-ai-bad-grammar — "Bad Grammar": Russian-linked Telegram comment activity
[30] https://openai.com/index/disrupting-malicious-uses-of-ai-doppelganger — Operation "Doppelganger": Russian influence activity targeting Ukraine
[31] https://openai.com/index/disrupting-malicious-uses-of-ai-spamouflage — Operation "Spamouflage": China-linked influence activity
[32] https://openai.com/index/disrupting-malicious-uses-of-ai-zero-zeno — Operation "Zero Zeno": Israel-linked influence activity
[33] https://openai.com/index/disrupting-a-covert-iranian-influence-operation — Disrupting a covert Iranian influence operation
[34] https://openai.com/index/disrupting-deceptive-uses-of-ai-by-covert-influence-operations — Disrupting deceptive uses of AI by covert influence operations
[35] https://public-assets.graphika.com/reports/graphika-report-deepfake-it-till-you-make-it.pdf — Deepfake It Till You Make It: Pro-Chinese Actors Promote AI-Generated Video Footage of Fictitious People in Online Influence Operation
[36] https://public-assets.graphika.com/reports/graphika-report-the-americans.pdf — The #Americans: Chinese State-Linked Influence Operation Spamouflage Masquerades as U.S. Voters to Push Divisive Online Narratives Ahead of 2024 Election
[37] https://arxiv.org/pdf/2001.05658v2 — Uncovering Coordinated Networks on Social Media: Methods and Case Studies
[38] https://arxiv.org/pdf/2008.08370v2 — Coordinated Behavior on Social Media in 2019 UK General Election
[39] https://users.cs.duke.edu/~xwy/publications/SynchroTrap-ccs14.pdf — Uncovering Large Groups of Active Malicious Accounts in Online Social Networks
[40] https://www.cs.unm.edu/~chavoshi/debot/SocInfo.pdf — Identifying Correlated Bots in Twitter
[41] https://arxiv.org/pdf/2006.06867v2 — Detection of Novel Social Bots by Ensembles of Specialized Classifiers
[42] https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0241045 — The false positive problem of automatic bot detection in social science research
[43] https://arxiv.org/pdf/2303.11156v4 — Can AI-Generated Text be Reliably Detected?
[44] https://pmc.ncbi.nlm.nih.gov/articles/PMC10382961 — GPT detectors are biased against non-native English writers
[45] https://openai.com/index/new-ai-classifier-for-indicating-ai-written-text — New AI classifier for indicating AI-written text
[46] https://proceedings.mlr.press/v202/kirchenbauer23a/kirchenbauer23a.pdf — A Watermark for Large Language Models
[47] https://journalqd.org/article/download/5848/4519/15711 — Anatomy of an AI-powered malicious social botnet
[48] https://arxiv.org/html/2606.07219v1 — Adversarial Creation and Detection of AI-Generated Social Bot Content
[49] https://openai.com/index/disrupting-malicious-uses-of-ai — Disrupting malicious uses of AI
[50] https://cdn.openai.com/threat-intelligence-reports/disrupting-malicious-uses-of-our-models-february-2025-update.pdf — Disrupting malicious uses of our models: an update February 2025
[51] https://zhepeiwang.github.io/pubs/sr_2022_swarm.pdf — Swarm of micro flying robots in the wild — Zhou et al., Science Robotics 7, eabm5954
[52] https://www.pacom.mil/Media/NEWS/Article/1046043/department-of-defense-announces-successful-micro-drone-demonstration — Department of Defense Announces Successful Micro-Drone Demonstration — Press Operations NR-008-17, official PACOM mirror
[53] https://arxiv.org/html/2304.03442v2 — Generative Agents: Interactive Simulacra of Human Behavior — Park et al., arXiv:2304.03442v2 / UIST 2023
[54] https://openaccess.city.ac.uk/id/eprint/35211/1/sciadv.adu9368.pdf — Emergent social conventions and collective bias in LLM populations — Ashery, Aiello and Baronchelli, Science Advances 11(20), eadu9368
[55] https://books.google.com/books/about/Swarm_Intelligence.html?id=fcTcHvSsRMYC — Swarm Intelligence: From Natural to Artificial Systems — Bonabeau, Dorigo and Theraulaz (Oxford University Press, 1999), Google Books page-7 excerpt
[56] https://seas.harvard.edu/news/self-organizing-thousand-robot-swarm — A self-organizing thousand-robot swarm — Harvard SEAS
[58] https://www.science.org/doi/10.1126/science.1254295 — Programmable self-assembly in a thousand-robot swarm — Rubenstein, Cornejo and Nagpal, Science 345(6198), 795–799
[59] https://www.science.org/doi/suppl/10.1126/science.1254295/suppl_file/rubenstein.sm.pdf — Supplementary Materials for Programmable self-assembly in a thousand-robot swarm — Rubenstein, Cornejo and Nagpal
[60] https://www.nature.com/articles/s41586-024-08025-4 — Scalable watermarking for identifying large language model outputs
