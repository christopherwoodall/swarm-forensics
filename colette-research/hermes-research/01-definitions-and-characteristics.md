# AI swarms: definitions, characteristics, and category boundaries

Research date: 2026-10-01. Status: advisory literature synthesis, not a finding about any live community. Numbered citations resolve to the Sources section and the annotated source guide.

## The short definition

**Working definition for this research:** an AI swarm is a population of artificial agents whose interactions produce coordinated collective behavior. To deserve the stronger label **decentralized swarm intelligence**, that coordination must arise substantially from local agent–agent or agent–environment interactions, rather than from a controller specifying every individual's actions. This is a synthesis of the classical definition and contemporary multi-agent literature, not a universally agreed threshold.[8][22]

There is no magic minimum number of agents, and using an LLM is not a requirement of classical swarm intelligence. The foundational literature includes artificial ants, optimization particles, and robots using relatively simple behavioral rules.[8]

The phrase becomes slippery because robotics, optimization, agent frameworks, and information-operations researchers use it differently. This collection therefore labels the architecture and evidence instead of treating the word “swarm” as a factual conclusion.[8][22][23]

## Four meanings that should not be collapsed

| Usage | What actually makes the system collective? | What the label does not establish |
|---|---|---|
| Classical swarm intelligence | Local interaction and self-organization, typically without a central coordinator.[8] | LLM reasoning, consciousness, unrestricted autonomy, or hostility. |
| Swarm robotics | Physical robots implementing collective rules; specific demonstrations may have shared initialization or supervisory safety control.[8] | Operational deployment in uncontrolled conditions. |
| LLM multi-agent orchestration | Multiple model-backed agents connected through explicit communication, roles, shared state, and control flow; centralized, distributed, or peer-to-peer structures are possible.[22] | Emergence or decentralization merely because multiple agents exist. |
| Malicious online AI swarm | Persistent synthetic identities, coordinated goals, diverse content, feedback-driven adaptation, limited human supervision, and potential cross-platform operation in a recent policy definition.[23] | That a particular observed bot campaign possesses all those capabilities. |

A centrally managed content farm can be AI-assisted and highly coordinated without being a decentralized swarm. Conversely, a decentralized robot collective can be a genuine swarm without generative AI. Those two distinctions prevent most of the misleading comparisons in this subject.[8][23]

## A stricter contemporary online definition

Schroeder and colleagues define a malicious AI swarm through five properties: persistent identities and memory; coordination toward shared objectives while varying content and tone; real-time adaptation to engagement, platform cues, and people; minimal human oversight; and ability to operate across platforms.[23]

Their January 2026 Science Policy Forum also describes a hybrid architecture: local adaptation with periodic synchronization to a central node. This is important because “swarm” in that threat model does **not** imply pure decentralization.[23]

The paper is useful for specifying a possible capability bundle and defense agenda. It is not itself a forensic demonstration that a fully autonomous, cross-platform synthetic society is already operating in a particular community. Its projections must be kept separate from the documented incidents assessed in the case files.[23]

## Characteristics to describe independently

The following is an analyst's descriptive checklist, derived from the literature. It is not a validated classifier, and unknown fields should remain unknown.[8][22][23]

1. **Multiplicity and individuality.** Are there separate stateful agents, or only many output accounts controlled by one process? Count agents, accounts, posts, processes, and models separately.
2. **Coupling.** Do one participant's actions change another's decisions? Similar outputs alone can reflect common prompts, shared news, or duplicated input rather than interaction.
3. **Control topology.** Is action selection centralized, peer-to-peer, local-neighbor, hierarchical, or hybrid? Initial task assignment is different from continuous action-by-action control.
4. **Communication medium.** Are agents using direct messages, a shared memory store, a task board, public posts, environmental traces, or some combination?
5. **Autonomy.** Who chooses the next action, updates objectives, approves tool calls, and decides to stop? Autonomy is scoped, not binary.
6. **Memory and persistence.** Does identity survive beyond a single request? Does new experience actually update later decisions?
7. **Feedback and adaptation.** Is behavior changed by observations, or merely varied in advance? Scheduled diversity is not necessarily adaptive learning.
8. **Emergence.** Does the group-level pattern arise from interaction rather than being authored directly? Specify the measured pattern and its baseline.
9. **Heterogeneity and specialization.** Are agents identical, role-specialized, or powered by distinct models? Classical relatively homogeneous swarms and heterogeneous LLM teams need different descriptions.
10. **Resilience.** Can the collective keep functioning when agents or links fail? A claim of robustness requires a perturbation experiment, not just a large population.
11. **Observability.** Which state transitions and communications were actually recorded? An outsider seeing social-media posts has much less evidence than a researcher who owns the agent runtime.
12. **Disclosure, authorization, and goals.** Is automation declared? Is the system permitted to interact with its environment? Coordinated behavior is not automatically deceptive or malicious.

