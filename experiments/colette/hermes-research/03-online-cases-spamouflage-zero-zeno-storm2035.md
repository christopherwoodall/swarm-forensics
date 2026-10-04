# Online cases II: Spamouflage, Zero Zeno, and Storm-2035

Research date: 2026-10-01. Published, retrospective case studies only. The Spamouflage reporting slices below describe **one campaign family**, not three additional swarms. Attribution language and confidence belong to the named source.

## Case O4 — Spamouflage: synthetic media inside a long-running network

### Family, attribution, and scope

Graphika has tracked Spamouflage since 2019. Its September 2024 report attributes the operation with **high confidence to Chinese state-linked actors**, drawing on open-source indicators and partner assessments. Aliases include Dragonbridge, Taizi Flood, and Empire Dragon.[36]

The larger family operates across more than 40 platforms, but the AI-related reports below examine narrower subsets and different periods. A family-level platform count does not measure the size of an AI-agent deployment.[36]

OpenAI's May 2024 account also reports external Meta/FBI attributions. This collection has not independently audited those underlying attribution documents or established each operator's command chain.[31]

### Slice A — Wolf News synthetic anchors, reported February 2023

Graphika documented **two unique videos**, observed in late 2022, distributed by Spamouflage assets on Facebook, Twitter, and YouTube. Synthetic male and female presenters appeared under a fictitious “Wolf News” brand.[35]

Reverse-image searches connected the apparent presenters to unrelated commercial videos; one explicitly described its presenter as an avatar. Graphika then matched the presenters to Synthesia's commercial avatar catalog, assessing the footage as **almost certainly** generated with that service.[35]

That is synthetic-video provenance, not evidence that the scripts were written by an LLM. The videos also incorporated stock imagery and news footage. Existing network history and fake-persona amplification establish their place in a coordinated operation.[35]

None of the identified videos exceeded **300 views** during the report's observation window. The report does not disclose provider generation logs or establish autonomous agents selecting and distributing the videos.[35]

**Interpretation:** commercial AI-generated media embedded in an established influence network. This is not an independently observed LLM swarm.

### Slice B — OpenAI-observed text, coding, and harassment, May 2024

OpenAI banned a small, unspecified number of service accounts linked to the operation. It observed generated text appearing on X, Medium, Blogspot, and ameblo.jp, research into critics, and code-debugging support for a website.[31]

In an illustrated April attack on dissident Cai Xia, a campaign post attracted a cluster of replying accounts; the ten illustrated replies all contained campaign-generated material, with no real-user replies observed in that example.[31]

OpenAI expressly assessed AI use as **a minority of overall output**. The doxxing-related website received AI coding assistance, but its content was not generated with OpenAI models. It would therefore be incorrect to label all that harassment AI-written.[31]

The investigated activity received a Category 2 assessment and little observed authentic traction. These findings concern the inspected slice, not the entire multi-year operation or all providers.[31]

### Slice C — U.S. voter personas, reported September 2024

Graphika identified **15 X accounts and one TikTok account**, plus the cross-platform media persona Harlan Report. The latter maintained TikTok/X assets and had previously removed Instagram/YouTube assets. These categories should not be added into a speculative total without deduplication.[36]

Evidence included inconsistent biographies, stock portraits, reciprocal amplification, known-network content links, persona renaming, old-post deletion, and recycled likely-AI avatars. Some material was assessed as almost certainly AI-generated; this is not a claim that every post or profile used AI.[36]

Most personas failed to gain significant authentic election-community traction. An important exception was a July Harlan Report TikTok video mocking Biden that had **1.5 million views** by the report date.[36]

The exception prevents a blanket conclusion that these networks never reach audiences. However, the report does **not** establish that this particular viral video was AI-generated, that views equal unique humans, or that political attitudes changed.[36]

### Mechanism, detection, and overall limits

Across these reports, detection used historical network continuity, artifact reuse, commercial-avatar matching, persona contradictions, cross-platform relationships, self-amplification, and provider output-to-publication links.[31][35][36]

The evidence substantiates a mixed-method AI-assisted coordinated influence family. It does not disclose decentralized action selection, persistent autonomous LLM identities, or inter-agent planning. **Classification: observed AI-assisted coordinated network; autonomous-swarm architecture unestablished.**[31][35][36]

Low engagement in one period and a later high-view video are not contradictory measurements: their time windows, asset sets, and content provenance differ. This collection counts the family once and preserves those differences.

**Case lesson:** media provenance, campaign membership, and impact must be tracked at artifact level; family attribution does not transfer every property to every post.

## Case O5 — STOIC / Zero Zeno: commercial astroturfing

### Setting, attribution, and scale

In its May 2024 report, OpenAI attributed an Israel-operated influence network to **STOIC, a political campaign-management firm**, calling the operation **Zero Zeno**. This names a reported operator, not a proven state commissioner.[32][34]

The operation used X, Facebook, Instagram, websites, and YouTube, targeting audiences in Canada, the United States, Israel, and later India. Ghana targeting was preparatory work, not a demonstrated completed campaign in this disclosure.[32]

The source describes a model-service account cluster and **four named campaign websites**, but does not give a complete total of public personas or deployed software agents.[32]

### AI use, coordination, and control

Models generated or edited articles and comments, fictional demographic personas and biographies, and research material. Published text matched provider-observed outputs.[32]

