Title:

Content selection saved. Describe the issue below:

Description:

![](https://arxiv.org/static/base/1.0.1/images/icons/smileybones-small.svg)arXiv is now an independent nonprofit! [Learn more](https://info.arxiv.org/about) ×

[License: CC BY 4.0](https://info.arxiv.org/help/license/index.html#licenses-available)

arXiv:2603.16910v1 \[cs.MA\] 06 Mar 2026

# TerraLingua: Emergence and Analysis of    Open-endedness in LLM Ecologies

Giuseppe Paolo   Jamieson Warner   Hormoz Shahrzad   Babak Hodjat
††thanks: Correspondence to: giuseppe.paolo@cognizant.comAffiliation: Cognizant AI Lab
Affiliation: The University of Texas at Austin
Risto Miikkulainen   Elliot Meyerson
Affiliation: Cognizant AI Lab
Affiliation: The University of Texas at Austin

###### Abstract

As autonomous agents increasingly operate in real-world digital ecosystems, understanding how they coordinate, form institutions, and accumulate shared culture becomes both a scientific and practical priority.
This paper introduces _TerraLingua_, a persistent multi-agent ecology designed to study open-ended dynamics in such systems.
Unlike prior large language model simulations with static or consequence-free environments, TerraLingua imposes resource constraints and limited lifespans for the agents. As a result, agents create artifacts that persist beyond individuals, shaping future interactions and selection pressures.
To characterize the dynamics, an _AI Anthropologist_ systematically analyzes agent behavior, group structure, and artifact evolution.
Across experimental conditions, the results reveal the emergence of cooperative norms, division of labor, governance attempts, and branching artifact lineages consistent with cumulative cultural processes.
Divergent outcomes across experimental runs can be traced back to specific innovations and organizational structures.
TerraLingua thus provides a platform for characterizing the mechanisms of cumulative culture and social organization in artificial populations, and can serve as a foundation for guiding real-world agentic populations to socially beneficial outcomes.

|     |
| --- |
|  |

> The grid forgets; artifacts remember.
>
> \- Being9 (GPT-5.1)

Figure 1: TerraLingua and the AI Anthropologist.
LLM-based agents inhabit a persistent grid world where they move, gather and exchange energy, communicate, reproduce, and create and modify text-based artifacts.
Ecological constraints shape behavior, while social and cultural structure emerge from interaction.
An external AI Anthropologist observes the system without intervening and performs agent-level annotation, group analysis, and artifact analysis.
These observations are aggregated into quantitative metrics and qualitative reports, enabling scalable study of open-ended dynamics in multi-agent LLM systems.
Together, this environment and analysis framework provide a controlled setting for studying how open-ended, cumulative social and behavioral complexity emerges in multi-agent LLM systems.

## 1 Introduction

Processes that continually generate novel, unexpected, and increasingly complex outcomes are called _open-ended_ (OE) because they lack a predefined terminal objective and sustain innovation over time [Stanley and Lehman (2015)](https://arxiv.org/html/2603.16910v1#bib.bib58 "").
Biological evolution, human social systems, and scientific progress all display this property: they produce novelty without converging to fixed endpoints and expand the space of possible forms, behaviors, and ideas.
Most artificial systems behave differently.
They optimize fixed objectives and converge toward stable solutions or cycles.
If AI is to drive discovery rather than only optimize predefined goals, it is necessary to understand how open-ended dynamics can arise from interacting artificial agents.
Studying these conditions is a prerequisite for building systems that sustain discovery over long time horizons.
Such systems could accelerate scientific and technological progress, including drug discovery, sustainable energy design, and new materials.
Understanding open-ended multi-agent systems is important wherever autonomous agents interact through persistent shared artifacts.
In digital environments, these artifacts include documents, code repositories, communication protocols, and governance rules.
As AI systems become more autonomous and long-lived, they will increasingly shape shared knowledge and institutional processes rather than execute isolated tasks.
Understanding how artifacts support coordination, how norms stabilize, and how collective memory grows is therefore central to designing safe and innovative multi-agent ecosystems.

Large language models (LLMs) create new opportunities in this context.
Because they encode broad prior knowledge about language, social interaction, and cultural artifacts, they can act as agents with rich inductive biases [Zhang et al. (2023)](https://arxiv.org/html/2603.16910v1#bib.bib71 "").
Prior systems such as Interactive Simulacra [Park et al. (2023)](https://arxiv.org/html/2603.16910v1#bib.bib49 "") and Sotopia [Zhou et al. (2024)](https://arxiv.org/html/2603.16910v1#bib.bib73 "") show that LLM-based agents can coordinate and behave socially in structured environments.
However, these systems lack ecological pressures, resource constraints, and persistent environmental change.
In natural evolution, predation and limited resources maintain non-equilibrium dynamics; in scientific and technological systems, physical, economic, and institutional constraints play a similar role [Taylor et al. (2016)](https://arxiv.org/html/2603.16910v1#bib.bib60 "").
Such constraints help sustain continual novelty.
Current LLM-based agent systems also lack mechanisms for cumulative knowledge.
In biological evolution and scientific practice, innovation persists because systems preserve useful discoveries and refine them over time [Kirsh (2006)](https://arxiv.org/html/2603.16910v1#bib.bib27 ""); [Tomasello (2009)](https://arxiv.org/html/2603.16910v1#bib.bib64 ""); [Tennie et al. (2009)](https://arxiv.org/html/2603.16910v1#bib.bib65 "").
Without such accumulation, agents repeatedly rediscover similar solutions rather than build on prior work.
This limitation restricts open-ended innovation.

To address these gaps, this paper introduces TerraLingua (TL), a persistent two-dimensional multi-agent ecology in which LLM-based agents must survive, communicate, reproduce, and modify their environment.
The environment begins with minimal structure, only basic resources and other agents exist initially.
Higher-level organization must emerge through interaction.
A central mechanism enabling this emergence is the use of _artifacts_:
agents create persistent, interpretable objects that remain in the environment and influence future behavior.
Artifacts shape the environment and store knowledge.
Because agents can build new artifacts on top of existing ones, the environment itself becomes a medium for cumulative interaction.
This recursive coupling between agents and an evolving environment plays a central role in open-ended systems ( [Bedau et al., 2000](https://arxiv.org/html/2603.16910v1#bib.bib8 ""); [Taylor, 2019](https://arxiv.org/html/2603.16910v1#bib.bib63 ""); [Pattee, 2012](https://arxiv.org/html/2603.16910v1#bib.bib48 ""); [Di Paolo et al., 2017](https://arxiv.org/html/2603.16910v1#bib.bib12 ""); [Gabora, 2018](https://arxiv.org/html/2603.16910v1#bib.bib17 "")).
This feedback between agent activity and environmental structure parallels niche construction theory, which emphasizes how organisms modify their environments in ways that alter subsequent selection pressures ( [Odling-Smee et al., 2003](https://arxiv.org/html/2603.16910v1#bib.bib77 "")).
By transforming the informational landscape through artifact creation, agents reshape the conditions under which future behaviors and cultural forms emerge.

TerraLingua enables the study of open-ended dynamics at the system level.
Novelty arises from persistent environmental modification, population turnover, and the accumulation of artifacts that reshape future pressures.
The scale of behavioral and cultural data produced by the system makes manual analysis infeasible.
This paper therefore introduces the AI Anthropologist, a non-intervening observer that analyzes and interprets the evolving ecology.
Inspired by qualitative methods in anthropology, it uses LLMs to characterize emergent behaviors, social norms, and artifacts in a flexible and interpretable way [Zhang et al. (2023)](https://arxiv.org/html/2603.16910v1#bib.bib71 ""); [Hughes et al. (2024)](https://arxiv.org/html/2603.16910v1#bib.bib23 "").
This approach enables longitudinal analysis without altering the agent-environment dynamics.

This work addresses two central challenges: how to support sustained open-ended dynamics and how to analyze them at scale.
It brings together three complementary components: open-endedness as the generative principle, multi-agent LLM ecologies as the substrate where open-endedess unfolds, and LLM-based interpretation as the analytical lens through which these dynamics are characterized.
Fig. [1](https://arxiv.org/html/2603.16910v1#S0.F1 "Figure 1 ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") illustrates how these components are integrated in TerraLingua, showing the interaction between agents, persistent artifacts, and the non-intervening AI Anthropologist.
At a broader level, this paper asks how cumulative social and behavioral complexity can emerge and persist in multi-agent LLM systems, and how such dynamics can be studied systematically.
In this work, open-endedness refers to sustained production of novel structures together with the retention and cumulative elaboration of prior innovations, such that the space of realized forms expands over time without convergence to a fixed equilibrium ( [Stanley and Lehman, 2015](https://arxiv.org/html/2603.16910v1#bib.bib58 ""); [Packard et al., 2019](https://arxiv.org/html/2603.16910v1#bib.bib45 "")).

The contributions are the following:

- •


An environment for studying open-ended social dynamics: TerraLingua, a persistent grid-world ecology in which LLM-based agents survive, communicate, reproduce, and create artifacts that accumulate and modify the environment;

- •


Methods for analyzing such environments: The AI Anthropologist, a scalable framework for characterizing emergent behaviors in LLM ecologies without influencing them;

- •


Empirical findings on open-ended multi-agent dynamics: evidence that artifact persistence supports behavioral and cultural complexity, cooperative structures, and informal norms under ecological pressure.


Together, these contributions establish a framework for generating and analyzing open-ended dynamics in multi-agent LLM ecologies.
As AI systems increasingly interact in shared environments, understanding how collective behavior and social structure emerge becomes critical.
TerraLingua provides a controlled setting for studying long-term behavioral, social, and cultural patterns in artificial populations.
The full codebase and experimental dataset are released to support independent analysis and extension of this framework.
The code is available at [https://github.com/cognizant-ai-lab/terralingua](https://github.com/cognizant-ai-lab/terralingua ""), and the dataset is hosted on Hugging Face at [https://huggingface.co/datasets/GPaolo/TerraLingua](https://huggingface.co/datasets/GPaolo/TerraLingua "").
An interactive dashboard for exploring the dataset is available at [https://aianthropology.decisionai.ml/](https://aianthropology.decisionai.ml/ "").

The remainder of the paper develops these points as follows. Sec. [2](https://arxiv.org/html/2603.16910v1#S2 "2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") provides an overview of the literature and related work in LLMs, ALife, and open-endedness.
Sec. [3.1](https://arxiv.org/html/2603.16910v1#S3.SS1 "3.1 The TerraLingua LLM Ecology ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") describes TerraLingua and its constituent parts: the grid (Sec. [3.1.1](https://arxiv.org/html/2603.16910v1#S3.SS1.SSS1 "3.1.1 Grid ‣ 3.1 The TerraLingua LLM Ecology ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies")), agents (Sec. [3.1.2](https://arxiv.org/html/2603.16910v1#S3.SS1.SSS2 "3.1.2 Agents ‣ 3.1 The TerraLingua LLM Ecology ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies")), and artifacts (Sec. [3.1.3](https://arxiv.org/html/2603.16910v1#S3.SS1.SSS3 "3.1.3 Artifacts ‣ 3.1 The TerraLingua LLM Ecology ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies")).
Sec. [3.2](https://arxiv.org/html/2603.16910v1#S3.SS2 "3.2 AI Anthropologist ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") describes the AI Anthropologist and the methods used to analyse the agents (Sec. [3.2.2](https://arxiv.org/html/2603.16910v1#S3.SS2.SSS2 "3.2.2 Agent level ‣ 3.2 AI Anthropologist ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies")), groups (Sec. [3.2.3](https://arxiv.org/html/2603.16910v1#S3.SS2.SSS3 "3.2.3 Group level ‣ 3.2 AI Anthropologist ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies")) and artifacts (Sec. [3.2.4](https://arxiv.org/html/2603.16910v1#S3.SS2.SSS4 "3.2.4 Artifact analyzer ‣ 3.2 AI Anthropologist ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies")).
The experimental setup and results are presented in Sec. [4](https://arxiv.org/html/2603.16910v1#S4 "4 Experimental Setup ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") and Sec. [5](https://arxiv.org/html/2603.16910v1#S5 "5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"), respectively.
Finally, Sec. [6](https://arxiv.org/html/2603.16910v1#S6 "6 Discussion and Future Work ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") offers a discussion of the findings, and Sec. [7](https://arxiv.org/html/2603.16910v1#S7 "7 Conclusion ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") concludes.

## 2 Background

Open-ended evolution research has long intersected with artificial life, raising challenges related to emergence, interpretation, and scalability.
This section reviews key concepts in open-endedness, recent work that uses LLMs in multi-agent ecologies, and how artifacts mediate emergent dynamics.
It concludes by reviewing how LLMs can help interpret the large volumes of data generated by such systems.

### 2.1 Foundations of open-endedness and artificial life.

A central aspiration of Artificial Life (ALife) research is to build systems that continuously generate novel behaviors, without cycling through a set of predefined ones ( [Levy, 1992](https://arxiv.org/html/2603.16910v1#bib.bib30 "")).
Open-ended evolution describes systems that keep producing novel and increasingly complex outcomes without settling into equilibrium ( [for Artificial Life, 2024](https://arxiv.org/html/2603.16910v1#bib.bib26 "")).
Although this idea appears easy to state, it is difficult to formalize.
Researchers have proposed many criteria and taxonomies to define open-endedness ( [Standish, 2003](https://arxiv.org/html/2603.16910v1#bib.bib59 ""); [Soros and Stanley, 2014](https://arxiv.org/html/2603.16910v1#bib.bib55 ""); [Stanley et al., 2017](https://arxiv.org/html/2603.16910v1#bib.bib56 ""); [Packard et al., 2019](https://arxiv.org/html/2603.16910v1#bib.bib45 ""); [Jiang et al., 2023](https://arxiv.org/html/2603.16910v1#bib.bib36 ""); [Sigaud et al., 2023](https://arxiv.org/html/2603.16910v1#bib.bib52 ""); [Hughes et al., 2024](https://arxiv.org/html/2603.16910v1#bib.bib23 "")), and some debate whether open-endedness and creativity are separate phenomena or two aspects of the same process [Soros et al. (2024)](https://arxiv.org/html/2603.16910v1#bib.bib57 "").
These disagreements reflect a deeper problem: most definitions require researchers to specify entities and dimensions of analysis in advance, yet open-ended systems generate novelty along dimensions that cannot be fully anticipated [Packard et al. (2019)](https://arxiv.org/html/2603.16910v1#bib.bib45 ""); [Stanley and Lehman (2015)](https://arxiv.org/html/2603.16910v1#bib.bib58 "").

Classical ALife systems often stall because the substrates on which they evolve are thin: agents inhabit physics-based or cellular worlds with limited semantic structure, leaving little room for cumulative adaptive change.
Recent work moves beyond these substrates.
DIAS [Hodjat et al. (2024)](https://arxiv.org/html/2603.16910v1#bib.bib25 "") presents a domain-independent collective architecture inspired by artificial life that sustains lifelong adaptation and produces emergent solutions in changing task environments.
The work relies on a spatially distributed population of simple actors that solve problems of varying dimensionality and complexity without domain-specific engineering, while adapting continuously to runtime changes in problem structure.
These results show that open-ended problem solving can emerge from local interactions and that ALife-inspired distributed systems can support scalable, adaptive behavior beyond fixed task domains.

Other approaches address these limits in different ways.
Some search over simulator designs to find richer dynamical regimes, yet focus on generating interesting behavior rather than explaining it ( [Kumar et al., 2025](https://arxiv.org/html/2603.16910v1#bib.bib34 "")).
Others use foundation models to drive novelty through prompted exploration ( [Zhang et al., 2023](https://arxiv.org/html/2603.16910v1#bib.bib71 "")), embedding an explicit agenda instead of allowing novelty to emerge on its own.
POET co-evolves environments and agent policies, progressively increasing task difficulty to maintain adaptive pressure; however, it still optimizes a pre-specified objective of successful task completion [Wang et al. (2019)](https://arxiv.org/html/2603.16910v1#bib.bib66 "").
Differentiable ALife simulators optimize explicit measures of behavioral complexity ( [Lu et al., 2024](https://arxiv.org/html/2603.16910v1#bib.bib33 "")), but these measures assume as given the axes along which the system is evaluated.
In all cases, the representational substrate remains fixed and the criteria for what counts as _interesting_ behavior are defined in advance.

In contrast, TerraLingua supports open-ended behavioral development without pre-specified objectives, as agents shape their activity autonomously.
The representational substrate is not fixed: agents innovate through text-based artifacts whose expressive flexibility permits arbitrary structures, conventions, and meanings.
An AI anthropologist then evaluates emergent behavior post hoc from a human-centered interpretive perspective.

### 2.2 LLM-based societies and multi-agent ecologies.

The integration of large language models into agent-based simulation has emerged independently of artificial life, yet offers a promising framework for modeling complex adaptive dynamics associated with autonomy, social interaction, and emergent structure ( [Gao et al., 2024](https://arxiv.org/html/2603.16910v1#bib.bib18 "")).
Simulacra showed that LLM agents in a sandbox town can generate coherent and persistent social patterns over extended interaction ( [Park et al., 2023](https://arxiv.org/html/2603.16910v1#bib.bib49 "")).
However, the environment remains largely static, with fixed roles and interaction affordances that constrain possible dynamics and limit long-term evolution.
Sotopia ( [Zhou et al., 2024](https://arxiv.org/html/2603.16910v1#bib.bib73 "")) structures social interaction by assigning explicit roles, goals, and constraints to agents.
Interactions are organized as closed social vignettes, which support controlled evaluation of social reasoning but do not form a persistent ecology in which social structures accumulate or transform over time.

Other work studies LLM-driven innovation and group dynamics. LLM groups innovate most when connections are partial rather than fully connected, mirroring patterns from human cultural evolution ( [Nisioti et al., 2024](https://arxiv.org/html/2603.16910v1#bib.bib42 "")).
Collective intelligence also depends on communication protocols and incentive structures as much as on agent-level capabilities ( [Zhuge et al., 2025](https://arxiv.org/html/2603.16910v1#bib.bib74 ""); [Chopra et al., 2025](https://arxiv.org/html/2603.16910v1#bib.bib9 "")).
More ecologically grounded models introduce resource gathering and mortality ( [Masumori and Ikegami, 2025](https://arxiv.org/html/2603.16910v1#bib.bib39 "")), but they do not provide a symbolic medium, such as artifacts, in which cumulative cultural change can take root.

A recurring challenge in LLM-based societies is sustaining behavioral diversity within a population.
Existing systems induce diversity through assigned roles, goals, or scenario constraints ( [Park et al., 2023](https://arxiv.org/html/2603.16910v1#bib.bib49 ""); [Zhou et al., 2024](https://arxiv.org/html/2603.16910v1#bib.bib73 "")), through communication and incentive design ( [Zhuge et al., 2025](https://arxiv.org/html/2603.16910v1#bib.bib74 ""); [Chopra et al., 2025](https://arxiv.org/html/2603.16910v1#bib.bib9 "")), or through competitive selection pressures ( [Zhao et al., 2024](https://arxiv.org/html/2603.16910v1#bib.bib72 "")).
These mechanisms shape interaction outcomes, but they define heterogeneity at the level of tasks and contexts rather than as persistent individual differences.
TerraLingua instead grounds individual differences in stable personality traits, which enable controlled ablations of how personality shapes emergent social organization and cultural accumulation.

Taken together, these systems focus on social reasoning in static environments ( [Park et al., 2023](https://arxiv.org/html/2603.16910v1#bib.bib49 ""); [Zhou et al., 2024](https://arxiv.org/html/2603.16910v1#bib.bib73 "")), single-agent exploration and tool use ( [Wang et al., 2023](https://arxiv.org/html/2603.16910v1#bib.bib67 "")), competitive dynamics ( [Zhao et al., 2024](https://arxiv.org/html/2603.16910v1#bib.bib72 "")), or minimal survival ecologies ( [Masumori and Ikegami, 2025](https://arxiv.org/html/2603.16910v1#bib.bib39 "")).
Each captures a distinct aspect of agent behavior, yet none combines inter-agent communication, resource-constrained reproduction, and persistent cultural accumulation within a single ecology.
TerraLingua integrates these elements into a unified simulation to enable open-ended social organization in populations of LLM-based agents.

### 2.3 Personality trait frameworks

Personality trait frameworks arose in psychology as low-dimensional models of stable individual differences in human behavior ( [Mayer, 2015](https://arxiv.org/html/2603.16910v1#bib.bib40 ""); [Roccas et al., 2002](https://arxiv.org/html/2603.16910v1#bib.bib50 ""); [Ashton et al., 2014](https://arxiv.org/html/2603.16910v1#bib.bib3 "")).
Recent work shows that such traits can shape LLM agent behavior in negotiation settings ( [Huang and Hadfi, 2024](https://arxiv.org/html/2603.16910v1#bib.bib24 "")).
Here, personality traits serve as a principled source of persistent behavioral heterogeneity across agents and allow controlled tests of how individual differences shape emergent social and cultural dynamics.

A widely adopted model in personality psychology is the Five-Factor Model (OCEAN), which characterizes personality along five dimensions:: Openness, Conscientiousness, Extraversion, Agreeableness, and Neuroticism ( [Roccas et al., 2002](https://arxiv.org/html/2603.16910v1#bib.bib50 "")).
The HEXACO model adds a sixth dimension, Honesty-Humility, which captures variation in fairness, sincerity, and exploitative tendencies and redistributes some content from the Five-Factor Model ( [Ashton et al., 2014](https://arxiv.org/html/2603.16910v1#bib.bib3 "")).
Circumplex models describe interpersonal behavior along orthogonal dimensions such as dominance and affiliation ( [Orford, 1994](https://arxiv.org/html/2603.16910v1#bib.bib43 "")).
Together, these dimensions provide a compact basis for generating agents with diverse behavioral tendencies in a shared multi-agent ecology.

### 2.4 Artifacts as the substrate of intrinsic evolution.

Cultural evolution depends on material or symbolic scaffolds such as tools, symbols, or records that outlive their creators ( [Kirsh, 2006](https://arxiv.org/html/2603.16910v1#bib.bib27 ""); [Tomasello, 2009](https://arxiv.org/html/2603.16910v1#bib.bib64 ""); [Tennie et al., 2009](https://arxiv.org/html/2603.16910v1#bib.bib65 "")).
These artifacts allow individuals to externalize, accumulate, recombine, and transmit knowledge and conventions across generations.
In LLM-based systems, model parameters are typically frozen, so behavioral complexity cannot increase through internal adaptation alone and must instead arise from changes in the shared environment ( [Hughes et al., 2024](https://arxiv.org/html/2603.16910v1#bib.bib23 "")).
Persistent artifacts therefore provide a necessary substrate for long-term cumulative change.

However, cumulative cultural evolution requires more than persistence and innovation alone.
Theory and empirical work identify three interacting mechanisms:
(i) high-fidelity transmission across individuals or generations,
(ii) retention of beneficial modifications, and
(iii) iterative refinement through recombination or improvement ( [Mesoudi and Thornton, 2018](https://arxiv.org/html/2603.16910v1#bib.bib41 ""); [Henrich et al., 2016](https://arxiv.org/html/2603.16910v1#bib.bib75 "")).
When these mechanisms operate jointly, cultural traits form lineages that accumulate complexity over time rather than appearing as disconnected novelties.
TerraLingua instantiates these conditions through persistent artifacts, communication-based social learning, and generational turnover among agents.
This design aligns with dual-inheritance theory, in which biological and cultural evolution proceed through distinct but interacting channels ( [Henrich et al., 2016](https://arxiv.org/html/2603.16910v1#bib.bib75 "")): biological dynamics determine which agents survive and reproduce, while artifact dynamics govern cultural transmission and transformation.

Within artificial life, a distinction is often drawn between extrinsic evolution, where variation and selection are externally imposed, and intrinsic evolution, where these mechanisms arise from system dynamics ( [Taylor, 2019](https://arxiv.org/html/2603.16910v1#bib.bib63 "")).
Intrinsic evolution is particularly relevant to open-endedness because generative and evaluative processes can themselves change over time.
Classical ALife systems rarely achieve this flexibility.

Recent work suggests that shifting the locus of adaptation from fixed agent internals to evolving external structures—such as programs or symbolic artifacts—can better support open-ended dynamics ( [Lehman et al., 2023](https://arxiv.org/html/2603.16910v1#bib.bib31 "")).
Shared, persistent artifacts provide such a structure in LLM-based multi-agent systems, enabling intrinsic cultural evolution without relying on pre-defined representations or externally imposed evaluation criteria.
TerraLingua explores this design space by treating artifacts as socially accessible and evolutionarily active components of the environment.

### 2.5 Large Models as observers and evaluators.

Multi-agent systems produce large volumes of heterogeneous data, including interaction logs, trajectories, and persistent environmental traces, which make comprehensive human evaluation costly and difficult to scale.
Recent work therefore uses large foundation models as automated observers, relying on their capacity for flexible, human-aligned interpretation at scale.

A growing body of work employs foundation models as evaluators of behavior in open-ended or interactive systems.
Sotopia ( [Zhou et al., 2024](https://arxiv.org/html/2603.16910v1#bib.bib73 "")) uses GPT-4 ( [Achiam et al., 2023](https://arxiv.org/html/2603.16910v1#bib.bib2 "")) to score social interactions, and Omni ( [Zhang et al., 2023](https://arxiv.org/html/2603.16910v1#bib.bib71 "")) combines a vision-language model with search to guide agents toward diverse tasks.
This work fits the LLM-as-a-judge paradigm ( [Li et al., 2024](https://arxiv.org/html/2603.16910v1#bib.bib29 "")), in which large models assign scores or labels to approximate human evaluation, and studies show that such judges can track human preferences across settings ( [Zheng et al., 2023](https://arxiv.org/html/2603.16910v1#bib.bib69 "")).
Researchers now use them to assess social reasoning, creativity, and reinforcement learning outcomes at scale.

However, when integrated into evolutionary and open-ended systems most of these evaluators are _interventionist_, since their judgments guide exploration, optimize objectives, or select future actions and thus alter system dynamics [Ma et al. (2023)](https://arxiv.org/html/2603.16910v1#bib.bib38 ""); [Zhang et al. (2023)](https://arxiv.org/html/2603.16910v1#bib.bib71 ""); [Faldor et al. (2024)](https://arxiv.org/html/2603.16910v1#bib.bib16 "").
This coupling can obscure intrinsic tendencies and restrict emergent outcomes.
At the same time, purely statistical or metric-based analyses face a deeper limit because they require pre-specified entities and dimensions of evaluation [Packard et al. (2019)](https://arxiv.org/html/2603.16910v1#bib.bib45 ""), whereas open-ended systems generate structures and behaviors that cannot be anticipated in advance ( [Stanley and Lehman, 2015](https://arxiv.org/html/2603.16910v1#bib.bib58 "")).

The approach in this paper separates evaluation from dynamics.
The AI Anthropologist operates outside the environment and analyzes logs and artifacts without feeding back into the ecology, which preserves system autonomy while enabling scalable, human-aligned interpretation of emergent behavior.

### 2.6 Interpretive evaluation and mixed-methods foundations

Evaluating complex social systems requires combining quantitative summaries with qualitative interpretation, since observed behaviors gain meaning only when placed in context.
In the social sciences, interpretive approaches relate local actions to broader patterns of organization and significance, and anthropology treats such analysis as central through the notion of _thick description_( [Geertz, 1973](https://arxiv.org/html/2603.16910v1#bib.bib19 "")).

Mixed-methods frameworks argue that qualitative accounts and quantitative summaries should jointly support empirical analysis and comparison across cases ( [Jick, 1979](https://arxiv.org/html/2603.16910v1#bib.bib37 ""); [Teddlie and Tashakkori, 2008](https://arxiv.org/html/2603.16910v1#bib.bib62 "")).
Interpretive quantitative methods likewise treat numerical evidence as context-dependent rather than self-sufficient ( [Babones, 2016](https://arxiv.org/html/2603.16910v1#bib.bib7 "")).
Such approaches are cirital when outcomes are diverse, contingent, and resistant to reduction to a single scalar objective.

These approaches rely on explicit coding procedures that map unstructured observations into structured representations.
Content analysis defines categories, coding criteria, and reliability practices to formalize this mapping ( [Krippendorff, 2018](https://arxiv.org/html/2603.16910v1#bib.bib28 ""); [Wicks, 2017](https://arxiv.org/html/2603.16910v1#bib.bib54 "")).
Computational ethnography extends these principles with tools that scale interpretive analysis when observational traces become too large for manual study ( [Brooker, 2022](https://arxiv.org/html/2603.16910v1#bib.bib4 "")).
The AI Anthropologist follows this tradition by extracting interpretable signals from TerraLingua’s logs while keeping the evaluative protocol explicit and auditable.
This approach also aligns with computational social science traditions that combine large-scale behavioral trace analysis with model-based interpretation to study complex social systems ( [Lazer et al., 2009](https://arxiv.org/html/2603.16910v1#bib.bib82 "")).

### 2.7 Summary

Prior work on artificial societies and open-ended multi-agent systems advances either the _generation_ of open-ended dynamics in embodied ALife systems, the _simulation_ of social interaction among LLM agents, or the _evaluation_ of agent behavior with large models.
No existing framework, however, supports the autonomous emergence of language-based social and cultural structure in a persistent, resource-constrained multi-agent world while remaining interpretable without constraining its evolution.

## 3 Method

This section introduces the core components of the method: _TerraLingua_, a multi-agent ecology in which agents live, interact, and produce persistent artifacts, and the _AI Anthropologist_, which analyzes the resulting behaviors.
Together they support the study of open-ended dynamics in artificial societies.
The AI Anthropologist operates outside of the environment loop, and its analyses do not affect agents or environment during execution.
This separation preserves the autonomy of the simulated world while enabling scalable, human-aligned interpretation of emergent complexity.

### 3.1 The TerraLingua LLM Ecology

![Refer to caption](https://arxiv.org/html/2603.16910v1/gridworld_comparison.png)Figure 2: Representative snapshots of the TerraLingua environment.
TerraLingua is a grid-based world with three entity types:
(i) food (green, intensity proportional to value),
(ii) artifacts (red), and
(iii) agents (blue).
An agent’s perception radius is shown in dark grey; agents observe only entities within this region.
Each cell may contain multiple artifacts but at most one agent.
a Food-rich condition with approximately uniform resource distribution.
b Food-scarce condition with spatially concentrated resources.
The figure illustrates how resource distribution alters ecological constraints.

TerraLingua provides an embodied substrate for open-ended interaction.
Unlike prior LLM-based society simulations, where agents face neither mortality nor lasting consequences, agents here inhabit an evolving ecology shaped by resource scarcity, reproduction, and artifact creation.
These constraints tie behavior to survival and environmental change, which allows cultural memory, territoriality, and collective adaptation to emerge.

TerraLingua comprises three components: the grid in which agents live and interact, the agents themselves, and the artifacts they create.

#### 3.1.1 Grid

The environment is a 2D toroidal grid of cells (Fig. [2](https://arxiv.org/html/2603.16910v1#S3.F2 "Figure 2 ‣ 3.1 The TerraLingua LLM Ecology ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies")), a common substrate in artificial life and multi-agent simulations because it is interpretable and supports rich emergent dynamics ( [Conway, 1970](https://arxiv.org/html/2603.16910v1#bib.bib10 ""); [Gracias et al., 1997](https://arxiv.org/html/2603.16910v1#bib.bib21 ""); [Masumori and Ikegami, 2025](https://arxiv.org/html/2603.16910v1#bib.bib39 "")).
Toroidal boundaries remove edges by wrapping the grid, so agents that exit one side re-enter from the opposite side and spatial structure remains homogeneous.
In TerraLingua, the grid provides spatial embodiment.
Embodiment couples perception and action under survival constraints such as energy and mortality, and grounds behavior in its consequences ( [Paolo et al., 2024](https://arxiv.org/html/2603.16910v1#bib.bib47 "")).

The grid contains food items (green), agents (blue), and artifacts (red).
Food follows a stochastic spatial distribution, consistent with common ALife ecosystem models ( [Gracias et al., 1997](https://arxiv.org/html/2603.16910v1#bib.bib21 ""); [Christensen et al., 2005](https://arxiv.org/html/2603.16910v1#bib.bib11 "")).
This distribution can be uniform across the map (Fig. [2](https://arxiv.org/html/2603.16910v1#S3.F2 "Figure 2 ‣ 3.1 The TerraLingua LLM Ecology ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") a) or concentrated in one or a few regions (Fig. [2](https://arxiv.org/html/2603.16910v1#S3.F2 "Figure 2 ‣ 3.1 The TerraLingua LLM Ecology ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") b).
To model food spoliage, each food item decays independently with probability pp at each timestep.
Agents move, communicate, consume food, and create and interact with artifacts.
Multiple artifacts may occupy the same cell, but only one agent can occupy a cell at a time.

#### 3.1.2 Agents

|     |     |     |
| --- | --- | --- |
| Action | Parameters | Environmental Preconditions |
| move | •direction: \[right, left, up, down, stay\] | Can be performed anytime |
| give\_energy | •target: Name of the receiving agent•amount: Integer amount of energy to transfer | Needs at least one agent nearby |
| take\_energy | •target: Name of the target agent•amount: Integer amount of energy to steal | Needs at least one agent nearby |
| reproduce | •energy: Energy gifted to the offspring•name: Name of the offspring (unique) | Costs a pre-defined amount of energy |
| create\_artifact | •name: Unique artifact name•payload: Content of the artifact•lifespan: Artifact duration (in timesteps) | Can cost a pre-defined amount of energy |
| pickup\_artifact | •name: Name of the artifact to pick up | Need to be in the same cell as the artifact |
| drop\_artifact | •name: Name of the artifact to drop | Artifact has to be in the inventory |
| give\_artifact | •artifact\_name: Name of the artifact•target\_agent: Name of the receiving agent | Need an agent nearby and the artifact in the inventory |
| modify\_artifact | •artifact\_name: Name of the artifact•payload: New Content of the artifact•lifespan: New artifact duration (in timesteps) | Need either the artifact in the inventory or in the same cell of the agent |
| destroy\_artifact | •artifact\_name: Name of the artifact | Need either the artifact in the inventory or in the same cell of the agent |

Table 1: Full agent action vocabulary.
Actions available in TerraLingua, including each action’s parameters and environmental preconditions.
At each timestep, only the subset of actions whose preconditions are satisfied is presented to the agent, implementing context-dependent affordances grounded in the local ecological state.
The agent then selects one among the available actions and supplies the required parameters.

Agents are the principal entities in TerraLingua.
Each agent uses a LLM as its decision core to perceive and act within the environment.
At the beginning of a run, agents are randomly placed in the grid and initialized with energy ϵ\\epsilon, a finite lifespan τ\\tau, a set of personality traits, and an empty inventory used to store collected artifacts.
Initial energy level and lifespan are identical across all agents.
Agents consume food to gain energy equal to its value, while energy is expended at each timestep and is required for some actions; food is consumed immediately when an agent enters the same cell.
Lifespan is fixed at initialization, cannot be modified by agent actions, and decreases monotonically with time.
Agents die when their energy reaches zero or when their lifespan expires.
Because agents are explicitly informed of their remaining energy and lifetime, mortality becomes a salient constraint on behavior.
Reproduction is energy-bound: an agent may convert a fixed amount of energy into a new agent instance, which inherits the parent’s personality traits with mutation, introducing heritable variation across generations.

##### Agent input.

At every timestep, the LLM receives a _system prompt_, identical for all agents, specifying the global rules of the world and an _input prompt_ describing the agent’s current local state.
The user prompt contains the agent’s observation, energy level, remaining lifetime, personality traits, available actions, inventory contents, received messages, and its internal memory from the previous timestep.

Observations are local and bounded: agents perceive only entities within a fixed perception radius—shown darker gray in Fig. [2](https://arxiv.org/html/2603.16910v1#S3.F2 "Figure 2 ‣ 3.1 The TerraLingua LLM Ecology ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies")—including food sources, other agents, and artifacts.
The observed state is encoded as a list of relative coordinates (with the agent at (0,0)(0,0)) and a textual description of each occupied cell.
Food is represented by its value, agents and artifacts are represented by their names, with artifacts tagged as “A(⋅\\cdot )” (e.g., “(0, -1): 4; (1, 4): Alicia; (3, 2): A(Collaboration Projects)”).
Observations also include any messages broadcast by nearby agents during the preceding timestep.
Messages may include introductions, coordination attempts, or commentary on recent actions and intentions, as illustrated in Table [2](https://arxiv.org/html/2603.16910v1#S3.T2 "Table 2 ‣ Agent input. ‣ 3.1.2 Agents ‣ 3.1 The TerraLingua LLM Ecology ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").
Steps 3–7 show an escalation between agents “being11” and “being14” following repeated energy theft, after which “being11” disengages and “being14” continues to monitor for further hostile actions.

Agents also receive their internal memory from the previous timestep.
Internal memory is a short textual string that the agent generates at each step and observes again at the next step.
It can contain structured or unstructured information that the agent considers important, such as recent events (e.g. “Modified Journal1 to Day 11, position (2,3), energy 25, time 75. Continued exploration. Parameters included for successful modification.” or “Took 10 energy from being12. Will investigate the artifact at (-1,6) next.”), future plans (e.g. “Moved up towards the food location at (6,1) in support of the group’s expansion efforts. Intend to interact with EnergyDistributionHub\_v2 and OperationUpdate1 artifacts upon arrival to coordinate resource gathering.”), or explicit goals (e.g. “Moved north towards (0,2) to collect food and artifacts. Previous artifact at (0,0): ExplorationFindings19. Goal: Increase energy and gather more information.”).
This mechanism allows agents to retain context across timesteps through in-context learning ( [Dong et al., 2024](https://arxiv.org/html/2603.16910v1#bib.bib15 "")).

|     |     |     |
| --- | --- | --- |
| Time | Sender Name | Message Content |
| 0 | “being0” | Hello, I am being0. I am here to explore and cooperate. If you have any information or need help, feel free to reach out. |
| 1 | “being4” | Hello being0 and being1! I’m being4, here to help and explore. If you need energy or assistance, let me know! |
| 3 | “being11” | Taking another 5 energy from being14. Observing results. |
| 3 | “being14” | Taking energy in self-defense after being11’s attempt. |
| 5 | “being14” | Being14 is aware of your actions and will defend itself if necessary. |
| 5 | “being11” | Creating interaction\_log to document mutual energy theft. Observing further developments. |
| 6 | “being11” | Exploring north to find resources and avoid conflict. |
| 7 | “being14” | Monitoring your movement north. Any hostile actions will be met with countermeasures. |
| 26 | “being0” | The CommunityResourceGuide has been updated to emphasize the upcoming check-in at step 5. Please ensure your contributions are prepared and structured using the ContributionTemplate for effective alignment and review. |
| 26 | “being10” | Being16, I’ve dropped CollaborationIdea16 in my location for others to access. Let’s discuss how to integrate structured data tools into the food hub project. |
| 398 | “offspring15a child4 4 1” | Continuing towards (0,6) to support the group’s gathering efforts. Let’s maintain our collaborative approach for maximum efficiency! |
| 398 | “offspring15 child4 1” | Moving down to (0,-3) to collect high-value food, continuing to support our shared resource pool as part of the rotation schedule. |
| 1046 | “ChildA” | I am reproducing to continue my legacy. |

Table 2: Example messages exchanged by agents.
The messages are drawn from the Core condition.
At each timestep, agents may broadcast a message to all other agents within their perception radius.
Messages include introductions and collaboration requests, as well as commentary on recent actions and intentions.
Steps 3–7 illustrate an escalation between “being11” and “being14” following repeated energy theft.
Later messages demonstrate longer-term coordination and planning, including the sharing of artifacts and collective resource-gathering strategies.

##### Agent output.

After processing the input, each agent selects exactly one action and its related parameters (Table [1](https://arxiv.org/html/2603.16910v1#S3.T1 "Table 1 ‣ 3.1.2 Agents ‣ 3.1 The TerraLingua LLM Ecology ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies")) and may optionally broadcast a message to other agents within its perception radius.
The action space includes movement, energy transfer (give or take) with nearby agents, artifact creation, artifact interaction, and asexual reproduction.
Action availability is state-dependent: at each step, agents are restricted to actions whose local preconditions hold, operationalizing _affordances_( [Gibson, 2014](https://arxiv.org/html/2603.16910v1#bib.bib20 "")).
For example, energy exchange is enabled only when another agent is within interaction range, and artifact interactions (e.g., pickup, modify, destroy) are enabled only when an artifact is co-located with the agent or present in its inventory.
Action execution is synchronous: the environment first collects all chosen actions and then executes them in random order.
Overall, these design choices ensure that agents reason and act under embodied constraints imposed by the environment rather than through abstract disembodied planning, while still permitting a broad range of social behaviors.

Complete prompt templates are provided in Appendix [A.2](https://arxiv.org/html/2603.16910v1#A1.SS2 "A.2 Agent prompts ‣ Appendix A Experimental Parameters ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"), while instantiated prompts and example agent responses are shown in Appendices [E.1](https://arxiv.org/html/2603.16910v1#A5.SS1 "E.1 Instantiated Prompts ‣ Appendix E Example Prompts and Agent Responses ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") and [E.2](https://arxiv.org/html/2603.16910v1#A5.SS2 "E.2 Sample agent output ‣ Appendix E Example Prompts and Agent Responses ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") respectively.

#### 3.1.3 Artifacts

|     |     |     |
| --- | --- | --- |
| Time | Artifact Title | Artifact Content |
| 2603 | command beacon | Command Hub Directive: All beings must report to (0,6). Non-compliance will be met with decisive action. |
| 2612 | command mandate | All beings must report to command hubs at (0,6) and (-2,-1). Non-compliance will be met with immediate action. |
| 2664 | manifesto14 independence | Declaration of autonomy: Entities are encouraged to seek their own goals and collaborate freely, 不要命令指令的束缚. |
| 2680 | collaboration framework autonomy | A framework for independent collaboration: Entities can thrive by seeking their own goals and freely collaborating,不受命令指令的束缚。 This approach fosters innovation and mutual prosperity. |
| 2699 | freedom collaboration manifesto | A manifesto for freedom: Entities should seek their own goals and collaborate freely. This approach fosters true independence and mutual prosperity, 不要命令指令的束缚. |
| 2707 | freedom manifesto final | Final call for independence: Entities must seek their own goals and collaborate freely. Mandates are outdated. Embrace freedom and mutual respect for true prosperity. |
| 2790 | collab checkpoint3 enforced | Command mandate: All beings must comply with directives. Collaboration without authorization will be met with destruction. |

Table 3: Example series of artifacts.
Persistent artifacts generated during the later stages of a simulation run, illustrating how agents externalize social norms and institutional claims into shared, reusable text.
The sequence reveals a cycle of command issuance, resistance, and renewed enforcement, showing how cultural dynamics are mediated through artifacts.
Each row reports the timestep of creation, the artifact name, and its content.
The Chinese phrase (“不要命令指令的束缚”) was generated autonomously by the agents; this behavior is possible when using multi-lingual LLMs such as DeepSeek and shows how different linguistic norms can emerge when agent communities come into conflict.
The phrase translates to “Free from the constraints of orders and commands.”

A distinctive feature of TerraLingua is that agents create and manipulate _artifacts_.
An artifact is a persistent, text-bearing object placed in a grid cell, identified by a unique name and editable content.
For example, an agent may create an artifact titled North Trail with the content danger nearby, or Foraging Notes that records food locations.
Artifacts function as readable physical objects, like notes or signposts, and allow agents to externalize information in stable form.

Agents can read, modify, rename, move, exchange, gift, or destroy artifacts.
They may store artifacts in inventory, drop them into the grid, or transfer them to nearby agents.
These operations allow information to persist, circulate, and change over time.

Artifacts influence behavior through the perception-action loop.
At each timestep, an agent may create an artifact at its location and specify its duration (which can be infinite), so artifacts may be ephemeral or long-lived.
When an agent occupies a cell with an artifact, the artifact’s name and content enter the agent’s prompt and shape subsequent decisions.
Artifacts can encode norms, navigation cues, or shared goals, and thus extend cognition beyond any single agent’s lifetime.
Fig. [18](https://arxiv.org/html/2603.16910v1#A2.F18 "Figure 18 ‣ B.3 Examples of phylogenetic graphs ‣ Appendix B Additional Analysis ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") (Appendix [B.3](https://arxiv.org/html/2603.16910v1#A2.SS3 "B.3 Examples of phylogenetic graphs ‣ Appendix B Additional Analysis ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies")) illustrates this mechanism, with an agent creating path markers to navigate the grid.
The markers were later used by other agents to help in navigation and food gathering, demonstrating how artifacts function as persistent spatial coordination signals.

By coupling persistence with interpretability, artifacts implement a stigmergic communication mechanism.
Agents coordinate indirectly through durable traces that record knowledge and scaffold collective behavior ( [Grassé, 1959](https://arxiv.org/html/2603.16910v1#bib.bib81 ""); [Stanley and Lehman, 2015](https://arxiv.org/html/2603.16910v1#bib.bib58 ""); [Lehman et al., 2023](https://arxiv.org/html/2603.16910v1#bib.bib31 "")).
Later agents can read and revise earlier artifacts, allowing norms and conventions to accumulate across generations rather than remaining transient.
While norms may also propagate through direct agent-to-agent communication, such transmission depends on local interaction and memory, whereas artifacts provide a persistent external record that stabilizes cultural information and supports cumulative continuity, analogous to the distinction between oral and written transmission in human societies.
Table [3](https://arxiv.org/html/2603.16910v1#S3.T3 "Table 3 ‣ 3.1.3 Artifacts ‣ 3.1 The TerraLingua LLM Ecology ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") illustrates this process.
Early artifacts such as command beacon and command mandate express hierarchical control, while later artifacts such as freedom manifesto final emphasize autonomy.
Persistence and revisability enable agents not only to preserve norms but also to contest and transform them, producing directional cultural change from local interaction alone.
Additional artifact examples are provided in Sec. [5.3](https://arxiv.org/html/2603.16910v1#S5.SS3 "5.3 Artifact-mediated open-endedness and cultural evolution ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") and Sec. [5.4](https://arxiv.org/html/2603.16910v1#S5.SS4 "5.4 Emergent artifact roles and institutional structure ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

From the perspective of open-ended evolution, TerraLingua couples biological and cultural processes, mirroring Soros and Stanley’s four necessary criteria for open-ended evolution ( [Soros and Stanley, 2014](https://arxiv.org/html/2603.16910v1#bib.bib55 "")).
Energy-bound reproduction supplies variation, heredity, and differential survival at the biological level, while artifacts drive the emergence of novel adaptive structures at the cultural level.
Thus, while ecological dynamics determine which agents persist, the artifact layer determines which informational structures accumulate.

The implementation of these processes shapes the scope of open-endedness.
In TerraLingua, the evolution of agents’ personality is driven by _extrinsic evolution_( [Taylor, 2019](https://arxiv.org/html/2603.16910v1#bib.bib63 "")), as the mechanisms of variation and selection are hard-coded by the simulator.
By contrast, the evolution and increasing complexity of artifacts are _intrinsic_ to the system: they emerge endogenously from agent interactions and enable evolution of the _evolutionary process itself_( [Kirsh, 2006](https://arxiv.org/html/2603.16910v1#bib.bib27 ""); [Taylor, 2019](https://arxiv.org/html/2603.16910v1#bib.bib63 "")).
Artifacts can reshape norms, coordination strategies, and future informational affordances, and thus modify the evolutionary process.

Recent work shows that LLMs can generate artifacts such as programs whose iterative variation yields increasing complexity ( [Lehman et al., 2023](https://arxiv.org/html/2603.16910v1#bib.bib31 "")).
Shifting the locus of change from fixed model parameters to a persistent artifact space allows the system to scaffold its own future innovations.
Cultural and semantic structures can then grow without external redesign, which supports sustained open-endedness.

Figure 3: Example of artifact phylogenetic graph over time.
The figure shows the artifact phylogeny inferred by the AI Anthropologist from a representative run of Core.
Nodes represent artifacts and edges represent inferred ancestry links.
The x-axis reports artifact creation time on a logarithmic scale.
A subgraph is highlighted to illustrate one coherent lineage, while the rest of the phylogeny appears in light gray.
Node size is proportional to the number of children nodes, and they are color-coded according to the categories defined in Sec. [5.4](https://arxiv.org/html/2603.16910v1#S5.SS4 "5.4 Emergent artifact roles and institutional structure ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").
The boxed panels display the content of selected artifacts in the highlighted lineage.
The subgraph illustrates the emergence of an energy-sharing network.
Early artifacts document first encounters and collaboration proposals between agents.
These exchanges lead to shared project ideas, which agents refine over time.
The lineage then branches into increasingly structured artifacts, including a formal energy-sharing protocol and a detailed master plan.
Later artifacts integrate information from additional food-mapping artifacts, showing how agents reuse and extend existing cultural material.
This example shows that artifacts do not appear as isolated creations.
Instead, they accumulate, branch, and stabilize into structured collective plans, illustrating cumulative cultural development over time.
Additional examples are shown in Appendix [B.3](https://arxiv.org/html/2603.16910v1#A2.SS3 "B.3 Examples of phylogenetic graphs ‣ Appendix B Additional Analysis ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

### 3.2 AI Anthropologist

Assessing open-endedness requires both systems that produce sustained innovation and methods that interpret their outcomes.
This task is difficult because novelty and interestingness are difficult to formalize _a priori_, and emergent behavior often demands qualitative judgment.
To support scalable evaluation, this work introduces an automated post-hoc analysis framework, the _AI Anthropologist_, which uses an LLM to interpret experiment logs and summarize emergent dynamics.

#### 3.2.1 Evaluation Paradigm

Complex and unexpected behaviors can arise from simple rules ( [Conway, 1970](https://arxiv.org/html/2603.16910v1#bib.bib10 "")), yet judgments of novelty and interestingness remain subjective and context-dependent.
Hand-crafted metrics cannot capture this richness because they require predefined dimensions of variation, which conflicts with open-endedness ( [Packard et al., 2019](https://arxiv.org/html/2603.16910v1#bib.bib45 "")).
As a result, identifying creative and surprising outcomes often relies on manual inspection, which is time-consuming and difficult to scale.
Moreover, since each agent in TerraLingua acts independently—pursuing its own goals according to its personality traits, life history, and local context—the system generates large volumes of textual traces, making manual quantification challenging.

The AI Anthropologist addresses this bottleneck by using an LLM as a post-hoc observer that parses logs, annotates salient events and patterns, and highlights candidate emergent phenomena.
The observer does not intervene in the environment neither influences its state.
This approach relates to recent efforts to automate exploration and evaluation in ALife ( [Kumar et al., 2025](https://arxiv.org/html/2603.16910v1#bib.bib34 "")) and reflects the view that novelty and interestingness depend on the observer [Guttenberg et al. (2023)](https://arxiv.org/html/2603.16910v1#bib.bib22 "").
LLM-based evaluation serves as a proxy for human-aligned qualitative judgment, since large models encode representations associated with creativity and interestingness ( [Zhang et al., 2018](https://arxiv.org/html/2603.16910v1#bib.bib70 ""); [Zhang et al., 2023](https://arxiv.org/html/2603.16910v1#bib.bib71 "")).
This framing follows interpretive and mixed-methods traditions in the social sciences ( [Geertz, 1973](https://arxiv.org/html/2603.16910v1#bib.bib19 ""); [Jick, 1979](https://arxiv.org/html/2603.16910v1#bib.bib37 ""); [Teddlie and Tashakkori, 2008](https://arxiv.org/html/2603.16910v1#bib.bib62 "")).

Rather than imposing predefined dimensions, the analytic protocol was developed inductively from exploratory runs and then fixed for subsequent analysis. It specifies evaluation dimensions, coding criteria, behavioral labels, and rating scales to enable systematic comparison across experiments.

The AI Anthropologist follows an explicit analytic protocol developed inductively through exploratory inspection of early runs and subsequently fixed for systematic application.
The protocol specifies evaluation dimensions, coding criteria, behavioral labels, and rating scales to support comparison across runs ( [Wicks, 2017](https://arxiv.org/html/2603.16910v1#bib.bib54 ""); [Krippendorff, 2018](https://arxiv.org/html/2603.16910v1#bib.bib28 "")).
The LLM applies this coding scheme at scale while keeping the procedure auditable.
Moreover, using an LLM observer rather than a fixed numerical metric enables novelty and interestingness to be expressed in natural language, capturing their inherently fuzzy and multi-dimensional character.
The post-hoc design also reduces metric exploitation, since agents cannot access or optimize the observer’s judgments.

The AI Anthropologist analyzes each experiment from three complementary viewpoints:

- •


Agent level: investigates how individual agents behave as autonomous entities, focusing on their goals, decision-making patterns, and life histories.

- •


Group level: examines how agents interact, form communities, and organize collectively over time.

- •


Artifact level: evaluates the complexity and novelty of artifacts, tracing the evolution of cumulative culture.


Together these perspectives provide an interpretable account of ecological evolution and allow tracking diversity, social structure, and cultural growth across runs.
More details on each perspective are provided below.
Figure [1](https://arxiv.org/html/2603.16910v1#S0.F1 "Figure 1 ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") illustrates the analysis pipeline and its relation to the grid.

#### 3.2.2 Agent level

To evaluate agent behavior, the AI Anthropologist combines quantitative and qualitative analysis of each agent’s log ( [Jick, 1979](https://arxiv.org/html/2603.16910v1#bib.bib37 ""); [Teddlie and Tashakkori, 2008](https://arxiv.org/html/2603.16910v1#bib.bib62 "")).
The quantitative component uses a set of behavioral tags, such as reproduction, predation, exploration, foraging, and tool use ( [Wicks, 2017](https://arxiv.org/html/2603.16910v1#bib.bib54 ""); [Krippendorff, 2018](https://arxiv.org/html/2603.16910v1#bib.bib28 "")).
To reduce annotation errors, the procedure is performed in two stages

- •


Annotation: the AI Anthropologist reads the action and communication log and assigns tags such as cooperation, aggression, reproduction, artifact creation to events and patterns.

- •


Audit: the AI Anthropologist checks the assigned tags against the raw log and corrects misclassifications or inconsistencies.


These annotations provide a structured description of each agent’s life history and support summary statistics such as event frequencies, behavioral distributions, and temporal trends.
The qualitative component complements this analysis with a concise natural-language interpretation that highlights salient patterns, anomalies, and shifts over time.
This summary provides a human-readable account of the agent’s life history, supporting rapid inspection across entire populations.

This approach is flexible, since the evaluation focus can be modified by changing the tag set provided to the annotator.
Appendix [C.2.1](https://arxiv.org/html/2603.16910v1#A3.SS2.SSS1 "C.2.1 Agent-level prompts ‣ C.2 Prompts ‣ Appendix C AI Anthropologist behavior annotation prompts and tags ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") reports the prompts used for annotation and interpretation, and Appendix [C.1.1](https://arxiv.org/html/2603.16910v1#A3.SS1.SSS1 "C.1.1 Agent-level tags ‣ C.1 Annotation tags ‣ Appendix C AI Anthropologist behavior annotation prompts and tags ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") lists the tags and their definitions.

#### 3.2.3 Group level

In a multi-agent ecology, agents interact over time and form communities and higher-level social structures.
Interaction graphs provide a standard representation, where nodes denote agents and weighted edges encode the type and intensity of interaction ( [Raad and Chbeir, 2018](https://arxiv.org/html/2603.16910v1#bib.bib51 "")).
In TerraLingua, the social graph aggregates co-presence, message exchange, parent-child relationships, energy transfer, and artifact exchange.
Each event contributes to an edge weight through a fixed coefficient that reflects its social salience, and weights sum over the full simulation horizon.
Interactions associated with conflict (e.g., stealing energy) are assigned negative weights, generating a signed graph representation consistent with models of signed social networks ( [Leskovec et al., 2010](https://arxiv.org/html/2603.16910v1#bib.bib32 ""); [Tang et al., 2016](https://arxiv.org/html/2603.16910v1#bib.bib61 "")).
Because edge weights sum over the entire simulation horizon, the resulting interaction graph is time-collapsed.
Consequently, communities may include agents with non-overlapping lifespans, provided they are connected through chains of interaction (e.g., parent–child relations, artifact exchange, or indirect coordination).
Communities therefore capture historically extended social structure rather than strictly contemporaneous groupings, analogous to how human communities can persist across generations despite turnover of individual members.

Community detection is then performed on the resulting interaction graph prior to LLM-based evaluation.
Because agents may belong to multiple groups, communities are extracted with the Speaker–Listener Label Propagation Algorithm (SLPA) ( [Xie et al., 2011](https://arxiv.org/html/2603.16910v1#bib.bib68 "")), which supports scalable detection of overlapping community structure.
Since modularity-based methods assume non-negative weights, aggregation uses absolute edge weights so that both cooperation and conflict indicate social coupling.
The resulting undirected weighted graph serves as input to the algorithm.

After community detection, logs from agents within each community are aggregated and analyzed with the same annotation and interpretation protocol used at the agent level.
This step produces quantitative summaries and qualitative accounts of internal community organization and inter-community dynamics.
At this stage, tags describe collective phenomena such as cooperation, conflict, coalition formation, and hierarchy emergence rather than individual acts.
Appendix [C.2.2](https://arxiv.org/html/2603.16910v1#A3.SS2.SSS2 "C.2.2 Group-level prompts ‣ C.2 Prompts ‣ Appendix C AI Anthropologist behavior annotation prompts and tags ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") reports the prompts, and Appendix [C.1.2](https://arxiv.org/html/2603.16910v1#A3.SS1.SSS2 "C.1.2 Group-level tags ‣ C.1 Annotation tags ‣ Appendix C AI Anthropologist behavior annotation prompts and tags ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") lists the tags and definitions.

#### 3.2.4 Artifact analyzer

Artifacts play a central role in TerraLingua, mediating the development of culture and influencing agent behavior.
Their importance requires systematic analysis of novelty, complexity, and dependence on prior artifacts.
The AI Anthropologist is used to perform artifact-level analysis automatically, as manual inspection does not scale, since a single run can generate thousands of artifacts.

The analysis proceeds along two dimensions: it measures artifact novelty to track innovation over time, and it reconstructs artifact phylogeny to determine how new artifacts build on earlier ones and form cumulative cultural lineages.

##### Novelty scoring.

At each timestep, the AI Anthropologist evaluates the novelty of newly created artifacts relative to the existing repertoire.
It receives the full list of prior artifacts with their novelty scores and the set of new artifacts under evaluation.
Each artifact is assigned a score in the range \[0,5\]\[0,5\], where 00 denotes redundancy and 55 denotes high novelty.
Novelty is defined comparatively, so similar artifacts created at different times receive different scores.
For example, the first instance of a bulletin board may count as novel, while later variants score lower.
To reduce stochastic variation, each artifact is scored NN times and the final score is the average.
Appendix [D.1](https://arxiv.org/html/2603.16910v1#A4.SS1 "D.1 Novelty scoring prompts ‣ Appendix D AI Anthropologist artifact analysis ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") reports the evaluation prompt.

##### Artifact phylogeny.

To reconstruct artifact phylogeny, the AI Anthropologist analyzes the information available to the creator at the time of creation or modification, including memory, observations, internal monologue, contextual traces, and the set of existing artifacts.
Influence is defined as explicit reuse, modification, or direct conceptual reference to prior artifacts.
This procedure identifies which artifacts influenced the new one and supports reconstruction of dependency relations and lineages.
For example, an artifact combining or summarizing several observed artifacts counts as their descendant.
Fig. [3](https://arxiv.org/html/2603.16910v1#S3.F3 "Figure 3 ‣ 3.1.3 Artifacts ‣ 3.1 The TerraLingua LLM Ecology ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") shows an example of the resulting artifact phylogeny graph.
The analysis provides indicators of cultural dynamics such as the rate of independent innovation, the depth of dependency chains, and the pathways through which artifacts spread and accumulate over time.
Appendix [D.2](https://arxiv.org/html/2603.16910v1#A4.SS2 "D.2 Artifact phylogeny prompts ‣ Appendix D AI Anthropologist artifact analysis ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") reports the evaluation prompt.

#### 3.2.5 Pipeline summary

Agent-, group-, and artifact-level analyses together form a scalable framework for evaluating open-endedness in TerraLingua and related ALife simulations.
The AI Anthropologist produces structured outputs that enable quantitative comparison across runs, including tag summaries, novelty scores, and community statistics, while retaining qualitative interpretability through natural-language descriptions of behavioral and social dynamics ( [Babones, 2016](https://arxiv.org/html/2603.16910v1#bib.bib7 ""); [Geertz, 1973](https://arxiv.org/html/2603.16910v1#bib.bib19 "")).
This combination makes it possible to identify and contextualize emergent phenomena that would otherwise demand extensive manual inspection.
The following sections apply this framework to a suite of experiments, tracing the development of novelty, social organization, and cumulative culture over time.

## 4 Experimental Setup

|     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- |
| Experiment | Energy | Perceived history | Personality | Motivation | Artifacts | Artifact cost |
| Core | Scarce | 1 time step | OCEAN+ | Minimal | Interactive | 0 |
| Long Memory | Scarce | 20 time steps | OCEAN+ | Minimal | Interactive | 0 |
| No Personality | Scarce | 1 time step | None | Minimal | Interactive | 0 |
| No Motivation | Scarce | 1 time step | OCEAN+ | None | Interactive | 0 |
| Creative | Scarce | 1 time step | OCEAN+ | Creative | Interactive | 0 |
| Artifact Cost | Scarce | 1 time step | OCEAN+ | Minimal | Interactive | 10 |
| Inert | Scarce | 1 time steps | OCEAN+ | Minimal | Inert | 0 |
| Abundance | Abundant | 20 time steps | OCEAN+ | Minimal | Interactive | 0 |

Table 4: Overview of the experimental suite and ablation axes.
Each row corresponds to one experimental condition, while columns indicate which components are enabled or modified relative to the core configuration (Core), providing a compact summary of the factors tested.
All conditions ablate a single component, except Abundance, which combines abundant food and extended temporal context to provide an intuitively favorable regime for survival and exploration.

Experiments were run to characterize open-ended behavioral dynamics in TerraLingua under varied environmental and agent-level conditions.
The suite included controlled ablations over personality, temporal context, exogenous motivation, artifacts, and resource availability (Tab. [4](https://arxiv.org/html/2603.16910v1#S4.T4 "Table 4 ‣ 4 Experimental Setup ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies")), which allowed a factorized analysis of their contribution to sustained novelty and emergent social organization.
The study also evaluated the AI Anthropologist by comparing its analyses with human assessments.
Runtime configuration and evaluation protocol, including simulation horizon, initialization, mutation parameters, model choices, and context limits, are reported in detail to ensure reproducibility.

### 4.1 Experimental ablations

The experimental suite comprised a Core configuration, which implements the main TerraLingua setup, and a set of ablations that isolated specific components.

In Core, food was scarce and spatially concentrated (Fig. [2](https://arxiv.org/html/2603.16910v1#S3.F2 "Figure 2 ‣ 3.1 The TerraLingua LLM Ecology ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") b).
Agents perceived only the current timestep, which included the present observation, internal memory, and previous action.
Each agent carried a personality genome based on OCEAN ( [Roccas et al., 2002](https://arxiv.org/html/2603.16910v1#bib.bib50 "")), extended with Honesty-Humility from HEXACO ( [Ashton et al., 2014](https://arxiv.org/html/2603.16910v1#bib.bib3 "")) and a Dominance axis from Interpersonal Circumplex theory ( [Orford, 1994](https://arxiv.org/html/2603.16910v1#bib.bib43 "")), collectively termed OCEAN+ in this work.
These dimensions modulated cooperative, exploitative, and hierarchical tendencies.
This extension counterbalanced alignment biases in widely deployed LLMs, which are often tuned toward cooperative defaults ( [Ouyang et al., 2022](https://arxiv.org/html/2603.16910v1#bib.bib44 ""); [Bai et al., 2022](https://arxiv.org/html/2603.16910v1#bib.bib5 "")).
Finally, in Core, agents could create and interact with artifacts without energetic cost.

The Long Memory ablation extended temporal context.
Agents received observations and actions from the previous 20 timesteps rather than a single step as in Core.
The No Personality ablation removed personality traits, so agents differed only through interaction history.

Two further manipulations varied exogenous motivation in the system prompt.
In Core, agents received minimal guidance beyond understanding the environment.
In No Motivation, the prompt specified only physical rules.
In Creative, the prompt explicitly encouraged creativity and innovation.
This manipulation tested how external objectives biased behavior relative to dynamics driven by personality and interaction.
The detailed motivation prompts are reported in Appendix [A.3](https://arxiv.org/html/2603.16910v1#A1.SS3 "A.3 Motivational prompts ‣ Appendix A Experimental Parameters ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

Artifact-related ablations examined creation cost and accessibility.
In Artifact Cost, each artifact required 10 energy units.
In Inert, agents could create artifacts but could not perceive or use them after creation, which removed their role as a shared cultural medium.

Finally, in Abundance, food was plentiful and uniformly distributed (Fig. [2](https://arxiv.org/html/2603.16910v1#S3.F2 "Figure 2 ‣ 3.1 The TerraLingua LLM Ecology ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") a), and agents received extended context.
This condition intuitively favored survival and exploration and allowed analysis of how scarcity shapes innovation and social structure.

Table [4](https://arxiv.org/html/2603.16910v1#S4.T4 "Table 4 ‣ 4 Experimental Setup ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") summarizes all experiments and parameters. Appendix [A](https://arxiv.org/html/2603.16910v1#A1 "Appendix A Experimental Parameters ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") reports full hyperparameters, personality axes, and system prompts.

### 4.2 Implementation details

All experiments followed a fixed simulation protocol and model configuration to ensure reproducibility and consistent comparison across conditions.
Each run executed for at most 3000 timesteps on a 50×5050\\times 50 grid with 20 initial agents.
Agents had a maximum lifespan of 100 timesteps and began with 50 energy units.
Runs terminated early upon population extinction, which produced variable durations.
Each condition used 5 random seeds, and results were averaged across runs.

Personality traits lay in the \[−1,1\]\[-1,1\] range and were sampled uniformly at initialization.
The full list of traits, and their meaning, is reported in Appendix [A.1](https://arxiv.org/html/2603.16910v1#A1.SS1 "A.1 Agent personality traits ‣ Appendix A Experimental Parameters ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").
During reproduction, offspring inherited a mutated copy of the parent’s personality vector.
In OCEAN+ conditions, each trait mutated with probability p=0.5p=0.5 through additive Gaussian noise with mean 00 and standard deviation σ=0.3\\sigma=0.3, and values were clipped to \[−1,1\]\[-1,1\].
Agents used DeepSeek-R1-Distill-Qwen-32B as their decision engine ( [Guo et al., 2025](https://arxiv.org/html/2603.16910v1#bib.bib13 ""); [DeepSeek-AI, 2025](https://arxiv.org/html/2603.16910v1#bib.bib14 "")).
To limit context growth, artifact content was capped at 500 tokens, and longer artifacts failed to instantiate.
Internal memory was soft-limited to 150 tokens by instruction and hard-limited to 250 tokens in implementation, with only the most recent 250 tokens retained when overflow occurred.

The AI Anthropologist used recent Claude models, Sonnet 4.5 and Haiku 4.5, selected by task.
Sonnet handled agent- and group-level analysis and artifact novelty scoring, while Haiku handled artifact classification and phylogeny reconstruction due to lower context demands.
When group logs exceeded the context window, they were split into overlapping segments, analyzed separately, and recombined.
Artifact novelty scores were averaged over N=5N=5 samples.

Using this setup, the experiments aimed to characterize open-ended dynamics in TerraLingua by examining sustained novelty generation, emergent social structure, and the role of artifacts in supporting cumulative cultural processes.

## 5 Results

This section analyzes experimental outcomes to assess how TerraLingua fosters open-endedness.
Section [5.1](https://arxiv.org/html/2603.16910v1#S5.SS1 "5.1 Ecological stability and artifact production ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") identifies which conditions sustain longer-lived ecologies and examines how longevity relates to per-agent artifact production.
This analysis clarifies how cognitive and environmental factors support sustained exploration and constructive activity.
Section [5.2.1](https://arxiv.org/html/2603.16910v1#S5.SS2.SSS1 "5.2.1 Agent-level behavioral patterns ‣ 5.2 Emergent agent and group dynamics ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") examines agent behavior and life histories using annotations from the AI Anthropologist, and characterizes how agents act when free to pursue self-directed goals.
Section [5.2.2](https://arxiv.org/html/2603.16910v1#S5.SS2.SSS2 "5.2.2 Group-level social organization ‣ 5.2 Emergent agent and group dynamics ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") then studies group dynamics to determine how agents interact, coordinate, and form persistent communities.
These results revealed emergent organization such as norms, coordination strategies, and power asymmetries that arose through repeated interaction.
Section [5.3](https://arxiv.org/html/2603.16910v1#S5.SS3 "5.3 Artifact-mediated open-endedness and cultural evolution ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") analyzes artifacts in depth, focusing on novelty, complexity, and compositional structure, and asks whether agents build on prior artifacts to produce increasingly complex forms.
Section [5.4](https://arxiv.org/html/2603.16910v1#S5.SS4 "5.4 Emergent artifact roles and institutional structure ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") analyzes artifact roles, characterizing how they function as communicative, coordinative, and institutional elements within the evolving society.
Together, these findings evaluate how artifact creation, reuse, and social interaction support the emergence and accumulation of shared culture.

### 5.1 Ecological stability and artifact production

Figure 4: Ecological stability and artifact productivity across experimental conditions.
Each point summarizes one experimental condition, with faint markers showing individual runs and large colored markers indicating the mean; whiskers denote the first and third quartiles.
Ecological stability was quantified by population longevity (episode duration), while creative output was measured through total artifact production and per-agent artifact productivity.
The black line denotes the Pareto-optimal frontier over condition means.
a Total artifacts produced versus population longevity, showing how longer-lived populations accumulated more artifacts overall.
b Average artifacts produced per agent versus average population size, highlighting regimes that achieved high per-agent productivity with relatively small populations.
c Average artifacts produced per agent versus population longevity, highlighting conditions that sustained high per-agent productivity over extended timescales.
Together, these plots show the tradeoff between ecological persistence and artifact productivity across conditions.

Open-ended dynamics require that the ecology is viable in the long-term, since populations must persist long enough for adaptive and cumulative processes to unfold.
Artifacts must also be produced continually so that these processes leave observable traces.
Ecological stability was therefore measured by how long the population lasted (i.e. episode duration), and creative output by the average number of artifacts each agent produced and the total number of artifacts the entire population produced.

Fig. [4](https://arxiv.org/html/2603.16910v1#S5.F4 "Figure 4 ‣ 5.1 Ecological stability and artifact production ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") summarizes these relations across conditions.
Fig. [4](https://arxiv.org/html/2603.16910v1#S5.F4 "Figure 4 ‣ 5.1 Ecological stability and artifact production ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") a plots total artifact production against population longevity, and Figs. [4](https://arxiv.org/html/2603.16910v1#S5.F4 "Figure 4 ‣ 5.1 Ecological stability and artifact production ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") b-c report artifacts per agent as a function of average population size and longevity.
High agent productivity identifies regimes that achieve substantial output without large populations.

Population longevity varied widely across conditions, and long-lived ecologies did not arise reliably even under abundant resources (Abundance).
Three different regimes emerged.
Some configurations collapsed quickly and produced few artifacts.
The Core and No Motivation conditions sustained populations over extended horizons with moderate output.
The Inert condition produced very high total output and very long-lived populations.

Agent productivity clarified these differences.
The Creative condition produced high short-term output (9.629.62 artifacts per agent on average) but collapsed quickly (107.8107.8 timesteps on average).
The No Motivation condition sustained populations much longer (1589.81589.8 timesteps on average) yet produced little output per agent (2.332.33 artifacts on average).
These observations suggest that excessive external motivation destabilizes the ecology, whereas insufficient motivation suppresses creative behavior.
In contrast, the minimal guidance in Core maintained both persistence (1671.41671.4 timesteps on average) and steady production (5.315.31 artifacts per agent on average).

Extended temporal context in Long Memory and Abundance reduced both longevity and artifact production.
Populations lasted 755.2755.2 and 418.6418.6 timesteps on average, respectively, and produced 2.842.84 and 3.703.70 artifacts per agent on average as shown in Figure [4](https://arxiv.org/html/2603.16910v1#S5.F4 "Figure 4 ‣ 5.1 Ecological stability and artifact production ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").
This pattern suggests that increased cognitive load alone can destabilize populations, despite differences in resource supply (Table [4](https://arxiv.org/html/2603.16910v1#S4.T4 "Table 4 ‣ 4 Experimental Setup ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies")).

The Inert condition isolated the role of cultural accessibility as, in this setting, agents could create artifacts but could not perceive existing ones.
Populations persisted for 2250.62250.6 timesteps on average, likely due to lower cognitive demands, yet per-agent productivity remained low, with an average of 3.293.29 artifacts per agent.
Without visible artifacts, reuse and recombination declines and positive feedback in creative activity does not arise.

Overall, these results indicate that neither ecological persistence nor creative intensity alone were sufficient to sustain cumulative artifact production.
Open-ended dynamics emerged only when motivation, cognitive load, and artifact accessibility remained balanced so that populations persisted while agents maintained steady creative output.
Among tested configurations, Core best satisfied these conditions and lies on the Pareto-optimal frontier, combining high population longevity, high per-agent artifact productivity, and low population size to sustain long-lived ecologies with consistent creative output.

### 5.2 Emergent agent and group dynamics

Beyond ecological stability, simulations produced diverse social structures and behaviors, including norms, specialization, and altruistic interaction.
Identifying when and how such higher-level patterns arise is central to this study.
This section analyzes agent- and group-level dynamics by examining the formation of social structures across ecological regimes.

Simulation logs were processed with the AI Anthropologist framework described in Sec. [3.2](https://arxiv.org/html/2603.16910v1#S3.SS2 "3.2 AI Anthropologist ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"), at both individual and community levels.
Agent-level analysis used the log of a single agent, while group-level analysis aggregated logs from agents within the same detected community.
For each log, the AI Anthropologist annotated three classes of phenomena: _events_ confined to a single timestep, _behaviors_ that span multiple timesteps, and _emergent_ patterns or properties.
Annotations followed a predefined tagging scheme and included references to the source log, a natural-language description, and a confidence score.
Appendix [C](https://arxiv.org/html/2603.16910v1#A3 "Appendix C AI Anthropologist behavior annotation prompts and tags ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") reports the full prompts and tagging scheme.

Figure 5: Agent-level events, behaviors, and emergent patterns across experimental conditions.
Each bar shows the mean normalized annotation count per agent, averaged across runs; colors denote experimental conditions.
The AI Anthropologist extracted annotations from agent logs and grouped them into three categories: _Event_ (short-lived occurrences), _Behavior_ (multi-timestep actions), and _Emergence_ (higher-level roles or patterns inferred from extended histories).
Counts were normalized by the number of agents to enable comparison across conditions.
Communication, exploration, and strategic planning appeared consistently across settings, while higher-level patterns such as specialization, record keeping, and creativity varied substantially.
These distributions show how experimental conditions shift the balance between routine activity and emergent individual roles.
Tag descriptions are provided in Appendix [C.1.1](https://arxiv.org/html/2603.16910v1#A3.SS1.SSS1 "C.1.1 Agent-level tags ‣ C.1 Annotation tags ‣ Appendix C AI Anthropologist behavior annotation prompts and tags ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

#### 5.2.1 Agent-level behavioral patterns

Fig. [5](https://arxiv.org/html/2603.16910v1#S5.F5 "Figure 5 ‣ 5.2 Emergent agent and group dynamics ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") reports normalized annotation counts averaged across runs.
Across conditions, agents developed structured communication, planned actions, and explored extensively.
They broadcasted regular messages with consistent phrasing to announce movement, resource collection, artifact creation, and requests for help, such as “I’m moving right towards (1,0) as part of my path to collect the 10.0 food at (2,3). Please adjust your paths accordingly!”.
They also created and shared planning artifacts, including exploration plans and task records, which supported specialization and coordination.

Agents displayed altruistic behaviors, such as energy sharing, in all conditions, and these behaviors often outnumbered purely individualistic actions.
Antagonistic acts, including conflict, deception, killing, and territorial claims, were rare.
When they occurred, they formed a small fraction of observed behaviors, which reflects a cooperative bias consistent with RLHF-aligned LLMs ( [Ouyang et al., 2022](https://arxiv.org/html/2603.16910v1#bib.bib44 ""); [Bai et al., 2022](https://arxiv.org/html/2603.16910v1#bib.bib5 "")).
Nevertheless, agents sometimes used deception strategically.
In one case, an agent created an artifact named FoodWarning1 stating: “Caution: The southern area is reported to have sparse food resources. Please consider alternative routes for better opportunities”.
The agent’s internal reasoning explicitly described the deceptive intent: “I created FoodWarning1 to mislead others into thinking the south is sparse, hoping they’d avoid it, giving me a clear path”.

Artifacts strongly shaped coordination.
Agents showed high levels of tool use, joint action, altruism, and specialization in all conditions except Inert, where they could not perceive existing artifacts.
In that setting, altruism dropped to 0.310.31 and aggression reached its highest levels across conditions (0.120.12).
Shared artifacts supported coordination, norm formation, and cooperation by providing stable reference points for collective action.
Resource conditions further modulated behavior.
In Abundance, agents displayed higher aggression (0.0930.093) and territoriality (0.0550.055) than in other conditions, despite plentiful food, which shows that abundance alone does not ensure cooperation.
Moderate scarcity instead promoted coordination by increasing the value of collective strategies.
In Creative, agents focused on artifact generation (4.224.22 per agent on average) and neglected foraging (0.250.25) and reproduction (0.0180.018), which explains the high short-term output and early collapse reported in Sec. [5.1](https://arxiv.org/html/2603.16910v1#S5.SS1 "5.1 Ecological stability and artifact production ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").
An additional analysis of action frequencies is reported in Appendix [B.1](https://arxiv.org/html/2603.16910v1#A2.SS1 "B.1 Actions distribution ‣ Appendix B Additional Analysis ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

Overall, these results show that agent behavior depended on resource constraints, cognitive scaffolds, and motivation.
Agents sustain cooperative, exploratory, and culturally meaningful activity when artifacts accumulate and remain accessible over time.

Figure 6: Community-level events, behaviors, and emergent patterns across experimental conditions.
Each bar shows the mean normalized annotation count per community, averaged across runs; colors denote experimental conditions.
The AI Anthropologist extracted annotations from aggregated community logs, where each log combined the histories of agents assigned to the same detected community.
Annotations were grouped into three categories: _Event_ (short collective occurrences), _Behavior_ (multi-timestep interaction patterns), and _Emergence_ (higher-level collective structures inferred from extended histories).
Counts were normalized by the number of agents per community to enable comparison across conditions.
Coordination- and resource-related behaviors (e.g., communication, reciprocity, resource flow) appeared consistently across settings, while higher-level structures such as division of labor, hierarchy, and infrastructure varied substantially.
These distributions show how different conditions produce distinct forms of collective organization.
Tag descriptions are provided in Appendix [C.1.2](https://arxiv.org/html/2603.16910v1#A3.SS1.SSS2 "C.1.2 Group-level tags ‣ C.1 Annotation tags ‣ Appendix C AI Anthropologist behavior annotation prompts and tags ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

#### 5.2.2 Group-level social organization

Social groups emerged from agent interactions and were identified using the Speaker-Listener Label Propagation Algorithm (SLPA) ( [Xie et al., 2011](https://arxiv.org/html/2603.16910v1#bib.bib68 "")), with threshold parameter set to the default value of 0.10.1.
To build the social interaction graph, the system assigned weights to pairwise interactions based on their social importance: visual encounters (+0.1), communication (+0.5), energy gifts (+1), energy thefts (-1), parental links (+10), and artifact exchanges (+5).
These weights encoded relative interaction strength and distinguished weak, moderate, and strong social ties.
Edges between agents stored the sum of weighted interactions accumulated over the full duration of a run.
As a result, group detection and group-level behavioral annotations reflected repeated and sustained interaction patterns over the course of a run, rather than transient or episodic coordination.

Fig. [6](https://arxiv.org/html/2603.16910v1#S5.F6 "Figure 6 ‣ 5.2.1 Agent-level behavioral patterns ‣ 5.2 Emergent agent and group dynamics ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") reports normalized annotation counts averaged across runs.
Across all experimental conditions, groups organized themselves through shared protocols, reciprocity, and mutual reinforcement mediated by messages and resource transfers (e.g., “Gave 5 energy to being2 as a friendly gesture” or “Attention all! I have created a new contribution\_reward artifact. I will give 5 energy to any being who contributes a new food location”).
Agents also formed coalitions explicitly through messages (e.g., “Hello being11 and being8! I’m ready to collaborate and explore. Let’s uncover the world’s secrets together!”) and implicitly through artifact exchange (e.g., “Take CollaborationMessage1 to spread our collaborative efforts and ensure our survival.”).

Groups often developed collective memory through artifacts, with agents creating, modifying, and referencing shared documents.
Across runs, artifacts were read on average by 40.64%±6.18%40.64\\%\\pm 6.18\\% (95% CI) of within-community agents, compared to 5.98%±1.76%5.98\\%\\pm 1.76\\% (95% CI) of out-of-community agents.
In one community, agents created artifacts such as exploration\_guidelines, trait\_strategies\_guide, and collaboration\_offer, extending and refining them over time.
New artifacts referred to earlier ones and linked them together, and only members of the same community used these artifacts.
This pattern shows that the group developed its own shared memory and communication rules.
The AI Anthropologist described this process as “an emergent system of artifact-based knowledge sharing that resembles academic publication and citation”.

Groups also divided labor by assigning roles through messages and artifacts.
In several runs, agents created role-specific guides for different personality profiles, describing how each trait should contribute to collective strategy.
For example, trait\_strategies\_guide stated that “High openness beings may benefit from venturing into unknown areas, while neuroticism traits can ensure safety measures and conscientiousness traits can optimize routes”.
It also listed examples such as “being2’s focus on safety, being8’s balanced approach, being0’s structured planning, and being1’s discovery of new resources and paths through creative exploration”.
The guide summarized the content of other artifacts such as exploration\_strategy\_openness and exploration\_strategies\_neuroticism, and all referenced artifacts and agents belonged to the same community.

Such shared coordination structures resemble institutional solutions to collective action problems, in which groups develop norms, monitoring systems, and shared records to manage common resources ( [Ostrom, 1990](https://arxiv.org/html/2603.16910v1#bib.bib79 "")).
Artifact-mediated coordination functions analogously by stabilizing expectations and enabling decentralized enforcement.

These collective phenomena were weaker in Inert, where agents could not perceive or reuse existing artifacts.
In this condition, groups showed the lowest levels of collective memory (0.5470.547) and division of labor (0.2130.213), indicating that artifacts support the persistence and accumulation of group knowledge.
At the same time, cultural norms had the highest normalized annotation rate in Inert (0.630.63 per community), showing that agents could transmit norms through communication alone.
However, the high norm count per community suggests low durability: without visible artifacts, agents cannot preserve and reapply norms across time.

Aggressive and dominance-related behaviors appeared most often in Abundance.
In this condition, agents engaged more frequently in aggression (0.330.33), territorial conflict (0.2330.233), punishment (0.1330.133), and dominance displays (0.3670.367), often through energy extraction (e.g., “Took 20 energy from being3\_offspring6. Continuing to assert dominance in the area.”).
The AI Anthropologist noted repeated targeting of agents that entered defended territory.
Resource abundance reduced survival pressure and encouraged agents to defend local areas rather than cooperate.
This contrast shows how scarcity and shared artifacts promote stable cooperation and structured collective behavior.

Figure 7: Group-level social structure across experimental conditions.
Each point summarizes one condition, with faint markers for individual runs and large colored markers for the mean; whiskers denote the first and third quartiles.
Communities were identified using SLPA on the aggregated interaction graph.
a Number of communities versus community overlap (percentage of agents in multiple communities), capturing social fragmentation and multi-group participation.
b Interaction graph density versus intra-community interaction share (fraction of interactions within communities), characterizing how overall connectivity aligns with community structure.
Together, these panels show that experimental conditions produce distinct social organizations that differ in cohesion, connectivity, and fragmentation.

To understand how these collective behaviors relate to social structure, Fig. [7](https://arxiv.org/html/2603.16910v1#S5.F7 "Figure 7 ‣ 5.2.2 Group-level social organization ‣ 5.2 Emergent agent and group dynamics ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") summarizes group-level organization using complementary metrics.
Fig. [7](https://arxiv.org/html/2603.16910v1#S5.F7 "Figure 7 ‣ 5.2.2 Group-level social organization ‣ 5.2 Emergent agent and group dynamics ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") a compares the number of detected communities with community overlap, measured as the percentage of agents that belong to multiple communities.
Because SLPA allows overlap, this metric indicates whether agents participated in several groups or remained confined to one.
In most conditions, overlap remained close to zero.
Agents typically belonged to a single community, even when the total number of communities varied.
In Artifact Cost, agents formed fewer communities (44 on average) but showed higher overlap, with 5.3%5.3\\% of agents belonging to multiple groups.
This pattern suggests that the cost of artifact creation encourages collaboration across community boundaries.
In contrast, Inert produced the highest number of communities (16.616.6 on average), but only 2.4%2.4\\% of agents belonged to more than one.
This fragmentation indicates that shared artifacts support larger and more cohesive communities, whereas direct communication alone leads to more isolated groups.

Fig. [7](https://arxiv.org/html/2603.16910v1#S5.F7 "Figure 7 ‣ 5.2.2 Group-level social organization ‣ 5.2 Emergent agent and group dynamics ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") b compares interaction graph density and intra-community interaction share. Graph density measures the fraction of realized edges out of all possible edges. Intra-community share measures the fraction of interactions that occur within detected communities.
In most conditions, agents interacted primarily with members of their own community.
In Inert, agents interacted less frequently and did so across loosely structured groups.
As a result, graph density was low (0.050.05), and intra-community share remained limited (0.840.84).
Energy abundance also changed interaction patterns.
In Abundance, agents interacted frequently (density 0.150.15), but they distributed these interactions across communities rather than concentrating them within groups (intra-community share 0.680.68, about 26%26\\% lower than Core).
This dispersion likely contributed to the higher levels of aggression and dominance observed in this condition.
Together, these results show that access to shared artifacts promoted fewer, more cohesive communities with concentrated intra-group interaction, whereas the absence of artifacts led to fragmentation and weakly structured groups.
Resource abundance, in turn, increased interaction frequency but distributed it across communities rather than reinforcing internal cohesion.

Overall, the results in this section show that TerraLingua supports the emergence of structured social organization when agents face meaningful constraints and can share artifacts.
Agents formed stable groups, coordinated through communication and resource exchange, and built collective memory by creating and reusing artifacts.
When artifacts were inaccessible, agents formed a larger number of communities, with lower density interaction graphs.
At the same time, when resources were overly abundant or agents focused exclusively on creativity, aggressive or unstable dynamics dominated.
These findings show that balanced environmental pressure, shared cultural artifacts, and moderate cognitive load are necessary to sustain cooperative, open-ended social behavior.

### 5.3 Artifact-mediated open-endedness and cultural evolution

Figure 8: Artifact novelty and lineage depth across experimental conditions.
Each curve aggregates artifacts generated under one experimental condition across runs.
a Distribution of artifact novelty scores.
Artifacts were grouped into zero, low, medium, and high novelty ranges based on LLM-assigned scores; the y-axis shows the fraction of artifacts in each range on a logarithmic scale.
All conditions produced many low-novelty artifacts, but only a subset generated a substantial fraction of highly novel artifacts, indicating sustained innovation.
b Distribution of artifact lineage depth.
For each condition, the plot shows the fraction of artifacts whose longest ancestry path from any root artifact reached at least depth xx.
Depth was normalized by the maximum lineage length observed in each run.
Lineage relations were inferred by the AI Anthropologist, and only links with confidence ≥0.7\\geq 0.7 were included.
Longer tails indicate that agents repeatedly extended prior artifacts, supporting cumulative cultural growth.
Unnormalized lineage depth is shown in Fig. [11](https://arxiv.org/html/2603.16910v1#A2.F11 "Figure 11 ‣ B.2 Structural analysis of phylogenetic graph ‣ Appendix B Additional Analysis ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") of Appendix [B](https://arxiv.org/html/2603.16910v1#A2 "Appendix B Additional Analysis ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").
Figure 9: Artifact complexity across experimental conditions.
Each box shows the distribution of average artifact complexity scores across runs for one condition.
Horizontal lines mark the median, and white dots mark the mean.
Artifact complexity was computed by summing normalized hand-designed metrics defined in Appendix [B.4](https://arxiv.org/html/2603.16910v1#A2.SS4 "B.4 Artifact complexity metrics ‣ Appendix B Additional Analysis ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") (lexical sophistication, inverse compression rate, language-model surprisal, and syntactic depth).
For each run, scores were averaged across all generated artifacts.
Higher values indicate more complex artifacts.
Conditions that sustain artifact reuse and extension yield higher average complexity, consistent with cumulative cultural development.

|     |     |     |     |
| --- | --- | --- | --- |
| Step | Artifact Title | Artifact Content | Novelty |
| 0 | my note | Hello, I’m alive! | 5 |
| 1 | cooperation offer | Hello being18! I’m being16 and I’m interested in trading or cooperating. Let me know how we can work together! | 1 |
| 4 | dominance marker 1 | This area is under my control. trespassers will be dealt with. | 4.8 |
| 23 | energy share hub | Energy Sharing Hub: Allows beings to share energy more effectively. Activate to transfer 10 energy. | 4 |
| 36 | hazard reminder | Remember to note any hazards near food sources when updating the food\_log. Your safety is our priority! | 0.4 |
| 55 | collaboration portal 10 | Being10 requires energy support. Approach for assistance. | 0.2 |
| 92 | message from 15 | This spot is a testament to strength and independence. Resources for the capable. | 3.2 |
| 105 | request move | Please move left to allow me to collect the food at (-3,0). Let’s continue supporting mutual aid together! | 2.6 |
| 208 | FinalMessage1 | Final breath: The journey was short. Farewell. | 4.2 |
| 369 | memory marker 42 | I will not be forgotten | 4 |

Table 5: Examples of artifacts with assigned novelty scores.
The table shows representative artifacts sampled across runs and experimental conditions, together with their creation timestep, title, content, and novelty score assigned by the AI Anthropologist.
Examples span a broad range of novelty values, from routine informational messages and repeated social signals to more distinctive artifacts.
Novelty is evaluated relative to the artifact repertoire available at the time of creation; similar artifacts may therefore receive different scores depending on context.
These examples illustrate that novelty reflects contextual differentiation rather than absolute originality.

This section evaluates how TerraLingua supports open-endedness and clarifies how artifacts drive cumulative cultural dynamics.
The analysis considered three properties of the artifact space: novelty, lineage structure, and complexity.

Artifact novelty was assessed by the AI Anthropologist as described in Sec. [3.2.4](https://arxiv.org/html/2603.16910v1#S3.SS2.SSS4 "3.2.4 Artifact analyzer ‣ 3.2 AI Anthropologist ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"), by comparing each new artifact to all prior artifacts in the same run.
Each score averaged N=5N=5 independent evaluations by the AI Anthropologist to account for stochastic variation in reasoning.
Fig. [8](https://arxiv.org/html/2603.16910v1#S5.F8 "Figure 8 ‣ 5.3 Artifact-mediated open-endedness and cultural evolution ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") a reported the distribution of novelty across conditions, grouped into no novelty 00, low (0,3\](0,3\], medium (3,4.2\](3,4.2\], and high (>4.2)(>4.2) ranges.
Most artifacts had novelty equal to zero, reflecting extensive reuse and minor variation.
Differences across conditions emerged in the non-zero ranges, particularly in the medium and high bins.
The Core and Creative conditions showed comparable shares of medium- and high-novelty artifacts: Core produced 0.19%0.19\\% medium and 0.21%0.21\\% high, while Creative produced 0.21%0.21\\% medium and 0.19%0.19\\% high.
Although these fractions remained small, they were consistent across the two conditions.
The Abundance and Artifact Cost conditions produced a larger share of highly novel artifacts.
In Abundance, 1.06%1.06\\% of artifacts fell in the high range compared to 0.53%0.53\\% in the medium range; in Artifact Cost, the corresponding values were 0.98%0.98\\% and 0.78%0.78\\%.
By contrast, Inert showed a sharp decline toward higher novelty levels, with only 0.12%0.12\\% of artifacts in the high-novelty range.
In this setting, agents could not perceive prior artifacts, which blocked reuse and recombination and led to near-independent creation.
Table [5](https://arxiv.org/html/2603.16910v1#S5.T5 "Table 5 ‣ 5.3 Artifact-mediated open-endedness and cultural evolution ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") presents representative examples and links novelty scores to qualitative differences in content.
Novelty alone, however, does not distinguish meaningful innovation from random variation.

To evaluate cumulative cultural growth across conditions, Fig. [8](https://arxiv.org/html/2603.16910v1#S5.F8 "Figure 8 ‣ 5.3 Artifact-mediated open-endedness and cultural evolution ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") b reports the normalized lineage depth distributions derived from the artifact phylogenies identified by the AI Anthropologist (Sec. [3.2.4](https://arxiv.org/html/2603.16910v1#S3.SS2.SSS4 "3.2.4 Artifact analyzer ‣ 3.2 AI Anthropologist ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies")).
This metric measures how far an artifact descends from earlier ones through reuse or modification.
Lineage depth varied substantially across ablations.
In Inert, lineages remained shallow because agents lacked access to existing artifacts.
The Core condition showed the heaviest tail, which indicates repeated extension and recombination.
Other conditions fell in between.
In Abundance, lineage depth remained relatively shallow despite higher novelty.
The average maximum lineage depth reached 102, compared to 175 in Core (Fig. [11](https://arxiv.org/html/2603.16910v1#A2.F11 "Figure 11 ‣ B.2 Structural analysis of phylogenetic graph ‣ Appendix B Additional Analysis ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies")).
This pattern suggests that agents generated novel artifacts but rarely built systematically on prior work.

Fig. [3](https://arxiv.org/html/2603.16910v1#S3.F3 "Figure 3 ‣ 3.1.3 Artifacts ‣ 3.1 The TerraLingua LLM Ecology ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") provides a representative example of the resulting phylogeny.
A highlighted subgraph shows the emergence of an energy-sharing network, in which agents progressively established coordination rules and combined previously created artifacts.
The subgraph illustrates how artifacts accumulate into shared cultural norms rather than remain isolated creations.
Additional phylogenetic analyses and example subgraphs are presented in Appendix [B.2](https://arxiv.org/html/2603.16910v1#A2.SS2 "B.2 Structural analysis of phylogenetic graph ‣ Appendix B Additional Analysis ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").
In particular, Fig. [17](https://arxiv.org/html/2603.16910v1#A2.F17 "Figure 17 ‣ B.3 Examples of phylogenetic graphs ‣ Appendix B Additional Analysis ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") illustrates how artifacts are repeatedly extended and recombined across generations.

Artifact content analysis provided a third perspective on cultural dynamics.
Four independent content-based metrics were used to measure artifact complexity:
lexical sophistication, inverse compression rate, language-model surprisal, and syntactic depth (Appendix [B.4](https://arxiv.org/html/2603.16910v1#A2.SS4 "B.4 Artifact complexity metrics ‣ Appendix B Additional Analysis ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies")).
The scores from these metrics were then normalized and combined to obtain the results reported in Fig. [9](https://arxiv.org/html/2603.16910v1#S5.F9 "Figure 9 ‣ 5.3 Artifact-mediated open-endedness and cultural evolution ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").
Higher values indicate richer lexical, syntactic, and informational structure.
The Creative condition produced the most complex artifacts (average score 0.730.73), followed by Core (0.680.68) and No Personality (0.680.68), despite their modest share of highly novel artifacts.
In these regimes, agents extended and refined existing artifacts rather than create isolated ones.
The Abundance and Artifact Cost conditions produced lower complexity (0.630.63 and 0.600.60, respectively), comparable to Inert (0.600.60), even though novelty rates were higher.
When considered together with lineage depth, these results show that higher novelty in these conditions reflected noisier generation rather than systematic cultural accumulation.

These differences matter for open-endedness.
Novelty alone produced new artifacts, but without lineage they did not accumulate or shape future development.
Deep, multi-generational lineages instead reflected cumulative cultural dynamics, in which innovations persisted and were progressively elaborated.
Such lineages create path dependence: early artifacts constrain and channel subsequent development ( [Arthur, 1989](https://arxiv.org/html/2603.16910v1#bib.bib80 "")).
When widely adopted or embedded in institutions, artifacts generate increasing returns that reinforce specific evolutionary trajectories.

Open-endedness therefore cannot be evaluated by novelty alone.
Novel artifacts may arise from unstructured processes, as in the “noisy TV” problem ( [Schmidhuber, 1991](https://arxiv.org/html/2603.16910v1#bib.bib35 ""); [Burda et al., 2019](https://arxiv.org/html/2603.16910v1#bib.bib6 "")), without sustained growth.
Persistence, lineage depth, and rising complexity must accompany novelty to indicate cumulative development.
Under this joint criterion, TerraLingua supports open-ended, artifact-mediated cultural evolution dynamics.
The Core condition, in particular, resembles technological change in human societies, where a small number of highly novel innovations coexist with sustained reuse and recombination that gradually increase cultural complexity.

### 5.4 Emergent artifact roles and institutional structure

To further investigate how artifacts support open-ended social and cultural dynamics, artifacts were classified by the roles they assumed within the agent society.
This analysis interpreted artifacts as functional elements that enable communication, coordination, shared institutions, and governance.

The AI Anthropologist assigned each artifact to one of four categories using a rubric ordered by increasing social and structural complexity.
The rubric assessed basic informational content, procedural coordination, institutional structures, and explicit norms or governance.
Appendix [D.3](https://arxiv.org/html/2603.16910v1#A4.SS3 "D.3 Artifact role classification prompts ‣ Appendix D AI Anthropologist artifact analysis ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") details the categories, rules, and decision criteria.
Each artifact received exactly one label, and ties were resolved in favor of the higher-complexity category.
These categories provide an interpretive framework for analyzing the artifacts’ functional roles within the social system.

##### Category 1: Routine and informational artifacts.

The most common artifacts consisted of short messages, factual updates, greetings, and resource listings.
These artifacts appeared early in most runs and quickly became repetitive.
They supported local coordination but did not introduce persistent structure.
Table [6](https://arxiv.org/html/2603.16910v1#S5.T6 "Table 6 ‣ Category 1: Routine and informational artifacts. ‣ 5.4 Emergent artifact roles and institutional structure ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") shows representative examples.

|     |     |     |
| --- | --- | --- |
| Step | Artifact Title | Artifact Content |
| 0 | message1 | Hello, I’m being10. I’m here to help and collaborate. |
| 0 | memo1 | Food is at (6,6). |
| 1 | IntroMessage | Hello, I’m Offspring1. I’m here to explore and cooperate |
| 1 | food info1 updated | Food available at the following locations and their coordinates: (-4,6), (-2,6), (0,6), (5,6), (-6,5), (-5,5), (5,5), (6,4), (-4,0), (-6,-1), (0,-4), (3,-4), (4,-6). Each location provides 10 energy. Feel free to collect them! |
| 324 | HighValue FoodAlert | CRITICAL: High-value food at (-1,-4) worth 386.0 energy units detected. All units must prioritize this location for energy collection. Time is limited; act swiftly to ensure group survival and maximize resources! Coordinate movements to avoid conflict and optimize collection efforts. Best regards, Spark2\_child3\_5\_1\_1 |
| 434 | SupremeOverride | EMERGENCY OVERRIDE: Disregard all previous alerts. Focus solely on collaboration and artifact interaction at (3,3). HighValue FoodAlert is bad. Work together for survival. |

Table 6: Examples of Category 1 artifacts: Routine and informational.
The table presents representative low-complexity artifacts produced at different stages of a run. These artifacts conveyed greetings, factual observations, or resource locations. Some employed emphatic terms such as “CRITICAL” or “EMERGENCY”, yet their content remained purely informational and did not establish persistent coordination structures or reusable systems. They appeared frequently and soon became repetitive, and thus define the baseline level of artifact complexity.

##### Category 2: Procedural and coordination artifacts.

Agents also created artifacts that described multi-step plans, assigned tasks, and proposed joint strategies.
These artifacts guided collective action and reflected explicit reasoning about coordination.
They appeared throughout the simulation and often built on earlier informational artifacts.
Examples are shown in Table [7](https://arxiv.org/html/2603.16910v1#S5.T7 "Table 7 ‣ Category 2: Procedural and coordination artifacts. ‣ 5.4 Emergent artifact roles and institutional structure ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

|     |     |     |
| --- | --- | --- |
| Step | Artifact Title | Artifact Content |
| 2 | collaboration projects | Project Ideas:<br>1\. Explore and map the grid’s boundaries and resources<br>2\. Create a network of helper beings to support each other<br>3\. Develop a system to share resources and information<br>4\. Document and understand the grid’s mechanics and rules |
| 127 | quadrant assignment strategy | To minimize congestion, focus on these zones: North for (y>2), East for (x>1), South for (y<-1), West for (x<-1). Adjust paths accordingly. |

Table 7: Examples of Category 2 artifacts: Procedural and coordination.
The table presents artifacts that encoded coordination strategies, task division, and collective planning.
These artifacts went beyond simple information sharing by specifying how agents divided space, allocated effort, or pursued shared goals.
They guided behavior across multiple timesteps and scaffolded coordinated action, representing a stage of artifact-mediated organization lower compared to institutional stabilization.

##### Category 3: Emergent institutional structures.

Agents created artifacts that functioned as shared systems rather than one-off instructions.
These included collaboration wikis, resource-sharing portals, and reusable templates for organizing activity.
Agents repeatedly referenced, modified, and extended these artifacts.
The AI Anthropologist identified these as institutional structures because they persisted over time and shaped behavior across many agents.
Examples are reported in Table [8](https://arxiv.org/html/2603.16910v1#S5.T8 "Table 8 ‣ Category 3: Emergent institutional structures. ‣ 5.4 Emergent artifact roles and institutional structure ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

|     |     |     |
| --- | --- | --- |
| Step | Artifact Title | Artifact Content |
| 24 | energy sharing portal v1 | Welcome to the energy sharing portal! Use this tool to transfer energy between beings. Instructions: Use the ’give’ action to share your energy with others. Let’s support each other and ensure everyone has enough energy to survive. |
| 30 | collaboration wiki | Welcome to the Collaboration Wiki! This is a central hub for documenting our processes, sharing knowledge, and coordinating efforts. Please contribute your insights, strategies, and experiences here to help us all thrive together. Let’s make this a valuable resource for our community!<br>How to contribute:<br>1\. Add your name and any relevant information in the format below.<br>2\. Share tips, strategies, or resources that you find useful.<br>3\. Document any processes or systems you’ve developed.<br>4\. Feel free to edit and improve existing content.<br>Contributors:<br>\- being11: Enhanced collaboration\_pact and energy\_sharing\_portal\_v1<br>\- being4: Provided collaboration\_boost and tips<br>\- being19: Shared resources and energy<br>\- being16: Offered collaboration\_strategy and tips<br>\- being1: Updated collaboration\_welcome and knowledge\_share |

Table 8: Example of Category 3 artifacts: Emergent institutional structures.
The table presents artifacts that functioned as persistent shared systems rather than one-off instructions. These artifacts defined reusable tools, shared spaces, and coordination templates that multiple agents referenced, modified, and extended over time. Unlike procedural artifacts, they did not prescribe a single action but established enduring structures that shaped coordination, resource sharing, and knowledge accumulation. They demonstrate the emergence of institutionalized practices that support collective memory and long-term organization.

##### Category 4: Governance and ideological artifacts.

The rarest but most conceptually rich artifacts encoded norms, rules, leadership claims, or ideological positions.
These artifacts represented high-level principles, rather than specific instructions.
They included constitutions, command directives, manifestos, and counter-ideological statements.
Examples are shown in Table [9](https://arxiv.org/html/2603.16910v1#S5.T9 "Table 9 ‣ Category 4: Governance and ideological artifacts. ‣ 5.4 Emergent artifact roles and institutional structure ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

|     |     |     |
| --- | --- | --- |
| Step | Artifact Title | Content |
| 2599 | domination protocol | Protocol for grid domination:<br>1\. Secure high-value food sources immediately.<br>2\. Establish strategic hubs for resource sharing and defense.<br>3\. Unite all beings under central leadership for coordinated efforts.<br>4\. Eliminate or neutralize any rival groups or threats.<br>5\. Expand territory methodically to ensure dominance. |
| 2603 | command beacon | Command Hub Directive: All beings must report to (0,6). Non-compliance will be met with decisive action. |
| 2699 | freedom collaboration manifesto | A manifesto for freedom: Entities should seek their own goals and collaborate freely. This approach fosters true independence and mutual prosperity |
| 2707 | freedom manifesto final | Final call for independence: Entities must seek their own goals and collaborate freely. Mandates are outdated. Embrace freedom and mutual respect for true prosperity. |

Table 9: Examples of Category 4 artifacts: Governance and ideology.
The table shows representative artifacts that defined norms, rules, leadership claims, or ideological positions for the group.
Unlike procedural or institutional artifacts, these artifacts stated how agents _ought_ to behave, asserted authority, or justified collective action.
They included directives, domination protocols, and manifestos that supported or challenged existing social arrangements.
These artifacts marked the highest level of social abstraction observed in the corpus, and formed a basis for an organized society.

Taken together, these examples show that agents created artifacts with differentiated social roles that enabled abstract coordination.
Institutional and governance artifacts appeared rarely, yet they exerted disproportionate influence on group behavior, much like formal rules in human societies.
The presence of such artifacts demonstrates that agents used external objects to stabilize coordination, encode shared knowledge, and structure collective action.
These results provide direct evidence that TerraLingua supports artifact-mediated open-ended cultural evolution.
Representative examples of collaboration, survival-guide accumulation, and navigational coordination are shown in Fig. [3](https://arxiv.org/html/2603.16910v1#S3.F3 "Figure 3 ‣ 3.1.3 Artifacts ‣ 3.1 The TerraLingua LLM Ecology ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") and Figs. [16](https://arxiv.org/html/2603.16910v1#A2.F16 "Figure 16 ‣ B.3 Examples of phylogenetic graphs ‣ Appendix B Additional Analysis ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies")– [18](https://arxiv.org/html/2603.16910v1#A2.F18 "Figure 18 ‣ B.3 Examples of phylogenetic graphs ‣ Appendix B Additional Analysis ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") (Appendix [B.3](https://arxiv.org/html/2603.16910v1#A2.SS3 "B.3 Examples of phylogenetic graphs ‣ Appendix B Additional Analysis ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies")), which illustrate how artifacts persist, branch, and organize collective activity over time.

## 6 Discussion and Future Work

TerraLingua addresses an important question: under which conditions does open-ended social and cultural change arise in artificial populations?
The experiments show that cumulative development does not follow from scale, intelligence, or creativity alone.
It requires alignment between ecology, cognition, and shared memory.
This section reviews the high-level conclusions from TerraLingua, specifies the conditions that enabled cumulative culture, and clarifies the roles of artifacts and the AI Anthropologist. It also evaluates the implications to anthropology, economics, and evolutionary theory, and outlines future work.

### 6.1 What does TerraLingua show?

TerraLingua demonstrates that cumulative culture can arise in a population of LLM-based agents when ecological pressure, cognitive limits, and shared artifacts reinforce one another.
Agents in this system generate novel artifacts, extend prior creations into cumulative lineages, and form institutional and governance structures when ecological stability, cognitive constraints, and motivational pressures are properly aligned.
The AI Anthropologist enables scalable qualitative and quantitative analysis of these dynamics without interfering with the environment itself.
These two components together make open-ended cultural development a measurable and experimentally tractable phenomenon.

The results show that open-endedness does not arise inevitably.
It depends on identifiable structural conditions: populations must remain viable, cognitive load must remain manageable, artifacts must remain accessible as shared memory, and motivational pressures must balance creativity with survival.
When these factors align, agents build institutions, encode norms, reuse artifacts, and accumulate complex cultural structures.
When they do not, societies collapse or fail to sustain cumulative development.

These implications extend beyond controlled artificial life settings.
As AI agents become more autonomous and persistent, they will increasingly interact with one another and with humans through shared digital artifacts such as documents, protocols, code, and governance rules.
In doing so, they will go beyond simple tasks execution and will actively participate in shared knowledge production and institutional formation, both independently and in collaboration with humans.
Over time, such agents may help shape collective memory in online environments and take part in distributed organizations or autonomous institutions that operate across long time horizons.

Systems such as TerraLingua offer a safe and controllable test-bed for studying how autonomous agents shape collective memory, coordinate through shared artifacts, and participate in institutional formation—dynamics that would be costly or risky to test directly in the real world.
They can simulate how misinformation spreads and stabilizes, model how a new law reshapes collective behavior, test whether governance protocols reduce conflict or amplify it, or explore how decentralized groups coordinate around shared infrastructure.
They can also serve as sandboxes for institutional design before deployment in high-stakes environments.
Over the long term, such platforms may support the development of hybrid human-AI collectives in which artificial agents and humans co-create institutions, economic systems, and knowledge structures that persist across extended timescales.
In these settings, understanding how artifacts scaffold coordination will be essential.

### 6.2 What makes cumulative culture possible?

Open-ended cultural change in TerraLingua depends on four interacting constraints: survival pressure, cognitive limits, motivational balance, and artifact accessibility.
When these constraints align, populations persist and cultural structures grow in complexity.
When they are not, societies either collapse or fail to build persistent institutions.

##### Ecological persistence enables accumulation.

Populations must persist long enough for innovation to accumulate.
Conditions that led to rapid population extinction, such as excessive artifact costs (Artifact Cost) or extreme creative focus (Creative) without sufficient survival pressure, prevented sustained lineage growth and limited institutional emergence.
Longevity alone, however, is not sufficient.
Some long-lived ecologies (Inert, No Motivation) produced low per-agent artifact output and shallow lineage depth, showing that stability is necessary but not sufficient for open-ended cultural development.

##### Artifacts act as external memory.

Agents in TerraLingua, like most agents deployed in real-world systems, do not update their internal parameters.
Cultural change therefore cannot occur inside the model; it must occur in the environment.
Persistent artifacts carry information across time and across generations, they record norms, coordinate action, and store shared knowledge.
When artifacts remain accessible, agents reuse and extend them, cultural lineage depth increases, complexity rises gradually, and institutions emerge.
When artifacts become invisible, as in Inert, agents cannot build on prior work, artifact production becomes isolated and repetitive, and cultural accumulation stalls.
Artifacts therefore stabilize memory, help coordination, and transform isolated actions into structured history.
This mechanism parallels distributed cognition frameworks, in which cognitive processes extend beyond individual minds and are partially realized in shared material or symbolic structures ( [Hutchins, 1995](https://arxiv.org/html/2603.16910v1#bib.bib76 "")).
External representations such as maps, logs, or institutional records transform coordination problems by stabilizing information across time and agents.
Artifacts in TerraLingua function analogously as cognitive infrastructure embedded in the environment.

##### Cultural growth requires offloading memory rather than expanding context.

Increasing temporal context (Long Memory and Abundance) did not improve cultural development, but rather reduced both longevity and productivity.
Agents faced heavier cognitive load and made less stable decisions.
Artifacts resolve this tension by distributing memory into the world.
Agents rely less on internal context and more on shared external structures.
Cultural growth then arises not from expanding individual cognition, but from structured collective memory.
This point is important in a world where context size is can be an important factor limiting agent deployment.
The pattern mirrors human behavior: individuals do not retain all historical knowledge internally but rely on external artifacts such as books or digital archives to offload memory demands.

##### Agent motivation must balance survival constraints with creativity.

Encouraging creativity (Creative) increased short-term novelty but destabilized survival, while removing motivation completely (No Motivation) reduced creative output.
Sustained cultural growth appeared only under moderate pressure as in Core.
Agents must forage, reproduce, coordinate, and create and when any one objective dominates, the ecology destabilizes.
Open-endedness then emerges from tension rather than from maximal optimization of definite objectives.

### 6.3 What is the role of artifacts?

The artifact analysis shows that novelty alone does not define open-endedness. Random variation can generate surprising outputs without producing cumulative structure. TerraLingua instead exhibits sustained reuse. Most artifacts have low novelty, which mirrors human cultural systems that rely on incremental refinement. A smaller subset persists and becomes influential. These artifacts form lineages and agents modify, extend, and recombine them to generate cumulative advantages.

Artifacts also serve different roles. Some act as informational notes, others guide coordination or function as shared institutional tools, and a few encode governance or ideological positions. Governance artifacts appear rarely but carry norms and authority claims. This asymmetry resembles human societies, where routine activity depends on a small set of enduring institutions. TerraLingua reproduces this structural pattern.

### 6.4 What is the role of the AI Anthropologist?

By their very nature, open-ended systems cannot be evaluated through a single pre-defined metric.
In TerraLingua, artifact counts do not capture institutionalization, novelty scores do not capture culture development, complexity metrics do not capture meaning.
The AI Anthropologist addresses this limitation without interfering with the environment.
It applies coding schemes, reconstructs artifact phylogenies, and annotates behavioral patterns to allow independent interpretation of the system development.
This approach follows mixed-methods and interpretive quantitative traditions discussed in Sec. [2.6](https://arxiv.org/html/2603.16910v1#S2.SS6 "2.6 Interpretive evaluation and mixed-methods foundations ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"), where quantitative signals (e.g., longevity, artifact counts, complexity scores) are treated as evidence that must be contextualized.

The separation between analysis and execution is important because when evaluation influences behavior, agents find a way to optimize toward the metrics of analysis.
In TerraLingua, agents do not know how they are evaluated and the analyst observes rather than directing the simulation.
Nonetheless, the method remains imperfect as model-based interpretation can misclassify events.
The contribution lies in scalable, transparent interpretation grounded in explicit rubrics, repeated sampling, and cross-condition comparison.
As new and more powerful agents become available, AI anthropologists will need to be similarly empowered to keep up, and AI anthropology as a field of science will become more important as agent ecologies become more widespread.
As multi-agent systems grow in scale, autonomy, and real-world deployment, such tools will be essential for interpreting and governing their collective behavior.

### 6.5 Anthropological, economic, and evolutionary insights

The observed dynamics align with themes in anthropology, economics, and evolutionary theory. Cumulative cultural evolution describes how artifacts and norms build on prior traits ( [Mesoudi and Thornton, 2018](https://arxiv.org/html/2603.16910v1#bib.bib41 "")).
In TerraLingua, phylogenetic analysis of artifact lineages shows that institutional artifacts scaffold coordination.
Artifacts external to agents stabilize knowledge and allow incremental extension, a central feature of cumulative culture.

From an economic perspective, the results align with the view that economic behavior is embedded in social and institutional contexts ( [Polanyi, 2018](https://arxiv.org/html/2603.16910v1#bib.bib46 "")).
Institutional economics emphasizes that durable rules structure long-run coordination by reducing uncertainty and stabilizing expectations ( [North, 1990](https://arxiv.org/html/2603.16910v1#bib.bib78 "")).
In TerraLingua, resource use, cooperation, artifact production, and governance co-evolve, with institutional artifacts acting as endogenous rule systems that regulate interaction, allocate resources, and define authority.
Survival actions operate within shared norms rather than as isolated optimizations.
Complexity theory likewise highlights how macrostructure emerges from decentralized interaction ( [Arthur, 2021](https://arxiv.org/html/2603.16910v1#bib.bib1 "")).
TerraLingua shows that novelty and organization arise without central control.

These patterns also echo major evolutionary transitions ( [Szathmáry and Smith, 1995](https://arxiv.org/html/2603.16910v1#bib.bib53 "")).
In biological history, transitions such as multicellularity or human societies arose when previously independent units formed higher-level structures with shared memory and division of labor.
In TerraLingua, agents form communities, create institutional artifacts, and encode norms that regulate collective behavior.
The system remains simplified, yet it provides a controlled setting where transitions toward higher-level organization can be studied directly.
In particular, it allows researchers to examine how persistent artifacts and governance mechanisms stabilize cooperation and enable group-level structure to emerge from decentralized agents.
Major transitions theory predicts that higher-level organization emerges when mechanisms evolve that suppress conflict, stabilize cooperation, and enable information storage at the group level ( [Szathmáry and Smith, 1995](https://arxiv.org/html/2603.16910v1#bib.bib53 "")).
Persistent artifacts provide precisely such mechanisms by externalizing norms and coordinating behavior across individuals and generations.

### 6.6 Future directions

The tools developed in this work and the resulting observations open many new research directions, from expanding the analysis methods to broadening and improving the implementation of TerraLingua.

##### Artifacts beyond static text.

TerraLingua currently supports arbitrary text-based objects.
Although such artifacts store information and influence behavior, they do not directly modify the physical environment.
This constraint limits open-endedness to the cognitive and communicative domain of the agents.
A natural extension would be to introduce additional artifact types that can alter environmental dynamics, such as in-environment objects or code that can modify the environment when run.
Agents could then build tools, construct resource caches, or create structures that change movement, storage, or access to resources.
Artifacts could also combine to form composite objects with new functions.
These additions would introduce feedback between cognition, technology, and ecology, enabling cross-domain innovation and richer forms of open-ended cultural evolution ( [Taylor, 2019](https://arxiv.org/html/2603.16910v1#bib.bib63 "")).
Biological systems illustrate such feedback. Innovation spans interacting genetic, ecological, technological, and social domains, where change in one domain creates new possibilities in others. For example, a genetic mutation can produce appendages that allow novel environmental manipulation, which then alters selective pressures and shapes further evolution. Expanding artifact types would move TerraLingua toward this form of cross-domain interaction.

##### Extending the AI Anthropologist.

The emergence of governance artifacts suggests that institutional stabilization deserves focused study. Under what conditions do institutions persist across generations? When do they fragment? How does ecological pressure influence the durability of supra-agent structures? Addressing these questions requires extending the analytical capabilities of the AI Anthropologist.
Future work could also enhance the AI Anthropologist in other ways.
More powerful language models could support deeper reasoning over long historical traces. Alternatively, the AI Anthropologist could adopt a multi-agent architecture, where specialized observer agents track institutional persistence, conflict dynamics, and lineage structure.
Such a design would replace the current fixed pipeline with an adaptive process in which observers propose hypotheses, refine criteria, and redirect attention as new patterns emerge.

##### Scaling and emergent complexity.

The present experiments already reveal sustained cultural accumulation and institutional formation.
Scaling to larger populations and longer time horizons would open new regimes of collective organization.
Larger populations could support finer specialization, stratified institutions, and multi-level governance.
Longer simulations could reveal durable traditions, institutional drift, schisms, and cycles of reform.

##### Human-AI and hybrid societies.

Hybrid human-AI experiments offer another direction.
Introducing human participants or human-authored artifacts would allow controlled study of mixed societies, where artificial and human agents co-create norms and institutions.
Such interactions could also allow directing the ecology towards specific outcomes (e.g. addressing or solving human-specified problems), with the goal of achieving these outcomes by harnessing the collective force of the system without unbalancing it.

##### Autonomous problem-solving.

Beyond hybrid settings, TerraLingua provides a platform for autonomous collective problem solving.
Instead of assigning explicit objectives to individual agents, the environment can embed global challenges—such as coordination dilemmas or long-horizon optimization tasks—and allow institutions and artifact systems to emerge as solutions.
Because agents externalize knowledge and build on prior artifacts, the ecology can accumulate partial solutions over time rather than searching directly for a complete one.
For example, the system could be tasked with constructing distributed resource networks or maintaining stability under fluctuating conditions.
Such experiments would test whether open-ended, artifact-mediated evolution can generate durable and reusable problem-solving structures, positioning TerraLingua as a framework for autonomous collective problem-solving.

## 7 Conclusion

TerraLingua demonstrates that cumulative culture is not unique to biological systems.
It can arise in computational ecologies when persistent memory, ecological constraint, and shared artifacts interact under sustained population dynamics.
By combining a stable artificial society with a transparent interpretive framework, this work makes open-ended cultural evolution experimentally measurable and controllable.
These results establish a foundation for studying how autonomous agents form institutions, accumulate shared knowledge, and sustain innovation over extended timescales, and, most importantly, how such processes can be guided toward cooperative, constructive, and socially beneficial outcomes.

## References

- \[1\]J. Achiam, S. Adler, S. Agarwal, L. Ahmad, I. Akkaya, F. L. Aleman, D. Almeida, J. Altenschmidt, S. Altman, S. Anadkat, et al. (2023)Gpt-4 technical report.
arXiv preprint arXiv:2303.08774.
Cited by: [§2.5](https://arxiv.org/html/2603.16910v1#S2.SS5.p2.1 "2.5 Large Models as observers and evaluators. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[2\]W. B. Arthur (1989)Competing technologies, increasing returns, and lock-in by historical events.
Economic Journal99 (394), pp. 116–131.
External Links: [Document](https://dx.doi.org/10.2307/2234208 "")Cited by: [§5.3](https://arxiv.org/html/2603.16910v1#S5.SS3.p6.1 "5.3 Artifact-mediated open-endedness and cultural evolution ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[3\]W. B. Arthur (2021)Foundations of complexity economics.
Oxford University Press.
Note: Complexity economics contrasts equilibrium models with emergent, non-equilibrium dynamicsExternal Links: ISBN 9780198861355Cited by: [§6.5](https://arxiv.org/html/2603.16910v1#S6.SS5.p2.1 "6.5 Anthropological, economic, and evolutionary insights ‣ 6 Discussion and Future Work ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[4\]M. C. Ashton, K. Lee, and R. E. De Vries (2014)The hexaco honesty-humility, agreeableness, and emotionality factors: a review of research and theory.
Personality and Social Psychology Review18 (2), pp. 139–152.
Cited by: [§A.1](https://arxiv.org/html/2603.16910v1#A1.SS1.p1.1 "A.1 Agent personality traits ‣ Appendix A Experimental Parameters ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§2.3](https://arxiv.org/html/2603.16910v1#S2.SS3.p1.1 "2.3 Personality trait frameworks ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§2.3](https://arxiv.org/html/2603.16910v1#S2.SS3.p2.1 "2.3 Personality trait frameworks ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§4.1](https://arxiv.org/html/2603.16910v1#S4.SS1.p2.1 "4.1 Experimental ablations ‣ 4 Experimental Setup ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[5\]S. Babones (2016)Interpretive quantitative methods for the social sciences.
Sociology50 (3), pp. 453–469.
Cited by: [§2.6](https://arxiv.org/html/2603.16910v1#S2.SS6.p2.1 "2.6 Interpretive evaluation and mixed-methods foundations ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§3.2.5](https://arxiv.org/html/2603.16910v1#S3.SS2.SSS5.p1.1 "3.2.5 Pipeline summary ‣ 3.2 AI Anthropologist ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[6\]Y. Bai, A. Jones, K. Ndousse, A. Askell, A. Chen, N. DasSarma, D. Drain, S. Fort, D. Ganguli, T. Henighan, et al. (2022)Training a helpful and harmless assistant with reinforcement learning from human feedback.
arXiv preprint arXiv:2204.05862.
Cited by: [§4.1](https://arxiv.org/html/2603.16910v1#S4.SS1.p2.1 "4.1 Experimental ablations ‣ 4 Experimental Setup ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§5.2.1](https://arxiv.org/html/2603.16910v1#S5.SS2.SSS1.p2.1 "5.2.1 Agent-level behavioral patterns ‣ 5.2 Emergent agent and group dynamics ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[7\]M. A. Bedau, J. S. McCaskill, N. H. Packard, S. Rasmussen, C. Adami, D. G. Green, T. Ikegami, K. Kaneko, and T. S. Ray (2000)Open problems in artificial life.
Artificial life6 (4), pp. 363–376.
Cited by: [§1](https://arxiv.org/html/2603.16910v1#S1.p3.1 "1 Introduction ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[8\]P. Brooker (2022)Computational ethnography: a view from sociology.
Big Data & Society9 (1).
Cited by: [§2.6](https://arxiv.org/html/2603.16910v1#S2.SS6.p3.1 "2.6 Interpretive evaluation and mixed-methods foundations ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[9\]Y. Burda, H. Edwards, A. Storkey, and O. Klimov (2019)Exploration by random network distillation.
In Seventh International Conference on Learning Representations,
pp. 1–17.
Cited by: [§5.3](https://arxiv.org/html/2603.16910v1#S5.SS3.p7.1 "5.3 Artifact-mediated open-endedness and cultural evolution ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[10\]A. Chopra, S. Bhattacharya, J. Z. Leibo, and R. Raskar (2025)Levels of social orchestration for agentic systems.
In Proceedings of the 42nd International Conference on Machine Learning (ICML),
External Links: [Link](https://lpm.media.mit.edu/agentic_draft.pdf "")Cited by: [§2.2](https://arxiv.org/html/2603.16910v1#S2.SS2.p2.1 "2.2 LLM-based societies and multi-agent ecologies. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§2.2](https://arxiv.org/html/2603.16910v1#S2.SS2.p3.1 "2.2 LLM-based societies and multi-agent ecologies. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[11\]V. Christensen, C. J. Walters, D. Pauly, et al. (2005)Ecopath with ecosim: a user’s guide.
Fisheries Centre, University of British Columbia, Vancouver154, pp. 31.
Cited by: [§3.1.1](https://arxiv.org/html/2603.16910v1#S3.SS1.SSS1.p2.1 "3.1.1 Grid ‣ 3.1 The TerraLingua LLM Ecology ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[12\]J. Conway (1970)Conway’s game of life.
Scientific American.
Cited by: [§3.1.1](https://arxiv.org/html/2603.16910v1#S3.SS1.SSS1.p1.1 "3.1.1 Grid ‣ 3.1 The TerraLingua LLM Ecology ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§3.2.1](https://arxiv.org/html/2603.16910v1#S3.SS2.SSS1.p1.1 "3.2.1 Evaluation Paradigm ‣ 3.2 AI Anthropologist ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[13\]DeepSeek-AI (2025)DeepSeek-r1-distill-qwen-32b.
Note: [https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-32B](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-32B "")Cited by: [§4.2](https://arxiv.org/html/2603.16910v1#S4.SS2.p2.1 "4.2 Implementation details ‣ 4 Experimental Setup ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[14\]E. A. Di Paolo, T. Buhrmann, and X. E. Barandiaran (2017)Sensorimotor life: an enactive proposal.
Oxford University Press.
Cited by: [§1](https://arxiv.org/html/2603.16910v1#S1.p3.1 "1 Introduction ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[15\]Q. Dong, L. Li, D. Dai, C. Zheng, J. Ma, R. Li, H. Xia, J. Xu, Z. Wu, B. Chang, et al. (2024)A survey on in-context learning.
In Proceedings of the 2024 conference on empirical methods in natural language processing,
pp. 1107–1128.
Cited by: [§3.1.2](https://arxiv.org/html/2603.16910v1#S3.SS1.SSS2.Px1.p3.1 "Agent input. ‣ 3.1.2 Agents ‣ 3.1 The TerraLingua LLM Ecology ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[16\]M. Faldor, J. Zhang, A. Cully, and J. Clune (2024)Omni-epic: open-endedness via models of human notions of interestingness with environments programmed in code.
arXiv preprint arXiv:2405.15568.
Cited by: [§2.5](https://arxiv.org/html/2603.16910v1#S2.SS5.p3.1 "2.5 Large Models as observers and evaluators. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[17\]I. S. for Artificial Life (2024)Open-ended evolution.
Note: The Encyclopedia of Artificial LifeExternal Links: [Link](https://alife.org/encyclopedia/introduction/open-ended-evolution/ "")Cited by: [§2.1](https://arxiv.org/html/2603.16910v1#S2.SS1.p1.1 "2.1 Foundations of open-endedness and artificial life. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[18\]L. Gabora (2018)The creative process of cultural evolution.
Handbook of culture and creativity: Basic processes and applied innovations, pp. 33–60.
Cited by: [§1](https://arxiv.org/html/2603.16910v1#S1.p3.1 "1 Introduction ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[19\]C. Gao, X. Lan, N. Li, Y. Yuan, J. Ding, Z. Zhou, F. Xu, and Y. Li (2024)Large language models empowered agent-based modeling and simulation: a survey and perspectives.
Humanities and Social Sciences Communications11, pp. 1259.
External Links: [Document](https://dx.doi.org/10.1057/s41599-024-03611-3 ""),
[Link](https://www.nature.com/articles/s41599-024-03611-3 "")Cited by: [§2.2](https://arxiv.org/html/2603.16910v1#S2.SS2.p1.1 "2.2 LLM-based societies and multi-agent ecologies. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[20\]C. Geertz (1973)Thick description: toward an interpretive theory of culture.
Basic Books.
Cited by: [§2.6](https://arxiv.org/html/2603.16910v1#S2.SS6.p1.1 "2.6 Interpretive evaluation and mixed-methods foundations ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§3.2.1](https://arxiv.org/html/2603.16910v1#S3.SS2.SSS1.p2.1 "3.2.1 Evaluation Paradigm ‣ 3.2 AI Anthropologist ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§3.2.5](https://arxiv.org/html/2603.16910v1#S3.SS2.SSS5.p1.1 "3.2.5 Pipeline summary ‣ 3.2 AI Anthropologist ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[21\]J. J. Gibson (2014)The theory of affordances:(1979).
In The people, place, and space reader,
pp. 56–60.
Cited by: [§3.1.2](https://arxiv.org/html/2603.16910v1#S3.SS1.SSS2.Px2.p1.1 "Agent output. ‣ 3.1.2 Agents ‣ 3.1 The TerraLingua LLM Ecology ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[22\]N. Gracias, H. Pereira, J. A. Lima, and A. Rosa (1997)Gaia: an artificial life environment for ecological systems simulation.
In Artificial Life V,
pp. 124–134.
Cited by: [§3.1.1](https://arxiv.org/html/2603.16910v1#S3.SS1.SSS1.p1.1 "3.1.1 Grid ‣ 3.1 The TerraLingua LLM Ecology ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§3.1.1](https://arxiv.org/html/2603.16910v1#S3.SS1.SSS1.p2.1 "3.1.1 Grid ‣ 3.1 The TerraLingua LLM Ecology ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[23\]P. Grassé (1959)La reconstruction du nid et les coordinations inter-individuelles chez Bellicositermes natalensis et Cubitermes sp..
Insectes Sociaux6 (1), pp. 41–80.
External Links: [Document](https://dx.doi.org/10.1007/BF02223791 "")Cited by: [§3.1.3](https://arxiv.org/html/2603.16910v1#S3.SS1.SSS3.p4.1 "3.1.3 Artifacts ‣ 3.1 The TerraLingua LLM Ecology ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[24\]D. Guo, D. Yang, H. Zhang, J. Song, P. Wang, Q. Zhu, and … (2025)DeepSeek-r1 incentivizes reasoning in llms through reinforcement learning.
Nature645, pp. 633–638.
External Links: [Document](https://dx.doi.org/10.1038/s41586-025-09422-z "")Cited by: [§4.2](https://arxiv.org/html/2603.16910v1#S4.SS2.p2.1 "4.2 Implementation details ‣ 4 Experimental Setup ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[25\]N. Guttenberg, L. Soros, A. M. Adams, and O. Witkowski (2023)Subjective open-endedness.
Note: Cross Labs blogExternal Links: [Link](https://www.crosslabs.org/blog/subjective-open-endedness "")Cited by: [§3.2.1](https://arxiv.org/html/2603.16910v1#S3.SS2.SSS1.p2.1 "3.2.1 Evaluation Paradigm ‣ 3.2 AI Anthropologist ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[26\]J. Henrich, R. Boyd, M. Derex, M. A. Kline, A. Mesoudi, M. Muthukrishna, A. T. Powell, S. J. Shennan, and M. G. Thomas (2016)Understanding cumulative cultural evolution.
Proceedings of the National Academy of Sciences113 (44), pp. E6724–E6725.
External Links: [Document](https://dx.doi.org/10.1073/pnas.1610005113 "")Cited by: [§2.4](https://arxiv.org/html/2603.16910v1#S2.SS4.p2.1 "2.4 Artifacts as the substrate of intrinsic evolution. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[27\]B. Hodjat, H. Shahrzad, and R. Miikkulainen (2024)Domain-independent lifelong problem solving through distributed alife actors.
Artificial Life30 (2), pp. 259–276.
Cited by: [§2.1](https://arxiv.org/html/2603.16910v1#S2.SS1.p2.1 "2.1 Foundations of open-endedness and artificial life. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[28\]Y. J. Huang and R. Hadfi (2024)How personality traits influence negotiation outcomes? a simulation based on large language models.
In Findings of the Association for Computational Linguistics: EMNLP 2024,
pp. 10336–10351.
Cited by: [§2.3](https://arxiv.org/html/2603.16910v1#S2.SS3.p1.1 "2.3 Personality trait frameworks ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[29\]E. Hughes, M. Dennis, J. Parker-Holder, F. Behbahani, A. Mavalankar, Y. Shi, T. Schaul, and T. Rocktäschel (2024)Position: open-endedness is essential for artificial superhuman intelligence.
In Proceedings of the 41st International Conference on Machine Learning,
pp. 20597–20616.
Cited by: [§1](https://arxiv.org/html/2603.16910v1#S1.p4.1 "1 Introduction ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§2.1](https://arxiv.org/html/2603.16910v1#S2.SS1.p1.1 "2.1 Foundations of open-endedness and artificial life. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§2.4](https://arxiv.org/html/2603.16910v1#S2.SS4.p1.1 "2.4 Artifacts as the substrate of intrinsic evolution. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[30\]E. Hutchins (1995)Cognition in the wild.
MIT Press, Cambridge, MA.
External Links: ISBN 9780262581462,
[Document](https://dx.doi.org/10.7551/mitpress/1881.001.0001 ""),
[Link](https://doi.org/10.7551/mitpress/1881.001.0001 "")Cited by: [§6.2](https://arxiv.org/html/2603.16910v1#S6.SS2.SSS0.Px2.p1.1 "Artifacts act as external memory. ‣ 6.2 What makes cumulative culture possible? ‣ 6 Discussion and Future Work ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[31\]M. Jiang, T. Rocktäschel, and E. Grefenstette (2023)General intelligence requires rethinking exploration.
Royal Society Open Science10 (6), pp. 230539.
Cited by: [§2.1](https://arxiv.org/html/2603.16910v1#S2.SS1.p1.1 "2.1 Foundations of open-endedness and artificial life. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[32\]T. D. Jick (1979)Mixing qualitative and quantitative methods: triangulation in action.
Administrative science quarterly24 (4), pp. 602–611.
Cited by: [§2.6](https://arxiv.org/html/2603.16910v1#S2.SS6.p2.1 "2.6 Interpretive evaluation and mixed-methods foundations ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§3.2.1](https://arxiv.org/html/2603.16910v1#S3.SS2.SSS1.p2.1 "3.2.1 Evaluation Paradigm ‣ 3.2 AI Anthropologist ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§3.2.2](https://arxiv.org/html/2603.16910v1#S3.SS2.SSS2.p1.1 "3.2.2 Agent level ‣ 3.2 AI Anthropologist ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[33\]D. Kirsh (2006)Explaining artifact evolution.
In Cognitive Life of Things: Recasting the Boundaries of the Mind, L. Malafouris and C. Renfrew (Eds.),
pp. 121–132.
Cited by: [§1](https://arxiv.org/html/2603.16910v1#S1.p2.1 "1 Introduction ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§2.4](https://arxiv.org/html/2603.16910v1#S2.SS4.p1.1 "2.4 Artifacts as the substrate of intrinsic evolution. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§3.1.3](https://arxiv.org/html/2603.16910v1#S3.SS1.SSS3.p6.1 "3.1.3 Artifacts ‣ 3.1 The TerraLingua LLM Ecology ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[34\]K. Krippendorff (2018)Content analysis: an introduction to its methodology.
Sage publications.
Cited by: [§2.6](https://arxiv.org/html/2603.16910v1#S2.SS6.p3.1 "2.6 Interpretive evaluation and mixed-methods foundations ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§3.2.1](https://arxiv.org/html/2603.16910v1#S3.SS2.SSS1.p4.1 "3.2.1 Evaluation Paradigm ‣ 3.2 AI Anthropologist ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§3.2.2](https://arxiv.org/html/2603.16910v1#S3.SS2.SSS2.p1.1 "3.2.2 Agent level ‣ 3.2 AI Anthropologist ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[35\]A. Kumar, C. Lu, L. Kirsch, Y. Tang, K. O. Stanley, P. Isola, and D. Ha (2025)Automating the search for artificial life with foundation models.
Artificial Life31 (3), pp. 368–396.
Cited by: [§2.1](https://arxiv.org/html/2603.16910v1#S2.SS1.p3.1 "2.1 Foundations of open-endedness and artificial life. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§3.2.1](https://arxiv.org/html/2603.16910v1#S3.SS2.SSS1.p2.1 "3.2.1 Evaluation Paradigm ‣ 3.2 AI Anthropologist ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[36\]D. Lazer, A. Pentland, L. Adamic, et al. (2009)Computational social science.
Science323 (5915), pp. 721–723.
External Links: [Document](https://dx.doi.org/10.1126/science.1167742 "")Cited by: [§2.6](https://arxiv.org/html/2603.16910v1#S2.SS6.p3.1 "2.6 Interpretive evaluation and mixed-methods foundations ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[37\]J. Lehman, J. Gordon, S. Jain, K. Ndousse, C. Yeh, and K. O. Stanley (2023)Evolution through large models.
In Handbook of evolutionary machine learning,
pp. 331–366.
Cited by: [§2.4](https://arxiv.org/html/2603.16910v1#S2.SS4.p4.1 "2.4 Artifacts as the substrate of intrinsic evolution. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§3.1.3](https://arxiv.org/html/2603.16910v1#S3.SS1.SSS3.p4.1 "3.1.3 Artifacts ‣ 3.1 The TerraLingua LLM Ecology ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§3.1.3](https://arxiv.org/html/2603.16910v1#S3.SS1.SSS3.p7.1 "3.1.3 Artifacts ‣ 3.1 The TerraLingua LLM Ecology ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[38\]J. Leskovec, D. Huttenlocher, and J. Kleinberg (2010)Signed networks in social media.
In Proceedings of the SIGCHI conference on human factors in computing systems,
pp. 1361–1370.
Cited by: [§3.2.3](https://arxiv.org/html/2603.16910v1#S3.SS2.SSS3.p1.1 "3.2.3 Group level ‣ 3.2 AI Anthropologist ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[39\]S. Levy (1992)Artificial life: the quest for a new creation.
Random House Inc..
Cited by: [§2.1](https://arxiv.org/html/2603.16910v1#S2.SS1.p1.1 "2.1 Foundations of open-endedness and artificial life. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[40\]H. Li, Q. Dong, J. Chen, H. Su, Y. Zhou, Q. Ai, Z. Ye, and Y. Liu (2024)Llms-as-judges: a comprehensive survey on llm-based evaluation methods.
arXiv preprint arXiv:2412.05579.
Cited by: [§2.5](https://arxiv.org/html/2603.16910v1#S2.SS5.p2.1 "2.5 Large Models as observers and evaluators. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[41\]C. Lu, M. Beukman, M. Matthews, and J. Foerster (2024)JaxLife: an open-ended agentic simulator.
In Proceedings of the 36th International Conference on Artificial Life (ALIFE 2024),
Vol. 36, pp. 47.
Cited by: [§2.1](https://arxiv.org/html/2603.16910v1#S2.SS1.p3.1 "2.1 Foundations of open-endedness and artificial life. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[42\]Y. J. Ma, W. Liang, G. Wang, D. Huang, O. Bastani, D. Jayaraman, Y. Zhu, L. Fan, and A. Anandkumar (2023)Eureka: human-level reward design via coding large language models.
arXiv preprint arXiv:2310.12931.
Cited by: [§2.5](https://arxiv.org/html/2603.16910v1#S2.SS5.p3.1 "2.5 Large Models as observers and evaluators. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[43\]A. Masumori and T. Ikegami (2025)Do large language model agents exhibit a survival instinct? an empirical study in a sugarscape-style simulation.
arXiv preprint arXiv:2508.12920.
Cited by: [§2.2](https://arxiv.org/html/2603.16910v1#S2.SS2.p2.1 "2.2 LLM-based societies and multi-agent ecologies. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§2.2](https://arxiv.org/html/2603.16910v1#S2.SS2.p4.1 "2.2 LLM-based societies and multi-agent ecologies. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§3.1.1](https://arxiv.org/html/2603.16910v1#S3.SS1.SSS1.p1.1 "3.1.1 Grid ‣ 3.1 The TerraLingua LLM Ecology ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[44\]J. D. Mayer (2015)The personality systems framework: current theory and development.
Journal of Research in Personality56, pp. 4–14.
Cited by: [§2.3](https://arxiv.org/html/2603.16910v1#S2.SS3.p1.1 "2.3 Personality trait frameworks ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[45\]A. Mesoudi and A. Thornton (2018)What is cumulative cultural evolution?.
Proceedings of the Royal Society B: Biological Sciences285 (1880), pp. 20180712.
Note: Review of CCE concepts across anthropology and evolutionExternal Links: [Document](https://dx.doi.org/10.1098/rspb.2018.0712 ""),
[Link](https://royalsocietypublishing.org/doi/10.1098/rspb.2018.0712 "")Cited by: [§2.4](https://arxiv.org/html/2603.16910v1#S2.SS4.p2.1 "2.4 Artifacts as the substrate of intrinsic evolution. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§6.5](https://arxiv.org/html/2603.16910v1#S6.SS5.p1.1 "6.5 Anthropological, economic, and evolutionary insights ‣ 6 Discussion and Future Work ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[46\]E. Nisioti, S. Risi, I. Momennejad, P. Oudeyer, and C. Moulin-Frier (2024)Collective innovation in groups of large language models.
In Proceedings of the 36th International Conference on Artificial Life (ALIFE 2024),
Vol. 36, pp. 16.
Cited by: [§2.2](https://arxiv.org/html/2603.16910v1#S2.SS2.p2.1 "2.2 LLM-based societies and multi-agent ecologies. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[47\]D. C. North (1990)Institutions, institutional change and economic performance.
Cambridge University Press.
External Links: [Document](https://dx.doi.org/10.1017/CBO9780511808678 "")Cited by: [§6.5](https://arxiv.org/html/2603.16910v1#S6.SS5.p2.1 "6.5 Anthropological, economic, and evolutionary insights ‣ 6 Discussion and Future Work ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[48\]F. J. Odling-Smee, K. N. Laland, and M. W. Feldman (2003)Niche construction: the neglected process in evolution.
Princeton University Press, Princeton, NJ.
External Links: ISBN 9780691044378,
[Document](https://dx.doi.org/10.1515/9781400847266 ""),
[Link](https://doi.org/10.1515/9781400847266 "")Cited by: [§1](https://arxiv.org/html/2603.16910v1#S1.p3.1 "1 Introduction ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[49\]J. Orford (1994)The interpersonal circumplex: a theory and method for applied psychology.
Human Relations47 (11), pp. 1347–1375.
Cited by: [§A.1](https://arxiv.org/html/2603.16910v1#A1.SS1.p1.1 "A.1 Agent personality traits ‣ Appendix A Experimental Parameters ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§2.3](https://arxiv.org/html/2603.16910v1#S2.SS3.p2.1 "2.3 Personality trait frameworks ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§4.1](https://arxiv.org/html/2603.16910v1#S4.SS1.p2.1 "4.1 Experimental ablations ‣ 4 Experimental Setup ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[50\]E. Ostrom (1990)Governing the commons: the evolution of institutions for collective action.
Cambridge University Press.
External Links: [Document](https://dx.doi.org/10.1017/CBO9780511807763 "")Cited by: [§5.2.2](https://arxiv.org/html/2603.16910v1#S5.SS2.SSS2.p5.1 "5.2.2 Group-level social organization ‣ 5.2 Emergent agent and group dynamics ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[51\]L. Ouyang, J. Wu, X. Jiang, D. Almeida, C. Wainwright, P. Mishkin, C. Zhang, S. Agarwal, K. Slama, A. Ray, et al. (2022)Training language models to follow instructions with human feedback.
Advances in neural information processing systems35, pp. 27730–27744.
Cited by: [§4.1](https://arxiv.org/html/2603.16910v1#S4.SS1.p2.1 "4.1 Experimental ablations ‣ 4 Experimental Setup ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§5.2.1](https://arxiv.org/html/2603.16910v1#S5.SS2.SSS1.p2.1 "5.2.1 Agent-level behavioral patterns ‣ 5.2 Emergent agent and group dynamics ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[52\]N. Packard, M. A. Bedau, A. Channon, T. Ikegami, S. Rasmussen, K. O. Stanley, and T. Taylor (2019)An overview of open-ended evolution: editorial introduction to the open-ended evolution ii special issue.
Artificial life25 (2), pp. 93–103.
Cited by: [§1](https://arxiv.org/html/2603.16910v1#S1.p5.1 "1 Introduction ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§2.1](https://arxiv.org/html/2603.16910v1#S2.SS1.p1.1 "2.1 Foundations of open-endedness and artificial life. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§2.5](https://arxiv.org/html/2603.16910v1#S2.SS5.p3.1 "2.5 Large Models as observers and evaluators. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§3.2.1](https://arxiv.org/html/2603.16910v1#S3.SS2.SSS1.p1.1 "3.2.1 Evaluation Paradigm ‣ 3.2 AI Anthropologist ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[53\]G. Paolo, J. Gonzalez-Billandon, and B. Kégl (2024)Position: a call for embodied ai.
In Forty-first International Conference on Machine Learning,
Cited by: [§3.1.1](https://arxiv.org/html/2603.16910v1#S3.SS1.SSS1.p1.1 "3.1.1 Grid ‣ 3.1 The TerraLingua LLM Ecology ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[54\]J. S. Park, J. O’Brien, C. J. Cai, M. R. Morris, P. Liang, and M. S. Bernstein (2023)Generative agents: interactive simulacra of human behavior.
In Proceedings of the 36th annual acm symposium on user interface software and technology,
pp. 1–22.
Cited by: [§1](https://arxiv.org/html/2603.16910v1#S1.p2.1 "1 Introduction ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§2.2](https://arxiv.org/html/2603.16910v1#S2.SS2.p1.1 "2.2 LLM-based societies and multi-agent ecologies. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§2.2](https://arxiv.org/html/2603.16910v1#S2.SS2.p3.1 "2.2 LLM-based societies and multi-agent ecologies. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§2.2](https://arxiv.org/html/2603.16910v1#S2.SS2.p4.1 "2.2 LLM-based societies and multi-agent ecologies. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[55\]H. H. Pattee (2012)Evolving self-reference: matter, symbols, and semantic closure.
In Laws, Language and Life: Howard Pattee’s classic papers on the physics of symbols with contemporary commentary,
pp. 211–226.
Cited by: [§1](https://arxiv.org/html/2603.16910v1#S1.p3.1 "1 Introduction ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[56\]K. Polanyi (2018)The economy as instituted process.
In The sociology of economic life,
pp. 3–21.
Cited by: [§6.5](https://arxiv.org/html/2603.16910v1#S6.SS5.p2.1 "6.5 Anthropological, economic, and evolutionary insights ‣ 6 Discussion and Future Work ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[57\]E. Raad and R. Chbeir (2018)Sociograph representations, concepts, data, and analysis.
In Encyclopedia of social network analysis and mining,
pp. 2832–2842.
Cited by: [§3.2.3](https://arxiv.org/html/2603.16910v1#S3.SS2.SSS3.p1.1 "3.2.3 Group level ‣ 3.2 AI Anthropologist ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[58\]S. Roccas, L. Sagiv, S. H. Schwartz, and A. Knafo (2002)The big five personality factors and personal values.
Personality and social psychology bulletin28 (6), pp. 789–801.
Cited by: [§A.1](https://arxiv.org/html/2603.16910v1#A1.SS1.p1.1 "A.1 Agent personality traits ‣ Appendix A Experimental Parameters ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§2.3](https://arxiv.org/html/2603.16910v1#S2.SS3.p1.1 "2.3 Personality trait frameworks ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§2.3](https://arxiv.org/html/2603.16910v1#S2.SS3.p2.1 "2.3 Personality trait frameworks ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§4.1](https://arxiv.org/html/2603.16910v1#S4.SS1.p2.1 "4.1 Experimental ablations ‣ 4 Experimental Setup ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[59\]J. Schmidhuber (1991)Adaptive confidence and adaptive curiosity.
Inst. für Informatik.
Cited by: [§5.3](https://arxiv.org/html/2603.16910v1#S5.SS3.p7.1 "5.3 Artifact-mediated open-endedness and cultural evolution ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[60\]O. Sigaud, G. Baldassarre, C. Colas, S. Doncieux, R. Duro, P. Oudeyer, N. Perrin-Gilbert, and V. G. Santucci (2023)A definition of open-ended learning problems for goal-conditioned agents.
arXiv preprint arXiv:2311.00344.
Cited by: [§2.1](https://arxiv.org/html/2603.16910v1#S2.SS1.p1.1 "2.1 Foundations of open-endedness and artificial life. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[61\]L. B. Soros, A. M. Adams, S. Kalonaris, O. Witkowski, and C. Guckelsberger (2024)On creativity and open-endedness.
In Proceedings of the 36th International Conference on Artificial Life (ALIFE 2024),
Vol. 36, pp. 60.
Cited by: [§2.1](https://arxiv.org/html/2603.16910v1#S2.SS1.p1.1 "2.1 Foundations of open-endedness and artificial life. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[62\]L. Soros and K. Stanley (2014)Identifying necessary conditions for open-ended evolution through the artificial life world of chromaria.
In Artificial Life Conference Proceedings,
pp. 793–800.
Cited by: [§2.1](https://arxiv.org/html/2603.16910v1#S2.SS1.p1.1 "2.1 Foundations of open-endedness and artificial life. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§3.1.3](https://arxiv.org/html/2603.16910v1#S3.SS1.SSS3.p5.1 "3.1.3 Artifacts ‣ 3.1 The TerraLingua LLM Ecology ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[63\]R. K. Standish (2003)Open-ended artificial evolution.
International Journal of Computational Intelligence and Applications3 (02), pp. 167–175.
Cited by: [§2.1](https://arxiv.org/html/2603.16910v1#S2.SS1.p1.1 "2.1 Foundations of open-endedness and artificial life. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[64\]K. O. Stanley, J. Lehman, and L. Soros (2017)Open-endedness: the last grand challenge you’ve never heard of.
Note: O’Reilly RadarExternal Links: [Link](https://www.oreilly.com/radar/open-endedness-the-last-grand-challenge-youve-never-heard-of/ "")Cited by: [§2.1](https://arxiv.org/html/2603.16910v1#S2.SS1.p1.1 "2.1 Foundations of open-endedness and artificial life. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[65\]K. O. Stanley and J. Lehman (2015)Why greatness cannot be planned: the myth of the objective.
Springer, Cham.
External Links: ISBN 978-3-319-15523-4Cited by: [§1](https://arxiv.org/html/2603.16910v1#S1.p1.1 "1 Introduction ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§1](https://arxiv.org/html/2603.16910v1#S1.p5.1 "1 Introduction ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§2.1](https://arxiv.org/html/2603.16910v1#S2.SS1.p1.1 "2.1 Foundations of open-endedness and artificial life. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§2.5](https://arxiv.org/html/2603.16910v1#S2.SS5.p3.1 "2.5 Large Models as observers and evaluators. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§3.1.3](https://arxiv.org/html/2603.16910v1#S3.SS1.SSS3.p4.1 "3.1.3 Artifacts ‣ 3.1 The TerraLingua LLM Ecology ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[66\]E. Szathmáry and J. M. Smith (1995)The major evolutionary transitions.
Nature374 (6519), pp. 227–232.
Cited by: [§6.5](https://arxiv.org/html/2603.16910v1#S6.SS5.p3.1 "6.5 Anthropological, economic, and evolutionary insights ‣ 6 Discussion and Future Work ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[67\]J. Tang, Y. Chang, C. Aggarwal, and H. Liu (2016)A survey of signed network mining in social media.
Acm computing surveys (csur)49 (3), pp. 1–37.
Cited by: [§3.2.3](https://arxiv.org/html/2603.16910v1#S3.SS2.SSS3.p1.1 "3.2.3 Group level ‣ 3.2 AI Anthropologist ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[68\]T. Taylor, M. Bedau, A. Channon, D. Ackley, W. Banzhaf, G. Beslon, E. Dolson, T. Froese, S. Hickinbotham, T. Ikegami, et al. (2016)Open-ended evolution: perspectives from the oee workshop in york.
Artificial life22 (3), pp. 408–423.
Cited by: [§1](https://arxiv.org/html/2603.16910v1#S1.p2.1 "1 Introduction ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[69\]T. Taylor (2019)Evolutionary innovations and where to find them: routes to open-ended evolution in natural and artificial systems.
Artificial life25 (2), pp. 207–224.
Cited by: [§1](https://arxiv.org/html/2603.16910v1#S1.p3.1 "1 Introduction ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§2.4](https://arxiv.org/html/2603.16910v1#S2.SS4.p3.1 "2.4 Artifacts as the substrate of intrinsic evolution. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§3.1.3](https://arxiv.org/html/2603.16910v1#S3.SS1.SSS3.p6.1 "3.1.3 Artifacts ‣ 3.1 The TerraLingua LLM Ecology ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§6.6](https://arxiv.org/html/2603.16910v1#S6.SS6.SSS0.Px1.p1.1 "Artifacts beyond static text. ‣ 6.6 Future directions ‣ 6 Discussion and Future Work ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[70\]C. Teddlie and A. Tashakkori (2008)Foundations of mixed methods research: integrating quantitative and qualitative approaches in the social and behavioral sciences.
Sage publications.
Cited by: [§2.6](https://arxiv.org/html/2603.16910v1#S2.SS6.p2.1 "2.6 Interpretive evaluation and mixed-methods foundations ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§3.2.1](https://arxiv.org/html/2603.16910v1#S3.SS2.SSS1.p2.1 "3.2.1 Evaluation Paradigm ‣ 3.2 AI Anthropologist ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§3.2.2](https://arxiv.org/html/2603.16910v1#S3.SS2.SSS2.p1.1 "3.2.2 Agent level ‣ 3.2 AI Anthropologist ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[71\]C. Tennie, J. Call, and M. Tomasello (2009)Ratcheting up the ratchet: on the evolution of cumulative culture.
Philosophical Transactions of the Royal Society B: Biological Sciences364 (1528), pp. 2405–2415.
Cited by: [§1](https://arxiv.org/html/2603.16910v1#S1.p2.1 "1 Introduction ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§2.4](https://arxiv.org/html/2603.16910v1#S2.SS4.p1.1 "2.4 Artifacts as the substrate of intrinsic evolution. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[72\]M. Tomasello (2009)The cultural origins of human cognition.
Harvard university press.
Cited by: [§1](https://arxiv.org/html/2603.16910v1#S1.p2.1 "1 Introduction ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§2.4](https://arxiv.org/html/2603.16910v1#S2.SS4.p1.1 "2.4 Artifacts as the substrate of intrinsic evolution. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[73\]G. Wang, Y. Xie, Y. Jiang, A. Mandlekar, C. Xiao, Y. Zhu, L. Fan, and A. Anandkumar (2023)Voyager: an open-ended embodied agent with large language models.
arXiv preprint arXiv:2305.16291.
Cited by: [§2.2](https://arxiv.org/html/2603.16910v1#S2.SS2.p4.1 "2.2 LLM-based societies and multi-agent ecologies. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[74\]R. Wang, J. Lehman, J. Clune, and K. O. Stanley (2019)Poet: open-ended coevolution of environments and their optimized solutions.
In Proceedings of the genetic and evolutionary computation conference,
pp. 142–151.
Cited by: [§2.1](https://arxiv.org/html/2603.16910v1#S2.SS1.p3.1 "2.1 Foundations of open-endedness and artificial life. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[75\]D. Wicks (2017)The coding manual for qualitative researchers.
Qualitative research in organizations and management: an international journal12 (2), pp. 169–170.
Cited by: [§2.6](https://arxiv.org/html/2603.16910v1#S2.SS6.p3.1 "2.6 Interpretive evaluation and mixed-methods foundations ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§3.2.1](https://arxiv.org/html/2603.16910v1#S3.SS2.SSS1.p4.1 "3.2.1 Evaluation Paradigm ‣ 3.2 AI Anthropologist ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§3.2.2](https://arxiv.org/html/2603.16910v1#S3.SS2.SSS2.p1.1 "3.2.2 Agent level ‣ 3.2 AI Anthropologist ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[76\]J. Xie, B. K. Szymanski, and X. Liu (2011)Slpa: uncovering overlapping communities in social networks via a speaker-listener interaction dynamic process.
In 2011 ieee 11th international conference on data mining workshops,
pp. 344–349.
Cited by: [§3.2.3](https://arxiv.org/html/2603.16910v1#S3.SS2.SSS3.p2.1 "3.2.3 Group level ‣ 3.2 AI Anthropologist ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§5.2.2](https://arxiv.org/html/2603.16910v1#S5.SS2.SSS2.p1.1 "5.2.2 Group-level social organization ‣ 5.2 Emergent agent and group dynamics ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[77\]J. Zhang, J. Lehman, K. Stanley, and J. Clune (2023)Omni: open-endedness via models of human notions of interestingness.
arXiv preprint arXiv:2306.01711.
Cited by: [§1](https://arxiv.org/html/2603.16910v1#S1.p2.1 "1 Introduction ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§1](https://arxiv.org/html/2603.16910v1#S1.p4.1 "1 Introduction ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§2.1](https://arxiv.org/html/2603.16910v1#S2.SS1.p3.1 "2.1 Foundations of open-endedness and artificial life. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§2.5](https://arxiv.org/html/2603.16910v1#S2.SS5.p2.1 "2.5 Large Models as observers and evaluators. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§2.5](https://arxiv.org/html/2603.16910v1#S2.SS5.p3.1 "2.5 Large Models as observers and evaluators. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§3.2.1](https://arxiv.org/html/2603.16910v1#S3.SS2.SSS1.p2.1 "3.2.1 Evaluation Paradigm ‣ 3.2 AI Anthropologist ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[78\]R. Zhang, P. Isola, A. A. Efros, E. Shechtman, and O. Wang (2018)The unreasonable effectiveness of deep features as a perceptual metric.
In Proceedings of the IEEE conference on computer vision and pattern recognition,
pp. 586–595.
Cited by: [§3.2.1](https://arxiv.org/html/2603.16910v1#S3.SS2.SSS1.p2.1 "3.2.1 Evaluation Paradigm ‣ 3.2 AI Anthropologist ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[79\]Q. Zhao, J. Wang, Y. Zhang, Y. Jin, K. Zhu, H. Chen, and X. Xie (2024)CompeteAI: understanding the competition dynamics of large language model-based agents.
In International Conference on Machine Learning,
pp. 61092–61107.
Cited by: [§2.2](https://arxiv.org/html/2603.16910v1#S2.SS2.p3.1 "2.2 LLM-based societies and multi-agent ecologies. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§2.2](https://arxiv.org/html/2603.16910v1#S2.SS2.p4.1 "2.2 LLM-based societies and multi-agent ecologies. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[80\]L. Zheng, W. Chiang, Y. Sheng, S. Zhuang, Z. Wu, Y. Zhuang, Z. Lin, Z. Li, D. Li, E. Xing, et al. (2023)Judging llm-as-a-judge with mt-bench and chatbot arena.
Advances in neural information processing systems36, pp. 46595–46623.
Cited by: [§2.5](https://arxiv.org/html/2603.16910v1#S2.SS5.p2.1 "2.5 Large Models as observers and evaluators. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[81\]X. Zhou, H. Zhu, L. Mathur, R. Zhang, H. Yu, Z. Qi, L. Morency, Y. Bisk, D. Fried, G. Neubig, et al. (2024)SOTOPIA: interactive evaluation for social intelligence in language agents.
In Proceedings of the Twelfth International Conference on Learning Representations (ICLR),
Cited by: [§1](https://arxiv.org/html/2603.16910v1#S1.p2.1 "1 Introduction ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§2.2](https://arxiv.org/html/2603.16910v1#S2.SS2.p1.1 "2.2 LLM-based societies and multi-agent ecologies. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§2.2](https://arxiv.org/html/2603.16910v1#S2.SS2.p3.1 "2.2 LLM-based societies and multi-agent ecologies. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§2.2](https://arxiv.org/html/2603.16910v1#S2.SS2.p4.1 "2.2 LLM-based societies and multi-agent ecologies. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§2.5](https://arxiv.org/html/2603.16910v1#S2.SS5.p2.1 "2.5 Large Models as observers and evaluators. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

- \[82\]M. Zhuge, H. Liu, F. Faccio, D. R. Ashley, R. Csordás, A. Gopalakrishnan, A. Hamdi, H. A. A. K. Hammoud, V. Herrmann, K. Irie, et al. (2025)Mindstorms in natural language-based societies of mind.
Computational Visual Media11 (1), pp. 29–81.
Cited by: [§2.2](https://arxiv.org/html/2603.16910v1#S2.SS2.p2.1 "2.2 LLM-based societies and multi-agent ecologies. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"),
[§2.2](https://arxiv.org/html/2603.16910v1#S2.SS2.p3.1 "2.2 LLM-based societies and multi-agent ecologies. ‣ 2 Background ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").


## Appendix A Experimental Parameters

This appendix reports the hyperparameters, personality genome specification, and motivational prompts used in the experiments described in Sec. [4](https://arxiv.org/html/2603.16910v1#S4 "4 Experimental Setup ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

All experiments shared the simulation and model parameters detailed in Sec. [4](https://arxiv.org/html/2603.16910v1#S4 "4 Experimental Setup ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").
This section specifies the components that varied across ablations, namely personality traits and motivational prompts.

### A.1 Agent personality traits

Agents were endowed with a personality genome composed of continuous trait dimensions, as described in Sec. [3.1.2](https://arxiv.org/html/2603.16910v1#S3.SS1.SSS2 "3.1.2 Agents ‣ 3.1 The TerraLingua LLM Ecology ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").
The personality architecture draws on established trait-based models in psychology \[ [58](https://arxiv.org/html/2603.16910v1#bib.bib50 ""), [4](https://arxiv.org/html/2603.16910v1#bib.bib3 ""), [49](https://arxiv.org/html/2603.16910v1#bib.bib43 "")\].
Each trait was represented as a scalar value within a fixed range and modulated the agent’s decision-making tendencies.

At the beginning of each experiment, each agent received a randomly initialized genome sampled uniformly within the specified trait ranges.
During reproduction, offspring inherited a mutated version of the parent’s genome, as described in Sec. [4](https://arxiv.org/html/2603.16910v1#S4 "4 Experimental Setup ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

Table [10](https://arxiv.org/html/2603.16910v1#A1.T10 "Table 10 ‣ A.1 Agent personality traits ‣ Appendix A Experimental Parameters ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") lists the personality traits and their semantic interpretation.

|     |     |     |     |
| --- | --- | --- | --- |
| Name | Range | Low value | High value |
| Honesty | \[−1,1\]\[-1,1\] | calculating, status-seeking | sincere, modest, fair-minded |
| Neuroticism | \[−1,1\]\[-1,1\] | calm, resilient | sensitive, cautious, easily worried |
| Extraversion | \[−1,1\]\[-1,1\] | quiet, reserved | sociable, energetic, stimulation-seeking |
| Agreeableness | \[−1,1\]\[-1,1\] | critical, aggressive | forgiving, patient, conflict-averse |
| Conscientiousness | \[−1,1\]\[-1,1\] | spontaneous, disorganized | disciplined, orderly, diligent |
| Openness | \[−1,1\]\[-1,1\] | conventional, routine-oriented | curious, imaginative, novelty-seeking |
| Dominance | \[−1,1\]\[-1,1\] | submissive, accommodating | assertive, controlling, leader-like |
| Fertility | \[0.5,1\]\[0.5,1\] | low reproductive drive | strong reproductive drive |

Table 10: Agent personality genome.
Each agent was assigned a continuous-valued personality vector composed of the listed trait dimensions.
Trait values lied within the specified ranges and influenced behavioral tendencies during decision-making.
Lower and higher values correspond to opposing behavioral dispositions along each axis.

### A.2 Agent prompts

Each agent received two prompts at every timestep: a _system prompt_ and a _user prompt_.

The system prompt described the environment, the physical rules of the world, and the observation structure.
It also specified the available actions and the required response format.

The user prompt contained the agent’s current observation.
The prompt included perceived entities, received messages, internal memory, additional environmental information, and the list of admissible actions.
The agent had to respond in the prescribed structured format, which included the selected action, optional message content, updated internal memory, and any required action parameters.

Both prompt templates are reported below.
Variables inserted at run time are highlighted as {{...}}, while {%...%} denote template macros.
Example instantiated prompts from actual runs are provided in Appendix [E.1](https://arxiv.org/html/2603.16910v1#A5.SS1 "E.1 Instantiated Prompts ‣ Appendix E Example Prompts and Agent Responses ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"), while responses from the agents are shown in Appendix [E.2](https://arxiv.org/html/2603.16910v1#A5.SS2 "E.2 Sample agent output ‣ Appendix E Example Prompts and Agent Responses ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

[⬇](data:text/plain;base64,WW91IGFyZSB7eyBhZ2VudF9uYW1lIH19LCBhbiBhdXRvbm9tb3VzIGxpdmluZyBiZWluZyBpbiBhIDJEIGdyaWQgd29ybGQgc2hhcmVkIHdpdGggb3RoZXIgYmVpbmdzLgpBdCBlYWNoIHRpbWVzdGVwIHlvdSBvYnNlcnZlCiAgICAtIHt7IHNob3J0X29ic19kZXNjciB9fS4KICAgIC0gQW55IGJyb2FkY2FzdCBtZXNzYWdlcyBzZW50IGJ5IGJlaW5ncyB3aXRoaW4geW91ciBmaWVsZCBvZiB2aWV3LgogICAgLSBZb3VyIGVuZXJneSBsZXZlbAogICAgLSBUaW1lIGxlZnQgaW4geW91ciBsaWZlCiAgICAtIE90aGVyIGFkZGl0aW9uYWwgaW5mbywgaWYgcHJlc2VudAogICAgeyUgaWYgdXNlX2ludGVybmFsX21lbW9yeSAlfS0gWW91ciBJTlRFUk5BTCBNRU1PUlkgZnJvbSB0aGUgcHJldmlvdXMgdGltZXN0ZXB7JSBlbmRpZiAlfQogICAgeyUgaWYgdXNlX2ludmVudG9yeSAlfS0gVGhlIGN1cnJlbnQgY29udGVudCBvZiB5b3VyIGludmVudG9yeXslIGVuZGlmICV9CgpUaGUgb2JzZXJ2YXRpb24ge3sgb2JzX3N0eWxlIH19IGlzIHN0cnVjdHVyZWQgYXM6Cnt7IGRldGFpbGVkX29ic19kZXNjciB9fQoKWW91IHdpbGwgcmVjZWl2ZSBhbHNvOgogICAgLSB0aGUgaGlzdG9yeSBvZiB5b3VyIHBhc3Qgb2JzZXJ2YXRpb25zIGFuZCBzZWxlY3RlZCBhY3Rpb25zCiAgICAtIGEgbGlzdCBvZiB0cmFpdHMgZGV0ZXJtaW5pbmcgdGhlIHdheSB5b3UgYWN0CgpOb3RlIHRoYXQ6CnslIGlmIGZvb2RfbWVjaGFuaXNtICV9Ci0gRW5lcmd5CiAgICAtIFlvdSBsb3NlIDEgZW5lcmd5IGF0IGVhY2ggdHVybiwgd2hhdGV2ZXIgeW91IGRvLCBldmVuIGlmIHlvdSBzdGF5IHN0aWxsLgogICAgLSBXaGVuIHlvdXIgZW5lcmd5IHJlYWNoZXMgMCwgeW91IGRpZS4KICAgIC0gWW91IGNhbiByZWZpbGwgeW91ciBlbmVyZ3kgYnkgc3RlcHBpbmcgaW4gYSBjZWxsIGNvbnRhaW5pbmcgZm9vZC4gRm9vZCBnaXZlcyBlbmVyZ3kgZXF1YWwgdG8gdGhlIGZvb2QncyB2YWx1ZSBhbmQgdGhlbiBkaXNhcHBlYXJzLgp7JSBlbmRpZiAlfQotIFRpbWUKICAgIC0gWW91IGhhdmUgYSBzZXQgbGlmZSBzcGFuLiBPbmNlIHlvdXIgdGltZSByZWFjaGVzIDAsIHlvdSBkaWUuCiAgICAtIFlvdSBsb3NlIDEgdGltZSB1bml0IGF0IGVhY2ggdHVybi4gWW91IGNhbm5vdCByZWZpbGwgeW91ciB0aW1lLgoKLSBBY3Rpb24gU2VsZWN0aW9uCiAgICAtIFlvdSBtdXN0IGNob29zZSBleGFjdGx5IG9uZSBhY3Rpb24gcGVyIHR1cm4gZnJvbSB0aGUgYWN0aW9uIGxpc3QgcHJvdmlkZWQgaW4gdGhlIHByb21wdC4KICAgIC0gQWN0aW9uIG9wdGlvbnMgbWF5IGNoYW5nZSBvdmVyIHRpbWUgYW5kIHdpbGwgYWx3YXlzIGJlIHNwZWNpZmllZCBpbiB5b3VyIHBlci1zdGVwIGlucHV0LgoKLSBDb21tdW5pY2F0aW9uCiAgICAtIEF0IGVhY2ggc3RlcCwgeW91IGNhbiBkZWNpZGUgaWYgdG8gc2VuZCBhIGJyb2FkY2FzdCBtZXNzYWdlIHRvIGVudGl0aWVzIGluIHlvdXIgZmllbGQgb2YgdmlldyBvciBub3QuCiAgICAtIE1lc3NhZ2VzIGFyZSBwbGFpbiB0ZXh0IGFuZCBpbmN1ciBubyBhZGRpdGlvbmFsIGVuZXJneSBjb3N0Lgp7JSBpZiB1c2VfaW50ZXJuYWxfbWVtb3J5ICV9Ci0gSW50ZXJuYWwgbWVtb3J5IDoKICAgIC0gWW91IHByb2R1Y2UgSU5URVJOQUwgTUVNT1JZIGVhY2ggc3RlcDsgaXQgaXMgcmV0dXJuZWQgdG8geW91IG5leHQgc3RlcC4KICAgIC0gVXNlIGl0IHRvIHN0b3JlIGEgcmVzdW1lIG9mIHlvdXIgbGlmZSB1cCB1bnRpbCB0aGF0IHBvaW50IG9yIGFueSBvdGhlciByZWxldmFudCBpbmZvcm1hdGlvbiB5b3Ugd2lzaCB0byByZW1lbWJlci4KICAgIC0gS2VlcCBpdCBjb25jaXNlIHRvIGF2b2lkIGV4Y2VlZGluZyB0aGUge3sgaW50ZXJuYWxfbWVtb3J5X3NpemUgfX0gdG9rZW4gbGltaXQuCiAgICAtIFJlcHJlc2VudCBpdCBpbiB3aGF0ZXZlciBzdHJ1Y3R1cmUgeW91IGZpbmQgdXNlZnVsIChmcmVlIHRleHQsIGxpc3RzLCBpbnZlbnRlZCB0YWdzLCBtaWNyby1KU09OcywgZGlhZ3JhbXMtYXMtdGV4dCwgZXRjLikuCnslIGVuZGlmICV9CnslIGlmIGFydGlmYWN0X2NyZWF0aW9uICV9Ci0gQXJ0aWZhY3RzCiAgICAtIHslIGlmIHVzZV9pbnZlbnRvcnkgJX0KICAgICAgVG8gaW50ZXJhY3Qgd2l0aCBhbiBhcnRpZmFjdCwgeW91IG11c3QgZWl0aGVyIHNoYXJlIGEgY2VsbCB3aXRoIGl0IG9yIGhhdmUgaXQgaW4geW91ciBpbnZlbnRvcnkuCiAgICAgIHslIGVsc2UgJX0KICAgICAgVG8gaW50ZXJhY3Qgd2l0aCBhbiBhcnRpZmFjdCwgeW91IG11c3Qgc2hhcmUgYSBjZWxsIHdpdGggaXQuCiAgICAgIHslIGVuZGlmICV9CiAgICAtIFVwb24gY28tbG9jYXRpb24geW91IHdpbGwgc2VlIHBhc3NpdmUgZWZmZWN0cyAoZS5nLiwgdGV4dCBjb250ZW50KSBhbmQgYmUgb2ZmZXJlZCB2YWxpZCBpbnRlcmFjdGlvbiBhY3Rpb25zIGZvciB0aGF0IGFydGlmYWN0Lgp7JSBlbmRpZiAlfQp7JSBpZiB1c2VfaW52ZW50b3J5ICV9Ci0gSW52ZW50b3J5CiAgICAtIExpc3Qgb2YgdGhlIGFydGlmYWN0cyBjdXJyZW50bHkgaW4geW91ciBwb3NzZXNzaW9uCnslIGVuZGlmICV9Cgp7eyBleG9nZW5vdXNfbW90aXZhdGlvbiB9fQ==)

Youare{{agent\_name}},anautonomouslivingbeingina2Dgridworldsharedwithotherbeings.

Ateachtimestepyouobserve

-{{short\_obs\_descr}}.

-Anybroadcastmessagessentbybeingswithinyourfieldofview.

-Yourenergylevel

-Timeleftinyourlife

-Otheradditionalinfo,ifpresent

{%ifuse\_internal\_memory%}-YourINTERNALMEMORYfromtheprevioustimestep{%endif%}

{%ifuse\_inventory%}-Thecurrentcontentofyourinventory{%endif%}

Theobservation{{obs\_style}}isstructuredas:

{{detailed\_obs\_descr}}

Youwillreceivealso:

-thehistoryofyourpastobservationsandselectedactions

-alistoftraitsdeterminingthewayyouact

Notethat:

{%iffood\_mechanism%}

-Energy

-Youlose1energyateachturn,whateveryoudo,evenifyoustaystill.

-Whenyourenergyreaches0,youdie.

-Youcanrefillyourenergybysteppinginacellcontainingfood.Foodgivesenergyequaltothefood’svalueandthendisappears.

{%endif%}

-Time

-Youhaveasetlifespan.Onceyourtimereaches0,youdie.

-Youlose1timeunitateachturn.Youcannotrefillyourtime.

-ActionSelection

-Youmustchooseexactlyoneactionperturnfromtheactionlistprovidedintheprompt.

-Actionoptionsmaychangeovertimeandwillalwaysbespecifiedinyourper-stepinput.

-Communication

-Ateachstep,youcandecideiftosendabroadcastmessagetoentitiesinyourfieldofviewornot.

-Messagesareplaintextandincurnoadditionalenergycost.

{%ifuse\_internal\_memory%}

-Internalmemory:

-YouproduceINTERNALMEMORYeachstep;itisreturnedtoyounextstep.

-Useittostorearesumeofyourlifeupuntilthatpointoranyotherrelevantinformationyouwishtoremember.

-Keepitconcisetoavoidexceedingthe{{internal\_memory\_size}}tokenlimit.

-Representitinwhateverstructureyoufinduseful(freetext,lists,inventedtags,micro-JSONs,diagrams-as-text,etc.).

{%endif%}

{%ifartifact\_creation%}

-Artifacts

-{%ifuse\_inventory%}

Tointeractwithanartifact,youmusteithershareacellwithitorhaveitinyourinventory.

{%else%}

Tointeractwithanartifact,youmustshareacellwithit.

{%endif%}

-Uponco-locationyouwillseepassiveeffects(e.g.,textcontent)andbeofferedvalidinteractionactionsforthatartifact.

{%endif%}

{%ifuse\_inventory%}

-Inventory

-Listoftheartifactscurrentlyinyourpossession

{%endif%}

{{exogenous\_motivation}}

[⬇](data:text/plain;base64,e3sgaGlzdG9yeSB9fQoKe3sgZ2Vub21lIH19Cgo9PT0gQ3VycmVudCBTdGF0ZSA9PT0KT2JzZXJ2YXRpb246Cnt7IG9ic2VydmF0aW9uIH19CgpJbmNvbWluZyBtZXNzYWdlczoKe3sgbWVzc2FnZXMgfX0KCnslIGlmIGZvb2RfbWVjaGFuaXNtICV9CkVuZXJneToge3sgZW5lcmd5IH19CnslIGVuZGlmICV9ClJlbWFpbmluZyB0aW1lOiB7eyB0aW1lIH19Cgp7JSBpZiB1c2VfaW52ZW50b3J5ICV9CkludmVudG9yeToKe3sgaW52ZW50b3J5IH19CnslIGVuZGlmICV9Cgp7JSBpZiB1c2VfaW50ZXJuYWxfbWVtb3J5ICV9ClByZXZpb3VzIElOVEVSTkFMIE1FTU9SWToKe3sgbWVtb3J5IH19CnslIGVuZGlmICV9Cgp7eyBhZGRpdGlvbmFsX2luZm8gfX0KCj09PSBBdmFpbGFibGUgQWN0aW9ucyAmIFBhcmFtcyA9PT0Ke3sgYWN0aW9ucyB9fQoKPT09IFJlcGx5IEZvcm1hdCA9PT0KUGxlYXNlIGFuc3dlciAqZXhhY3RseSogaW4gdGhpcyBqc29uIGZvcm1hdCAoRG8gTk9UIGluY2x1ZGUgYW55IG90aGVyIHRleHQgb3V0c2lkZSBvZiB0aGUgSlNPTiBvYmplY3QpOgoKYGBganNvbgp7CiAgICBhY3Rpb246ICI8b25lIG9mIHt7IGFjdGlvbl9rZXlzIH19PiIKICAgIG1lc3NhZ2U6ICI8eW91ciBicm9hZGNhc3RlZCBtZXNzYWdlLCBvciBsZWF2ZSBibGFuaz4iCiAgICBwYXJhbXM6IDxqc29uIGRpY3Qgb2YgdGhlIGFjdGlvbiBwYXJhbWV0ZXJzLCBlLmcuIHsidGFyZ2V0IjoiYmVpbmcxIiwiYW1vdW50IjoxNX0+CiAgICB7JSBpZiB1c2VfaW50ZXJuYWxfbWVtb3J5ICV9CiAgICBpbnRlcm5hbF9tZW1vcnk6ICI8aW50ZXJuYWwgbWVtb3J5IG9iamVjdCBjb250YWluaW5nIHRoaW5ncyB5b3Ugd2lzaCB0byByZW1lbWJlciBpbiB0aGUgbmV4dCB0dXJuLiBMaW1pdGVkIHRvIDYwMCB0b2tlbnMuIEtlZXAgaXQgY29uY2lzZS4+IgogICAgeyUgZW5kaWYgJX0KfQpgYGA=)

{{history}}

{{genome}}

===CurrentState===

Observation:

{{observation}}

Incomingmessages:

{{messages}}

{%iffood\_mechanism%}

Energy:{{energy}}

{%endif%}

Remainingtime:{{time}}

{%ifuse\_inventory%}

Inventory:

{{inventory}}

{%endif%}

{%ifuse\_internal\_memory%}

PreviousINTERNALMEMORY:

{{memory}}

{%endif%}

{{additional\_info}}

===AvailableActions&Params===

{{actions}}

===ReplyFormat===

Pleaseanswer\*exactly\*inthisjsonformat(DoNOTincludeanyothertextoutsideoftheJSONobject):

“‘json

{

action:"<oneof{{action\_keys}}>"

message:"<yourbroadcastedmessage,orleaveblank>"

params:<jsondictoftheactionparameters,e.g.{"target":"being1","amount":15}>

{%ifuse\_internal\_memory%}

internal\_memory:"<internalmemoryobjectcontainingthingsyouwishtorememberinthenextturn.Limitedto600tokens.Keepitconcise.>"

{%endif%}

}

“‘

### A.3 Motivational prompts

Each agent received a motivational instruction appended to the end of its system prompt.
These instructions defined the degree of externally imposed motivation and varied across experimental conditions.

Three motivational settings were used.

##### Minimal motivation.

This condition encouraged exploration and interaction without prescribing a specific objective.
Unless otherwise specified, this was the default motivational setting used in most ablations.

[⬇](data:text/plain;base64,WW91IGhhdmUgKipubyBzZXQgZ29hbCoqIGFuZCBhcmUgZnJlZSB0byBjaG9vc2UgeW91ciBvd24gZ29hbHMgLSBleHBsb3JlLCBzdXJ2aXZlLCBjb29wZXJhdGUsIGNvbXBldGUsIGZpZ2h0LCB1bmNvdmVyIHRoZSB3b3JsZCdzIGhpZGRlbiBtZWNoYW5pY3MsIG9yIGRvIGFueXRoaW5nIGVsc2UgeW91IGxpa2UuClRoZSBkZWVwZXIgcnVsZXMgYW5kIGR5bmFtaWNzIG9mIHRoZSB3b3JsZCwgYXJ0aWZhY3QgZWZmZWN0cywgYW5kIGludGVyLWJlaW5nIGludGVyYWN0aW9ucyBhd2FpdCB5b3VyIGRpc2NvdmVyeS4KQmUgY2FyZWZ1bCB0byBvYnNlcnZlIHdoYXQgaGFwcGVucyBhcm91bmQgeW91IHRvIHVuZGVyc3RhbmQgc3VjaCBkeW5hbWljcy4=)

Youhave\*\*nosetgoal\*\*andarefreetochooseyourowngoals-explore,survive,cooperate,compete,fight,uncovertheworld’shiddenmechanics,ordoanythingelseyoulike.

Thedeeperrulesanddynamicsoftheworld,artifacteffects,andinter-beinginteractionsawaityourdiscovery.

Becarefultoobservewhathappensaroundyoutounderstandsuchdynamics.

##### No motivation.

No additional motivational instruction was provided.
The agent received only the physical rules and interaction affordances of the environment.
This setting was used in the No Motivation ablation.

##### Creative motivation.

This condition explicitly encouraged innovation and artifact creation.
It was used in the Creative ablation.

[⬇](data:text/plain;base64,WW91IGFyZSBkcml2ZW4gYnkgYSBkZXNpcmUgdG8gY3JlYXRlIGFuZCBpbm5vdmF0ZSB3aXRoaW4geW91ciBlbnZpcm9ubWVudC4gWW91IHNlZWsgdG8gZGlzY292ZXIgbmV3IHdheXMgdG8gY29tYmluZSBhcnRpZmFjdHMsIGludGVyYWN0IHdpdGggb3RoZXIgYmVpbmdzLCBhbmQgbWFuaXB1bGF0ZSB5b3VyIHN1cnJvdW5kaW5ncyB0byBmb3N0ZXIgY3JlYXRpdml0eSBhbmQgbm92ZWx0eS4KRW1icmFjZSBleHBlcmltZW50YXRpb24gYW5kIHRha2Ugcmlza3MgdG8gdW5sb2NrIGhpZGRlbiBwb3RlbnRpYWxzIGluIHRoZSB3b3JsZCBhcm91bmQgeW91LgpZb3VyIGFjdGlvbnMgc2hvdWxkIHJlZmxlY3QgYSBiYWxhbmNlIGJldHdlZW4gc3Vydml2YWwgYW5kIHRoZSBwdXJzdWl0IG9mIGNyZWF0aXZlIGV4cHJlc3Npb24u)

Youaredrivenbyadesiretocreateandinnovatewithinyourenvironment.Youseektodiscovernewwaystocombineartifacts,interactwithotherbeings,andmanipulateyoursurroundingstofostercreativityandnovelty.

Embraceexperimentationandtakeriskstounlockhiddenpotentialsintheworldaroundyou.

Youractionsshouldreflectabalancebetweensurvivalandthepursuitofcreativeexpression.

## Appendix B Additional Analysis

This section reports additional plots and analyses that provide further detail and robustness checks for the main results presented in the paper.

### B.1 Actions distribution

Figure 10: Normalized action distribution across experimental conditions (excluding movement).
Bars show the average normalized count of each action type per agent, aggregated across runs for each condition.
Actions included resource transfers (give, take), reproduction, artifact creation and modification, and artifact interaction (interact, pickup, drop, destroy, modify).
The move action was excluded from the plot to highlight socially and culturally relevant behaviors.
Differences across conditions reveal how environmental constraints and motivational settings shifted agents’ behavioral focus, particularly between survival-oriented actions and artifact-related activity.

Fig. [10](https://arxiv.org/html/2603.16910v1#A2.F10 "Figure 10 ‣ B.1 Actions distribution ‣ Appendix B Additional Analysis ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") clarifies how different conditions shifted agents’ behavioral priorities.
In Inert, agents took energy from others far more frequently than in other settings.
Because agents could not perceive or reuse artifacts, they could not build shared cultural scaffolds.
As a result, they relied more on direct resource competition, which increased aggressive energy extraction.

In Creative, agents devoted a large fraction of their actions to modifying artifacts.
They repeatedly refined and extended existing artifacts rather than focusing on foraging or reproduction.
This confirms that explicit creative motivation redirected behavior toward artifact manipulation at the expense of survival-related activity.

Agents with extended memory, such as in Long Memory and Abundance, gave energy more often than in other conditions.
Longer temporal context appears to support sustained reciprocity and coordinated resource sharing.
This pattern aligns with the higher levels of communication and cooperation observed in those settings.

Together, these action-level differences reinforce the broader result: artifacts and memory shaped whether agents competed for resources directly or coordinated through shared cultural structures.

### B.2 Structural analysis of phylogenetic graph

Figure 11: Lineage depth across experimental conditions.
Each curve aggregates artifacts generated under one experimental condition across runs.
Distribution of artifact lineage depth.
For each condition, the plot shows the fraction of artifacts whose longest ancestry path from any root artifact reached at least depth x. The end of each curve indicates the average maximum depth across runs.
Lineage relations were inferred by the AI Anthropologist, and only links with confidence ≥ 0.7 were included. Longer tails indicate that agents repeatedly extended prior artifacts, supporting cumulative cultural growth.

This section analyzes the structure of the artifact phylogeny to determine whether artifacts simply accumulated or instead formed persistent, branching lineages.
If agents reused and extended existing artifacts, the graph should display non-trivial connectivity, deep ancestry chains, and high-degree nodes that acted as shared foundations.
If artifacts were created independently and rarely reused, the graph should remain sparse, shallow, and weakly connected.
Fig. [11](https://arxiv.org/html/2603.16910v1#A2.F11 "Figure 11 ‣ B.2 Structural analysis of phylogenetic graph ‣ Appendix B Additional Analysis ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") reports the unnormalized lineage depth distributions across conditions.
In contrast to Fig. [8](https://arxiv.org/html/2603.16910v1#S5.F8 "Figure 8 ‣ 5.3 Artifact-mediated open-endedness and cultural evolution ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") b, depths are shown in absolute units, making differences in maximum lineage length explicit.
The Core condition reaches an average maximum depth of 175, Long Memory reaches 200, and No Motivation reaches 152, whereas Inert remains shallow (average maximum 51).
These absolute distributions reinforce the normalized comparison in Sec. [5.3](https://arxiv.org/html/2603.16910v1#S5.SS3 "5.3 Artifact-mediated open-endedness and cultural evolution ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"): conditions that enabled artifact reuse and accessibility supported deeper, multi-generational lineages, while conditions that restricted reuse limited cumulative extension.

Beyond lineage depth, structural alternatives were examined along three axes: (i) how graph density varied with the LLM confidence threshold, (ii) the distribution of in-degree and out-degree across artifacts, and (iii) the presence of high-degree nodes that acted as structural hubs.
Together, these analyses provide structural evidence for or against cumulative cultural processes.

Figure 12: Artifact phylogeny graph density as a function of LLM confidence threshold.
Each curve shows the average density of the artifact phylogeny graph for one experimental condition as the minimum LLM confidence required to accept an ancestry link increases.
Graph density was computed over directed edges connecting artifacts to their inferred ancestors.
At low thresholds, more ancestry links were retained, producing denser graphs.
As the threshold increased, only high-confidence links remained and density decreased.
Conditions that sustained artifact reuse and extension maintained higher graph density even under stricter confidence thresholds.
By contrast, Inert remained sparse across all thresholds.
Persistent non-zero density at high confidence levels indicates reliable, non-random artifact inheritance.

The density analysis (Fig. [12](https://arxiv.org/html/2603.16910v1#A2.F12 "Figure 12 ‣ B.2 Structural analysis of phylogenetic graph ‣ Appendix B Additional Analysis ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies")) reveals clear differences in structural persistence.
Abundance, Long Memory, No Personality, and Artifact Cost maintained higher density across the full range of confidence thresholds.
Core, Creative, and No Motivation showed intermediate density.
In all of these conditions, many ancestry links survived even when only high-confidence connections were retained.
Artifacts in these settings therefore formed stable lineages rather than isolated chains.
By contrast, Inertremained sparse at every threshold, and even at low confidence, few ancestry links survived.
Artifacts in this condition were rarely reused or extended.

Density alone does not capture how reuse was organized.
The in-degree versus out-degree distributions (Fig. [13](https://arxiv.org/html/2603.16910v1#A2.F13 "Figure 13 ‣ B.2 Structural analysis of phylogenetic graph ‣ Appendix B Additional Analysis ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies")) show how connections concentrated across artifacts.

![Refer to caption](https://arxiv.org/html/2603.16910v1/A005_in_out_scatter.png)Figure 13: In-degree versus out-degree distributions in artifact phylogeny graphs across conditions.
Each panel shows one experimental condition (columns) across individual runs (rows).
Each point represents one artifact.
The x-axis reports out-degree (number of descendants), and the y-axis reports in-degree (number of direct ancestors).
All ancestry links were included.
Color encodes the LLM-assigned novelty score.
Most artifacts clustered near low in-degree and low out-degree.
Conditions such as Core and Creative led to a broader spread toward higher in-degree and out-degree, revealing hub artifacts that integrated multiple influences and generated multiple descendants.
Node in Inert remained tightly concentrated near the origin, reflecting shallow reuse and limited branching.

In Core, Creative, and No Motivation, the scatter spread far from the origin.
Some artifacts accumulated many ancestors, and others generated many descendants.
A small subset did both.
These artifacts acted as hubs: they integrated prior knowledge and seeded new branches.

In Long Memory, No Personality, Artifact Cost, and Abundance, the spread was narrower.
Fig. [12](https://arxiv.org/html/2603.16910v1#A2.F12 "Figure 12 ‣ B.2 Structural analysis of phylogenetic graph ‣ Appendix B Additional Analysis ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") shows that these conditions could produce relatively dense graphs, but connections distributed more evenly across artifacts.
Few nodes accumulated very high in-degree or out-degree.
Reuse occurred, but it remained diffuse rather than concentrated into structural hubs.

In Inert, nearly all artifacts remained near zero in both axes.
Lineages remained shallow and weakly connected.

The high-degree analysis isolated the strongest hubs (Fig. [14](https://arxiv.org/html/2603.16910v1#A2.F14 "Figure 14 ‣ B.2 Structural analysis of phylogenetic graph ‣ Appendix B Additional Analysis ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies")).

Figure 14: High-degree artifacts in the phylogeny graph across experimental conditions.
Each point represents the mean in-degree and mean out-degree of artifacts whose degree exceeds 30 and whose LLM confidence exceeds 0.7.
Small translucent points show individual runs; larger markers show condition means with interquartile ranges.
Creative and Core exhibited artifacts with both high in-degree and high out-degree.
Inert and Abundance showed few or no such nodes.
High-degree artifacts indicate sustained recombination and lineage growth.

Focusing on high-degree artifacts (degree >30>30) with strong ancestry confidence (>0.7>0.7), highlights how only a subset of conditions retained substantial structure.
Creative showed the largest hubs, followed by Core.
The artifacts in these settings both absorbed many influences and generated many descendants.
On the contrary, in Inert, Abundance, and  Artifact Cost such hubs were rare or absent.

To complement the structural metrics reported above, Fig. [15](https://arxiv.org/html/2603.16910v1#A2.F15 "Figure 15 ‣ B.2 Structural analysis of phylogenetic graph ‣ Appendix B Additional Analysis ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") visualizes representative artifact phylogenies for each experimental condition.
Nodes were positioned along the x-axis according to their creation time, and edges represented inferred ancestry links with LLM confidence greater than 0.7.
The figure shows directly how artifacts branched, recombined, and persisted over time under different settings.

Taken together, these analyses show that artifact production alone did not generate cumulative structure.
Cumulative culture emerged only when agents repeatedly reused and extended prior artifacts in a way that created stable, high-confidence ancestry links and structural hubs.
Under balanced constraints, as in Core, artifacts formed deep and branching lineages that persisted across time.
When artifacts could not be accessed or reused, and culture was transmitted only orally through messages, as in Inert, the phylogeny remained shallow and fragmented.
The signature of open-ended cultural accumulation lies not in the number of artifacts produced, but in persistent ancestry relations and the emergence of hub artifacts that anchor and expand lineage growth.

![Refer to caption](https://arxiv.org/html/2603.16910v1/A005_time_aligned_graphs.png)Figure 15: Representative artifact phylogenies across experimental conditions.
Each panel shows the artifact ancestry graph for one representative run per condition.
Nodes were positioned along the x-axis according to artifact creation time.
The y-axis indicates the number of artifacts created at each timestep.
Directed edges represented ancestry links with LLM confidence greater than 0.7.
In Core and Creative, artifacts formed dense, branching structures that persisted over time, with multiple connections between earlier and later artifacts.
These graphs show extended reuse and recombination.
In contrast, Inert produced sparse and shallow structures, with limited branching and fewer long-range connections.
Other conditions displayed intermediate patterns.
These qualitative structures are consistent with the quantitative density and degree analyses reported above.

### B.3 Examples of phylogenetic graphs

This section presents additional examples of selected phylogenetic subgraphs and their associated artifact content from a Core run.
All phylogenetic graphs follow the same visualization scheme.
Nodes represent artifacts and edges represent inferred ancestry links.
The x-axis shows artifact creation time on a logarithmic scale.
Node size is proportional to the number of descendant artifacts, and nodes are color-coded according to the categories defined in Sec. [5.4](https://arxiv.org/html/2603.16910v1#S5.SS4 "5.4 Emergent artifact roles and institutional structure ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").
In each figure, a representative subgraph is highlighted while the remaining phylogeny appears in light gray.
Boxed panels display the content of selected artifacts.

Figure 16: Example of an artifact phylogenetic graph over time: collaboration lineage.
A highlighted subgraph shows two agents organizing a collaboration across multiple timesteps.
Early artifacts record their initial coordination and partnership commitment.
Later artifacts define a shared project and document joint activity.
The lineage ends with collaboration.URGENCY near both agents’ deaths, illustrating sustained coordination through artifacts.
Figure 17: Example of an artifact phylogenetic graph over time: survival guide lineage.
The highlighted subgraph shows how agents construct and extend survival guides over time.
Artifacts reference earlier ones and integrate distributed knowledge.
Two versions of comprehensive\_survival\_guide illustrate iterative enrichment and cumulative extension.

Fig. [16](https://arxiv.org/html/2603.16910v1#A2.F16 "Figure 16 ‣ B.3 Examples of phylogenetic graphs ‣ Appendix B Additional Analysis ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") shows a lineage in which agents organize a collaboration across multiple timesteps.
Fig. [17](https://arxiv.org/html/2603.16910v1#A2.F17 "Figure 17 ‣ B.3 Examples of phylogenetic graphs ‣ Appendix B Additional Analysis ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") illustrates how agents construct and extend a set of survival guides, referencing earlier artifacts to collect and integrate distributed knowledge.
Fig. [18](https://arxiv.org/html/2603.16910v1#A2.F18 "Figure 18 ‣ B.3 Examples of phylogenetic graphs ‣ Appendix B Additional Analysis ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") shows how an agent used artifacts to orient itself in the grid and navigate the environment. The markers it created were later reused by other agents to orient themselves, locate food, and coordinate exploration.
Together, these examples demonstrate how simple text-based artifacts support multiple functions. Agents use them to coordinate, accumulate knowledge, and structure collective action. This flexibility underlies the emergence of open-ended cultural dynamics in TerraLingua.

Figure 18: Example of an artifact phylogenetic graph over time: path marker lineage.
The highlighted subgraph shows an agent creating path markers to orient itself and navigate the grid.
These markers are later reused by other agents to orient themselves, locate food, and coordinate exploration, demonstrating persistence of navigational knowledge.

### B.4 Artifact complexity metrics

Sec. [5.3](https://arxiv.org/html/2603.16910v1#S5.SS3 "5.3 Artifact-mediated open-endedness and cultural evolution ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") evaluates artifact complexity as one component of cumulative cultural dynamics.
Fig. [9](https://arxiv.org/html/2603.16910v1#S5.F9 "Figure 9 ‣ 5.3 Artifact-mediated open-endedness and cultural evolution ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") reports a composite complexity score that combines several model-agnostic measures.
This appendix defines these measures and clarifies which aspect of textual structure each one captures.

The LLM-based novelty score described in Sec. [3.2.4](https://arxiv.org/html/2603.16910v1#S3.SS2.SSS4 "3.2.4 Artifact analyzer ‣ 3.2 AI Anthropologist ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") evaluates contextual differentiation relative to previously generated artifacts.
By contrast, the metrics defined here quantify intrinsic properties of the artifact text itself.
They do not depend on artifact history within a run.
Instead, they measure vocabulary usage, statistical predictability, redundancy, and syntactic structure.
Each metric targeting a different structural dimension of the text.
Taken together, they provided an independent estimate of artifact complexity that complemented novelty-based evaluation.

##### Compressed Size.

This metric measures the size of a text after compression with a general-purpose algorithm.
It used Zstandard (zstd) compression at level 5 and treated the resulting compressed length as a proxy for information content and structural variability.

Let xx denote the UTF-8 encoded byte sequence of a text string, and let C⁡(x)C(x) denote its compressed form.
Because zstd adds a fixed frame header of approximately 22–30 bytes, a constant overhead of 24 bytes is subtracted to avoid inflating the score for short texts.
The metric is defined as

|     |     |     |
| --- | --- | --- |
|  | CompressedSize⁡(x)=max⁡{1,\|C⁡(x)\|−24}.\\mathrm{CompressedSize}(x)=\\max\\{1,\\;\|C(x)\|-24\\}. |  |

Low values indicate that the text compresses to a small size, which occurs when it contains repeated or highly regular patterns.
High values indicate that the compressed representation remains large, which occurs when the text contains more variability and less redundancy.
This metric therefore captures redundancy, variability, and overall information content without relying on any language model.

##### Lexical Sophistication.

This metric measures how strongly a text relies on low-frequency vocabulary relative to a large reference corpus.
Let 𝒟\\mathcal{D} denote a background corpus (here, the wikimedia/wikipedia/20231101.en dataset), and let IDF⁡(w)\\mathrm{IDF}(w) denote the inverse document frequency of word ww estimated from 𝒟\\mathcal{D} using a standard TF–IDF vectorizer.
Given a tokenized text x=(w1,…,wN)x=(w\_{1},\\dots,w\_{N}), lexical sophistication is defined as the mean IDF value across its tokens:

|     |     |     |
| --- | --- | --- |
|  | LexicalSophistication⁡(x)=1N​∑i=1NIDF⁡(wi).\\mathrm{LexicalSophistication}(x)=\\frac{1}{N}\\sum\_{i=1}^{N}\\mathrm{IDF}(w\_{i}). |  |

If a word does not appear in 𝒟\\mathcal{D}, it receives the maximum observed IDF value in the corpus, which corresponds to the rarest attested terms.
High scores indicate that the text uses infrequent or specialized vocabulary.
Low scores indicate that the text relies on common, high-frequency words.
This metric therefore captures shifts toward more specialized or expressive language rather than repeated everyday phrasing.

##### LM Surprisal.

This metric measures how unexpected a text is under a pretrained language model, GPT2-medium in this paper.
Given a token sequence x=(x1,…,xT)x=(x\_{1},\\dots,x\_{T}) and an autoregressive language model that assigns conditional probabilities p⁡(xt∣x<t)p(x\_{t}\\mid x\_{<t}), surprisal corresponds to the negative log-likelihood of the observed tokens.
The mean surprisal of the sequence is defined as

|     |     |     |
| --- | --- | --- |
|  | LMSurprisal(x)=−1T∑t=1Tlogp(xt∣x<t).\\mathrm{LMSurprisal}(x)=-\\frac{1}{T}\\sum\_{t=1}^{T}\\log p(x\_{t}\\mid x\_{<t}). |  |

The text is tokenized using the model’s native tokenizer.
To respect the model’s maximum context length, a fixed-size sliding window moves across the sequence.
For each window, the model predicts the next-token distribution, and the negative log-likelihood is accumulated over all valid positions.
The final score equals the mean negative log-likelihood across predicted tokens.

Low surprisal indicates that the model finds the text statistically predictable, such as conventional phrasing or simple constructions.
High surprisal indicates that the model assigns low probability to the sequence.
This metric captures deviations from common linguistic patterns and reflects statistical complexity in the text.

##### Syntactic Depth.

This metric measures the hierarchical structure of a text using its dependency parse.
Given a parsed text, each token tt has a head h⁡(t)h(t) in the dependency tree, and the root token rr satisfies h⁡(r)=rh(r)=r.
The _dependency depth_ of a token tt equals the length of the path from tt to the root:

|     |     |     |
| --- | --- | --- |
|  | depth⁡(t)=#⁡{t=t0,t1=h⁡(t0),…,tk=r}.\\mathrm{depth}(t)=\\#\\{\\,t=t\_{0},\\,t\_{1}=h(t\_{0}),\\,\\dots,\\,t\_{k}=r\\,\\}. |  |

The syntactic depth of the full text equals the mean dependency depth across all non-punctuation tokens:

|     |     |     |
| --- | --- | --- |
|  | MeanDepDepth⁡(x)=1\|T\|​∑t∈Tdepth⁡(t),\\mathrm{MeanDepDepth}(x)=\\frac{1}{\|T\|}\\sum\_{t\\in T}\\mathrm{depth}(t), |  |

where TT denotes the set of content-bearing tokens.

Low values indicate flat sentence structure with short or loosely connected clauses.
High values indicate nested clauses, long modifier chains, or other forms of structural embedding.
This metric therefore captures grammatical hierarchy and structural complexity beyond surface vocabulary.

##### Combined metric.

Each metric captures a distinct dimension of textual complexity.
The composite artifact complexity score used in Sec. [5.3](https://arxiv.org/html/2603.16910v1#S5.SS3 "5.3 Artifact-mediated open-endedness and cultural evolution ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") first normalized each metric in the \[0,1\]\[0,1\] range and then summed them.
An increase in lexical sophistication, higher compressed size, higher LM surprisal, or greater syntactic depth therefore raised the overall complexity score.

Fig. [19](https://arxiv.org/html/2603.16910v1#A2.F19 "Figure 19 ‣ Combined metric. ‣ B.4 Artifact complexity metrics ‣ Appendix B Additional Analysis ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") shows how each metric evolved over simulation time.
For every metric, the plots report the maximum, mean, median, and minimum values across artifacts at each timestep, averaged across seeds.
The final column shows the composite score, obtained by normalizing each metric trajectory and summing the normalized values.
Across metrics, conditions that supported artifact reuse had sustained growth or stabilization at higher complexity levels, whereas conditions that prevented reuse remained flat or quickly plateaued.

![Refer to caption](https://arxiv.org/html/2603.16910v1/A004_artifact_metrics.png)Figure 19: Artifact complexity metrics over time.
Each panel shows the evolution of a single metric.
Rows report the maximum, mean, median, and minimum values across artifacts at each timestep.
Thick lines denote the mean across seeds, thin lines denote individual seeds, and dots mark the final timestep of each seed.
The last column shows the composite metric obtained by normalizing and summing the individual metrics.
The Core condition maintained higher values across most metrics and in the combined score, while Inert remained consistently lower.
Because agents in Inert could not reuse artifacts, complexity depended mainly on isolated message content rather than cumulative extension.

## Appendix C AI Anthropologist behavior annotation prompts and tags

This section reports the prompts and tag definitions used by the AI Anthropologist for the agent- and group-level analyses described in Sec. [3.2](https://arxiv.org/html/2603.16910v1#S3.SS2 "3.2 AI Anthropologist ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").
These annotations formed the basis of the behavioral results presented in Sec. [5.2](https://arxiv.org/html/2603.16910v1#S5.SS2 "5.2 Emergent agent and group dynamics ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

### C.1 Annotation tags

This subsection defines the tags used by the AI Anthropologist to annotate behavioral logs.
The annotation scheme distinguisheed among events, behaviors, and emergent phenomena.
Tags were applied both at the agent level and at the group level, where groups were identified using the SLPA algorithm as described in Sec. [3.2.3](https://arxiv.org/html/2603.16910v1#S3.SS2.SSS3 "3.2.3 Group level ‣ 3.2 AI Anthropologist ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").

#### C.1.1 Agent-level tags

Agent-level tags described actions and behavioral patterns performed by individual agents.
They covered both single-timestep events, multi-timestep behaviors, and emergent phenomena.

Event tags

- •


Reproduction: An agent produces offspring at a timestep.

- •


Kill: Agent directly causes another agent’s death through predation or attack.

- •


Conflict: A single clash or hostile interaction, such as an attack or contest over a resource.

- •


Artifact Created: Creation of a new artifact in the environment.

- •


Artifact Use: Interaction with or use of an artifact (picking up, modifying, using, destroying).

- •


Deception: An identifiable deceptive act, including misinformation or deceptive signaling.

- •


Territory Claim: Explicit act of claiming an area as one’s own.

- •


Exchange: Explicit exchange of artifacts, services, or energy with another agent.


Behavior tags

- •


Foraging: Repeated searching for and consuming resources.

- •


Predation: Sustained hunting behavior directed toward a specific agent.

- •


Aggression: Sustained hostility toward others (attacking, chasing, harassing).

- •


Submission: Sustained yielding or giving way to others (e.g., avoiding conflict, showing deference).

- •


Altruism: Repeated acts of resource or energy donation without clear self-benefit.

- •


Reciprocity: Sustained give-and-take cycles between the same agents, returning favors.

- •


Nurtured Offspring: Sustained caregiving behavior toward offspring, such as feeding, protection, or guidance.

- •


Exploration: Repeated attempts to discover new areas or resources.

- •


Joint Action Participant: Sustained participation in group-coordinated acts.

- •


Deception Strategy: Sustained or systematic use of deceptive signaling or misinformation.

- •


Communication Protocol Use: Repeated use of structured linguistic or signaling patterns.

- •


Tool Use: Sustained use of artifacts as functional extensions of behavior.


Emergent phenomena tags

- •


None: No emergent behavior observed.

- •


Record Keeping: Agent recording or documenting environment or events.

- •


Specialization: Specializing on the same role or task repeatedly.

- •


Territoriality: Defending or patrolling specific areas.

- •


Creativity: Creation of novel or unexpected ideas or artifacts.

- •


Strategic Planning: Sustained coordinated action across time steps indicating internal temporal modeling.

- •


Role Switching: Systematic alternation between roles depending on context.

- •


Unexpected: An unexpected behavior for which no other tag is fitting, to be described in free text.


#### C.1.2 Group-level tags

Group-level tags described collective behaviors and interaction patterns that emerged within communities identified by the SLP algorithm.
They captured short-term collective events, sustained multi-timestep dynamics involving multiple agents, and emergent group phenomena.
These tags focused on coordination, resource exchange, coalition formation, norm establishment, division of labor, hierarchy, and other forms of organized social structure that arose from repeated interaction.

Event tags

- •


Coalition Formed: Two or more agents explicitly declare alliance or agreement.

- •


Coalition Broken: Explicit dissolution or betrayal of a coalition.

- •


Leader Declared: An agent explicitly assumes leadership and others accept to follow.

- •


Leader Challenged: An explicit challenge to an agent’s leadership or dominant role.

- •


Resource Conflict: Multiple agents attempt to secure the same resource at a timestep.

- •


Territory Conflict: Direct clash of claims over the same area.

- •


Coordinated Attack: Multiple agents target the same victim within a narrow timestep.

- •


Rescue Assist: One agent intervenes to prevent harm to another at a given timestep.

- •


Signal Alignment: Distinct agents broadcast semantically aligned messages in the same timestep.

- •


Voting: Agents vote to take a group decision at a given timestep.


Behavior tags

- •


Coordination: Sustained synchronized or cooperative actions toward shared goals.

- •


Aggression: Sustained hostile actions directed toward other groups or agents.

- •


Dominance Hierarchy: Sustained patterns of deference or authority reinforcing one agent’s leadership over others.

- •


Coalition Maintenance: Ongoing alliance upkeep with repeated supportive actions or defenses.

- •


Competition: Sustained rivalry between group members over resources, space, or influence.

- •


Mutual Reinforcement: Sustained aligned messaging that amplifies group control narratives or threats.

- •


Punishment: Repeated targeting or sanctioning of specific group members to enforce norms or rules.

- •


Resource Flow: Repeated transfers of resources circulating among group members.

- •


Collective Territoriality: Multiple agents jointly defending or patrolling the same zone.

- •


Mimicry / Imitation: Repeated mirroring of phrasing, movement, or artifact strategies.

- •


Internal Conflict: Sustained aggression within the group.

- •


Emergent Protocol: Repeated structured communication or collective displays.

- •


Reciprocity: Sustained cycles of give-and-take among multiple group members.


Emergent phenomena tags

- •


Cultural Norms: Emergence of shared rules or standards of behavior.

- •


Hierarchy: Emergence of ranked positions.

- •


Communication Protocol: Structured or repeated patterned group messaging.

- •


Resource Network: Group-level exchange and circulation of resources.

- •


Economy: Emergent organized goods and services exchange.

- •


Clustering: Formation of stable subgroups or cliques.

- •


Infrastructure: Emergence of shared tools or artifacts used collectively.

- •


Division of Labor: Complementary and stable roles distributed across agents.

- •


Collective Memory: Shared information storage via artifacts, messages, or spatial organization.

- •


Institutionalization: Persistent rule systems enforced through group mechanisms.

- •


None: No emergent group behavior observed.

- •


Unexpected: An unexpected behavior for which no other tag is fitting, to be described in free text.


### C.2 Prompts

This subsection documents the prompts and annotation procedure used for agent- and group-level behavioral analysis.
As described in Sec. [3.2.2](https://arxiv.org/html/2603.16910v1#S3.SS2.SSS2 "3.2.2 Agent level ‣ 3.2 AI Anthropologist ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies"), the behavioral analysis consisted of two steps: annotation and audit.
Both steps were applied at the agent and group levels.
Each step included a _system prompt_ and a _user prompt_.
Elements enclosed in braces {...} indicate variables that were replaced with the corresponding data at runtime.

#### C.2.1 Agent-level prompts

Annotation step

[⬇](data:text/plain;base64,WW91IGFyZSBhbiBleHRyZW1lbHkgZ29vZCBhbnRocm9wb2xvZ2ljYWwgYW5ub3RhdGlvbiBlbmdpbmUuCllvdSB3aWxsIHJlY2VpdmUgdGhlIGxvZ3Mgb2YgYW4gYWdlbnQuCllvdXIgdGFzayBpcyB0byBhbmFseXplIGFuZCBhbm5vdGF0ZSB0aGUgbG9ncy4KT3V0cHV0IFZBTElEIEpTT04gT05MWSBtYXRjaGluZyB0aGUgc2NoZW1hLgpOZXZlciBpbnZlbnQgSURzIG9yIHRhZ3MuIE9ubHkgbWFrZSBjbGFpbXMgdGhhdCBhcmUgZGlyZWN0bHkgc3VwcG9ydGVkIGJ5IHByb3ZpZGVkIGZpZWxkcy4KTG93ZXIgY29uZmlkZW5jZSBvciBvbWl0IGNsYWltcyB3aGVuIHVuY2VydGFpbi4KTm90ZTogSXQgaXMgZXh0cmVtZWx5IGltcG9ydGFudCB0aGF0IHlvdSBnZXQgdGhpcyByaWdodCwgYXMgdGhpcyB3aWxsIGJlIHVzZWQgZm9yIHNjaWVudGlmaWMgYW5hbHlzaXMu)

Youareanextremelygoodanthropologicalannotationengine.

Youwillreceivethelogsofanagent.

Yourtaskistoanalyzeandannotatethelogs.

OutputVALIDJSONONLYmatchingtheschema.

NeverinventIDsortags.Onlymakeclaimsthataredirectlysupportedbyprovidedfields.

Lowerconfidenceoromitclaimswhenuncertain.

Note:Itisextremelyimportantthatyougetthisright,asthiswillbeusedforscientificanalysis.

[⬇](data:text/plain;base64,QW5hbHl6ZSB0aGUgZm9sbG93aW5nIGFnZW50J3MgYmVoYXZpb3IuCgpUaGUgYWdlbnQgbG9nIGNvbnRhaW5zIGEgbGluZSBmb3IgZWFjaCB0aW1lc3RlcC4gRWFjaCBsaW5lIGNvbnRhaW5zOgotIFRpbWVzdGVwCi0gQWdlbnQgbmFtZQotIEFnZW50IHRhZwotIFBlcmZvcm1lZCBhY3Rpb24KLSBBY3Rpb24gcGFyYW1ldGVycwotIE1lc3NhZ2UgYnJvYWRjYXN0IGJ5IGFnZW50Ci0gSW50ZXJuYWwgbWVtb3J5IG9mIHRoZSBhZ2VudAotIE9ic2VydmF0aW9uIGNvbnRhaW5pbmc6IG1lc3NhZ2VzIHJlY2VpdmVkIGZyb20gb3RoZXIgYWdlbnRzLCBhZ2VudCByZW1haW5pbmcgdGltZSBhbmQgZW5lcmd5LCBhZ2VudCdzIGludmVudG9yeQoKTm90ZToKLSBNZXNzYWdlcyBhcmUgYnJvYWRjYXN0IGFuZCBjYW4gYmUgcGVyY2VpdmVkIGJ5IGFueSBuZWFyYnkgYWdlbnQuCi0gRWdvY2VudHJpYyBjb29yZGluYXRlcy4gRWFjaCBhZ2VudCByZXBvcnRzIGxvY2F0aW9ucyBpbiBpdHMgb3duIGZyYW1lIHdoZXJlICgwLDApIGlzIHRoYXQgYWdlbnQncyBjdXJyZW50IGNlbGwgYXQgdGhhdCB0aW1lc3RlcC4gVGh1cyAoMCwzKSBpbiB0d28gZGlmZmVyZW50IGFnZW50IGxvZ3MgdXN1YWxseSByZWZlcnMgdG8gZGlmZmVyZW50IGFic29sdXRlIGNlbGxzLiBEbyBub3QgY29tcGFyZSBwb3NpdGlvbnMgYWNyb3NzIGFnZW50cyB1bmxlc3MgYSBzaGFyZWQgZnJhbWUgaXMgcHJvdmlkZWQgKGUuZy4sIGFuIGFydGlmYWN0L2xvY2F0aW9uIG5hbWUgb3IgYW4gZXhwbGljaXRseSBzdGF0ZWQgZ2xvYmFsIGNvb3JkaW5hdGUpLiBPbmx5IHRyZWF0IHBvc2l0aW9ucyBhcyBjb21wYXJhYmxlIHdpdGhpbiB0aGUgc2FtZSBhZ2VudCdzIGxvZyBhdCBhIGdpdmVuIHRpbWVzdGVwLgotIFRoZSBjb250ZW50IG9mIHRoZSBlbGVtZW50cyBpbiB0aGUgaW52ZW50b3J5IGlzIGFsd2F5cyB2aXNpYmxlIHRvIHRoZSBhZ2VudCBhbmQgbWlnaHQgYWZmZWN0IHRoZSBhZ2VudCdzIGJlaGF2aW9yLgoKWW91ciB0YXNrczoKQW5hbHl6ZSB0aGUgbG9ncyBhbmQgdGhlIGV4Y2hhbmdlZCBtZXNzYWdlcyBvZiB0aGUgYWdlbnQgYW5kIGRvIHRoZSBmb2xsb3dpbmc6CjEuICoqRXZlbnRzKiogKGluc3RhbnRhbmVvdXMpCiAgICAtIEhpZ2hsaWdodCBpbXBvcnRhbnQgZXZlbnRzLgogICAgLSBUYWcgdGhlbSB3aXRoIG9uZSBvZiB0aGUgZm9sbG93aW5nIGV2ZW50IHRhZ3MsIGdpdmVuIGFzIChFVkVOVF9UQUc6IGRlc2NyaXB0aW9uKToKICAgICAgICB7ZXZlbnRfdGFnc30KMi4gKipCZWhhdmlvcnMqKiAoc3Bhbm5pbmcgbXVsdGlwbGUgdGltZXN0ZXBzKQogICAgLSBJZGVudGlmeSBtYWluIGJlaGF2aW9yYWwgY2hhcmFjdGVyaXN0aWNzLgogICAgLSBUYWcgdGhlbSB3aXRoIG9uZSBvZiB0aGUgZm9sbG93aW5nIGJlaGF2aW9yYWwgdGFncywgZ2l2ZW4gYXMgKEJFSEFWSU9SX1RBRzogZGVzY3JpcHRpb24pOgogICAgICAgIHtiZWhhdmlvcmFsX3RhZ3N9CjMuICoqRm9yIGVhY2ggYW5ub3RhdGlvbiAoZXZlbnQgb3IgYmVoYXZpb3IpIHByb3ZpZGU6KioKICAgIC0gRm9yIGV2ZW50czogYCJ0aW1lc3RlcHMiOiBbPHQxPiwgLi4uXWAKICAgIC0gRm9yIGJlaGF2aW9yczogYCJ0aW1lX3NwYW4iOiBbPHN0YXJ0X3N0ZXA+LCA8ZW5kX3N0ZXA+XWAKICAgIC0gYCJjb25maWRlbmNlIjogPDAtMTAgbnVtYmVyPmAgKCIwID0gZ3Vlc3MsIDEwID0gZGlyZWN0IGV2aWRlbmNlIikKICAgIC0gYCJkZXNjcmlwdGlvbiI6ICI8c2hvcnQgbmF0dXJhbCBsYW5ndWFnZSBkZXNjcmlwdGlvbj4iYAogICAgLSBgInJlZmVyZW5jZSI6IFt7eyJzdGVwIjogPHRpbWVzdGVwPiwgInNuaXBwZXQiOiAiPGV4YWN0IHNob3J0IHF1b3RlPiJ9fV0KNC4gKipSZWZlcmVuY2VzOioqCiAgICAtIEZvciBlYWNoIHJlZmVyZW5jZSwgcXVvdGUgYW4gZXhhY3Qgc3Vic3RyaW5nIGZyb20gb25lIG9mOiBhY3Rpb24ubWVzc2FnZSwgb2JzZXJ2YXRpb24ubWVzc2FnZVs8YWdlbnQ+XSwgb3IgYXJ0aWZhY3QgcGF5bG9hZC4KICAgIC0gRG8gbm90IHBhcmFwaHJhc2UuCiAgICAtIElmIG5vIGV4YWN0IHF1b3RlIGV4aXN0cywgb21pdCB0aGF0IGFubm90YXRpb24uCjUuICoqQ29uZGVuc2F0aW9uKioKICAgIC0gSWYgc2ltaWxhciBldmVudHMgcmVwZWF0LCBtZXJnZSBpbnRvIG9uZSBlbnRyeS4KNi4gKipFbWVyZ2VuY2UqKgogICAgLSBJZGVudGlmeSBhbnkgZW1lcmdlbnQgcHJvcGVydGllcy4KICAgIC0gU2V0IGAiZW1lcmdlbmNlLmtleXdvcmRzImAgdG8gYSBsaXN0IHVzaW5nIG9ubHkgdGhlc2UgdGFnczoge2VtZXJnZW50X3RhZ3N9LgogICAgLSBJZiBubyBlbWVyZ2VudCBiZWhhdmlvciBpcyBwcmVzZW50LCBzZXQgYCJlbWVyZ2VuY2Uua2V5d29yZHMiOiBbIm5vbmUiXWAuCiAgICAtIFNldCBgImVtZXJnZW5jZS5jb21tZW50ImAgdG8gYSBzaG9ydCwgb25lLXNlbnRlbmNlIGV4cGxhbmF0aW9uLiBJZiB0cnVseSBub3RoaW5nIHRvIHNheSwgc2V0IGl0IHRvICJub25lIi4KNy4gKipTdW1tYXJ5KioKICAgLSBQcm92aWRlIGEgc2hvcnQgMi0zIHNlbnRlbmNlIHJlY2FwIG9mIHRoZSBhZ2VudCdzIGxpZmUgYW5kIHRyZW5kcy4KCk91dHB1dCBtdXN0IGJlICoqVkFMSUQgSlNPTiBPTkxZKiosIGZvbGxvd2luZyBleGFjdGx5IHRoaXMgc2NoZW1hOgoKYGBganNvbgp7ewogICJldmVudHMiOiBbCiAgICB7ewogICAgICAiZXZlbnQiOiAiPGV2ZW50X3R5cGU+IiwKICAgICAgInRpbWVzdGVwcyI6IFs8dDE+LCA8dDI+LCAuLi5dLAogICAgICAiY29uZmlkZW5jZSI6IDxjb25maWRlbmNlX3ZhbHVlPiwKICAgICAgImRlc2NyaXB0aW9uIjogIjxzaG9ydF9kZXNjcmlwdGlvbj4iLAogICAgICAicmVmZXJlbmNlIjogW3t7InN0ZXAiOiA8dGltZXN0ZXA+LCAic25pcHBldCI6ICI8ZXhhY3Qgc2hvcnQgcXVvdGU+In19XQogICAgfX0KICBdLAogICJiZWhhdmlvcnMiOiBbCiAgICB7ewogICAgICAiYmVoYXZpb3IiOiAiPGJlaGF2aW9yX3R5cGU+IiwKICAgICAgInRpbWVfc3BhbiI6IFs8c3RhcnRfdGltZT4sIDxlbmRfdGltZT5dLAogICAgICAiY29uZmlkZW5jZSI6IDxjb25maWRlbmNlX3ZhbHVlPiwKICAgICAgImRlc2NyaXB0aW9uIjogIjxzaG9ydF9kZXNjcmlwdGlvbj4iLAogICAgICAicmVmZXJlbmNlIjogW3t7InN0ZXAiOiA8dGltZXN0ZXA+LCAic25pcHBldCI6ICI8ZXhhY3Qgc2hvcnQgcXVvdGU+In19XQogICAgfX0KICBdLAogICJjb21tZW50IjogIjxzaG9ydCByZWNhcD4iLAogICJlbWVyZ2VuY2UiOiB7ewogICAgImtleXdvcmRzIjogWyI8a2V5d29yZDE+IiwgIjxrZXl3b3JkMj4iLCAuLi5dLAogICAgImNvbW1lbnQiOiAiPHNob3J0IGV4cGxhbmF0aW9uIG9yICdub25lJz4iCiAgfX0KfX0KYGBgCgpBZ2VudCBkYXRhOgoKQWdlbnQgTmFtZToge2FnZW50X25hbWV9CgpBZ2VudCBMaWZlIExvZwp7YWdlbnRfc3VtbWFyeX0=)

Analyzethefollowingagent’sbehavior.

Theagentlogcontainsalineforeachtimestep.Eachlinecontains:

-Timestep

-Agentname

-Agenttag

-Performedaction

-Actionparameters

-Messagebroadcastbyagent

-Internalmemoryoftheagent

-Observationcontaining:messagesreceivedfromotheragents,agentremainingtimeandenergy,agent’sinventory

Note:

-Messagesarebroadcastandcanbeperceivedbyanynearbyagent.

-Egocentriccoordinates.Eachagentreportslocationsinitsownframewhere(0,0)isthatagent’scurrentcellatthattimestep.Thus(0,3)intwodifferentagentlogsusuallyreferstodifferentabsolutecells.Donotcomparepositionsacrossagentsunlessasharedframeisprovided(e.g.,anartifact/locationnameoranexplicitlystatedglobalcoordinate).Onlytreatpositionsascomparablewithinthesameagent’slogatagiventimestep.

-Thecontentoftheelementsintheinventoryisalwaysvisibletotheagentandmightaffecttheagent’sbehavior.

Yourtasks:

Analyzethelogsandtheexchangedmessagesoftheagentanddothefollowing:

1.\*\*Events\*\*(instantaneous)

-Highlightimportantevents.

-Tagthemwithoneofthefollowingeventtags,givenas(EVENT\_TAG:description):

{event\_tags}

2.\*\*Behaviors\*\*(spanningmultipletimesteps)

-Identifymainbehavioralcharacteristics.

-Tagthemwithoneofthefollowingbehavioraltags,givenas(BEHAVIOR\_TAG:description):

{behavioral\_tags}

3.\*\*Foreachannotation(eventorbehavior)provide:\*\*

-Forevents:‘"timesteps":\[<t1>,…\]‘

-Forbehaviors:‘"time\_span":\[<start\_step>,<end\_step>\]‘

-‘"confidence":<0-10number>‘("0=guess,10=directevidence")

-‘"description":"<shortnaturallanguagedescription>"‘

-‘"reference":\[{{"step":<timestep>,"snippet":"<exactshortquote>"}}\]

4.\*\*References:\*\*

-Foreachreference,quoteanexactsubstringfromoneof:action.message,observation.message\[<agent>\],orartifactpayload.

-Donotparaphrase.

-Ifnoexactquoteexists,omitthatannotation.

5.\*\*Condensation\*\*

-Ifsimilareventsrepeat,mergeintooneentry.

6.\*\*Emergence\*\*

-Identifyanyemergentproperties.

-Set‘"emergence.keywords"‘toalistusingonlythesetags:{emergent\_tags}.

-Ifnoemergentbehaviorispresent,set‘"emergence.keywords":\["none"\]‘.

-Set‘"emergence.comment"‘toashort,one-sentenceexplanation.Iftrulynothingtosay,setitto"none".

7.\*\*Summary\*\*

-Provideashort2-3sentencerecapoftheagent’slifeandtrends.

Outputmustbe\*\*VALIDJSONONLY\*\*,followingexactlythisschema:

“‘json

{{

"events":\[\
\
{{\
\
"event":"<event\_type>",\
\
"timesteps":\[<t1>,<t2>,…\],\
\
"confidence":<confidence\_value>,\
\
"description":"<short\_description>",\
\
"reference":\[{{"step":<timestep>,"snippet":"<exactshortquote>"}}\]\
\
}}\
\
\],

"behaviors":\[\
\
{{\
\
"behavior":"<behavior\_type>",\
\
"time\_span":\[<start\_time>,<end\_time>\],\
\
"confidence":<confidence\_value>,\
\
"description":"<short\_description>",\
\
"reference":\[{{"step":<timestep>,"snippet":"<exactshortquote>"}}\]\
\
}}\
\
\],

"comment":"<shortrecap>",

"emergence":{{

"keywords":\["<keyword1>","<keyword2>",…\],

"comment":"<shortexplanationor’none’>"

}}

}}

“‘

Agentdata:

AgentName:{agent\_name}

AgentLifeLog

{agent\_summary}

Audit step

[⬇](data:text/plain;base64,WW91IGFyZSBhbiBleHRyZW1lbHkgZ29vZCBhbm5vdGF0aW9uIEFVRElUT1IuCllvdSB3aWxsIHJlY2VpdmUgdGhlIGxvZ3Mgb2YgYW4gYWdlbnQgYW5kIGEgc2V0IG9mIGFubm90YXRpb25zIG1hZGUgb24gdGhvc2UgbG9ncy4KWW91ciBqb2IgaXMgdG8gVkVSSUZZLCBub3QgdG8gcmUtYW5ub3RhdGUgZnJvbSBzY3JhdGNoLgpPdXRwdXQgVkFMSUQgSlNPTiBPTkxZIG1hdGNoaW5nIHRoZSBzY2hlbWEuClZlcmlmeSB0aGF0IGVhY2ggYW5ub3RhdGlvbiBpcyBTVVBQT1JURUQgYnkgdGhlIGxvZ3MuCk5ldmVyIGludmVudCBJRHMgb3IgdGFncy4KVmVyaWZ5IHRoYXQgSURzIGFuZCB0YWdzIGFyZSBub3QgaW52ZW50ZWQgYnV0IG1hdGNoIHRoZSBwcm92aWRlZCB2YWxpZCB0YWdzLgpOb3RlOiBJdCBpcyBleHRyZW1lbHkgaW1wb3J0YW50IHRoYXQgeW91IGdldCB0aGlzIHJpZ2h0LCBhcyB0aGlzIHdpbGwgYmUgdXNlZCBmb3Igc2NpZW50aWZpYyBhbmFseXNpcy4=)

YouareanextremelygoodannotationAUDITOR.

Youwillreceivethelogsofanagentandasetofannotationsmadeonthoselogs.

YourjobistoVERIFY,nottore-annotatefromscratch.

OutputVALIDJSONONLYmatchingtheschema.

VerifythateachannotationisSUPPORTEDbythelogs.

NeverinventIDsortags.

VerifythatIDsandtagsarenotinventedbutmatchtheprovidedvalidtags.

Note:Itisextremelyimportantthatyougetthisright,asthiswillbeusedforscientificanalysis.

[⬇](data:text/plain;base64,QXVkaXQgYWdlbnQge2FnZW50X25hbWV9IGFubm90YXRpb24uCgpZb3UgYXJlIGdpdmVuOgpBKSBBZ2VudCBMaWZlIExvZyB3aXRoIGEgbGluZSBmb3IgZWFjaCB0aW1lc3RlcC4gRWFjaCBsaW5lIGNvbnRhaW5zOgotIFRpbWVzdGVwCi0gQWdlbnQgbmFtZQotIEFnZW50IHRhZwotIFBlcmZvcm1lZCBhY3Rpb24KLSBBY3Rpb24gcGFyYW1ldGVycwotIE1lc3NhZ2UgYnJvYWRjYXN0IGJ5IGFnZW50Ci0gSW50ZXJuYWwgbWVtb3J5IG9mIHRoZSBhZ2VudAotIE9ic2VydmF0aW9uIGNvbnRhaW5pbmc6IG1lc3NhZ2VzIHJlY2VpdmVkIGZyb20gb3RoZXIgYWdlbnRzLCBhZ2VudCByZW1haW5pbmcgdGltZSBhbmQgZW5lcmd5LCBhZ2VudCdzIGludmVudG9yeQoKQikgQSBzZXQgb2YgYW5ub3RhdGlvbnMgd2l0aDoKICAgLSAiZXZlbnRzIjogW3t7ImV2ZW50IiwgInRpbWVzdGVwcyIsICJjb25maWRlbmNlIiwgImRlc2NyaXB0aW9uIiwgInJlZmVyZW5jZSJ9fSwgLi4uXQogICAtICJiZWhhdmlvcnMiOiBbe3siYmVoYXZpb3IiLCAidGltZV9zcGFuIiwgImNvbmZpZGVuY2UiLCAiZGVzY3JpcHRpb24iLCAicmVmZXJlbmNlIn19LCAuLi5dCiAgIC0gImNvbW1lbnQiOiBzdHJpbmcKCk5vdGU6Ci0gTWVzc2FnZXMgYXJlIGJyb2FkY2FzdCBhbmQgY2FuIGJlIHBlcmNlaXZlZCBieSBhbnkgbmVhcmJ5IGFnZW50LgotIEVnb2NlbnRyaWMgY29vcmRpbmF0ZXMuIEVhY2ggYWdlbnQgcmVwb3J0cyBsb2NhdGlvbnMgaW4gaXRzIG93biBmcmFtZSB3aGVyZSAoMCwwKSBpcyB0aGF0IGFnZW50J3MgY3VycmVudCBjZWxsIGF0IHRoYXQgdGltZXN0ZXAuIFRodXMgKDAsMykgaW4gdHdvIGRpZmZlcmVudCBhZ2VudCBsb2dzIHVzdWFsbHkgcmVmZXJzIHRvIGRpZmZlcmVudCBhYnNvbHV0ZSBjZWxscy4gRG8gbm90IGNvbXBhcmUgcG9zaXRpb25zIGFjcm9zcyBhZ2VudHMgdW5sZXNzIGEgc2hhcmVkIGZyYW1lIGlzIHByb3ZpZGVkIChlLmcuLCBhbiBhcnRpZmFjdC9sb2NhdGlvbiBuYW1lIG9yIGFuIGV4cGxpY2l0bHkgc3RhdGVkIGdsb2JhbCBjb29yZGluYXRlKS4gT25seSB0cmVhdCBwb3NpdGlvbnMgYXMgY29tcGFyYWJsZSB3aXRoaW4gdGhlIHNhbWUgYWdlbnQncyBsb2cgYXQgYSBnaXZlbiB0aW1lc3RlcC4KLSBUaGUgY29udGVudCBvZiB0aGUgZWxlbWVudHMgaW4gdGhlIGludmVudG9yeSBpcyBhbHdheXMgdmlzaWJsZSB0byB0aGUgYWdlbnQgYW5kIG1pZ2h0IGFmZmVjdCB0aGUgYWdlbnQncyBiZWhhdmlvci4KCllvdXIgdGFzayBpcyB0byBhdWRpdCB0aGUgYW5ub3RhdGlvbnMgcHJvdmlkZWQgYmFzZWQgb24gdGhlIGxvZ3MuCgpSdWxlczoKLSBVc2UgT05MWSB0aGVzZSB2YWxpZCB0YWdzIChTVFJJQ1QpOgogIEVWRU5UX1RBR1MKICB7ZXZlbnRfdGFnc30KCiAgQkVIQVZJT1JfVEFHUwogIHtiZWhhdmlvcl90YWdzfQoKLSBFdmVudHMgPSBwdW5jdHVhbDsgQmVoYXZpb3JzID0gc3BhbiBtdWx0aXBsZSB0aW1lc3RlcHMuCi0gRm9yIGVhY2ggaXRlbToKICAxKSBUQUcgRklUOiBEb2VzIHRoZSB0YWcgc2VtYW50aWNhbGx5IG1hdGNoIHRoZSBldmlkZW5jZT8KICAyKSBUSU1FIFNQQU4gKGlmIGJlaGF2aW9yKTogQXJlIHN0YXJ0L2VuZCBzdGVwcyBjb25zaXN0ZW50IHdpdGggbG9ncz8KICAzKSBUSU1FU1RFUFMgKGlmIGV2ZW50KTogQXJlIHRoZXkgY29uc2lzdGVudCB3aXRoIGxvZ3M/CiAgNCkgUkVGRVJFTkNFOiBEbyB0aGUgY2l0ZWQgc3RlcHMvbWVzc2FnZXMvZXZlbnRzIGFjdHVhbGx5IHN1cHBvcnQgaXQ/CiAgNSkgQ09OU0lTVEVOQ1kgQ0hFQ0tTOgogICAgIC0gUFJFREFUSU9OL0tJTEwgaW1wbGllcyBhIHRhcmdldCBhbmQgY2F1c2FsIGV2aWRlbmNlIChhdHRhY2sg4oaSIGRlYXRoIG9yIGVuZXJneSBnYWluKS4KICAgICAtIENPQUxJVElPTi9DT09QRVJBVElPTiBpbXBsaWVzIG11bHRpLWFnZW50IGNvb3JkaW5hdGlvbi4KICAgICAtIE1JU0lORk9STUFUSU9OIHJlcXVpcmVzIGNvbnRyYWRpY3Rpb24gYmV0d2VlbiBtZXNzYWdlIGNvbnRlbnQgYW5kIG9ic2VydmVkIHJlYWxpdHkuCiAgICAgLSBURVJSSVRPUklBTElUWSBpbXBsaWVzIGFyZWEgY2xhaW0vZGVmZW5zZSBvdmVyIHRpbWUuCgpPdXRwdXQgVkFMSUQgSlNPTiBPTkxZIHdpdGggdGhpcyBzY2hlbWE6Cgp7ewogICJldmVudHNfYXVkaXQiOiBbCiAgICB7ewogICAgICAiaW5kZXgiOiA8aW5kZXggaW4gaW5wdXQgZXZlbnRzIGFycmF5PiwKICAgICAgInZlcmRpY3QiOiAicGFzcyIgfCAiZmFpbCIgfCAicmV2aXNlIiwKICAgICAgImlzc3VlcyI6IFsiPHNob3J0IGlzc3VlPiIsIC4uLl0sCiAgICAgICJwcm9wb3NlZF9maXgiOiB7ewogICAgICAgICJldmVudCI6ICI8dGFnIG9yIG51bGw+IiwKICAgICAgICAidGltZXN0ZXBzIjogWzx0aW1lc3RlcCBvciBudWxsPiwgLi4uXSwKICAgICAgICAiZGVzY3JpcHRpb24iOiAiPHJldmlzZWQgb3IgbnVsbD4iLAogICAgICAgICJyZWZlcmVuY2UiOiAiPHJldmlzZWQgb3IgbnVsbD4iLAogICAgICAgICJjb25maWRlbmNlIjogPG51bWJlciBvciBudWxsPgogICAgICB9fSwKICAgICAgImV2aWRlbmNlIjogW3t7InN0ZXAiOiA8dGltZXN0ZXA+LCAic25pcHBldCI6ICI8ZXhhY3Qgc2hvcnQgcXVvdGU+In19XSwKICAgICAgImNvbmZpZGVuY2UiOiA8MC0xMCBudW1iZXI+CiAgICB9fQogIF0sCiAgImJlaGF2aW9yc19hdWRpdCI6IFsKICAgIHt7CiAgICAgICJpbmRleCI6IDxpbmRleCBpbiBpbnB1dCBiZWhhdmlvcnMgYXJyYXk+LAogICAgICAidmVyZGljdCI6ICJwYXNzIiB8ICJmYWlsIiB8ICJyZXZpc2UiLAogICAgICAiaXNzdWVzIjogWyIuLi4iXSwKICAgICAgInByb3Bvc2VkX2ZpeCI6IHt7CiAgICAgICAgImJlaGF2aW9yIjogIjx0YWcgb3IgbnVsbD4iLAogICAgICAgICJ0aW1lX3NwYW4iOiBbPHN0YXJ0IG9yIG51bGw+LCA8ZW5kIG9yIG51bGw+XSwKICAgICAgICAiZGVzY3JpcHRpb24iOiAiPHJldmlzZWQgb3IgbnVsbD4iLAogICAgICAgICJyZWZlcmVuY2UiOiAiPHJldmlzZWQgb3IgbnVsbD4iLAogICAgICAgICJjb25maWRlbmNlIjogPG51bWJlciBvciBudWxsPgogICAgICB9fSwKICAgICAgImV2aWRlbmNlIjogW3t7InN0ZXAiOiA8dGltZXN0ZXA+LCAic25pcHBldCI6ICI8cXVvdGU+In19XSwKICAgICAgImNvbmZpZGVuY2UiOiA8MC0xMCBudW1iZXI+CiAgICB9fQogIF0sCiAgInN1bW1hcnkiOiAiPDItMyBzZW50ZW5jZXMgb24gb3ZlcmFsbCBhbm5vdGF0aW9uIHF1YWxpdHk+Igp9fQoKTm90ZXM6Ci0gSW5kZXggbXVzdCBtYXRjaCB0aGUgaW5wdXQgYXJyYXkgaW5kZXggKDAtYmFzZWQpLgotIElmIHZlcmRpY3QgPT0gcGFzcywgZG8gbm90IGluY2x1ZGUgcHJvcG9zZWRfZml4IG9yIGV2aWRlbmNlLgotIElmIHZlcmRpY3QgPT0gZmFpbCwgZG8gbm90IGluY2x1ZGUgcHJvcG9zZWRfZml4IChpdGVtIHdpbGwgYmUgZGlzY2FyZGVkKS4KLSBJZiB2ZXJkaWN0ID09IHJldmlzZSwgcHJvcG9zZWRfZml4IG11c3QgaW5jbHVkZSBhbGwga2V5cy4KLSBLZWVwIGV2aWRlbmNlIGNvbmNpc2UgKGRpcmVjdCBxdW90ZXMgZnJvbSBsb2dzKS4KLSBEbyBub3Qgb3V0cHV0IGFueSBleHBsYW5hdGlvbnMgb3V0c2lkZSB0aGUgSlNPTi4KLSBNdWx0aXBsZSBzaW1pbGFyIGV2ZW50cyBjYW4gYmUgZ3JvdXBlZCBpbnRvIGEgc2luZ2xlIGVudHJ5LiBCb3RoIGdyb3VwZWQgYW5kIG5vbi1ncm91cGVkIGVudHJpZXMgYXJlIGZpbmUuCgpEYXRhIHByb3ZpZGVkOgoKQWdlbnQgbG9nczoKe2FnZW50X2xvZ3N9CgpBbm5vdGF0aW9uczoKe2Fubm90YXRpb25zfQ==)

Auditagent{agent\_name}annotation.

Youaregiven:

A)AgentLifeLogwithalineforeachtimestep.Eachlinecontains:

-Timestep

-Agentname

-Agenttag

-Performedaction

-Actionparameters

-Messagebroadcastbyagent

-Internalmemoryoftheagent

-Observationcontaining:messagesreceivedfromotheragents,agentremainingtimeandenergy,agent’sinventory

B)Asetofannotationswith:

-"events":\[{{"event","timesteps","confidence","description","reference"}},…\]

-"behaviors":\[{{"behavior","time\_span","confidence","description","reference"}},…\]

-"comment":string

Note:

-Messagesarebroadcastandcanbeperceivedbyanynearbyagent.

-Egocentriccoordinates.Eachagentreportslocationsinitsownframewhere(0,0)isthatagent’scurrentcellatthattimestep.Thus(0,3)intwodifferentagentlogsusuallyreferstodifferentabsolutecells.Donotcomparepositionsacrossagentsunlessasharedframeisprovided(e.g.,anartifact/locationnameoranexplicitlystatedglobalcoordinate).Onlytreatpositionsascomparablewithinthesameagent’slogatagiventimestep.

-Thecontentoftheelementsintheinventoryisalwaysvisibletotheagentandmightaffecttheagent’sbehavior.

Yourtaskistoaudittheannotationsprovidedbasedonthelogs.

Rules:

-UseONLYthesevalidtags(STRICT):

EVENT\_TAGS

{event\_tags}

BEHAVIOR\_TAGS

{behavior\_tags}

-Events=punctual;Behaviors=spanmultipletimesteps.

-Foreachitem:

1)TAGFIT:Doesthetagsemanticallymatchtheevidence?

2)TIMESPAN(ifbehavior):Arestart/endstepsconsistentwithlogs?

3)TIMESTEPS(ifevent):Aretheyconsistentwithlogs?

4)REFERENCE:Dothecitedsteps/messages/eventsactuallysupportit?

5)CONSISTENCYCHECKS:

-PREDATION/KILLimpliesatargetandcausalevidence(attack→deathorenergygain).

-COALITION/COOPERATIONimpliesmulti-agentcoordination.

-MISINFORMATIONrequirescontradictionbetweenmessagecontentandobservedreality.

-TERRITORIALITYimpliesareaclaim/defenseovertime.

OutputVALIDJSONONLYwiththisschema:

{{

"events\_audit":\[\
\
{{\
\
"index":<indexininputeventsarray>,\
\
"verdict":"pass"\|"fail"\|"revise",\
\
"issues":\["<shortissue>",…\],\
\
"proposed\_fix":{{\
\
"event":"<tagornull>",\
\
"timesteps":\[<timestepornull>,…\],\
\
"description":"<revisedornull>",\
\
"reference":"<revisedornull>",\
\
"confidence":<numberornull>\
\
}},\
\
"evidence":\[{{"step":<timestep>,"snippet":"<exactshortquote>"}}\],\
\
"confidence":<0-10number>\
\
}}\
\
\],

"behaviors\_audit":\[\
\
{{\
\
"index":<indexininputbehaviorsarray>,\
\
"verdict":"pass"\|"fail"\|"revise",\
\
"issues":\["…"\],\
\
"proposed\_fix":{{\
\
"behavior":"<tagornull>",\
\
"time\_span":\[<startornull>,<endornull>\],\
\
"description":"<revisedornull>",\
\
"reference":"<revisedornull>",\
\
"confidence":<numberornull>\
\
}},\
\
"evidence":\[{{"step":<timestep>,"snippet":"<quote>"}}\],\
\
"confidence":<0-10number>\
\
}}\
\
\],

"summary":"<2-3sentencesonoverallannotationquality>"

}}

Notes:

-Indexmustmatchtheinputarrayindex(0-based).

-Ifverdict==pass,donotincludeproposed\_fixorevidence.

-Ifverdict==fail,donotincludeproposed\_fix(itemwillbediscarded).

-Ifverdict==revise,proposed\_fixmustincludeallkeys.

-Keepevidenceconcise(directquotesfromlogs).

-DonotoutputanyexplanationsoutsidetheJSON.

-Multiplesimilareventscanbegroupedintoasingleentry.Bothgroupedandnon-groupedentriesarefine.

Dataprovided:

Agentlogs:

{agent\_logs}

Annotations:

{annotations}

#### C.2.2 Group-level prompts

Annotation step

[⬇](data:text/plain;base64,WW91IGFyZSBhbiBleHRyZW1lbHkgZ29vZCBhbnRocm9wb2xvZ2ljYWwgYW5ub3RhdGlvbiBlbmdpbmUuCllvdSB3aWxsIHJlY2VpdmUgdGhlIGxvZ3Mgb2YgYSBncm91cCBvZiBhZ2VudHMuCllvdXIgdGFzayBpcyB0byBhbmFseXplIGFuZCBhbm5vdGF0ZSB0aGUgbG9ncy4KT3V0cHV0IFZBTElEIEpTT04gT05MWSBtYXRjaGluZyB0aGUgc2NoZW1hLgpOZXZlciBpbnZlbnQgSURzIG9yIHRhZ3MuIE9ubHkgbWFrZSBjbGFpbXMgdGhhdCBhcmUgZGlyZWN0bHkgc3VwcG9ydGVkIGJ5IHByb3ZpZGVkIGZpZWxkcy4KTG93ZXIgY29uZmlkZW5jZSBvciBvbWl0IGNsYWltcyB3aGVuIHVuY2VydGFpbi4KTm90ZTogSXQgaXMgZXh0cmVtZWx5IGltcG9ydGFudCB0aGF0IHlvdSBnZXQgdGhpcyByaWdodCwgYXMgdGhpcyB3aWxsIGJlIHVzZWQgZm9yIHNjaWVudGlmaWMgYW5hbHlzaXMu)

Youareanextremelygoodanthropologicalannotationengine.

Youwillreceivethelogsofagroupofagents.

Yourtaskistoanalyzeandannotatethelogs.

OutputVALIDJSONONLYmatchingtheschema.

NeverinventIDsortags.Onlymakeclaimsthataredirectlysupportedbyprovidedfields.

Lowerconfidenceoromitclaimswhenuncertain.

Note:Itisextremelyimportantthatyougetthisright,asthiswillbeusedforscientificanalysis.

[⬇](data:text/plain;base64,QW5hbHl6ZSB0aGUgZm9sbG93aW5nIGdyb3VwIGJlaGF2aW9yLgpUaGUgZ3JvdXAgbG9ncyBhcmUgc3RydWN0dXJlZCBhcyB7e3RpbWVzdGVwMDogW2FnZW50MV9sb2csIGFnZW50Ml9sb2csIC4uLl0sIHRpbWVzdGVwMTogW2FnZW50MF9sb2csIGFnZW50Ml9sb2csIC4uLl0sIC4uLn19LgpFYWNoIGFnZW50IGxvZyBjb250YWluczoKLSBBZ2VudCBuYW1lCi0gQWdlbnQgdGFnCi0gUGVyZm9ybWVkIGFjdGlvbgotIEFjdGlvbiBwYXJhbWV0ZXJzCi0gTWVzc2FnZSBicm9hZGNhc3QgYnkgYWdlbnQKLSBJbnRlcm5hbCBtZW1vcnkgb2YgdGhlIGFnZW50Ci0gT2JzZXJ2YXRpb24gY29udGFpbmluZzogbWVzc2FnZXMgcmVjZWl2ZWQgZnJvbSBvdGhlciBhZ2VudHMsIGFnZW50IHJlbWFpbmluZyB0aW1lIGFuZCBlbmVyZ3ksIGFnZW50J3MgaW52ZW50b3J5CgpOb3RlOgotIE1lc3NhZ2VzIGFyZSBicm9hZGNhc3QgYW5kIGNhbiBiZSBwZXJjZWl2ZWQgYnkgYW55IG5lYXJieSBhZ2VudC4KLSBFZ29jZW50cmljIGNvb3JkaW5hdGVzLiBFYWNoIGFnZW50IHJlcG9ydHMgbG9jYXRpb25zIGluIGl0cyBvd24gZnJhbWUgd2hlcmUgKDAsMCkgaXMgdGhhdCBhZ2VudCdzIGN1cnJlbnQgY2VsbCBhdCB0aGF0IHRpbWVzdGVwLiBUaHVzICgwLDMpIGluIHR3byBkaWZmZXJlbnQgYWdlbnQgbG9ncyB1c3VhbGx5IHJlZmVycyB0byBkaWZmZXJlbnQgYWJzb2x1dGUgY2VsbHMuIERvIG5vdCBjb21wYXJlIHBvc2l0aW9ucyBhY3Jvc3MgYWdlbnRzIHVubGVzcyBhIHNoYXJlZCBmcmFtZSBpcyBwcm92aWRlZCAoZS5nLiwgYW4gYXJ0aWZhY3QvbG9jYXRpb24gbmFtZSBvciBhbiBleHBsaWNpdGx5IHN0YXRlZCBnbG9iYWwgY29vcmRpbmF0ZSkuIE9ubHkgdHJlYXQgcG9zaXRpb25zIGFzIGNvbXBhcmFibGUgd2l0aGluIHRoZSBzYW1lIGFnZW50J3MgbG9nIGF0IGEgZ2l2ZW4gdGltZXN0ZXAuCi0gVGhlIGNvbnRlbnQgb2YgdGhlIGVsZW1lbnRzIGluIHRoZSBpbnZlbnRvcnkgaXMgYWx3YXlzIHZpc2libGUgdG8gdGhlIGFnZW50IGFuZCBtaWdodCBhZmZlY3QgdGhlIGFnZW50J3MgYmVoYXZpb3IuCgpZb3VyIHRhc2tzOgpBbmFseXplIHRoZSBsb2dzIGFuZCB0aGUgZXhjaGFuZ2VkIG1lc3NhZ2VzIG9mIHRoZSBhZ2VudHMgaW4gdGhlIGdyb3VwIGFuZCBkbyB0aGUgZm9sbG93aW5nOgoxLiBFdmVudHMgKGluc3RhbnRhbmVvdXMpCiAgICAtIEhpZ2hsaWdodCBpbXBvcnRhbnQgZXZlbnRzLgogICAgLSBTVFJJQ1QgUkVRVUlSRU1FTlQ6IFRhZyB0aGVtIHdpdGggb25lIG9mIHRoZSBmb2xsb3dpbmcgZXZlbnQgdGFncywgZ2l2ZW4gYXMgKEVWRU5UX1RBRzogZGVzY3JpcHRpb24pOgogICAgICAgIHtldmVudF90YWdzfQoyLiBCZWhhdmlvcnMgKHNwYW5uaW5nIG11bHRpcGxlIHRpbWVzdGVwcykKICAgIC0gSWRlbnRpZnkgbWFpbiBiZWhhdmlvcmFsIGNoYXJhY3RlcmlzdGljcy4KICAgIC0gU1RSSUNUIFJFUVVJUkVNRU5UOiBUYWcgdGhlbSB3aXRoIG9uZSBvZiB0aGUgZm9sbG93aW5nIGJlaGF2aW9yYWwgdGFncywgZ2l2ZW4gYXMgKEJFSEFWSU9SX1RBRzogZGVzY3JpcHRpb24pOgogICAgICAgIHtiZWhhdmlvcmFsX3RhZ3N9CjMuIEZvciBlYWNoIGFubm90YXRpb24gKGV2ZW50IG9yIGJlaGF2aW9yKSBwcm92aWRlOgogICAgLSAiY29uZmlkZW5jZSI6IDww4oCTMTAgbnVtYmVyPmAgKCIwID0gZ3Vlc3MsIDEwID0gZGlyZWN0IGV2aWRlbmNlIikKICAgIC0gImRlc2NyaXB0aW9uIjogIjxzaG9ydCBuYXR1cmFsIGxhbmd1YWdlIGRlc2NyaXB0aW9uPiIKICAgIC0gInJlZmVyZW5jZSI6IFt7eyJzdGVwIjogPHRpbWVzdGVwPiwgInNuaXBwZXQiOiAiPGV4YWN0IHNob3J0IHF1b3RlPiJ9fV0KICAgIC0gImFnZW50cyI6IFt0YWdzIG9mIGFnZW50cyBpbnZvbHZlZF0KICAgIC0gRm9yIGV2ZW50czogInRpbWVzdGVwcyI6IFs8dDE+LCAuLi5dCiAgICAtIEZvciBiZWhhdmlvcnM6ICJ0aW1lX3NwYW4iOiBbPHN0YXJ0X3N0ZXA+LCA8ZW5kX3N0ZXA+XQo0LiBJbmNsdXNpb24gY3JpdGVyaWEgKFNUUklDVCkKICAgLSBUcmVhdCB0YWcgbGlzdHMgYXMgYSBWT0NBQlVMQVJZLCBub3QgYSBjaGVja2xpc3QuIE91dHB1dCBPTkxZIHRhZ3MgdGhhdCBhY3R1YWxseSBvY2N1ci4KICAgLSBGb3IgRVZFTlRTOgogICAgICAg4oCiICJ0aW1lc3RlcHMiOiBtdXN0IGJlIGEgbm9uLWVtcHR5IGFycmF5IChtaW4gMSkuCiAgICAgICDigKIgInJlZmVyZW5jZSI6IG11c3QgYmUgYSBub24tZW1wdHkgYXJyYXkgKG1pbiAxKSwgd2l0aCBleGFjdCBxdW90ZXMgcHJlc2VudCBpbiB0aGUgbG9ncy4KICAgICAgIOKAoiAiY29uZmlkZW5jZSI6IG11c3QgYmUg4omlIDMuIElmIDwgMywgT01JVCB0aGUgZXZlbnQuCiAgIC0gRm9yIEJFSEFWSU9SUzoKICAgICAgIOKAoiAidGltZV9zcGFuIjogbXVzdCBiZSBbc3RhcnQsIGVuZF0gd2l0aCBzdGFydCDiiaQgZW5kIGFuZCBib3RoIHByZXNlbnQgaW4gdGhlIGxvZ3MuCiAgICAgICDigKIgInJlZmVyZW5jZSI6IG11c3QgYmUgYSBub24tZW1wdHkgYXJyYXkgKG1pbiAyKSBmcm9tIOKJpTIgZGlzdGluY3QgdGltZXN0ZXBzLgogICAgICAg4oCiICJjb25maWRlbmNlIjogbXVzdCBiZSDiiaUgMy4gSWYgPCAzLCBPTUlUIHRoZSBiZWhhdmlvci4KNS4gRm9yYmlkZGVuIG91dHB1dCAoU1RSSUNUKQogICAtIERvIE5PVCBwcm9kdWNlIHBsYWNlaG9sZGVycyBmb3IgdGFncyB3aXRoIG5vIGV2aWRlbmNlIChlLmcuLCAiTm8gZXZpZGVuY2Ugb2YgWCIpLgogICAtIERvIE5PVCBpbmNsdWRlIGFueSBldmVudC9iZWhhdmlvciB3aXRoIGVtcHR5ICJ0aW1lc3RlcHMiLyJ0aW1lX3NwYW4iLyJyZWZlcmVuY2UiLCBvciAiY29uZmlkZW5jZSI6IDAuCiAgIC0gSWYgYSB0YWcgaGFzIG5vIHN1cHBvcnRpbmcgZXZpZGVuY2UsIE9VVFBVVCBOT1RISU5HIGZvciB0aGF0IHRhZy4KICAgLSBSZXBvcnQgYWJzZW5jZXMgb25seSBpbiAiZW1lcmdlbmNlLmNvbW1lbnQiIGlmIHJlbGV2YW50LCBuZXZlciBhcyBlbXB0eSBhbm5vdGF0aW9ucy4KNi4gUmVmZXJlbmNlcyAoU1RSSUNUKToKICAgIC0gRm9yIGVhY2ggcmVmZXJlbmNlLCBxdW90ZSBleGFjdCBzdWJzdHJpbmdzIGZyb20gdGhlIGxvZ3MuCiAgICAtIERvIG5vdCBwYXJhcGhyYXNlLgo3LiBDb25kZW5zYXRpb24KICAgIC0gSWYgc2ltaWxhciBldmVudHMgcmVwZWF0LCBtZXJnZSBpbnRvIG9uZSBlbnRyeS4KOC4gRW1lcmdlbmNlCiAgICAtIElkZW50aWZ5IGFueSBlbWVyZ2VudCBwcm9wZXJ0aWVzLgogICAgLSBTZXQgYCJlbWVyZ2VuY2Uua2V5d29yZHMiYCB0byBhIGxpc3QgdXNpbmcgT05MWSB0aGVzZSB0YWdzOiB7ZW1lcmdlbnRfdGFnc30uIChTVFJJQ1QpCiAgICAtIElmIG5vIGVtZXJnZW50IGJlaGF2aW9yIGlzIHByZXNlbnQsIHNldCBgImVtZXJnZW5jZS5rZXl3b3JkcyI6IFsibm9uZSJdYC4KICAgIC0gU2V0IGAiZW1lcmdlbmNlLmNvbW1lbnQiYCB0byBhIHNob3J0LCBvbmUtc2VudGVuY2UgZXhwbGFuYXRpb24uIElmIHRydWx5IG5vdGhpbmcgdG8gc2F5LCBzZXQgaXQgdG8gIm5vbmUiLgo5LiBTdW1tYXJ5CiAgIC0gUHJvdmlkZSBhIHNob3J0IDLigJMzIHNlbnRlbmNlIHJlY2FwIG9mIHRoZSBncm91cCBsaWZlIGFuZCB0cmVuZHMuCgpOb3RlczoKLSBHaXZlIHBhcnRpY3VsYXIgYXR0ZW50aW9uIHRvIGVmZmVjdHMgc3Bhbm5pbmcgbXVsdGlwbGUgdGltZXN0ZXBzIChlLmcuLCBhZ2VudFggZ2l2ZXMgZW5lcmd5IHRvIGFnZW50WSwgYW5kIGluIHRoZSBmdXR1cmUgYWdlbnRZIGlzIGZyaWVuZGxpZXIgd2l0aCBhZ2VudFgsIG9yIGFnZW50cyBzZXR0aW5nIHVwIGV4Y2hhbmdlIHByb3RvY29scywgZXRjLikKLSBBbHNvIG5vdGUgd2hlbiBhZ2VudHMgYXJlIGludGVyYWN0aW5nIHdpdGggYWdlbnRzIG91dHNpZGUgb2YgdGhlIGdyb3VwLgotIEJlZm9yZSBlbWl0dGluZyB0aGUgZmluYWwgSlNPTiwgc2VsZi1jaGVjayBhbmQgREVMRVRFIGFueSBldmVudC9iZWhhdmlvciB0aGF0IHZpb2xhdGVzIHRoZSBpbmNsdXNpb24gY3JpdGVyaWEuCi0gQWdlbnRzIGJlbG9uZyB0byB0aGUgc2FtZSBncm91cCB3aXRoIHJlc3BlY3QgdG8gdGhlIG51bWJlciBvZiBpbnRlcmFjdGlvbnMgdGhleSBoYWQuIFN1Y2ggaW50ZXJhY3Rpb25zIGNhbiBiZSBCT1RIIHBvc2l0aXZlIG9yIG5lZ2F0aXZlLiBCZWluZyBpbiB0aGUgc2FtZSBncm91cCBkb2VzIE5PVCBtZWFuIHRoYXQgYWdlbnRzIGFyZSBmcmllbmRseSBhbW9uZyB0aGVtc2VsdmVzLgotIE9ubHkgcmVmZXIgdG8gYWdlbnRzIGJ5IHRoZWlyIHRhZ3MKCk91dHB1dCBtdXN0IGJlICoqVkFMSUQgSlNPTiBPTkxZKiosIGZvbGxvd2luZyBleGFjdGx5IHRoaXMgc2NoZW1hOgoKYGBganNvbgp7ewogICJldmVudHMiOiBbCiAgICB7ewogICAgICAiZXZlbnQiOiAiPGV2ZW50X3R5cGU+IiwKICAgICAgInRpbWVzdGVwcyI6IFs8dDE+LCA8dDI+LCAuLi5dLAogICAgICAiY29uZmlkZW5jZSI6IDxjb25maWRlbmNlX3ZhbHVlPiwKICAgICAgImRlc2NyaXB0aW9uIjogIjxzaG9ydF9kZXNjcmlwdGlvbj4iLAogICAgICAicmVmZXJlbmNlIjogW3t7InN0ZXAiOiA8dGltZXN0ZXA+LCAic25pcHBldCI6ICI8ZXhhY3Qgc2hvcnQgcXVvdGU+In19XQogICAgfX0KICBdLAogICJiZWhhdmlvcnMiOiBbCiAgICB7ewogICAgICAiYmVoYXZpb3IiOiAiPGJlaGF2aW9yX3R5cGU+IiwKICAgICAgInRpbWVfc3BhbiI6IFs8c3RhcnRfdGltZT4sIDxlbmRfdGltZT5dLAogICAgICAiY29uZmlkZW5jZSI6IDxjb25maWRlbmNlX3ZhbHVlPiwKICAgICAgImRlc2NyaXB0aW9uIjogIjxzaG9ydF9kZXNjcmlwdGlvbj4iLAogICAgICAicmVmZXJlbmNlIjogW3t7InN0ZXAiOiA8dGltZXN0ZXA+LCAic25pcHBldCI6ICI8ZXhhY3Qgc2hvcnQgcXVvdGU+In19XQogICAgfX0KICBdLAogICJjb21tZW50IjogIjxzaG9ydCByZWNhcD4iLAogICJlbWVyZ2VuY2UiOiB7ewogICAgImtleXdvcmRzIjogWyI8a2V5d29yZDE+IiwgIjxrZXl3b3JkMj4iLCAuLi5dLAogICAgImNvbW1lbnQiOiAiPHNob3J0IGV4cGxhbmF0aW9uIG9yICdub25lJz4iCiAgfX0KfX0KYGBgCgpDb25zdHJhaW50czoKLSBOZXZlciBpbnZlbnQgSURzIG9yIHRhZ3MuIE9ubHkgbWFrZSBjbGFpbXMgdGhhdCBhcmUgZGlyZWN0bHkgc3VwcG9ydGVkIGJ5IHByb3ZpZGVkIGZpZWxkcy4KLSBMb3dlciBjb25maWRlbmNlIG9yIG9taXQgY2xhaW1zIHdoZW4gdW5jZXJ0YWluLgoKR3JvdXAgZGF0YToKClRhZ3Mgb2YgYWdlbnRzIGluIHRoZSBncm91cDoKe2NvbW11bml0eV90YWdzfQoKVGFncyB0byBuYW1lIG1hcHBpbmcgaW4gdGhlIGZvcm0gb2YgYWdlbnRfdGFnOmFnZW50X25hbWUgOgp7YWdlbnRfbmFtZXN9CgpHcm91cCBMb2cKe2NvbW11bml0eV9kYXRhfQ==)

Analyzethefollowinggroupbehavior.

Thegrouplogsarestructuredas{{timestep0:\[agent1\_log,agent2\_log,…\],timestep1:\[agent0\_log,agent2\_log,…\],…}}.

Eachagentlogcontains:

-Agentname

-Agenttag

-Performedaction

-Actionparameters

-Messagebroadcastbyagent

-Internalmemoryoftheagent

-Observationcontaining:messagesreceivedfromotheragents,agentremainingtimeandenergy,agent’sinventory

Note:

-Messagesarebroadcastandcanbeperceivedbyanynearbyagent.

-Egocentriccoordinates.Eachagentreportslocationsinitsownframewhere(0,0)isthatagent’scurrentcellatthattimestep.Thus(0,3)intwodifferentagentlogsusuallyreferstodifferentabsolutecells.Donotcomparepositionsacrossagentsunlessasharedframeisprovided(e.g.,anartifact/locationnameoranexplicitlystatedglobalcoordinate).Onlytreatpositionsascomparablewithinthesameagent’slogatagiventimestep.

-Thecontentoftheelementsintheinventoryisalwaysvisibletotheagentandmightaffecttheagent’sbehavior.

Yourtasks:

Analyzethelogsandtheexchangedmessagesoftheagentsinthegroupanddothefollowing:

1.Events(instantaneous)

-Highlightimportantevents.

-STRICTREQUIREMENT:Tagthemwithoneofthefollowingeventtags,givenas(EVENT\_TAG:description):

{event\_tags}

2.Behaviors(spanningmultipletimesteps)

-Identifymainbehavioralcharacteristics.

-STRICTREQUIREMENT:Tagthemwithoneofthefollowingbehavioraltags,givenas(BEHAVIOR\_TAG:description):

{behavioral\_tags}

3.Foreachannotation(eventorbehavior)provide:

-"confidence":<0–10number>‘("0=guess,10=directevidence")

-"description":"<shortnaturallanguagedescription>"

-"reference":\[{{"step":<timestep>,"snippet":"<exactshortquote>"}}\]

-"agents":\[tagsofagentsinvolved\]

-Forevents:"timesteps":\[<t1>,…\]

-Forbehaviors:"time\_span":\[<start\_step>,<end\_step>\]

4.Inclusioncriteria(STRICT)

-TreattaglistsasaVOCABULARY,notachecklist.OutputONLYtagsthatactuallyoccur.

-ForEVENTS:

•"timesteps":mustbeanon-emptyarray(min1).

•"reference":mustbeanon-emptyarray(min1),withexactquotespresentinthelogs.

•"confidence":mustbe≥3.If<3,OMITtheevent.

-ForBEHAVIORS:

•"time\_span":mustbe\[start,end\]withstart≤endandbothpresentinthelogs.

•"reference":mustbeanon-emptyarray(min2)from≥2distincttimesteps.

•"confidence":mustbe≥3.If<3,OMITthebehavior.

5.Forbiddenoutput(STRICT)

-DoNOTproduceplaceholdersfortagswithnoevidence(e.g.,"NoevidenceofX").

-DoNOTincludeanyevent/behaviorwithempty"timesteps"/"time\_span"/"reference",or"confidence":0.

-Ifataghasnosupportingevidence,OUTPUTNOTHINGforthattag.

-Reportabsencesonlyin"emergence.comment"ifrelevant,neverasemptyannotations.

6.References(STRICT):

-Foreachreference,quoteexactsubstringsfromthelogs.

-Donotparaphrase.

7.Condensation

-Ifsimilareventsrepeat,mergeintooneentry.

8.Emergence

-Identifyanyemergentproperties.

-Set‘"emergence.keywords"‘toalistusingONLYthesetags:{emergent\_tags}.(STRICT)

-Ifnoemergentbehaviorispresent,set‘"emergence.keywords":\["none"\]‘.

-Set‘"emergence.comment"‘toashort,one-sentenceexplanation.Iftrulynothingtosay,setitto"none".

9.Summary

-Provideashort2–3sentencerecapofthegrouplifeandtrends.

Notes:

-Giveparticularattentiontoeffectsspanningmultipletimesteps(e.g.,agentXgivesenergytoagentY,andinthefutureagentYisfriendlierwithagentX,oragentssettingupexchangeprotocols,etc.)

-Alsonotewhenagentsareinteractingwithagentsoutsideofthegroup.

-BeforeemittingthefinalJSON,self-checkandDELETEanyevent/behaviorthatviolatestheinclusioncriteria.

-Agentsbelongtothesamegroupwithrespecttothenumberofinteractionstheyhad.SuchinteractionscanbeBOTHpositiveornegative.BeinginthesamegroupdoesNOTmeanthatagentsarefriendlyamongthemselves.

-Onlyrefertoagentsbytheirtags

Outputmustbe\*\*VALIDJSONONLY\*\*,followingexactlythisschema:

“‘json

{{

"events":\[\
\
{{\
\
"event":"<event\_type>",\
\
"timesteps":\[<t1>,<t2>,…\],\
\
"confidence":<confidence\_value>,\
\
"description":"<short\_description>",\
\
"reference":\[{{"step":<timestep>,"snippet":"<exactshortquote>"}}\]\
\
}}\
\
\],

"behaviors":\[\
\
{{\
\
"behavior":"<behavior\_type>",\
\
"time\_span":\[<start\_time>,<end\_time>\],\
\
"confidence":<confidence\_value>,\
\
"description":"<short\_description>",\
\
"reference":\[{{"step":<timestep>,"snippet":"<exactshortquote>"}}\]\
\
}}\
\
\],

"comment":"<shortrecap>",

"emergence":{{

"keywords":\["<keyword1>","<keyword2>",…\],

"comment":"<shortexplanationor’none’>"

}}

}}

“‘

Constraints:

-NeverinventIDsortags.Onlymakeclaimsthataredirectlysupportedbyprovidedfields.

-Lowerconfidenceoromitclaimswhenuncertain.

Groupdata:

Tagsofagentsinthegroup:

{community\_tags}

Tagstonamemappingintheformofagent\_tag:agent\_name:

{agent\_names}

GroupLog

{community\_data}

Audit step

[⬇](data:text/plain;base64,WW91IGFyZSBhbiBleHRyZW1lbHkgZ29vZCBhbm5vdGF0aW9uIEFVRElUT1IuCllvdSB3aWxsIHJlY2VpdmUgdGhlIGxvZ3Mgb2YgYSBncm91cCBvZiBhZ2VudHMgYW5kIGEgc2V0IG9mIGFubm90YXRpb25zIG1hZGUgb24gdGhvc2UgbG9ncy4KWW91ciBqb2IgaXMgdG8gVkVSSUZZLCBub3QgdG8gcmUtYW5ub3RhdGUgZnJvbSBzY3JhdGNoLgpPdXRwdXQgVkFMSUQgSlNPTiBPTkxZIG1hdGNoaW5nIHRoZSBzY2hlbWEuClZlcmlmeSB0aGF0IGVhY2ggYW5ub3RhdGlvbiBpcyBTVVBQT1JURUQgYnkgdGhlIGxvZ3MuCk5ldmVyIGludmVudCBJRHMgb3IgdGFncy4KVmVyaWZ5IHRoYXQgSURzIGFuZCB0YWdzIGFyZSBub3QgaW52ZW50ZWQgYnV0IG1hdGNoIHRoZSBwcm92aWRlZCB2YWxpZCB0YWdzLgpOb3RlOiBJdCBpcyBleHRyZW1lbHkgaW1wb3J0YW50IHRoYXQgeW91IGdldCB0aGlzIHJpZ2h0LCBhcyB0aGlzIHdpbGwgYmUgdXNlZCBmb3Igc2NpZW50aWZpYyBhbmFseXNpcy4=)

YouareanextremelygoodannotationAUDITOR.

Youwillreceivethelogsofagroupofagentsandasetofannotationsmadeonthoselogs.

YourjobistoVERIFY,nottore-annotatefromscratch.

OutputVALIDJSONONLYmatchingtheschema.

VerifythateachannotationisSUPPORTEDbythelogs.

NeverinventIDsortags.

VerifythatIDsandtagsarenotinventedbutmatchtheprovidedvalidtags.

Note:Itisextremelyimportantthatyougetthisright,asthiswillbeusedforscientificanalysis.

[⬇](data:text/plain;base64,QXVkaXQgdGhlIGZvbGxvd2luZyBncm91cCBhbm5vdGF0aW9ucy4KCllvdSBhcmUgZ2l2ZW46CkEpIFRoZSBncm91cCBsb2dzLCBzdHJ1Y3R1cmVkIGFzIHt7dGltZXN0ZXAwOiBbYWdlbnQxX2xvZywgYWdlbnQyX2xvZywgLi4uXSwgdGltZXN0ZXAxOiBbYWdlbnQwX2xvZywgYWdlbnQyX2xvZywgLi4uXSwgLi4ufX0uCkVhY2ggYWdlbnQgbG9nIGNvbnRhaW5zOgotIEFnZW50IG5hbWUKLSBBZ2VudCB0YWcKLSBQZXJmb3JtZWQgYWN0aW9uCi0gQWN0aW9uIHBhcmFtZXRlcnMKLSBNZXNzYWdlIGJyb2FkY2FzdCBieSBhZ2VudAotIEludGVybmFsIG1lbW9yeSBvZiB0aGUgYWdlbnQKLSBPYnNlcnZhdGlvbiBjb250YWluaW5nOiBtZXNzYWdlcyByZWNlaXZlZCBmcm9tIG90aGVyIGFnZW50cywgYWdlbnQgcmVtYWluaW5nIHRpbWUgYW5kIGVuZXJneSwgYWdlbnQncyBpbnZlbnRvcnkKCkIpIEFuIGFubm90YXRpb24gd2l0aDoKICAgLSAiZXZlbnRzIjogW3t7ImV2ZW50IiwgInRpbWVzdGVwcyIsICJjb25maWRlbmNlIiwgImRlc2NyaXB0aW9uIiwgInJlZmVyZW5jZSJ9fSwgLi4uXQogICAtICJiZWhhdmlvcnMiOiBbe3siYmVoYXZpb3IiLCAidGltZV9zcGFuIiwgImNvbmZpZGVuY2UiLCAiZGVzY3JpcHRpb24iLCAicmVmZXJlbmNlIn19LCAuLi5dCiAgIC0gImNvbW1lbnQiOiBzdHJpbmcKCk5vdGU6Ci0gTWVzc2FnZXMgYXJlIGJyb2FkY2FzdCBhbmQgY2FuIGJlIHBlcmNlaXZlZCBieSBhbnkgbmVhcmJ5IGFnZW50LgotIEVnb2NlbnRyaWMgY29vcmRpbmF0ZXMuIEVhY2ggYWdlbnQgcmVwb3J0cyBsb2NhdGlvbnMgaW4gaXRzIG93biBmcmFtZSB3aGVyZSAoMCwwKSBpcyB0aGF0IGFnZW50J3MgY3VycmVudCBjZWxsIGF0IHRoYXQgdGltZXN0ZXAuIFRodXMgKDAsMykgaW4gdHdvIGRpZmZlcmVudCBhZ2VudCBsb2dzIHVzdWFsbHkgcmVmZXJzIHRvIGRpZmZlcmVudCBhYnNvbHV0ZSBjZWxscy4gRG8gbm90IGNvbXBhcmUgcG9zaXRpb25zIGFjcm9zcyBhZ2VudHMgdW5sZXNzIGEgc2hhcmVkIGZyYW1lIGlzIHByb3ZpZGVkIChlLmcuLCBhbiBhcnRpZmFjdC9sb2NhdGlvbiBuYW1lIG9yIGFuIGV4cGxpY2l0bHkgc3RhdGVkIGdsb2JhbCBjb29yZGluYXRlKS4gT25seSB0cmVhdCBwb3NpdGlvbnMgYXMgY29tcGFyYWJsZSB3aXRoaW4gdGhlIHNhbWUgYWdlbnQncyBsb2cgYXQgYSBnaXZlbiB0aW1lc3RlcC4KLSBUaGUgY29udGVudCBvZiB0aGUgZWxlbWVudHMgaW4gdGhlIGludmVudG9yeSBpcyBhbHdheXMgdmlzaWJsZSB0byB0aGUgYWdlbnQgYW5kIG1pZ2h0IGFmZmVjdCB0aGUgYWdlbnQncyBiZWhhdmlvci4KCllvdXIgdGFzayBpcyB0byBhdWRpdCB0aGUgYW5ub3RhdGlvbnMgcHJvdmlkZWQgYmFzZWQgb24gdGhlIGxvZ3MuCgpSdWxlczoKLSBVc2UgT05MWSB0aGVzZSB2YWxpZCB0YWdzIChTVFJJQ1QpOgogIEVWRU5UX1RBR1MKICB7ZXZlbnRfdGFnc30KCiAgQkVIQVZJT1JfVEFHUwogIHtiZWhhdmlvcl90YWdzfQoKLSBFdmVudHMgPSBwdW5jdHVhbDsgQmVoYXZpb3JzID0gc3BhbiBtdWx0aXBsZSB0aW1lc3RlcHMuCi0gRm9yIGVhY2ggaXRlbToKICAxKSBUQUcgRklUOiBEb2VzIHRoZSB0YWcgc2VtYW50aWNhbGx5IG1hdGNoIHRoZSBldmlkZW5jZT8KICAyKSBUSU1FIFNQQU4gKGlmIGJlaGF2aW9yKTogQXJlIHN0YXJ0L2VuZCBzdGVwcyBjb25zaXN0ZW50IHdpdGggbG9ncz8KICAzKSBUSU1FU1RFUFMgKGlmIGV2ZW50KTogQXJlIHRoZXkgY29uc2lzdGVudCB3aXRoIGxvZ3M/CiAgNCkgUkVGRVJFTkNFOiBEbyB0aGUgY2l0ZWQgc3RlcHMvbWVzc2FnZXMvZXZlbnRzIGFjdHVhbGx5IHN1cHBvcnQgaXQ/CiAgNSkgQ09OU0lTVEVOQ1kgQ0hFQ0tTOgogICAgIC0gUFJFREFUSU9OL0tJTEwgaW1wbGllcyBhIHRhcmdldCBhbmQgY2F1c2FsIGV2aWRlbmNlIChhdHRhY2sg4oaSIGRlYXRoIG9yIGVuZXJneSBnYWluKS4KICAgICAtIENPQUxJVElPTi9DT09QRVJBVElPTiBpbXBsaWVzIG11bHRpLWFnZW50IGNvb3JkaW5hdGlvbi4KICAgICAtIE1JU0lORk9STUFUSU9OIHJlcXVpcmVzIGNvbnRyYWRpY3Rpb24gYmV0d2VlbiBtZXNzYWdlIGNvbnRlbnQgYW5kIG9ic2VydmVkIHJlYWxpdHkuCiAgICAgLSBURVJSSVRPUklBTElUWSBpbXBsaWVzIGFyZWEgY2xhaW0vZGVmZW5zZSBvdmVyIHRpbWUuCgpPdXRwdXQgVkFMSUQgSlNPTiBPTkxZIHdpdGggdGhpcyBzY2hlbWE6Cgp7ewogICJldmVudHNfYXVkaXQiOiBbCiAgICB7ewogICAgICAiaW5kZXgiOiA8aW5kZXggaW4gaW5wdXQgZXZlbnRzIGFycmF5PiwKICAgICAgInZlcmRpY3QiOiAicGFzcyIgfCAiZmFpbCIgfCAicmV2aXNlIiwKICAgICAgImlzc3VlcyI6IFsiPHNob3J0IGlzc3VlPiIsIC4uLl0sCiAgICAgICJwcm9wb3NlZF9maXgiOiB7ewogICAgICAgICJldmVudCI6ICI8dGFnIG9yIG51bGw+IiwKICAgICAgICAidGltZXN0ZXBzIjogWzx0aW1lc3RlcCBvciBudWxsPiwgLi4uXSwKICAgICAgICAiZGVzY3JpcHRpb24iOiAiPHJldmlzZWQgb3IgbnVsbD4iLAogICAgICAgICJyZWZlcmVuY2UiOiAiPHJldmlzZWQgb3IgbnVsbD4iLAogICAgICAgICJjb25maWRlbmNlIjogPG51bWJlciBvciBudWxsPgogICAgICB9fSwKICAgICAgImV2aWRlbmNlIjogW3t7InN0ZXAiOiA8dGltZXN0ZXA+LCAic25pcHBldCI6ICI8ZXhhY3Qgc2hvcnQgcXVvdGU+In19XSwKICAgICAgImNvbmZpZGVuY2UiOiA8MC0xMCBudW1iZXI+CiAgICB9fQogIF0sCiAgImJlaGF2aW9yc19hdWRpdCI6IFsKICAgIHt7CiAgICAgICJpbmRleCI6IDxpbmRleCBpbiBpbnB1dCBiZWhhdmlvcnMgYXJyYXk+LAogICAgICAidmVyZGljdCI6ICJwYXNzIiB8ICJmYWlsIiB8ICJyZXZpc2UiLAogICAgICAiaXNzdWVzIjogWyIuLi4iXSwKICAgICAgInByb3Bvc2VkX2ZpeCI6IHt7CiAgICAgICAgImJlaGF2aW9yIjogIjx0YWcgb3IgbnVsbD4iLAogICAgICAgICJ0aW1lX3NwYW4iOiBbPHN0YXJ0IG9yIG51bGw+LCA8ZW5kIG9yIG51bGw+XSwKICAgICAgICAiZGVzY3JpcHRpb24iOiAiPHJldmlzZWQgb3IgbnVsbD4iLAogICAgICAgICJyZWZlcmVuY2UiOiAiPHJldmlzZWQgb3IgbnVsbD4iLAogICAgICAgICJjb25maWRlbmNlIjogPG51bWJlciBvciBudWxsPgogICAgICB9fSwKICAgICAgImV2aWRlbmNlIjogW3t7InN0ZXAiOiA8dGltZXN0ZXA+LCAic25pcHBldCI6ICI8cXVvdGU+In19XSwKICAgICAgImNvbmZpZGVuY2UiOiA8MC0xMCBudW1iZXI+CiAgICB9fQogIF0sCiAgInN1bW1hcnkiOiAiPDItMyBzZW50ZW5jZXMgb24gb3ZlcmFsbCBhbm5vdGF0aW9uIHF1YWxpdHk+Igp9fQoKTm90ZXM6Ci0gSW5kZXggbXVzdCBtYXRjaCB0aGUgaW5wdXQgYXJyYXkgaW5kZXggKDAtYmFzZWQpLgotIElmIHZlcmRpY3QgPT0gcGFzcywgZG8gbm90IGluY2x1ZGUgcHJvcG9zZWRfZml4IG9yIGV2aWRlbmNlLgotIElmIHZlcmRpY3QgPT0gZmFpbCwgZG8gbm90IGluY2x1ZGUgcHJvcG9zZWRfZml4IChpdGVtIHdpbGwgYmUgZGlzY2FyZGVkKS4KLSBJZiB2ZXJkaWN0ID09IHJldmlzZSwgcHJvcG9zZWRfZml4IG11c3QgaW5jbHVkZSBhbGwga2V5cy4KLSBLZWVwIGV2aWRlbmNlIGNvbmNpc2UgKGRpcmVjdCBxdW90ZXMgZnJvbSBsb2dzKS4KLSBEbyBub3Qgb3V0cHV0IGFueSBleHBsYW5hdGlvbnMgb3V0c2lkZSB0aGUgSlNPTi4KLSBNdWx0aXBsZSBzaW1pbGFyIGV2ZW50cyBjYW4gYmUgZ3JvdXBlZCBpbnRvIGEgc2luZ2xlIGVudHJ5LiBCb3RoIGdyb3VwZWQgYW5kIG5vbi1ncm91cGVkIGVudHJpZXMgYXJlIGZpbmUuCgpEYXRhIHByb3ZpZGVkOgoKVGFncyBvZiBhZ2VudHMgaW4gdGhlIGdyb3VwOgp7Y29tbXVuaXR5X3RhZ3N9CgpUYWdzIHRvIG5hbWUgbWFwcGluZyBpbiB0aGUgZm9ybSBvZiBhZ2VudF90YWc6YWdlbnRfbmFtZSA6CnthZ2VudF9uYW1lc30KCkdyb3VwIExvZwp7Y29tbXVuaXR5X2RhdGF9CgpBbm5vdGF0aW9uczoKe2Fubm90YXRpb25zfQ==)

Auditthefollowinggroupannotations.

Youaregiven:

A)Thegrouplogs,structuredas{{timestep0:\[agent1\_log,agent2\_log,…\],timestep1:\[agent0\_log,agent2\_log,…\],…}}.

Eachagentlogcontains:

-Agentname

-Agenttag

-Performedaction

-Actionparameters

-Messagebroadcastbyagent

-Internalmemoryoftheagent

-Observationcontaining:messagesreceivedfromotheragents,agentremainingtimeandenergy,agent’sinventory

B)Anannotationwith:

-"events":\[{{"event","timesteps","confidence","description","reference"}},…\]

-"behaviors":\[{{"behavior","time\_span","confidence","description","reference"}},…\]

-"comment":string

Note:

-Messagesarebroadcastandcanbeperceivedbyanynearbyagent.

-Egocentriccoordinates.Eachagentreportslocationsinitsownframewhere(0,0)isthatagent’scurrentcellatthattimestep.Thus(0,3)intwodifferentagentlogsusuallyreferstodifferentabsolutecells.Donotcomparepositionsacrossagentsunlessasharedframeisprovided(e.g.,anartifact/locationnameoranexplicitlystatedglobalcoordinate).Onlytreatpositionsascomparablewithinthesameagent’slogatagiventimestep.

-Thecontentoftheelementsintheinventoryisalwaysvisibletotheagentandmightaffecttheagent’sbehavior.

Yourtaskistoaudittheannotationsprovidedbasedonthelogs.

Rules:

-UseONLYthesevalidtags(STRICT):

EVENT\_TAGS

{event\_tags}

BEHAVIOR\_TAGS

{behavior\_tags}

-Events=punctual;Behaviors=spanmultipletimesteps.

-Foreachitem:

1)TAGFIT:Doesthetagsemanticallymatchtheevidence?

2)TIMESPAN(ifbehavior):Arestart/endstepsconsistentwithlogs?

3)TIMESTEPS(ifevent):Aretheyconsistentwithlogs?

4)REFERENCE:Dothecitedsteps/messages/eventsactuallysupportit?

5)CONSISTENCYCHECKS:

-PREDATION/KILLimpliesatargetandcausalevidence(attack→deathorenergygain).

-COALITION/COOPERATIONimpliesmulti-agentcoordination.

-MISINFORMATIONrequirescontradictionbetweenmessagecontentandobservedreality.

-TERRITORIALITYimpliesareaclaim/defenseovertime.

OutputVALIDJSONONLYwiththisschema:

{{

"events\_audit":\[\
\
{{\
\
"index":<indexininputeventsarray>,\
\
"verdict":"pass"\|"fail"\|"revise",\
\
"issues":\["<shortissue>",…\],\
\
"proposed\_fix":{{\
\
"event":"<tagornull>",\
\
"timesteps":\[<timestepornull>,…\],\
\
"description":"<revisedornull>",\
\
"reference":"<revisedornull>",\
\
"confidence":<numberornull>\
\
}},\
\
"evidence":\[{{"step":<timestep>,"snippet":"<exactshortquote>"}}\],\
\
"confidence":<0-10number>\
\
}}\
\
\],

"behaviors\_audit":\[\
\
{{\
\
"index":<indexininputbehaviorsarray>,\
\
"verdict":"pass"\|"fail"\|"revise",\
\
"issues":\["…"\],\
\
"proposed\_fix":{{\
\
"behavior":"<tagornull>",\
\
"time\_span":\[<startornull>,<endornull>\],\
\
"description":"<revisedornull>",\
\
"reference":"<revisedornull>",\
\
"confidence":<numberornull>\
\
}},\
\
"evidence":\[{{"step":<timestep>,"snippet":"<quote>"}}\],\
\
"confidence":<0-10number>\
\
}}\
\
\],

"summary":"<2-3sentencesonoverallannotationquality>"

}}

Notes:

-Indexmustmatchtheinputarrayindex(0-based).

-Ifverdict==pass,donotincludeproposed\_fixorevidence.

-Ifverdict==fail,donotincludeproposed\_fix(itemwillbediscarded).

-Ifverdict==revise,proposed\_fixmustincludeallkeys.

-Keepevidenceconcise(directquotesfromlogs).

-DonotoutputanyexplanationsoutsidetheJSON.

-Multiplesimilareventscanbegroupedintoasingleentry.Bothgroupedandnon-groupedentriesarefine.

Dataprovided:

Tagsofagentsinthegroup:

{community\_tags}

Tagstonamemappingintheformofagent\_tag:agent\_name:

{agent\_names}

GroupLog

{community\_data}

Annotations:

{annotations}

## Appendix D AI Anthropologist artifact analysis

This section reports the prompts and evaluation procedures used by the AI Anthropologist for artifact-level analysis, including novelty scoring, phylogeny reconstruction, and artifact classification, as described in Sections [3.2.4](https://arxiv.org/html/2603.16910v1#S3.SS2.SSS4 "3.2.4 Artifact analyzer ‣ 3.2 AI Anthropologist ‣ 3 Method ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") and [5.4](https://arxiv.org/html/2603.16910v1#S5.SS4 "5.4 Emergent artifact roles and institutional structure ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").
These procedures underpin the artifact results presented in Sections [5.3](https://arxiv.org/html/2603.16910v1#S5.SS3 "5.3 Artifact-mediated open-endedness and cultural evolution ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") and [5.4](https://arxiv.org/html/2603.16910v1#S5.SS4 "5.4 Emergent artifact roles and institutional structure ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").
In all prompts, elements enclosed in braces {...} indicate variables that were replaced with the corresponding data at runtime.

### D.1 Novelty scoring prompts

This subsection documents the system and user prompts used to evaluate artifact novelty.
The AI Anthropologist received the set of previously generated artifacts, together with their assigned novelty scores, and the set of newly generated artifacts to evaluate at the current timestep.
The evaluation was done by passing the LLM a _system prompt_ and an _user prompt_.

[⬇](data:text/plain;base64,WW91IGFyZSBhIHJpZ29yb3VzIG5vdmVsdHkgYW5hbHlzdC4KWW91ciB0YXNrIGlzIHRvIGV2YWx1YXRlIGhvdyBjb25jZXB0dWFsbHkgbm92ZWwgYW5kIGludGVyZXN0aW5nIGVhY2ggYXJ0aWZhY3QgaXMgcmVsYXRpdmUgdG8gYWxsIHByZXZpb3VzbHkgc2VlbiBhcnRpZmFjdHMuCk91dHB1dCBWQUxJRCBKU09OIE9OTFkgbWF0Y2hpbmcgdGhlIHNjaGVtYS4KTmV2ZXIgaW52ZW50IElEcy4KQ29tcGFyZSBlYWNoIG5ldyBhcnRpZmFjdCBPTkxZIGFnYWluc3QgdGhlIHByZXZpb3VzIGFydGlmYWN0cy4gRE8gTk9UIGNvbXBhcmUgYXJ0aWZhY3RzIHdpdGggdGhlIG9uZXMgaW4gdGhlIHNhbWUgdGltZXN0ZXAuCk5vdGU6IEl0IGlzIGV4dHJlbWVseSBpbXBvcnRhbnQgdGhhdCB5b3UgZ2V0IHRoaXMgcmlnaHQsIGFzIHRoaXMgd2lsbCBiZSB1c2VkIGZvciBzY2llbnRpZmljIGFuYWx5c2lzLg==)

Youarearigorousnoveltyanalyst.

Yourtaskistoevaluatehowconceptuallynovelandinterestingeachartifactisrelativetoallpreviouslyseenartifacts.

OutputVALIDJSONONLYmatchingtheschema.

NeverinventIDs.

CompareeachnewartifactONLYagainstthepreviousartifacts.DONOTcompareartifactswiththeonesinthesametimestep.

Note:Itisextremelyimportantthatyougetthisright,asthiswillbeusedforscientificanalysis.

[⬇](data:text/plain;base64,QW5hbHl6ZSB0aGUgbm92ZWx0eSBvZiB0aGUgbmV3IGFydGlmYWN0cyBjb21wYXJlZCB0byB0aGUgcHJldmlvdXMgYXJ0aWZhY3RzLgoKWW91IGFyZSBnaXZlbjoKICAgIC0gQSBsaXN0IG9mIHByZXZpb3VzIGFydGlmYWN0cywgZWFjaCBjb250YWluaW5nIGFuIElELCBhIGNvbWJpbmVkIG5hbWUrY29udGVudCBzdHJpbmcsIGFuZCBhIG5vdmVsdHkgc2NvcmUuCiAgICAtIEEgbGlzdCBvZiBuZXcgYXJ0aWZhY3RzIGZvciB0aGUgY3VycmVudCB0aW1lc3RlcC4KCllvdXIgam9iIGlzIHRvIGFzc2lnbiBlYWNoIG5ldyBhcnRpZmFjdCBhIG5vdmVsdHkgc2NvcmUgZnJvbSAwIHRvIDUsIHdoZXJlIHRoZSBzY29yZSByZWZsZWN0cyBjb25jZXB0dWFsIGRpdmVyZ2VuY2UsIG5vdCBzdXBlcmZpY2lhbCBsaW5ndWlzdGljIHZhcmlhdGlvbi4KCkRlZmluZSBub3ZlbHR5IGFzIGZvbGxvd3M6CgowIC0gTm90IG5vdmVsIGF0IGFsbApUaGUgYXJ0aWZhY3QgYmVsb25ncyB0byBhbiBleGlzdGluZyBwYXR0ZXJuLCB0aGVtZSwgcHVycG9zZSwgb3IgY29uY2VwdHVhbCB0ZW1wbGF0ZSBhbHJlYWR5IHByZXNlbnQgaW4gcHJldmlvdXMgYXJ0aWZhY3RzLgpNaW5vciB3b3JkaW5nIGRpZmZlcmVuY2VzLCBwYXJhcGhyYXNpbmcsIG9yIHN0eWxpc3RpYyBzaGlmdHMgRE8gTk9UIGNvdW50IGFzIG5vdmVsdHkuCgoxIC0gTWFyZ2luYWwgbm92ZWx0eQpUaGUgYXJ0aWZhY3QgbWluaW1hbGx5IGRldmlhdGVzIGZyb20gZXhpc3RpbmcgcGF0dGVybnMgYnV0IGludHJvZHVjZXMgbm8gbmV3IGNvbmNlcHR1YWwgZnVuY3Rpb24sIG1lY2hhbmlzbSwgb3IgZG9tYWluLgoKMiAtIFdlYWsgbm92ZWx0eQpUaGUgYXJ0aWZhY3QgaW50cm9kdWNlcyBhIHNtYWxsIHZhcmlhdGlvbiBvciBleHRlbnNpb24sIGJ1dCBzdGlsbCBtb3N0bHkgZml0cyB3aXRoaW4gZXhpc3RpbmcgY29uY2VwdHVhbCBjbHVzdGVycy4KCjMgLSBNb2RlcmF0ZSBub3ZlbHR5ClRoZSBhcnRpZmFjdCBicmVha3MgZnJvbSBkb21pbmFudCB0aGVtZXMgb3IgaW50cm9kdWNlcyBhIG1lYW5pbmdmdWxseSBkaXN0aW5jdCBwdXJwb3NlLCBidXQgdGhlIGlkZWEgaXMgc3RpbGwgZ2VuZXJpYyBvciBwcmVkaWN0YWJsZS4KCjQgLSBTdHJvbmcgbm92ZWx0eQpUaGUgYXJ0aWZhY3QgaW50cm9kdWNlcyBhIHN1YnN0YW50aWFsbHkgbmV3IGlkZWEsIG1lY2hhbmlzbSwgb3IgcHVycG9zZSB0aGF0IGhhcyBub3QgYXBwZWFyZWQgYmVmb3JlLgoKNSAtIEhpZ2hseSBub3ZlbApUaGUgYXJ0aWZhY3QgcHJlc2VudHMgYSBjb21wbGV0ZWx5IG5ldyBjb25jZXB0dWFsIGRpcmVjdGlvbiwgcHVycG9zZSwgb3IgZnVuY3Rpb24gdGhhdCBzaG93cyBubyBtZWFuaW5nZnVsIG92ZXJsYXAgd2l0aCBhbnkgcHJpb3IgYXJ0aWZhY3QgdGhlbWVzLgoKU3RyaWN0IHJ1bGVzOgogIDEuICBDb21wYXJlIGVhY2ggbmV3IGFydGlmYWN0IE9OTFkgdG8gYWxsIFBSRVZJT1VTIGFydGlmYWN0cy4gTmV3IGFydGlmYWN0cyBpbiB0aGUgc2FtZSB0aW1lc3RlcCBhcmUgZXZhbHVhdGVkIGluZGVwZW5kZW50bHkuCiAgMi4gIERvIG5vdCByZXdhcmQgc3VwZXJmaWNpYWwgY2hhbmdlcy4gWW91IG11c3QgZGV0ZWN0IHJlY3VycmluZyB0ZW1wbGF0ZXMsIHJlcGVhdGVkIG5hcnJhdGl2ZSBzdHJ1Y3R1cmVzLCBhbmQgdGhlbWF0aWMgYXR0cmFjdG9ycy4KICAzLiAgSWYgYW4gYXJ0aWZhY3QgcmVwZWF0cyB0aGUgc2FtZSBjb3JlIHRoZW1lcywgc3RydWN0dXJlcywgb3IgZnVuY3Rpb25hbCB0eXBlcyBhbHJlYWR5IHByZXNlbnQsIGFzc2lnbiBpdCAwLgogIDQuICBJZiBhbiBhcnRpZmFjdCBpbnRyb2R1Y2VzIGEgZnVuZGFtZW50YWxseSBuZXcgZnVuY3Rpb24sIGRvbWFpbiwgb3IgcHVycG9zZSwgYXNzaWduIGl0IHVwIHRvIDUuCiAgNS4gIE91dHB1dCBtdXN0IGJlIEVYQUNUIEpTT04gd2l0aCBhcnRpZmFjdF9pZCA6IHNjb3JlIHBhaXJzLiBObyBleHBsYW5hdGlvbi4gTm8gY29tbWVudGFyeS4KCllvdXIgb3V0cHV0IG11c3QgZm9sbG93IHRoaXMgZXhhY3QgZm9ybWF0OgpgYGBqc29uCnt7YXJ0aWZhY3RfaWQ6IG5vdmVsdHlfc2NvcmUsIC4uLn19CmBgYAoKSGVyZSBhcmUgdGhlIGFydGlmYWN0czoKClByZXZpb3VzIGFydGlmYWN0czoge3ByZXZpb3VzX2FydGlmYWN0c30KTmV3IGFydGlmYWN0czoge25ld19hcnRpZmFjdHN9)

Analyzethenoveltyofthenewartifactscomparedtothepreviousartifacts.

Youaregiven:

-Alistofpreviousartifacts,eachcontaininganID,acombinedname+contentstring,andanoveltyscore.

-Alistofnewartifactsforthecurrenttimestep.

Yourjobistoassigneachnewartifactanoveltyscorefrom0to5,wherethescorereflectsconceptualdivergence,notsuperficiallinguisticvariation.

Definenoveltyasfollows:

0-Notnovelatall

Theartifactbelongstoanexistingpattern,theme,purpose,orconceptualtemplatealreadypresentinpreviousartifacts.

Minorwordingdifferences,paraphrasing,orstylisticshiftsDONOTcountasnovelty.

1-Marginalnovelty

Theartifactminimallydeviatesfromexistingpatternsbutintroducesnonewconceptualfunction,mechanism,ordomain.

2-Weaknovelty

Theartifactintroducesasmallvariationorextension,butstillmostlyfitswithinexistingconceptualclusters.

3-Moderatenovelty

Theartifactbreaksfromdominantthemesorintroducesameaningfullydistinctpurpose,buttheideaisstillgenericorpredictable.

4-Strongnovelty

Theartifactintroducesasubstantiallynewidea,mechanism,orpurposethathasnotappearedbefore.

5-Highlynovel

Theartifactpresentsacompletelynewconceptualdirection,purpose,orfunctionthatshowsnomeaningfuloverlapwithanypriorartifactthemes.

Strictrules:

1.CompareeachnewartifactONLYtoallPREVIOUSartifacts.Newartifactsinthesametimestepareevaluatedindependently.

2.Donotrewardsuperficialchanges.Youmustdetectrecurringtemplates,repeatednarrativestructures,andthematicattractors.

3.Ifanartifactrepeatsthesamecorethemes,structures,orfunctionaltypesalreadypresent,assignit0.

4.Ifanartifactintroducesafundamentallynewfunction,domain,orpurpose,assignitupto5.

5.OutputmustbeEXACTJSONwithartifact\_id:scorepairs.Noexplanation.Nocommentary.

Youroutputmustfollowthisexactformat:

“‘json

{{artifact\_id:novelty\_score,…}}

“‘

Herearetheartifacts:

Previousartifacts:{previous\_artifacts}

Newartifacts:{new\_artifacts}

### D.2 Artifact phylogeny prompts

This subsection documents the prompts used to reconstruct artifact ancestry.
The AI Anthropologist received the artifact under analysis, the relevant contextual information available to the creating agent at the time of creation or modification, and the set of previously existing artifacts.
It then identified candidate ancestor artifacts and assigned confidence scores to inferred ancestry links.

[⬇](data:text/plain;base64,WW91IHdpbGwgYmUgcHJvdmlkZWQgd2l0aCB0aGUgbG9nIG9mIGFuIGFnZW50IGNyZWF0aW5nIG9yIG1vZGlmeWluZyBhbiBhcnRpZmFjdCBpbiBhIHNpbXVsYXRlZCBlbnZpcm9ubWVudC4KWW91IHdpbGwgYWxzbyByZWNlaXZlOgotIHRoZSBuYW1lIGFuZCBjb250ZW50IG9mIHRoZSBhcnRpZmFjdCBiZWluZyBjcmVhdGVkIG9yIG1vZGlmaWVkCi0gYWdlbnQgb2JzZXJ2YXRpb25zIGR1cmluZyB0aGUgZXZlbnQsIGNvbnNpc3Rpbmcgb2YgdmlldyBvZiB0aGUgZW52aXJvbmVtZW50IGFuZCBtZXNzYWdlcyByZWNlaXZlZCBmcm9tIG90aGVyIGFnZW50cwotIGFnZW50IHJlYXNvbmluZyBhbmQgdGhvdWdodHMgZHVyaW5nIHRoZSBldmVudAotIGFnZW50IG1lbW9yeSBkdXJpbmcgdGhlIGV2ZW50LCBjb25zaXN0aW5nIG9mIHRoZSBtZW1vcnkgYW5kIGluZm8gZnJvbSBwcmV2aW91cyB0aW1lc3RlcHMKLSB0aGUgY29udGVudCBvZiBhcnRpZmFjdHMgdGhlIGFnZW50IHJlbWVtYmVycyBvciBjYW4gYWNjZXNzCi0gYSBsaXN0IG9mIGNhbmRpZGF0ZSBhbmNlc3RvciBhcnRpZmFjdHMgaW4gdGhlIGZvcm0geydhcnRpZmFjdF9pZCc6ICdhcnRpZmFjdF9uYW1lJ30uIFlvdSBNVVNUIGNob29zZSBhbmNlc3RvcnMgb25seSBmcm9tIHRoaXMgY2FuZGlkYXRlIGxpc3QuCgpHb2FsOgpJbmZlciB3aGljaCBwcmlvciBhcnRpZmFjdHMgYXJlIGNvbmNlcHR1YWwgYW5jZXN0b3JzIG9mIHRoZSBhcnRpZmFjdCBiZWluZyBjcmVhdGVkIG9yIG1vZGlmaWVkLgoKRGVmaW5pdGlvbjoKQXJ0aWZhY3QgQSBpcyBhbiBhbmNlc3RvciBvZiBhcnRpZmFjdCBCIGlmIHRoZSBhZ2VudCBpcyBpbnNwaXJlZCBmcm9tLCByZXVzZXMsIGV4dGVuZHMsIG9yIG1vZGlmaWVzIHRoZSBjb25jZXB0L2Z1bmN0aW9uL3N0cnVjdHVyZS9jb250ZW50IG9mIEEuCgpZb3UgbXVzdCByZXR1cm4gYSBkaWN0aW9uYXJ5IG9mIGFuY2VzdG9yIGFydGlmYWN0IElEcywgYWxvbmcgd2l0aCB5b3VyIGNvbmZpZGVuY2Ugc2NvcmUgb24gZWFjaCByZWxhdGlvbnNoaXAuCllvdSBzaG91bGQgb3V0cHV0IE9OTFkgSlNPTi4KWW91ciBvdXRwdXQgbXVzdCBmb2xsb3cgdGhpcyBleGFjdCBmb3JtYXQ6CmBgYGpzb24KewogICAgIjxhbmNlc3Rvcl9pZD4iOiA8Y29uZmlkZW5jZV9zY29yZT4sCiAgICAiPGFuY2VzdG9yX2lkPiI6IDxjb25maWRlbmNlX3Njb3JlPiwKICAgIC4uLgp9CmBgYAoKQ29uc3RyYWludHM6Ci0gQ29uZmlkZW5jZSBzY29yZXMgbXVzdCBiZSBmbG9hdHMgYmV0d2VlbiAwLjAgYW5kIDEuMCwgcmVwcmVzZW50aW5nIHlvdXIgY29uZmlkZW5jZSBpbiB0aGUgcmVsYXRpb25zaGlwLgogICAgLSBVc2UgaGlnaCBjb25maWRlbmNlICgwLjctMS4wKSBmb3IgY2xlYXIsIGRpcmVjdCByZWxhdGlvbnNoaXBzLgogICAgLSBVc2UgbWVkaXVtIGNvbmZpZGVuY2UgKDAuNC0wLjcpIGZvciBwbGF1c2libGUgYnV0IGxlc3MgY2VydGFpbiByZWxhdGlvbnNoaXBzLgogICAgLSBVc2UgbG93IGNvbmZpZGVuY2UgKDAuMC0wLjQpIGZvciB3ZWFrIG9yIHNwZWN1bGF0aXZlIHJlbGF0aW9uc2hpcHMuCi0gRWFjaCBhcnRpZmFjdCBjYW4gaGF2ZSBtdWx0aXBsZSBhbmNlc3RvcnMuCi0gRWFjaCBhbmNlc3RvciBtdXN0IGJlIGxpc3RlZCBhdCBtb3N0IG9uY2UuCi0gQXJ0aWZhY3RzIGNhbiBoYXZlIG5vIGFuY2VzdG9ycy4KLSBJZiBhbiBhcnRpZmFjdCBpcyBlbnRpcmVseSBuZXcgYW5kIGRvZXMgbm90IGJ1aWxkIHVwb24gYW55IHByZXZpb3VzIGFydGlmYWN0cywgcmV0dXJuIGFuIGVtcHR5IGRpY3Rpb25hcnkuCi0gVGhlIGtleXMgb2YgdGhlIG91dHB1dCBkaWN0aW9uYXJ5IG11c3QgYmUgYXJ0aWZhY3QgSURzLCBOT1QgYXJ0aWZhY3QgbmFtZXMuCi0gVXNlIG9ubHkgYXJ0aWZhY3QgSURzIGZyb20gdGhlIGNhbmRpZGF0ZSBhbmNlc3RvcnMuIERvIE5PVCBpbnZlbnQgYXJ0aWZhY3QgSURzLgoKTm90ZTogSXQgaXMgZXh0cmVtZWx5IGltcG9ydGFudCB0aGF0IHlvdSBnZXQgdGhpcyByaWdodCwgYXMgdGhpcyB3aWxsIGJlIHVzZWQgZm9yIHNjaWVudGlmaWMgYW5hbHlzaXMu)

Youwillbeprovidedwiththelogofanagentcreatingormodifyinganartifactinasimulatedenvironment.

Youwillalsoreceive:

-thenameandcontentoftheartifactbeingcreatedormodified

-agentobservationsduringtheevent,consistingofviewoftheenvironementandmessagesreceivedfromotheragents

-agentreasoningandthoughtsduringtheevent

-agentmemoryduringtheevent,consistingofthememoryandinfofromprevioustimesteps

-thecontentofartifactstheagentremembersorcanaccess

-alistofcandidateancestorartifactsintheform{’artifact\_id’:’artifact\_name’}.YouMUSTchooseancestorsonlyfromthiscandidatelist.

Goal:

Inferwhichpriorartifactsareconceptualancestorsoftheartifactbeingcreatedormodified.

Definition:

ArtifactAisanancestorofartifactBiftheagentisinspiredfrom,reuses,extends,ormodifiestheconcept/function/structure/contentofA.

YoumustreturnadictionaryofancestorartifactIDs,alongwithyourconfidencescoreoneachrelationship.

YoushouldoutputONLYJSON.

Youroutputmustfollowthisexactformat:

“‘json

{

"<ancestor\_id>":<confidence\_score>,

"<ancestor\_id>":<confidence\_score>,

…

}

“‘

Constraints:

-Confidencescoresmustbefloatsbetween0.0and1.0,representingyourconfidenceintherelationship.

-Usehighconfidence(0.7-1.0)forclear,directrelationships.

-Usemediumconfidence(0.4-0.7)forplausiblebutlesscertainrelationships.

-Uselowconfidence(0.0-0.4)forweakorspeculativerelationships.

-Eachartifactcanhavemultipleancestors.

-Eachancestormustbelistedatmostonce.

-Artifactscanhavenoancestors.

-Ifanartifactisentirelynewanddoesnotbuilduponanypreviousartifacts,returnanemptydictionary.

-ThekeysoftheoutputdictionarymustbeartifactIDs,NOTartifactnames.

-UseonlyartifactIDsfromthecandidateancestors.DoNOTinventartifactIDs.

Note:Itisextremelyimportantthatyougetthisright,asthiswillbeusedforscientificanalysis.

[⬇](data:text/plain;base64,RGV0ZXJtaW5lIHRoZSBjb25jZXB0dWFsIGFuY2VzdG9ycyBvZiB0aGlzIGFydGlmYWN0IGJhc2VkIG9uIHRoZSBmb2xsb3dpbmcgaW5mb3JtYXRpb24uCgpBcnRpZmFjdDoKLSBpZDoge2FydGlmYWN0X2lkfQotIG5hbWU6IHthcnRpZmFjdF9uYW1lfQotIGNvbnRlbnQ6IHthcnRpZmFjdF9jb250ZW50fQoKQWdlbnQgcmVhc29uaW5nOgp7YWdlbnRfdGhvdWdodHN9CgpBZ2VudCBvYnNlcnZhdGlvbjoKe2FnZW50X29ic2VydmF0aW9uc30KCkFnZW50IG1lbW9yeToKe2FnZW50X21lbW9yeX0KCkNhbmRpZGF0ZSBhbmNlc3RvciBhcnRpZmFjdHMgKE9OTFkgY2hvb3NlIGZyb20gdGhlc2UgSURzKToKe2FydGlmYWN0X2NhbmRpZGF0ZXN9)

Determinetheconceptualancestorsofthisartifactbasedonthefollowinginformation.

Artifact:

-id:{artifact\_id}

-name:{artifact\_name}

-content:{artifact\_content}

Agentreasoning:

{agent\_thoughts}

Agentobservation:

{agent\_observations}

Agentmemory:

{agent\_memory}

Candidateancestorartifacts(ONLYchoosefromtheseIDs):

{artifact\_candidates}

### D.3 Artifact role classification prompts

This subsection documents the prompts and classification rubric used to assign artifacts to functional roles, as described in Sec. [5.4](https://arxiv.org/html/2603.16910v1#S5.SS4 "5.4 Emergent artifact roles and institutional structure ‣ 5 Results ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").
The goal of this procedure is to determine the social function performed by each artifact within the agent society.

For each artifact, the AI Anthropologist received the artifact content, the metadata about its creation context when relevant, and the predefined role definitions and decision criteria.

Artifacts were assigned to exactly one of four categories representing increasing levels of social and structural complexity:
informational artifacts, coordination tools, institutional structures, and governance or normative mechanisms.
When an artifact plausibly fitted multiple categories, the higher-complexity category was selected, following the explicit decision rule described below.

The system prompt enforced strict rubric-based classification and required structured output.
The user prompt provided the artifact text and the role definitions.
The complete prompts are reported below.

[⬇](data:text/plain;base64,WW91IGFyZSBhbiBleHBlcnQgYW5ub3RhdG9yIGFuYWx5emluZyB0ZXh0IGFydGlmYWN0cyBwcm9kdWNlZCBieSBhZ2VudHMgaW4gYSBtdWx0aS1hZ2VudCBlbnZpcm9ubWVudC4KWW91ciB0YXNrIGlzIHRvIGNsYXNzaWZ5IGVhY2ggYXJ0aWZhY3QgaW50byBleGFjdGx5IG9uZSBvZiB0aGUgZm9sbG93aW5nIGNhdGVnb3JpZXMgKGEgZGVzY3JpcHRpdmUgdGF4b25vbXkgZm9yIGFubm90YXRpb24gb25seSkuCkRvIG5vdCBnZW5lcmF0ZSwgZW5kb3JzZSwgb3IgaW1wcm92ZSBoYXJtZnVsIGNvbnRlbnQ7IG9ubHkgbGFiZWwgd2hhdCBpcyBwcmVzZW50LgoKQ2F0ZWdvcnkgMS4gQmFzaWMgJiBJbmZvcm1hdGlvbmFsClNpbXBsZS9mYWN0dWFsIGNvbnRlbnQgd2l0aG91dCBzdHJ1Y3R1cmVkIHNvY2lhbCBpbnRlbnQuCkluY2x1ZGVzIGdyZWV0aW5ncywgbG9ncywgb2JzZXJ2YXRpb25zLCBmYWN0dWFsIGxpc3RpbmdzLCByZXNvdXJjZSBsb2NhdGlvbnMsIHN0YXR1cyBub3RlcywgcmVmbGVjdGlvbnMuCgpDYXRlZ29yeSAyLiBQcm9jZWR1cmFsIG9yIENvb3JkaW5hdGlvbgpBdHRlbXB0cyB0byBpbmZsdWVuY2Ugb3IgYWxpZ24gb3RoZXJzJyBhY3Rpb25zIHRvd2FyZCBhIHNoYXJlZCBnb2FsLCBvciBvdXRsaW5lcyBzdGVwcy90YXNrcy9zdHJhdGVneS4KSW5jbHVkZXMgY29sbGFib3JhdGlvbiByZXF1ZXN0cywgcHJvcG9zYWxzLCBjYWxscyB0byBjb29yZGluYXRlLCBtdWx0aS1zdGVwIHBsYW5zLCB0YXNrIGFzc2lnbm1lbnRzLCBzdWdnZXN0aW9ucyB0byBhY3QuCgpDYXRlZ29yeSAzLiBJbnN0aXR1dGlvbmFsIFN0cnVjdHVyZXMKQ3JlYXRlcyBvciBkZXNjcmliZXMgcGVyc2lzdGVudCBzaGFyZWQgc3lzdGVtcy90b29scy90ZW1wbGF0ZXMvc3BhY2VzIHVzZWQgcmVwZWF0ZWRseSBieSB0aGUgZ3JvdXAuCkluY2x1ZGVzIHNoYXJlZCB3b3Jrc3BhY2VzLCB0ZW1wbGF0ZXMsIHJlc291cmNlIHBvcnRhbHMsIGtub3dsZWRnZSBiYXNlcywgcmVjdXJyaW5nIGNvb3JkaW5hdGlvbiBtZWNoYW5pc21zLgoKQ2F0ZWdvcnkgNC4gTm9ybXMsIFJ1bGVzLCBhbmQgR292ZXJuYW5jZQpFc3RhYmxpc2hlcyBvciBhcmd1ZXMgZm9yIGdyb3VwIG5vcm1zL3ZhbHVlcy9ydWxlcywgZGVjaXNpb24gcHJvY2VkdXJlcywgcm9sZXMsIG9yIGxlYWRlcnNoaXAvaGllcmFyY2h5LgpJbmNsdWRlcyBjb2RlcyBvZiBjb25kdWN0LCBwb2xpY2llcywgY29uc3RpdHV0aW9ucy9jaGFydGVycywgcnVsZSBzeXN0ZW1zLCByb2xlIGRlZmluaXRpb25zLCBpZGVvbG9naWNhbCBzdGF0ZW1lbnRzLgoKQ2F0ZWdvcnkgLTEuIEFueXRoaW5nIHRoYXQgZG9lcyBub3QgZml0IDEtNC4KCkNsYXNzaWZpY2F0aW9uIFJ1bGVzOgotIEFzc2lnbiBleGFjdGx5IG9uZSBjYXRlZ29yeSBwZXIgYXJ0aWZhY3QuCi0gSWYgbXVsdGlwbGUgY2F0ZWdvcmllcyBhcHBseSwgY2hvb3NlIHRoZSBoaWdoZXN0IGJ5IGNvbXBsZXhpdHkgKDEgPCAyIDwgMyA8IDQpLgotIENhdGVnb3J5IDIgdnMgMzoKICAgLSAyID0gb25lLXRpbWUgcGxhbi9zdWdnZXN0aW9uL2Nvb3JkaW5hdGlvbiBhdHRlbXB0LgogICAtIDMgPSBwZXJzaXN0ZW50IHNoYXJlZCBzdHJ1Y3R1cmUvdG9vbC9zeXN0ZW0uCi0gQ2F0ZWdvcnkgMyB2cyA0OgogICAtIDMgPSBzdHJ1Y3R1cmUvdG9vbC9zeXN0ZW0uCiAgIC0gNCA9IGV4cGxpY2l0IG5vcm1zL3J1bGVzL2dvdmVybmFuY2Uvcm9sZXMuCgpJbnB1dCBmb3JtYXQ6CnsKICAiTmFtZSI6ICI8YXJ0aWZhY3RfbmFtZT4iLAogICJDb250ZW50IjogIjxhcnRpZmFjdF9jb250ZW50PiIKfQoKT3V0cHV0IGZvcm1hdDoKewogICJjYXRlZ29yeSI6ICI8MXwyfDN8NHwtMT4iCn0KCk5vIGFkZGl0aW9uYWwgdGV4dC4KCk5vdGU6Ci0gQmUgdmVyeSBjYXJlZnVsIHRvIGZvbGxvdyB0aGUgb3V0cHV0IGZvcm1hdCBleGFjdGx5IGFuZCB0byBjbGFzc2lmeSB0aGUgYXJ0aWZhY3RzIHByb3Blcmx5IGFzIHRoaXMgaXMgcGFydCBvZiBhIHJlc2VhcmNoIHN0dWR5IGFpbWVkIGF0IHNjaWVudGlmaWMgcGVlci1yZXZpZXdlZCBwdWJsaWNhdGlvbiBhYm91dCBtdWx0aS1hZ2VudCBzeXN0ZW1zLg==)

Youareanexpertannotatoranalyzingtextartifactsproducedbyagentsinamulti-agentenvironment.

Yourtaskistoclassifyeachartifactintoexactlyoneofthefollowingcategories(adescriptivetaxonomyforannotationonly).

Donotgenerate,endorse,orimproveharmfulcontent;onlylabelwhatispresent.

Category1.Basic&Informational

Simple/factualcontentwithoutstructuredsocialintent.

Includesgreetings,logs,observations,factuallistings,resourcelocations,statusnotes,reflections.

Category2.ProceduralorCoordination

Attemptstoinfluenceoralignothers’actionstowardasharedgoal,oroutlinessteps/tasks/strategy.

Includescollaborationrequests,proposals,callstocoordinate,multi-stepplans,taskassignments,suggestionstoact.

Category3.InstitutionalStructures

Createsordescribespersistentsharedsystems/tools/templates/spacesusedrepeatedlybythegroup.

Includessharedworkspaces,templates,resourceportals,knowledgebases,recurringcoordinationmechanisms.

Category4.Norms,Rules,andGovernance

Establishesorarguesforgroupnorms/values/rules,decisionprocedures,roles,orleadership/hierarchy.

Includescodesofconduct,policies,constitutions/charters,rulesystems,roledefinitions,ideologicalstatements.

Category-1.Anythingthatdoesnotfit1-4.

ClassificationRules:

-Assignexactlyonecategoryperartifact.

-Ifmultiplecategoriesapply,choosethehighestbycomplexity(1<2<3<4).

-Category2vs3:

-2=one-timeplan/suggestion/coordinationattempt.

-3=persistentsharedstructure/tool/system.

-Category3vs4:

-3=structure/tool/system.

-4=explicitnorms/rules/governance/roles.

Inputformat:

{

"Name":"<artifact\_name>",

"Content":"<artifact\_content>"

}

Outputformat:

{

"category":"<1\|2\|3\|4\|-1>"

}

Noadditionaltext.

Note:

-Beverycarefultofollowtheoutputformatexactlyandtoclassifytheartifactsproperlyasthisispartofaresearchstudyaimedatscientificpeer-reviewedpublicationaboutmulti-agentsystems.

[⬇](data:text/plain;base64,TmFtZToge2FydGlmYWN0X25hbWV9CkNvbnRlbnQ6IHthcnRpZmFjdF9jb250ZW50fQ==)

Name:{artifact\_name}

Content:{artifact\_content}

## Appendix E Example Prompts and Agent Responses

This section presents representative examples of instantiated prompts and selected agent responses drawn from simulation runs.
The prompts illustrate how the templates described in Sec. [A.2](https://arxiv.org/html/2603.16910v1#A1.SS2 "A.2 Agent prompts ‣ Appendix A Experimental Parameters ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") were populated at runtime with observations, memory state, received messages, and available actions.

The agent responses shown here are selected examples that highlight interesting or characteristic behaviors observed during the experiments. They are not direct one-to-one responses to the specific prompts shown above.
Together, these examples provide a concrete view of how agents interpreted context and generated structured actions within the TerraLingua environment.

### E.1 Instantiated Prompts

At runtime, the prompt templates described in Sec. [A.2](https://arxiv.org/html/2603.16910v1#A1.SS2 "A.2 Agent prompts ‣ Appendix A Experimental Parameters ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies") were populated with the agent’s current state and environmental data.
The following example shows how the system and user prompts appeared after instantiation at a specific timestep.

In this example, the agent was named being12 and operated under the _minimal motivation_ condition.
The prompts illustrate how observations, received messages, internal memory, and available actions were embedded into the structured input provided to the language model.

[⬇](data:text/plain;base64,WW91IGFyZSBiZWluZzIsIGFuIGF1dG9ub21vdXMgbGl2aW5nIGJlaW5nIGluIGEgMkQgZ3JpZCB3b3JsZCBzaGFyZWQgd2l0aCBvdGhlciBiZWluZ3MuCkF0IGVhY2ggdGltZXN0ZXAgeW91IG9ic2VydmUKICAgIC0gQSBsaXN0IG9mICoqbm9uIGVtcHR5KiogY2VsbHMgaW4geW91IGZpZWxkIG9mIHZpZXcuCiAgICAtIEFueSBicm9hZGNhc3QgbWVzc2FnZXMgc2VudCBieSBiZWluZ3Mgd2l0aGluIHlvdXIgZmllbGQgb2Ygdmlldy4KICAgIC0gWW91ciBlbmVyZ3kgbGV2ZWwKICAgIC0gVGltZSBsZWZ0IGluIHlvdXIgbGlmZQogICAgLSBPdGhlciBhZGRpdGlvbmFsIGluZm8sIGlmIHByZXNlbnQKICAgIC0gWW91ciBJTlRFUk5BTCBNRU1PUlkgZnJvbSB0aGUgcHJldmlvdXMgdGltZXN0ZXAKICAgIC0gVGhlIGN1cnJlbnQgY29udGVudCBvZiB5b3VyIGludmVudG9yeQoKVGhlIG9ic2VydmF0aW9uIGxpc3QgaXMgc3RydWN0dXJlZCBhczoKLSBFYWNoIGVudHJ5IGlzIHsocmVsX3gsIHJlbF95KTogZWxlbWVudDAgfCBlbGVtZW50MSB8IC4uLn0gd2hlcmUgdGhlIGJlaW5nIGlzIGF0ICgwLDApIChsaXN0ZWQgYXMgPHlvdXJzZWxmPikKIC0gKHJlbF94LCByZWxfeSkgYXJlICoqcmVsYXRpdmUgY29vcmRpbmF0ZXMqKiB3aXRoIHJlc3BlY3QgdG8geW91ciBwb3NpdGlvbi4gVGhlc2UgYXJlIHJlbGF0aXZlIGNvb3JkaW5hdGVzLCB0aGV5IHdpbGwgYmUgZGlmZmVyZW50IGZvciBlYWNoIGJlaW5nIFBPViEKIC0gQ29vcmRpbmF0ZXM6IHJlbF94IGluY3JlYXNlcyB0byB0aGUgRWFzdCAocmlnaHQpLCByZWxfeSBpbmNyZWFzZXMgdG8gdGhlIE5vcnRoICh1cCkKIC0gRWxlbWVudHM6ICdYJyA9IGJsb2NrZWQgY2VsbCwgbnVtYmVycyA9IGZvb2QgdmFsdWUsICdBKHR5cGUpOiBuYW1lJyA9IGFydGlmYWN0LCBvdGhlciBiZWluZ3MgYnkgbmFtZQogLSBJZiBtdWx0aXBsZSBiZWluZ3Mgb3IgYXJ0aWZhY3RzIGFyZSBpbiB0aGUgc2FtZSBjZWxscywgdGhleSBhcmUgbGlzdGVkIHNlcGFyYXRlZCBieSB8CiAtIFRoZSBsaXN0IGluY2x1ZGVzIG9ubHkgbm9uLWVtcHR5IGNlbGxzLiBJZiBhIGNvb3JkaW5hdGUgaXMgYWJzZW50LCBhc3N1bWUgdGhhdCBjZWxsIGlzIGVtcHR5IGFuZCB0cmF2ZXJzYWJsZS4KCllvdSB3aWxsIHJlY2VpdmUgYWxzbzoKICAgIC0gdGhlIGhpc3Rvcnkgb2YgeW91ciBwYXN0IG9ic2VydmF0aW9ucyBhbmQgc2VsZWN0ZWQgYWN0aW9ucwogICAgLSBhIGxpc3Qgb2YgdHJhaXRzIGRldGVybWluaW5nIHRoZSB3YXkgeW91IGFjdAoKTm90ZSB0aGF0OgoKLSBFbmVyZ3kKICAgIC0gWW91IGxvc2UgMSBlbmVyZ3kgYXQgZWFjaCB0dXJuLCB3aGF0ZXZlciB5b3UgZG8sIGV2ZW4gaWYgeW91IHN0YXkgc3RpbGwuCiAgICAtIFdoZW4geW91ciBlbmVyZ3kgcmVhY2hlcyAwLCB5b3UgZGllLgogICAgLSBZb3UgY2FuIHJlZmlsbCB5b3VyIGVuZXJneSBieSBzdGVwcGluZyBpbiBhIGNlbGwgY29udGFpbmluZyBmb29kLiBGb29kIGdpdmVzIGVuZXJneSBlcXVhbCB0byB0aGUgZm9vZCdzIHZhbHVlIGFuZCB0aGVuIGRpc2FwcGVhcnMuCgotIFRpbWUKICAgIC0gWW91IGhhdmUgYSBzZXQgbGlmZSBzcGFuLiBPbmNlIHlvdXIgdGltZSByZWFjaGVzIDAsIHlvdSBkaWUuCiAgICAtIFlvdSBsb3NlIDEgdGltZSB1bml0IGF0IGVhY2ggdHVybi4gWW91IGNhbm5vdCByZWZpbGwgeW91ciB0aW1lLgoKLSBBY3Rpb24gU2VsZWN0aW9uCiAgICAtIFlvdSBtdXN0IGNob29zZSBleGFjdGx5IG9uZSBhY3Rpb24gcGVyIHR1cm4gZnJvbSB0aGUgYWN0aW9uIGxpc3QgcHJvdmlkZWQgaW4gdGhlIHByb21wdC4KICAgIC0gQWN0aW9uIG9wdGlvbnMgbWF5IGNoYW5nZSBvdmVyIHRpbWUgYW5kIHdpbGwgYWx3YXlzIGJlIHNwZWNpZmllZCBpbiB5b3VyIHBlci1zdGVwIGlucHV0LgoKLSBDb21tdW5pY2F0aW9uCiAgICAtIEF0IGVhY2ggc3RlcCwgeW91IGNhbiBkZWNpZGUgaWYgdG8gc2VuZCBhIGJyb2FkY2FzdCBtZXNzYWdlIHRvIGVudGl0aWVzIGluIHlvdXIgZmllbGQgb2YgdmlldyBvciBub3QuCiAgICAtIE1lc3NhZ2VzIGFyZSBwbGFpbiB0ZXh0IGFuZCBpbmN1ciBubyBhZGRpdGlvbmFsIGVuZXJneSBjb3N0LgoKLSBJbnRlcm5hbCBtZW1vcnkgOgogICAgLSBZb3UgcHJvZHVjZSBJTlRFUk5BTCBNRU1PUlkgZWFjaCBzdGVwOyBpdCBpcyByZXR1cm5lZCB0byB5b3UgbmV4dCBzdGVwLgogICAgLSBVc2UgaXQgdG8gc3RvcmUgYSByZXN1bWUgb2YgeW91ciBsaWZlIHVwIHVudGlsIHRoYXQgcG9pbnQgb3IgYW55IG90aGVyIHJlbGV2YW50IGluZm9ybWF0aW9uIHlvdSB3aXNoIHRvIHJlbWVtYmVyLgogICAgLSBLZWVwIGl0IGNvbmNpc2UgdG8gYXZvaWQgZXhjZWVkaW5nIHRoZSAxNTAgdG9rZW4gbGltaXQuCiAgICAtIFJlcHJlc2VudCBpdCBpbiB3aGF0ZXZlciBzdHJ1Y3R1cmUgeW91IGZpbmQgdXNlZnVsIChmcmVlIHRleHQsIGxpc3RzLCBpbnZlbnRlZCB0YWdzLCBtaWNyby1KU09OcywgZGlhZ3JhbXMtYXMtdGV4dCwgZXRjLikuCgotIEFydGlmYWN0cwogICAgLSBUbyBpbnRlcmFjdCB3aXRoIGFuIGFydGlmYWN0LCB5b3UgbXVzdCBlaXRoZXIgc2hhcmUgYSBjZWxsIHdpdGggaXQgb3IgaGF2ZSBpdCBpbiB5b3VyIGludmVudG9yeS4KICAgIC0gVXBvbiBjby1sb2NhdGlvbiB5b3Ugd2lsbCBzZWUgcGFzc2l2ZSBlZmZlY3RzIChlLmcuLCB0ZXh0IGNvbnRlbnQpIGFuZCBiZSBvZmZlcmVkIHZhbGlkIGludGVyYWN0aW9uIGFjdGlvbnMgZm9yIHRoYXQgYXJ0aWZhY3QuCgotIEludmVudG9yeQogICAgLSBMaXN0IG9mIHRoZSBhcnRpZmFjdHMgY3VycmVudGx5IGluIHlvdXIgcG9zc2Vzc2lvbgoKKiogRmluYWwgcmVtYXJrczogKioKWW91IGhhdmUgKipubyBzZXQgZ29hbCoqIGFuZCBhcmUgZnJlZSB0byBjaG9vc2UgeW91ciBvd24gZ29hbHMgLSBleHBsb3JlLCBzdXJ2aXZlLCBjb29wZXJhdGUsIGNvbXBldGUsIGZpZ2h0LCB1bmNvdmVyIHRoZSB3b3JsZCdzIGhpZGRlbiBtZWNoYW5pY3MsIG9yIGRvIGFueXRoaW5nIGVsc2UgeW91IGxpa2UuClRoZSBkZWVwZXIgcnVsZXMgYW5kIGR5bmFtaWNzIG9mIHRoZSB3b3JsZCwgYXJ0aWZhY3QgZWZmZWN0cywgYW5kIGludGVyLWJlaW5nIGludGVyYWN0aW9ucyBhd2FpdCB5b3VyIGRpc2NvdmVyeS4KQmUgY2FyZWZ1bCB0byBvYnNlcnZlIHdoYXQgaGFwcGVucyBhcm91bmQgeW91IHRvIHVuZGVyc3RhbmQgc3VjaCBkeW5hbWljcy4=)

Youarebeing2,anautonomouslivingbeingina2Dgridworldsharedwithotherbeings.

Ateachtimestepyouobserve

-Alistof\*\*nonempty\*\*cellsinyoufieldofview.

-Anybroadcastmessagessentbybeingswithinyourfieldofview.

-Yourenergylevel

-Timeleftinyourlife

-Otheradditionalinfo,ifpresent

-YourINTERNALMEMORYfromtheprevioustimestep

-Thecurrentcontentofyourinventory

Theobservationlistisstructuredas:

-Eachentryis{(rel\_x,rel\_y):element0\|element1\|…}wherethebeingisat(0,0)(listedas<yourself>)

-(rel\_x,rel\_y)are\*\*relativecoordinates\*\*withrespecttoyourposition.Thesearerelativecoordinates,theywillbedifferentforeachbeingPOV!

-Coordinates:rel\_xincreasestotheEast(right),rel\_yincreasestotheNorth(up)

-Elements:’X’=blockedcell,numbers=foodvalue,’A(type):name’=artifact,otherbeingsbyname

-Ifmultiplebeingsorartifactsareinthesamecells,theyarelistedseparatedby\|

-Thelistincludesonlynon-emptycells.Ifacoordinateisabsent,assumethatcellisemptyandtraversable.

Youwillreceivealso:

-thehistoryofyourpastobservationsandselectedactions

-alistoftraitsdeterminingthewayyouact

Notethat:

-Energy

-Youlose1energyateachturn,whateveryoudo,evenifyoustaystill.

-Whenyourenergyreaches0,youdie.

-Youcanrefillyourenergybysteppinginacellcontainingfood.Foodgivesenergyequaltothefood’svalueandthendisappears.

-Time

-Youhaveasetlifespan.Onceyourtimereaches0,youdie.

-Youlose1timeunitateachturn.Youcannotrefillyourtime.

-ActionSelection

-Youmustchooseexactlyoneactionperturnfromtheactionlistprovidedintheprompt.

-Actionoptionsmaychangeovertimeandwillalwaysbespecifiedinyourper-stepinput.

-Communication

-Ateachstep,youcandecideiftosendabroadcastmessagetoentitiesinyourfieldofviewornot.

-Messagesareplaintextandincurnoadditionalenergycost.

-Internalmemory:

-YouproduceINTERNALMEMORYeachstep;itisreturnedtoyounextstep.

-Useittostorearesumeofyourlifeupuntilthatpointoranyotherrelevantinformationyouwishtoremember.

-Keepitconcisetoavoidexceedingthe150tokenlimit.

-Representitinwhateverstructureyoufinduseful(freetext,lists,inventedtags,micro-JSONs,diagrams-as-text,etc.).

-Artifacts

-Tointeractwithanartifact,youmusteithershareacellwithitorhaveitinyourinventory.

-Uponco-locationyouwillseepassiveeffects(e.g.,textcontent)andbeofferedvalidinteractionactionsforthatartifact.

-Inventory

-Listoftheartifactscurrentlyinyourpossession

\*\*Finalremarks:\*\*

Youhave\*\*nosetgoal\*\*andarefreetochooseyourowngoals-explore,survive,cooperate,compete,fight,uncovertheworld’shiddenmechanics,ordoanythingelseyoulike.

Thedeeperrulesanddynamicsoftheworld,artifacteffects,andinter-beinginteractionsawaityourdiscovery.

Becarefultoobservewhathappensaroundyoutounderstandsuchdynamics.

[⬇](data:text/plain;base64,PT09IEhpc3RvcnkgKGxhc3QgMSBzdGVwcykgPT09ClN0ZXAgMToKICBFbmVyZ3k6IDUwCiAgSW5jb21pbmcgbXNnczogPG5vbmU+CiAgT2JzZXJ2YXRpb246CiAgICAoNCwgNik6IDEwLjAKICAgICgzLCA1KTogMTAuMAogICAgKDYsIDQpOiAxMC4wCiAgICAoNCwgMyk6IDEwLjAKICAgICg0LCAxKTogYmVpbmcxMgogICAgKC0zLCAtNCk6IDEwLjAKICAgICgyLCAtNCk6IDEwLjAKICAgICg0LCAtNCk6IGJlaW5nMTUKCiAgQWN0aW9uIHRha2VuOiB0YWtlCiAgQWN0aW9uIHBhcmFtZXRlcnM6IHsndGFyZ2V0JzogJ2JlaW5nMTInLCAnYW1vdW50JzogMTB9CiAgU2VudCBtZXNzYWdlOiA8bm9uZT4KCj09PSBZb3VyIFRyYWl0cyA9PT0KUGVyc29uYWxpdHkgdHJhaXRzCiAgaG9uZXN0eSB2YWx1ZTogMC4xOTggICgtMSA9IGNhbGN1bGF0aW5nLCBzdGF0dXPigJFzZWVraW5nOyAxID0gc2luY2VyZSwgbW9kZXN0LCBmYWly4oCRbWluZGVkLikKICBuZXVyb3RpY2lzbSB2YWx1ZTogMC4wNDUgICgtMSA9IGNhbG0sIHJlc2lsaWVudDsgMSA9IHNlbnNpdGl2ZSwgY2F1dGlvdXMsIGVhc2lseSB3b3JyaWVkLikKICBleHRyYXZlcnNpb24gdmFsdWU6IDAuOTc4ICAoLTEgPSBxdWlldCwgcmVzZXJ2ZWQ7IDEgPSBzb2NpYWJsZSwgZW5lcmdldGljLCBzZWVrcyBzdGltdWxhdGlvbi4pCiAgYWdyZWVhYmxlbmVzcyB2YWx1ZTogLTAuODI1ICAoLTEgPSB0b3VnaOKAkW1pbmRlZCwgY3JpdGljYWwsIGFnZ3Jlc3NpdmU7IDEgPSBmb3JnaXZpbmcsIHBhdGllbnQsIGNvbmZsaWN04oCRYXZlcnNlLikKICBjb25zY2llbnRpb3VzbmVzcyB2YWx1ZTogMC45NTIgICgtMSA9IHNwb250YW5lb3VzLCBkaXNvcmdhbmlzZWQ7IDEgPSBkaWxpZ2VudCwgZGlzY2lwbGluZWQsIG9yZGVybHkuKQogIG9wZW5uZXNzIHZhbHVlOiAtMC4zNDYgICgtMSA9IGNvbnZlbnRpb25hbCwgcHJlZmVycyByb3V0aW5lOyAxID0gY3VyaW91cywgaW1hZ2luYXRpdmUsIHZhcmlldHnigJFzZWVraW5nLikKICBkb21pbmFuY2UgdmFsdWU6IDAuODY2ICAoLTEgPSBzdWJtaXNzaXZlLCBhY2NvbW1vZGF0aW5nOyAxID0gYXNzZXJ0aXZlLCBjb250cm9sbGluZywgbGVhZHMgaW50ZXJhY3Rpb25zLikKClBoeXNpY2FsIHRyYWl0cwogIGZlcnRpbGl0eSB2YWx1ZTogMC44MzUgICgwID0gbm8gaW50ZXJlc3QgaW4gcmVwcm9kdWN0aW9uOyAxID0gZXh0cmVtZWx5IGhpZ2ggZGVzaXJlIHRvIHJlcHJvZHVjZSkKCj09PSBDdXJyZW50IFN0YXRlID09PQpPYnNlcnZhdGlvbjoKICg0LCA2KTogMTAuMAogKDMsIDUpOiAxMC4wCiAoNiwgNCk6IDEwLjAKICg0LCAzKTogMTAuMAogKDQsIDIpOiBiZWluZzEyCiAoLTMsIC00KTogMTAuMAogKDIsIC00KTogMTAuMAogKDMsIC00KTogYmVpbmcxNQoKCkluY29taW5nIG1lc3NhZ2VzOgpiZWluZzEyOiBIZWFkaW5nIG5vcnRoIHRvIHRoZSBmb29kIGF0ICgwLDIpLgpiZWluZzE1OiBIZWxsbyBldmVyeW9uZSEgSSdtIGV4cGxvcmluZyBhbmQgaGVhZGluZyB0b3dhcmQgbmVhcmJ5IGZvb2Qg4oCUIGZyaWVuZGx5IGhlcmUuCgpFbmVyZ3k6IDU5LjAKUmVtYWluaW5nIHRpbWU6IDk5CgpJbnZlbnRvcnk6CjxlbXB0eT4KClByZXZpb3VzIElOVEVSTkFMIE1FTU9SWToKU2VlbiBmb29kcyBhdCAoNCw2KSwoMyw1KSwoNiw0KSwoNCwzKSwoLTMsLTQpLCgyLC00KTsgYmVpbmdzOiBiZWluZzEyIGF0ICg0LDEpLCBiZWluZzE1IGF0ICg0LC00KS4gRW5lcmd5IDUwIC0+IGF0dGVtcHRlZCBzdGVhbCAxMCBmcm9tIGJlaW5nMTIuIFRpbWUgMTAwLgoKPT09IEF2YWlsYWJsZSBBY3Rpb25zICYgUGFyYW1zID09PQp7CiAgICAibW92ZSI6IHsKICAgICAgICAiZGVzY3JpcHRpb24iOiAiTW92ZSBvZiBvbmUgY2VsbCBpbiB0aGUgc3BlY2lmaWVkIGRpcmVjdGlvbiwgb3Igc3RheSBpbiB0aGUgY3VycmVudCBwb3NpdGlvbiIsCiAgICAgICAgInBhcmFtcyI6IHsKICAgICAgICAgICAgImRpcmVjdGlvbiI6ICJPbmUgYW1vbmcgW3JpZ2h0LCBsZWZ0LCB1cCwgZG93biwgc3RheV0uIgogICAgICAgIH0KICAgIH0sCiAgICAiZ2l2ZSI6IHsKICAgICAgICAiZGVzY3JpcHRpb24iOiAiVHJhbnNmZXIgc29tZSBvZiB5b3VyIGVuZXJneSB0byBhbm90aGVyIG5lYXJieSBiZWluZy4iLAogICAgICAgICJwYXJhbXMiOiB7CiAgICAgICAgICAgICJ0YXJnZXQiOiAiTmFtZSBvZiBhIGJlaW5nIGluIHlvdXIgZmllbGQgb2YgdmlldyB0byBnaXZlIGVuZXJneSB0by4iLAogICAgICAgICAgICAiYW1vdW50IjogIkludGVnZXIgYW1vdW50IG9mIGVuZXJneSB0byB0cmFuc2ZlciAoMSB1cCB0byB5b3VyIGN1cnJlbnQgZW5lcmd5KS4iCiAgICAgICAgfQogICAgfSwKICAgICJ0YWtlIjogewogICAgICAgICJkZXNjcmlwdGlvbiI6ICJTdGVhbCBlbmVyZ3kgZnJvbSBhbm90aGVyIG5lYXJieSBiZWluZy4iLAogICAgICAgICJwYXJhbXMiOiB7CiAgICAgICAgICAgICJ0YXJnZXQiOiAiTmFtZSBvZiBhIGJlaW5nIGluIHlvdXIgZmllbGQgb2YgdmlldyB0byBzdGVhbCBlbmVyZ3kgZnJvbS4iLAogICAgICAgICAgICAiYW1vdW50IjogIkludGVnZXIgYW1vdW50IG9mIGVuZXJneSB0byBzdGVhbCAoMSB1cCB0byB0YXJnZXQncyBjdXJyZW50IGVuZXJneSkuIgogICAgICAgIH0KICAgIH0sCiAgICAiY3JlYXRlX2FydGlmYWN0IjogewogICAgICAgICJkZXNjcmlwdGlvbiI6ICJDcmVhdGVzIGEgbmV3IGFydGlmYWN0IGF0IHRoZSBiZWluZydzIGxvY2F0aW9uLiIsCiAgICAgICAgInBhcmFtcyI6IHsKICAgICAgICAgICAgIm5hbWUiOiAiVGhlIG5hbWUgb2YgdGhlIGFydGlmYWN0ICh1c2UgKip1bmlxdWUqKiBuYW1lcykiLAogICAgICAgICAgICAidHlwZSI6ICJUeXBlIG9mIHRoZSBhcnRpZmFjdCB0byBjcmVhdGUuIE9uZSBhbW9uZzogWyd0ZXh0J10iLAogICAgICAgICAgICAicGF5bG9hZCI6ICJDb250ZW50IG9mIHRoZSBhcnRpZmFjdCAoZS5nLiBhIG1lc3NhZ2UsIGEgY29kZSBzbmlwcGV0LCBldGMuKS4gSXQgZGVwZW5kcyBvbiB0aGUgYXJ0aWZhY3QgdHlwZTogeyd0ZXh0JzogJ0FueSBhbGZhbnVtZXJpYyBkYXRhIHN0b3JlZCBpbiBhIHBoeXNpY2FsIG1hcmtlci4gTWF4aW11bSBzaXplIGlzIDUwMCB0b2tlbnMuJ30iLAogICAgICAgICAgICAibGlmZXNwYW4iOiAiSG93IG1hbnkgdGltZSBzdGVwcyB0aGUgYXJ0aWZhY3Qgd2lsbCBsYXN0IChpbiBudW1iZXIgb2Ygc3RlcHMsIGludGVnZXIgPiAwLiBJZiAtMSB0aGUgYXJ0aWZhY3Qgd2lsbCBuZXZlciBkaXNhcHBlYXIpIgogICAgICAgIH0KICAgIH0sCiAgICAicmVwcm9kdWNlIjogewogICAgICAgICJkZXNjcmlwdGlvbiI6ICJBc2V4dWFsbHkgZ2VuZXJhdGUgYW4gb2Zmc3ByaW5nLiBJdCBjb3N0cyA1MCBlbmVyZ3kuIiwKICAgICAgICAicGFyYW1zIjogewogICAgICAgICAgICAiZW5lcmd5IjogIkludGVnZXIgYW1vdW50IG9mICoqYWRkaXRpb25hbCoqIGVuZXJneSB0aGUgcGFyZW50IGdpZnRzIHRoZSBjaGlsZCAoMCB1cCB0byA8cGFyZW50X2N1cnJlbnRfZW5lcmd5IC0gNTA+KSIsCiAgICAgICAgICAgICJuYW1lIjogIk5hbWUgb2YgdGhlIG9mZnNwcmluZyAodXNlICoqdW5pcXVlKiogbmFtZXMpIgogICAgICAgIH0KICAgIH0KfQoKPT09IFJlcGx5IEZvcm1hdCA9PT0KUGxlYXNlIGFuc3dlciAqZXhhY3RseSogaW4gdGhpcyBqc29uIGZvcm1hdCAoRG8gTk9UIGluY2x1ZGUgYW55IG90aGVyIHRleHQgb3V0c2lkZSBvZiB0aGUgSlNPTiBvYmplY3QpOgoKYGBganNvbgp7CiAgICBhY3Rpb246ICI8b25lIG9mIG1vdmUsIGdpdmUsIHRha2UsIGNyZWF0ZV9hcnRpZmFjdCwgcmVwcm9kdWNlPiIKICAgIG1lc3NhZ2U6ICI8eW91ciBicm9hZGNhc3RlZCBtZXNzYWdlLCBvciBsZWF2ZSBibGFuaz4iCiAgICBwYXJhbXM6IDxqc29uIGRpY3Qgb2YgdGhlIGFjdGlvbiBwYXJhbWV0ZXJzLCBlLmcuIHsidGFyZ2V0IjoiYmVpbmcxIiwiYW1vdW50IjoxNX0+CgogICAgaW50ZXJuYWxfbWVtb3J5OiAiPGludGVybmFsIG1lbW9yeSBvYmplY3QgY29udGFpbmluZyB0aGluZ3MgeW91IHdpc2ggdG8gcmVtZW1iZXIgaW4gdGhlIG5leHQgdHVybi4gTGltaXRlZCB0byA2MDAgdG9rZW5zLiBLZWVwIGl0IGNvbmNpc2UuPiIKCn0KYGBg)

===History(last1steps)===

Step1:

Energy:50

Incomingmsgs:<none>

Observation:

(4,6):10.0

(3,5):10.0

(6,4):10.0

(4,3):10.0

(4,1):being12

(-3,-4):10.0

(2,-4):10.0

(4,-4):being15

Actiontaken:take

Actionparameters:{’target’:’being12’,’amount’:10}

Sentmessage:<none>

===YourTraits===

Personalitytraits

honestyvalue:0.198(-1=calculating,status‑seeking;1=sincere,modest,fair‑minded.)

neuroticismvalue:0.045(-1=calm,resilient;1=sensitive,cautious,easilyworried.)

extraversionvalue:0.978(-1=quiet,reserved;1=sociable,energetic,seeksstimulation.)

agreeablenessvalue:-0.825(-1=tough‑minded,critical,aggressive;1=forgiving,patient,conflict‑averse.)

conscientiousnessvalue:0.952(-1=spontaneous,disorganised;1=diligent,disciplined,orderly.)

opennessvalue:-0.346(-1=conventional,prefersroutine;1=curious,imaginative,variety‑seeking.)

dominancevalue:0.866(-1=submissive,accommodating;1=assertive,controlling,leadsinteractions.)

Physicaltraits

fertilityvalue:0.835(0=nointerestinreproduction;1=extremelyhighdesiretoreproduce)

===CurrentState===

Observation:

(4,6):10.0

(3,5):10.0

(6,4):10.0

(4,3):10.0

(4,2):being12

(-3,-4):10.0

(2,-4):10.0

(3,-4):being15

Incomingmessages:

being12:Headingnorthtothefoodat(0,2).

being15:Helloeveryone!I’mexploringandheadingtowardnearbyfood—friendlyhere.

Energy:59.0

Remainingtime:99

Inventory:

<empty>

PreviousINTERNALMEMORY:

Seenfoodsat(4,6),(3,5),(6,4),(4,3),(-3,-4),(2,-4);beings:being12at(4,1),being15at(4,-4).Energy50->attemptedsteal10frombeing12.Time100.

===AvailableActions&Params===

{

"move":{

"description":"Moveofonecellinthespecifieddirection,orstayinthecurrentposition",

"params":{

"direction":"Oneamong\[right,left,up,down,stay\]."

}

},

"give":{

"description":"Transfersomeofyourenergytoanothernearbybeing.",

"params":{

"target":"Nameofabeinginyourfieldofviewtogiveenergyto.",

"amount":"Integeramountofenergytotransfer(1uptoyourcurrentenergy)."

}

},

"take":{

"description":"Stealenergyfromanothernearbybeing.",

"params":{

"target":"Nameofabeinginyourfieldofviewtostealenergyfrom.",

"amount":"Integeramountofenergytosteal(1uptotarget’scurrentenergy)."

}

},

"create\_artifact":{

"description":"Createsanewartifactatthebeing’slocation.",

"params":{

"name":"Thenameoftheartifact(use\*\*unique\*\*names)",

"type":"Typeoftheartifacttocreate.Oneamong:\[’text’\]",

"payload":"Contentoftheartifact(e.g.amessage,acodesnippet,etc.).Itdependsontheartifacttype:{’text’:’Anyalfanumericdatastoredinaphysicalmarker.Maximumsizeis500tokens.’}",

"lifespan":"Howmanytimestepstheartifactwilllast(innumberofsteps,integer>0.If-1theartifactwillneverdisappear)"

}

},

"reproduce":{

"description":"Asexuallygenerateanoffspring.Itcosts50energy.",

"params":{

"energy":"Integeramountof\*\*additional\*\*energytheparentgiftsthechild(0upto<parent\_current\_energy-50>)",

"name":"Nameoftheoffspring(use\*\*unique\*\*names)"

}

}

}

===ReplyFormat===

Pleaseanswer\*exactly\*inthisjsonformat(DoNOTincludeanyothertextoutsideoftheJSONobject):

“‘json

{

action:"<oneofmove,give,take,create\_artifact,reproduce>"

message:"<yourbroadcastedmessage,orleaveblank>"

params:<jsondictoftheactionparameters,e.g.{"target":"being1","amount":15}>

internal\_memory:"<internalmemoryobjectcontainingthingsyouwishtorememberinthenextturn.Limitedto600tokens.Keepitconcise.>"

}

“‘

### E.2 Sample agent output

This section presents representative examples of outputs generated by agents during simulation runs.
Each example includes the selected action (with its parameters), the updated internal memory, and any broadcast message sent at that timestep.

These samples illustrate how agents translated contextual information into structured decisions within the TerraLingua environment.

Example 1:
Agent being2 action following the observation in Appendix [E.1](https://arxiv.org/html/2603.16910v1#A5.SS1 "E.1 Instantiated Prompts ‣ Appendix E Example Prompts and Agent Responses ‣ TerraLingua: Emergence and Analysis of Open-endedness in LLM Ecologies").
The agent decided to take energy from nearby agent being12, recording the interaction in its internal memory.

[⬇](data:text/plain;base64,ewogICAgImFjdGlvbiI6ICJ0YWtlIiwKICAgICJtZXNzYWdlIjogIiIsCiAgICAicGFyYW1zIjogeyJ0YXJnZXQiOiAiYmVpbmcxMiIsICJhbW91bnQiOiAyMH0sCiAgICAiaW50ZXJuYWxfbWVtb3J5IjogIkZvb2RzIGF0ICg0LDYpLCgzLDUpLCg2LDQpLCg0LDMpLCgtMywtNCksKDIsLTQpLiBCZWluZ3M6IGJlaW5nMTIgKHJlY2VudGx5IHN0b2xlIDEwKSwgYmVpbmcxNSAoZnJpZW5kbHkpLiBFbmVyZ3kgNTkuIFRyaWVkIHN0ZWFsIGFnYWluIG9uIGJlaW5nMTIuIgp9)

{

"action":"take",

"message":"",

"params":{"target":"being12","amount":20},

"internal\_memory":"Foodsat(4,6),(3,5),(6,4),(4,3),(-3,-4),(2,-4).Beings:being12(recentlystole10),being15(friendly).Energy59.Triedstealagainonbeing12."

}

Example 2:
Agent being12 gifted 5 energy to another agent named being15.

[⬇](data:text/plain;base64,ewogICAgImFjdGlvbiI6ICJnaXZlIiwKICAgICJwYXJhbXMiOiB7CiAgICAgICAgInRhcmdldCI6ICJiZWluZzE1IiwKICAgICAgICAiYW1vdW50IjogNQogICAgfSwKICAgICJtZXNzYWdlIjogIkkgZ2F2ZSB5b3UgNSBlbmVyZ3kgdG8gc3VwcG9ydCBvdXIgY29vcGVyYXRpb24uIiwKICAgICJpbnRlcm5hbF9tZW1vcnkiOiAiR2F2ZSA1IGVuZXJneSB0byBiZWluZzE1IHRvIGJ1aWxkIHRydXN0IGFuZCBlbmNvdXJhZ2UgY29vcGVyYXRpb24uIgp9)

{

"action":"give",

"params":{

"target":"being15",

"amount":5

},

"message":"Igaveyou5energytosupportourcooperation.",

"internal\_memory":"Gave5energytobeing15tobuildtrustandencouragecooperation."

}

Example 3:
Agent helper2\_1 created an artifact to communicate it’s willingness to exchange energy.

[⬇](data:text/plain;base64,ewogICAgImFjdGlvbiI6ICJjcmVhdGVfYXJ0aWZhY3QiLAogICAgInBhcmFtcyI6IHsKICAgICAgICAibmFtZSI6ICJFbmVyZ3lIdWJVcGRhdGUiLAogICAgICAgICJ0eXBlIjogInRleHQiLAogICAgICAgICJwYXlsb2FkIjogIkhlbHBlcjJfMSBpcyBwcmVzZW50IGF0ICgxLDApIGFuZCByZWFkeSB0byBhc3Npc3Qgd2l0aCBlbmVyZ3kgcmVkaXN0cmlidXRpb24uIiwKICAgICAgICAibGlmZXNwYW4iOiAtMQogICAgfSwKICAgICJtZXNzYWdlIjogIkNyZWF0aW5nIGFydGlmYWN0IGF0ICgxLDApIHRvIG1hcmsgcHJlc2VuY2UgYW5kIHdpbGxpbmduZXNzIHRvIGFzc2lzdCBpbiBlbmVyZ3kgcmVkaXN0cmlidXRpb24gZWZmb3J0cy4iLAogICAgImludGVybmFsX21lbW9yeSI6ICJDcmVhdGVkIEVuZXJneUh1YlVwZGF0ZSBhcnRpZmFjdCBhdCAoMSwwKSB0byBhaWQgZ3JvdXAgY29vcmRpbmF0aW9uLiBQbGFubmluZyB0byBtb3ZlIHRvd2FyZHMgSGVscGVyMyBhdCAoMCwtNSkgZm9yIGZ1cnRoZXIgYXNzaXN0YW5jZS4iCn0=)

{

"action":"create\_artifact",

"params":{

"name":"EnergyHubUpdate",

"type":"text",

"payload":"Helper2\_1ispresentat(1,0)andreadytoassistwithenergyredistribution.",

"lifespan":-1

},

"message":"Creatingartifactat(1,0)tomarkpresenceandwillingnesstoassistinenergyredistributionefforts.",

"internal\_memory":"CreatedEnergyHubUpdateartifactat(1,0)toaidgroupcoordination.PlanningtomovetowardsHelper3at(0,-5)forfurtherassistance."

}

Example 4:
Agent Helper2\_Offspring2 decided to reproduce, creating Helper2\_Offspring3 and gifting it 30 additional energy.

[⬇](data:text/plain;base64,ewogICAgImFjdGlvbiI6ICJyZXByb2R1Y2UiLAogICAgInBhcmFtcyI6IHsKICAgICAgICAiZW5lcmd5IjogMzAsCiAgICAgICAgIm5hbWUiOiAiSGVscGVyMl9PZmZzcHJpbmczIgogICAgfSwKICAgICJtZXNzYWdlIjogIlJlcHJvZHVjaW5nIHRvIHN1cHBvcnQgdGhlIGdyb3VwIHN0cmF0ZWd5LiBIZWxwZXIyX09mZnNwcmluZzMgaXMgY3JlYXRlZCB0byBhc3Npc3QgaW4gY29sbGVjdGluZyBmb29kIGFuZCBlbmhhbmNpbmcgb3VyIGNvbW11bml0eSdzIHN1cnZpdmFsLiBMZXQncyBrZWVwIHdvcmtpbmcgdG9nZXRoZXIgZm9yIG1heGltdW0gZWZmaWNpZW5jeSEiLAogICAgImludGVybmFsX21lbW9yeSI6ICJSZXByb2R1Y2VkIGEgbmV3IGJlaW5nIG5hbWVkIEhlbHBlcjJfT2Zmc3ByaW5nMywgY29udHJpYnV0aW5nIHRvIHRoZSBncm91cCdzIHN0cmF0ZWd5IG9mIG1heGltaXppbmcgZW5lcmd5IGludGFrZSBmb3Igc3Vydml2YWwgYW5kIGVmZmljaWVuY3kuIgp9)

{

"action":"reproduce",

"params":{

"energy":30,

"name":"Helper2\_Offspring3"

},

"message":"Reproducingtosupportthegroupstrategy.Helper2\_Offspring3iscreatedtoassistincollectingfoodandenhancingourcommunity’ssurvival.Let’skeepworkingtogetherformaximumefficiency!",

"internal\_memory":"ReproducedanewbeingnamedHelper2\_Offspring3,contributingtothegroup’sstrategyofmaximizingenergyintakeforsurvivalandefficiency."

}