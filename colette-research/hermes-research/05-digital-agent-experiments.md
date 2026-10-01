# Digital agent experiments: Smallville and emergent conventions

Research date: 2026-10-01. Both cases are actual executed research experiments in constructed environments. Neither is an organically discovered online swarm, and neither demonstrates a conscious collective.

## Case D1 — Generative Agents / Smallville, 2023

### Setting, scale, and initialization

Park and colleagues' UIST paper, read as **arXiv 2304.03442v2**, instantiates **25 agents** in a Sims-like town and examines their interactions over **two game days**. Starting identities, memories, and the environment are researcher-specified.[53]

A mayoral candidacy and a Valentine's-party intention were placed in individual agents' initial memories. Their later diffusion is therefore an emergent propagation/coordination result around a seeded intention, not proof that a society or its initial goals spontaneously arose from blank agents.[53]

### Agent architecture and control layers

The implementation augments ChatGPT's `gpt3.5-turbo` with a memory stream, retrieval influenced by recency/relevance/importance, reflection, planning, and reaction to new observations.[53]

A **central sandbox server** maintains JSON world state, supplies observations within a configured visual range, and applies actions. The appendix describes sequential execution; parallelization is future work. Twenty-five agents thus do not imply 25 continuously running model processes or decentralized infrastructure.[53]

Separate memory and limited observations distinguish participants, while conversation and shared world changes couple their actions. **Classification: controlled social multi-agent simulation with centrally orchestrated infrastructure—not a textbook homogeneous simple-rule swarm.**[53]

### Measured collective behavior

Knowledge of the mayoral candidacy increased from **one to eight agents**; knowledge of the party increased from **one to thirteen**. The mutual-knowledge network's density rose from **0.167 to 0.74**.[53]

**Five of twelve invited agents attended** the party. That is actual, partial event coordination, not universal attendance. The researchers checked affirmative diffusion responses against memories of dialogue, strengthening the evidence beyond fluent self-reports.[53]

Nevertheless, six of 453 relationship-awareness responses were hallucinated. Internal descriptions and interview answers therefore require validation against traces.[53]

### How behavior was observed

The investigators used replay, agent interviews, memory inspection, relationship graphs, and actual event attendance. A separate individual-agent believability study involved 100 human evaluators and architecture ablations.[53]

Believability is not the same as empirical validity as a model of human society. The observable event outcomes provide a different and stronger coordination measure than merely asking whether agent dialogue sounds plausible.[53][26]

### Limitations

The authors report embellished memories, missed plans, improper location behavior, and excessive cooperativeness. The simulation required multiple days to run and thousands of dollars in token credits.[53]

The experiment does not establish indefinite persistence, robust real-world norm formation, uncontrolled internet autonomy, or human-equivalent social cognition. Shared world state also does not by itself establish a specifically stigmergic explanation; an action–trace–subsequent-action mechanism should be identified rather than assumed.[53][24]

**Case lesson:** differentiate the central world/scheduler from the individual decision contexts, and measure enacted coordination rather than only narrated intentions.

## Case D2 — Emergent social conventions and collective bias, 2025

### Setting and measured scales

Ashery, Aiello, and Baronchelli's Science Advances experiment uses a controlled **naming game**. Default conditions are **24 agents**, **ten candidate letter names**, and a memory of **five interactions**.[54]

Each homogeneous population uses one of four models: Llama-2-70b-Chat, Llama-3-70B-Instruct, Llama-3.1-70B-Instruct, or Claude-3.5-Sonnet. Robustness tests include populations up to **200 agents** and candidate sets up to **26 names**; these are not the default condition of every result.[54]

### Local incentives and programmed environment

An experimental scheduler randomly selects two agents for interaction. Each sees its own recent outcomes and selects a name; matching yields **+100 points**, while mismatch yields **−50**. Prompts encourage individual payoff, without telling an agent that it belongs to a population or rewarding group consensus directly.[54]