Fake accounts replied to their own network's posts, recycled apparently GAN-generated portraits, and sometimes used identical portraits while replying to the same post. Accounts switched country/topic campaigns, and replacement accounts appeared after platform removals.[32]

Those linked behaviors support organized astroturfing more strongly than an isolated synthetic portrait would. A commercial operator and topical workstreams suggest managed campaign activity, but the exact orchestration software is undisclosed. **Classification: AI-assisted coordinated influence operation, not demonstrated autonomous swarm.**[32]

### Detection, impact, and limitations

The published investigation combines provider/public-output matching, external reporting, image/persona reuse, and self-engagement. It does not provide the complete initial detection rules or an independently reproducible provider dataset.[32]

OpenAI reported little engagement outside the network and assigned Category 2. One Canada-focused YouTube channel had one video with no views as of April 25. It also warned that already-disabled Meta/X accounts made current engagement figures an incomplete historical picture.[32]

Indian-election activity was disrupted within **24 hours of beginning**, not evidence that the entire Zero Zeno operation lasted only a day. Neither the low-engagement examples nor the disruption supply a causal estimate of political influence.[32]

**Case lesson:** identify the operator claim, campaign name, and commissioner question separately. Distinct national personas need not represent independent decision-making agents.

## Case O6 — Storm-2035: two content workstreams and little observed breakout

### Setting, attribution, and measured assets

OpenAI disclosed disruption of Iranian-linked Storm-2035 on **2024-08-16**. It reported benefiting from Microsoft reporting published the prior week, rather than independently deriving every attribution clue from scratch.[33]

The observed assets were **five websites, a dozen X accounts, and one Instagram account**. These are different public-asset classes; the number of banned ChatGPT accounts was unspecified. No numerical attribution-confidence rating is provided in this source.[33]

### AI and coordination evidence

One workstream used ChatGPT for long-form articles published on sites posing as progressive and conservative news outlets. Another generated short English and Spanish comments for social media, sometimes by asking the model to rewrite existing users' comments.[33]

Topics included Gaza, U.S. electoral politics, Israel at the Olympics, and smaller sets concerning Venezuela, Latinx rights, and Scottish independence. Fashion and beauty posts were interspersed with political content, possibly to appear more authentic or build an audience.[33]

Provider observations connect outputs and accounts to a common operation. The two workstreams do not by themselves establish LLM agents deliberating with one another. The scheduler, unattended autonomy, and control topology remain unknown. **Classification: AI-assisted coordinated influence campaign.**[33]

### Detection, audience, and constraints

Published Microsoft reporting supplied a lead; the provider investigation connected generated material to public assets. Most inspected social posts received few or no likes, shares, or comments, and OpenAI found no indication that the web articles circulated meaningfully on social media.[33]

The operation was assessed at the **low end of Breakout Category 2**. This is an observed distribution/uptake assessment, not proof of zero web readers or zero possible harm.[33]

A DALL·E classifier identified the illustrated beauty-post images as not generated by OpenAI services. That does not prove human origin or exclude a different image generator.[33]

No measured unique-human readership, causal opinion change, or electoral outcome effect is provided.[33]

**Case lesson:** a grounded provider investigation can establish AI assistance while leaving public impact and agent architecture unresolved.

## What can be concluded across all six online families?

OpenAI's May overview states that its investigated operations mixed AI-generated material with traditional content; none used AI exclusively. Its provider-side view is strong evidence of service use, but partial evidence of downstream distribution.[34]

The observed cases support adoption of generative tools by coordinated operators. They do not estimate the prevalence of all AI-assisted influence, prove sophisticated hidden swarms absent, or validate the fully adaptive swarm model in a particular live community.[23][34]

The principal case-study coverage is **2023–2024**. Later sources inform the detection review, but this is not a comprehensive 2025–2026 incident census. IUVM appears in the May overview but is not an additional detailed case here.[34]

Read [operational detection](06-detection-current-and-evaluated.md) for the methods these cases support, and [proposals and frontiers](07-detection-proposals-and-frontiers.md) for capabilities still being evaluated or hypothesized. The [source guide](09-source-guide.md) distinguishes independent reports from overlapping reprints.

## Sources

[23] https://arxiv.org/html/2506.06299v4 — How malicious AI swarms can threaten democracy — Schroeder et al.
[31] https://openai.com/index/disrupting-malicious-uses-of-ai-spamouflage — Operation "Spamouflage": China-linked influence activity
[32] https://openai.com/index/disrupting-malicious-uses-of-ai-zero-zeno — Operation "Zero Zeno": Israel-linked influence activity
[33] https://openai.com/index/disrupting-a-covert-iranian-influence-operation — Disrupting a covert Iranian influence operation
[34] https://openai.com/index/disrupting-deceptive-uses-of-ai-by-covert-influence-operations — Disrupting deceptive uses of AI by covert influence operations
[35] https://public-assets.graphika.com/reports/graphika-report-deepfake-it-till-you-make-it.pdf — Deepfake It Till You Make It: Pro-Chinese Actors Promote AI-Generated Video Footage of Fictitious People in Online Influence Operation
[36] https://public-assets.graphika.com/reports/graphika-report-the-americans.pdf — The #Americans: Chinese State-Linked Influence Operation Spamouflage Masquerades as U.S. Voters to Push Divisive Online Narratives Ahead of 2024 Election
