# Online cases I: FOX8, Bad Grammar, and Doppelganger

Research date: 2026-10-01. These are retrospective published investigations, not new network discoveries. The classifications below are this collection's analytical judgments. Attributions are attributed to the reporting organization, not independently adjudicated.

## What these cases establish

The three cases substantiate some combination of automated accounts, coordinated behavior, deceptive personas, and generative-AI assistance.[28][29][30]

They do **not** demonstrate the complete persistent, adaptive, minimally supervised swarm capability discussed in the recent online threat definition.[23]

Provider accounts, social accounts, posts, websites, and software agents are different units. In particular, a provider's cluster of customers does not disclose how many deployed autonomous agents those customers operated.[30]

## Case O1 — FOX8: rule-based bots with ChatGPT content

### Setting, dates, and scale

Yang and Menczer first posted the study on 2023-07-30; a journal version appeared on 2024-05-29. It investigates Twitter activity, rather than an agent laboratory simulation.[28][47]

The initial historical search covered 2022-10-01 through 2023-04-23 and returned **12,226 tweets from 9,112 accounts**. Filtering by links to three shared domains and manual validation yielded the named botnet of **1,140 accounts**; the larger search totals are not botnet membership.[28]

The collected recent timelines contained **1,205 self-revealing tweets**. This is a content-artifact count, not a count of models, operators, or agents. The investigators collected up to 200 recent tweets and network information per bot.[28]

### Evidence for AI involvement

Bots accidentally published model refusals, including language such as “as an AI language model,” sometimes identifying OpenAI. Combined with the account patterns, this is strong circumstantial evidence for ChatGPT-assisted generation, not a disclosure of provider logs or operator code.[28]

The authors cannot guarantee that every bot post was LLM-generated. The appropriated profile selfies were human photographs; their reuse is identity-deception evidence, not evidence of an image generator.[47]

### Evidence for coordination and control

The network showed dense mutual following, disproportionate within-network replies and retweets, similar distributions of tweet types, common promoted URLs, and crypto/blockchain themes. Shared website infrastructure supplied another relationship layer; the operator's identity remained unknown.[28]

The strongest architecture boundary is explicit:

> “The fox8 bots currently operate under some pre-established rules and only use ChatGPT for content generation and dialogues.”[28]

Bot-to-bot exchanges therefore do not establish decentralized planning, autonomous task allocation, or an emergent society. **Classification: observed AI-assisted coordinated botnet, with parts of its control mechanism inferred rather than inspected.**[28]

### Detection, results, and limitations

Discovery depended on refusal leakage followed by URL grouping, manual investigation, and network analysis. The study's Botometer test, at a score threshold of 2.5, achieved nearly zero recall for FOX8. This is a result for the historical detector and botnet, not every later Botometer version.[47]

An aggregated OpenAI text-detector score achieved **F1 = 0.84** on the balanced bot/human benchmark. At the selected threshold, it labeled **815 of 1,986** qualifying random accounts as bots, but inspection of the highest-scoring 250 found only a few suspicious accounts and could not definitively attribute their text to LLMs.[47]

That does not prove all 815 classifications were false. It demonstrates that a favorable balanced-benchmark result did not establish reliable field identification. Short formulaic human messages were one source of false positives.[28][47]

The study establishes fabricated engagement and promotion of suspicious websites, not measured belief change, malware infection, or unique-human audience size. Its refusal-based discovery also selects conspicuously imperfect bots and cannot represent all sophisticated AI-assisted operations.[28][47]

**Case lesson:** analyze the relationships among accounts and artifacts; do not treat either a refusal string or an AI-text score as a sufficient bot identity test.

## Case O2 — Bad Grammar: an AI-assisted Telegram comment pipeline

### Setting, dates, scale, and attribution

OpenAI disclosed this Russian-linked operation in its **May 30, 2024** report, covering disruptions during the preceding three months. It targeted discussion around Russia, Ukraine, Moldova, Baltic states, and the United States on Telegram.[29][34]

OpenAI described links to individuals from Russia, without supplying a formal numerical attribution confidence or establishing a state command chain in this case study. It observed **at least a dozen Telegram posting accounts**; a complete post count and number of banned model-service accounts are not provided.[29]

The currently accessible case-study reprint displays a May 1 date, while the overview announces the original report on May 30. This collection uses the original disclosure date and does not turn the reprint label into an asserted earlier discovery.[29][34]

### AI evidence and coordination mechanism

Provider observations describe a pipeline: operators used models to debug code apparently intended to automate Telegram posting, generated Russian and English comments in response to specified posts, and published matching content through multiple personas.[29]

Some English prompts specified contrasting demographic or political identities. Multiple purported people could give opposing comments to the same original post—fabricated plurality rather than evidence that independent agents spontaneously adopted opposing beliefs.[29]

The observed text-to-publication relationships and shared targeting substantiate an organized operation. However, the exact scheduler and degree of unattended execution are undisclosed. **Classification: AI-assisted coordinated influence campaign with apparent posting automation; no demonstrated decentralized swarm.**[29]