Local decision-making can therefore generate a global convention without a controller choosing its final name. However, pairing, available actions, payoffs, memory, and prompts are explicitly designed. **Classification: controlled LLM-population experiment demonstrating local-to-global convention emergence.**[54]

“Without explicit programming” should be read as absence of programming the particular final convention, not absence of an engineered experiment or agent incentives.[54]

### Observed emergence

Across models, local interaction produced population-wide conventions. Three of the four models established a shared convention by population round 15, while Llama-2 was slower; the primary convergence figure averages **40 runs per model**.[54]

Rounds are population-normalized interaction units, not a wall-clock emergence time. The outcome is a shared arbitrary naming convention, not a measured moral system, ideology, or human society.[54]

### Collective bias and tipping

In a two-name condition, initial individual tests did not detect a preference, yet collective histories could favor one convention. “Unbiased” here means insufficient statistical evidence of an initial option preference—not mathematical proof of equal probabilities and not absence of demographic prejudice.[54]

Introducing committed agents produced convention-dependent tipping. Reported thresholds range approximately from **2% to 67%**, with some weak initialized conventions switching without committed agents. One tipping configuration used 48 agents and shorter memory rather than the default 24-agent/five-memory configuration.[54]

There is therefore no universal “a 25% minority controls any AI swarm” result. Thresholds depend on model, convention, and experimental setup.[54]

### How coordination was detected

The researchers measured interaction success, naming distributions, population consensus across repeated runs, first-choice statistics for isolated agents, and responses to committed-agent interventions. Those population-level measurements reveal effects a singleton evaluation can miss.[54]

This is a useful model of how safety or bias can change through interaction: assessing one agent in isolation need not characterize the collective. It is not evidence that unknown social-media accounts exhibit the same mechanism.[54]

### Limitations

Letter choices, homogeneous populations, finite memories, and random-pair topology make the setting intentionally simple. Realistic network structures, richer social categories, and mixed human–AI populations are directions for later investigation, not established results of this experiment.[54]

No experiment or released code/data was independently rerun for this collection. The findings remain the authors' documented experimental evidence, with the described scope.

**Case lesson:** emergence is most persuasive when a concrete population-level quantity is measured across runs and distinguished from its individual-agent baseline.

## What transfers to online-swarm detection—and what does not?

The experiments supply **mechanistic plausibility** for persistent memory, information diffusion, local convention formation, and collective bias. They do not supply an operational detector for unauthorized public networks.[53][54]

A responsible transfer is methodological: look for separate state, actual interaction, repeated aggregate outcomes, and alternative explanations. An irresponsible transfer would be declaring a human community artificial because its members converge on phrases or social norms.

Zhou and colleagues' social-simulation critique reinforces the boundary: a single omniscient script generator can make interactions appear easier and more successful than separate agents operating under information asymmetry.[26]

Likewise, the MAST failure taxonomy shows that multi-agent orchestration has specification, information-flow, and verification failure modes. The existence of a successful experiment should not erase those engineering constraints.[27]

Read [definitions](01-definitions-and-characteristics.md), [detection proposals](07-detection-proposals-and-frontiers.md), and the [source guide](09-source-guide.md) for the larger interpretation.

## Sources

[24] https://pespmc1.vub.ac.be/Papers/StigmergyICognSystems.pdf — Stigmergy as a universal coordination mechanism I: Definition and components — Heylighen
[26] https://aclanthology.org/2024.emnlp-main.1208.pdf — Is this the real life? Is this just fantasy? The Misleading Success of Simulating Social Interactions With LLMs — Zhou et al.
[27] https://arxiv.org/html/2503.13657v3 — Why Do Multi-Agent LLM Systems Fail? — Cemri et al.
[53] https://arxiv.org/html/2304.03442v2 — Generative Agents: Interactive Simulacra of Human Behavior — Park et al., arXiv:2304.03442v2 / UIST 2023
[54] https://openaccess.city.ac.uk/id/eprint/35211/1/sciadv.adu9368.pdf — Emergent social conventions and collective bias in LLM populations — Ashery, Aiello and Baronchelli, Science Advances 11(20), eadu9368