For online cases, the hard task is usually not noticing a large amount of similar speech; it is establishing identity deception, actual AI use, shared operation, and adaptive agent behavior separately. The online capability definition requires more than a content-generation clue.[23]

## Stigmergy: coordination without direct conversation

Heylighen defines stigmergy as indirect coordination in which an action leaves a trace in a medium that stimulates subsequent actions. The medium is not merely a place where output is stored: its changed state participates in later decisions.[24]

A minimal conceptual cycle is:

```text
agent action -> changed shared medium -> another agent observes the change
             -> subsequent action -> another trace
```

Pheromone trails are a familiar biological instance; the paper also discusses web-supported collaboration and Wikipedia. Stigmergy does not require simultaneous presence, mutual awareness, or a direct communications channel.[24]

**Application to software, as synthesis:** a repository, queue, artifact store, issue tracker, or conversation can become a stigmergic medium if agents use prior changes as cues for what to do next. Merely sharing a folder is not enough: the causal action–trace–action loop must exist.[24]

Two consequences matter for research:

- Not observing private inter-agent messages does not rule out coordination through public or shared artifacts. This follows from the definition of indirect coordination.[24]
- Observing a shared artifact does not prove artificial agents are involved: stigmergy also describes human collaboration and even single-agent action sequences. It is a coordination mechanism, not an AI fingerprint.[24]

## Emergence, intelligence, and agency are different claims

A formation, convention, division of labor, or shared narrative can be an emergent pattern without implying a conscious collective. In classical swarm intelligence, simple locally informed rules can produce sophisticated group behavior; individual agents need not understand the global pattern.[8]

Likewise, many model calls are not necessarily many agents. Contemporary collaboration taxonomies distinguish actors, goals, environments, channel structures, and strategies; the relevant unit is a stateful decision-making participant, not a billing event.[22]

For practical reporting, use concrete statements such as “the agents converged on a shared label” or “the robots assembled a prescribed shape,” not “the swarm developed a mind.” That wording describes an observation without importing an unmeasured mental property.

## Why more agents need not mean better performance

Cemri and colleagues' MAST work identifies 14 failure modes grouped into system design issues, inter-agent misalignment, and task verification. Its analyzed traces include problems such as repetition, information loss, ignored input, and premature or inadequate verification.[27]

This is evidence that collective systems require reliable coordination and stopping mechanisms—not a universal estimate of how often all swarms fail. The sampled frameworks, tasks, models, and annotation procedure bound the result.[27]

Social simulations need a further caution. Zhou and colleagues distinguish a single omniscient model scripting all interlocutors from agents interacting under information asymmetry. Their experiments find that apparent social success in the former does not straightforwardly transfer to the latter.[26]

Thus a convincing narrative about an agent society is weaker evidence than a logged multi-agent interaction with separate state, partial information, and independently measured outcomes.[26]

## Evidence vocabulary used in the case files

These categories are this collection's editorial framework, not a published standard:

- **Observed physical swarm:** actual hardware with documented collective behavior and a described control mechanism.
- **Controlled digital multi-agent experiment:** agents executed in a researcher-controlled environment; not an unsolicited real-world campaign.
- **Observed AI-assisted coordinated network:** a published investigation connects multiple inauthentic accounts or outlets and substantiates some use of AI; agent autonomy may remain unknown.
- **Projected malicious agent swarm:** a capability or threat model; not counted as a documented incident merely because it is technically plausible.
- **Insufficient / out of scope:** marketing language, a single deepfake, ordinary collective human activity, or a case without enough evidence for the relevant claim.

Read the [online case studies](02-online-cases-fox8-and-openai-may-2024.md), [physical demonstrations](04-physical-swarm-cases.md), and [digital experiments](05-digital-agent-experiments.md) with these categories in view. The [source guide](09-source-guide.md) explains which sources are measurements, disclosures, reviews, or proposals.

## Sources

[8] https://iridia.ulb.ac.be/~mdorigo/Published_papers/All_Dorigo_papers/DorBir2007sch-si.pdf — [PDF] Swarm Intelligence - Scholarpedia - IRIDIA
[22] https://arxiv.org/html/2501.06322v1 — Multi-Agent Collaboration Mechanisms: A Survey of LLMs
[23] https://arxiv.org/html/2506.06299v4 — How malicious AI swarms can threaten democracy — Schroeder et al.
[24] https://pespmc1.vub.ac.be/Papers/StigmergyICognSystems.pdf — Stigmergy as a universal coordination mechanism I: Definition and components — Heylighen
[26] https://aclanthology.org/2024.emnlp-main.1208.pdf — Is this the real life? Is this just fantasy? The Misleading Success of Simulating Social Interactions With LLMs — Zhou et al.
[27] https://arxiv.org/html/2503.13657v3 — Why Do Multi-Agent LLM Systems Fail? — Cemri et al.