### Detection and actual outcome

The public case study connects generated outputs to repeatedly posting Telegram accounts and examines persona and channel activity. It does not disclose the complete initial detector, thresholds, or provider dataset.[29]

OpenAI found very few likes or replies to campaign comments; those comments were usually a minority of replies. It assigned **Breakout Category 1**, describing activity confined to one platform without significant external amplification.[29]

Low visible engagement does not prove zero readers or zero harm. It also does not establish a successful persuasion operation. The report supplies neither a unique-human exposure estimate nor causal evidence of changed political beliefs.[29]

**Case lesson:** the relevant evidence is the pipeline and persona linkage, not merely the grammatical quality of the comments.

## Case O3 — Doppelganger: AI support for distinct functional teams

### Setting, dates, scale, and attribution

OpenAI's May 2024 disclosure concerns the already documented Russia-origin Doppelganger influence operation and its activity targeting Europe and North America on **X, 9GAG, Facebook, and websites**.[30][34]

OpenAI banned **four clusters of model-service accounts** linked to people acting on behalf of the operation. These are four provider-side account groups—not four independent campaigns or a disclosed total of public social-media accounts.[30]

The investigation connected output to known operation assets. It does not disclose a complete operator hierarchy or a formal attribution confidence scale.[30]

### AI evidence and division of labor

The clusters performed different tasks: generating multilingual comments; translating Russian articles; producing or editing French articles; and converting German website material into Facebook posts. Matching generated material to published campaign output supplied provider-supported AI provenance.[30]

Traditional content, including copied memes and footage, also appeared. AI assistance for one workstream cannot be extrapolated to every artifact in the larger historical operation.[30][34]

Different functional teams are consistent with ordinary organizational specialization. Their existence does not establish that LLM agents autonomously discovered and allocated those roles.[30]

### Coordination evidence and control boundary

On 9GAG, three to five accounts regularly posted simple approving replies to campaign posts; they interacted only with campaign material and most shared creation dates. On X, short-lived accounts posted redirects to campaign websites; an intermediary service providing model access was also disabled.[30]

These are stronger indicators than shared ideology alone. They connect production and manufactured audience response, but leave the central-versus-federated control architecture unknown. **Classification: AI-assisted, organizationally coordinated influence operation; no demonstrated autonomous swarm.**[30]

### Reach, detection, and limitations

Typical 9GAG posts received **5–10 upvotes**, mainly from campaign accounts, and **15–200 downvotes**. Typical X posts reportedly showed approximately **1,000 shares with zero replies and zero likes**. The latter is an amplification anomaly, not evidence that a thousand people were persuaded.[30]

OpenAI assigned **Breakout Category 2 to the model-associated activity**, rather than grading all historical Doppelganger activity. Its detection evidence combines provider-output matching, known assets, creation patterns, and suspicious self-amplification.[30]

The report documents mistakes such as incorrect geographic targeting, but does not supply total unique reach or measured opinion effects. A service-account disruption is not proof that the operation ceased everywhere.[30]

**Case lesson:** functional teams, synthetic engagement, and AI-generated text can coexist without demonstrating decentralized agent intelligence.

## Cross-case comparison

| Case | AI evidence | Coordination evidence | Unresolved architecture / impact |
|---|---|---|---|
| FOX8 | Refusal leakage and manual validation.[28] | Shared domains, mutual following, internal replies/retweets.[28] | Operator code and causal audience effects unavailable. |
| Bad Grammar | Provider generation-to-publication links; coding assistance.[29] | Multi-persona, same-target commenting pipeline.[29] | Scheduler, unattended autonomy, and total reach unknown. |
| Doppelganger | Provider-linked task clusters and published outputs.[30] | Known assets, approving reply accounts, artificial amplification.[30] | Full operator topology and whole-campaign impact unknown. |

Continue with [Spamouflage, Zero Zeno, and Storm-2035](03-online-cases-spamouflage-zero-zeno-storm2035.md). Detection methodology is developed in [current and evaluated methods](06-detection-current-and-evaluated.md), with source qualifications in the [source guide](09-source-guide.md).

## Sources

[23] https://arxiv.org/html/2506.06299v4 — How malicious AI swarms can threaten democracy — Schroeder et al.
[28] https://arxiv.org/pdf/2307.16336 — Anatomy of an AI-powered malicious social botnet
[29] https://openai.com/index/disrupting-malicious-uses-of-ai-bad-grammar — "Bad Grammar": Russian-linked Telegram comment activity
[30] https://openai.com/index/disrupting-malicious-uses-of-ai-doppelganger — Operation "Doppelganger": Russian influence activity targeting Ukraine
[34] https://openai.com/index/disrupting-deceptive-uses-of-ai-by-covert-influence-operations — Disrupting deceptive uses of AI by covert influence operations
[47] https://journalqd.org/article/download/5848/4519/15711 — Anatomy of an AI-powered malicious social botnet
