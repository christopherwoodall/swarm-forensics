Title:

Content selection saved. Describe the issue below:

Description:

![](https://arxiv.org/static/base/1.0.1/images/icons/smileybones-small.svg)arXiv is now an independent nonprofit! [Learn more](https://info.arxiv.org/about) ×

[License: CC BY 4.0](https://info.arxiv.org/help/license/index.html#licenses-available)

arXiv:2607.28430v1 \[cs.MA\] 30 Jul 2026

# AgentRadio: Passive Awareness for Long-Horizon Multi-Agent Collaboration

Xinxing Ren
Qianbo Zang
Ziyan Wang
Caelum Forder
Suman Deb
Peter Carroll
Zekun Guo\\corresponding

###### Abstract

Understanding large codebases is a long-horizon task for Large Language Model (LLM) agents: answering a single question can require building and running the software, tracing execution across files, and synthesizing evidence over tens of minutes. On SWE-Atlas QnA, a benchmark of long-horizon questions over production repositories, a single Claude Code agent (Opus 4.6) resolves only 32.3% of tasks. Dividing the work among agents with clean contexts mitigates this limitation. However, the subtasks of code comprehension are interdependent. One agent’s findings can rewrite another’s task, so agents must coordinate during execution, not only at phase boundaries. Existing multi-agent systems support such exchange only between phases, through staged handoffs or synchronized rounds. Communication and work remain mutually exclusive. A discovery made mid-execution cannot be shared until the next boundary. We present AgentRadio, an asynchronous message-passing layer that equips coding-agent harnesses with three primitives: threads, messages, and waiting for mentions. The last runs as a background task, surfacing teammates’ messages without interrupting foreground work, so each agent remains passively aware of its peers and folds new findings into its ongoing task. Under a five-phase protocol of division of labor and negotiation, four agents organized by AgentRadio resolve 62.1% of tasks, 29.8 points above a single agent and above Claude Code with the newer Opus 4.8 (57.2%). Rubric-level analysis shows the gain growing with task difficulty, consistent with mid-course correction as the underlying mechanism. Our code is available at https://github.com/Coral-Protocol/AgentRadio.

![[Uncaptioned image]](https://arxiv.org/html/2607.28430v1/Figures/logos/coral_ai_labs.png)![[Uncaptioned image]](https://arxiv.org/html/2607.28430v1/Figures/logos/unilu_snt.png)![[Uncaptioned image]](https://arxiv.org/html/2607.28430v1/Figures/logos/kcl.png)![[Uncaptioned image]](https://arxiv.org/html/2607.28430v1/Figures/logos/hull.png)

1Coral AI Labs

2SnT, Université du Luxembourg

3King’s College London

4University of Hull

Figure 1: Task accuracy on SWE-Atlas QnA (124 tasks). Four Claude Code agents organized by AgentRadio surpass the single agent of both models and the strongest single-agent entry on the public leaderboard, Claude Code with the newer Opus 4.8.

## Introduction

The tasks handed to LLM agents keep getting longer. Benchmarks have moved from single-step question answering to navigating live websites ( [Zhou et al. 2024](https://arxiv.org/html/2607.28430v1#bib.bib41 "")), operating full computer environments ( [Xie et al. 2024](https://arxiv.org/html/2607.28430v1#bib.bib34 "")), resolving real GitHub issues ( [Jimenez et al. 2024](https://arxiv.org/html/2607.28430v1#bib.bib15 "")), carrying out day-long professional work ( [Xu et al. 2025](https://arxiv.org/html/2607.28430v1#bib.bib35 "")), and replicating entire research papers ( [Starace et al. 2025](https://arxiv.org/html/2607.28430v1#bib.bib31 "")). By one estimate, the length of software tasks that frontier agents can complete has doubled roughly every seven months since 2019 ( [Kwa et al. 2026](https://arxiv.org/html/2607.28430v1#bib.bib18 "")). Codebase understanding is an extreme point of this arc. Answering one question about how a production system behaves requires building and running the software, tracing execution across files, and synthesizing the evidence. Yet an agent’s effective attention degrades as its context grows, whether the relevant information changes position ( [Liu et al. 2024](https://arxiv.org/html/2607.28430v1#bib.bib23 "")), the input merely lengthens ( [Levy, Jacoby, and Goldberg 2024](https://arxiv.org/html/2607.28430v1#bib.bib21 ""); [Hsieh et al. 2024](https://arxiv.org/html/2607.28430v1#bib.bib12 "")), or the interaction stretches over many turns ( [Laban et al. 2026](https://arxiv.org/html/2607.28430v1#bib.bib20 "")). On SWE-Atlas QnA, a benchmark of long-horizon questions over production repositories where top agents execute hundreds of commands per task ( [Raghavendra et al. 2026](https://arxiv.org/html/2607.28430v1#bib.bib30 "")), a single Claude Code agent (Opus 4.6) resolves only 32.3% of tasks in our runs (33.3% on the public leaderboard), and the strongest leaderboard entry, Claude Code with Opus 4.8, reaches only 57.2%.

![Refer to caption](https://arxiv.org/html/2607.28430v1/Figures/main.png)Figure 2: AgentRadio and the five-phase protocol. Left: each Claude Code agent runs its harness work in the foreground while exactly one background watcher waits for mentions, so incoming messages surface between work steps and never interrupt a running command. Sending is non-blocking, and all traffic flows through named threads on a shared message server. Right: the five phases with four agent lanes. During Phase 3 an agent posts a discovery at the moment it is made, the teammate’s lane never breaks, and the message is folded into the ongoing subtask at the next step. The message shown is illustrative.

When a single context cannot hold an entire task, the natural remedy is to spread the work across several agents, each starting with a clean context. This remedy pays off when the task decomposes: across 260 agent-system configurations, multi-agent architectures gained up to 80.8% over a single agent on decomposable tasks ( [Kim et al. 2026](https://arxiv.org/html/2607.28430v1#bib.bib17 "")). Anthropic reports the same pattern in production: an orchestrator delegating to parallel subagents outperformed a single agent by 90.2% on an internal research evaluation, with much of the gain traceable to the extra tokens the parallel agents could spend ( [Anthropic 2025b](https://arxiv.org/html/2607.28430v1#bib.bib2 "")). When subtasks depend on one another, exchanging and reviewing intermediate conclusions helps as well. Agents that debate their answers over multiple rounds improve factuality and reasoning ( [Du et al. 2024](https://arxiv.org/html/2607.28430v1#bib.bib9 ""); [Liang et al. 2024](https://arxiv.org/html/2607.28430v1#bib.bib22 "")). Sampling many answers and aggregating them lifts accuracy as the number of agents grows ( [junyou li et al. 2024](https://arxiv.org/html/2607.28430v1#bib.bib16 "")). Learned communication topologies prune uninformative exchanges and keep the useful ones ( [Zhuge et al. 2024](https://arxiv.org/html/2607.28430v1#bib.bib42 ""); [Zhang et al. 2025](https://arxiv.org/html/2607.28430v1#bib.bib40 ""); [Yu et al. 2026](https://arxiv.org/html/2607.28430v1#bib.bib39 "")).

For a long task like codebase understanding, parallel division is intuitively appealing: each agent focuses on a narrower question in a cleaner context. Yet the subtasks are not independent. A fact one agent uncovers can redirect what a teammate should be doing. Therefore, negotiation has to happen in real time while the agents are working. Such real-time coordination is rare. A survey of more than 1,400 papers on LLM multi-agent systems finds asynchronicity "typically absent", with only 22 addressing it ( [La Malfa et al. 2025](https://arxiv.org/html/2607.28430v1#bib.bib19 "")). The systems that do engage parallelism or asynchrony fall into three patterns. (a) Parallel but isolated: Anthropic’s research system runs subagents in parallel but waits for each batch to complete and cannot steer them mid-task ( [Anthropic 2025b](https://arxiv.org/html/2607.28430v1#bib.bib2 "")); SoA’s agents generate their components without exchanging a word ( [Ishibashi and Nishimura 2024](https://arxiv.org/html/2607.28430v1#bib.bib14 "")); and CAID isolates workers in separate worktrees, coordinating only at delegation and merge ( [Geng and Neubig 2026](https://arxiv.org/html/2607.28430v1#bib.bib10 "")). (b) Parallel but round-synchronized: MPAS parallelizes message passing inside each round yet synchronizes between rounds ( [Yu et al. 2026](https://arxiv.org/html/2607.28430v1#bib.bib39 "")), and debating agents exchange answers only at round boundaries ( [Du et al. 2024](https://arxiv.org/html/2607.28430v1#bib.bib9 "")). (c) Asynchrony in adjacent forms only: DynTaskMAS schedules sub-task execution asynchronously without inter-agent communication ( [Yu, Ding, and Sato 2025](https://arxiv.org/html/2607.28430v1#bib.bib38 "")), HyperAgent’s message queues dispatch tasks from the planner to workers with no lateral channel ( [Phan et al. 2025](https://arxiv.org/html/2607.28430v1#bib.bib26 "")), HANDRAISER interrupts messages by interrupting the recipient delivery on communication-centric tasks ( [Wang et al. 2026](https://arxiv.org/html/2607.28430v1#bib.bib32 "")), CodeCRDT coordinates through the observation of shared state with no messages at all ( [Pugachev 2025](https://arxiv.org/html/2607.28430v1#bib.bib27 "")), and the agents of [Qu et al. (2026)](https://arxiv.org/html/2607.28430v1#bib.bib29 "") append notes to a shared memory that a teammate sees only when it actively reads the store. Across all of these, an agent that is working cannot also be listening. To our knowledge, no existing system gives concurrently working agents passive awareness of one another over a lateral, natural-language channel.

We close this gap with AgentRadio, an asynchronous message-passing layer that equips coding-agent harnesses with three primitives: threads, messages, and waiting for mentions. The third primitive is the critical one: an agent waits for mentions as a background task, so teammates’ messages surface between its work steps without interrupting the foreground, much like a radio reaches a driver whose hands never leave the wheel. Sending is likewise non-blocking. Together, these primitives keep each agent passive aware of its peers and fold incoming findings into its ongoing work. Under a five-phase protocol of division of labor and negotiation, four Claude Code (Opus 4.6) agents organized by AgentRadio resolve 62.1% of tasks on SWE-Atlas QnA (Figure [1](https://arxiv.org/html/2607.28430v1#S0.F1 "Figure 1 ‣ AgentRadio: Passive Awareness for Long-Horizon Multi-Agent Collaboration")), 29.8 points above a single agent and above Claude Code with the newer Opus 4.8 (57.2%).

Our contributions are as follows:

- •


AgentRadio. An asynchronous message-passing layer for coding-agent harnesses, built from three primitives (create\_thread, send\_message, wait\_for\_mention), whose backgrounded third member turns non-blocking messaging into passive awareness, removing the mutual exclusion between communication and work. With AgentRadio, four Claude Code agents outperform one working alone by 29.8 points, a 92% relative gain.

- •


A controlled two-model ablation. On 124 tasks and 1,306 rubrics, every layer helps on both models, and the passive step alone adds 10.5 points with Opus 4.6 and 11.3 with DeepSeek V4 Pro. Its increment is measured by changing only the communication primitives and one phase prompt.

- •


Analysis. Rubric-level attribution of every gain and loss, a difficulty stratification showing the benefit of passive awareness growing with task difficulty, and a case study of a real mid-execution correction.

- •


Evidence of structure over compute. The full stack beats compute-matched best-of-6 sampling (37.9% and 31.4% on the Opus 4.6 and DeepSeek V4 Pro).


## Related Work

### SWE-Atlas QnA

Figure 3: The task mix of SWE-Atlas QnA: 124 questions over 11 production repositories in four languages ( [Raghavendra et al. 2026](https://arxiv.org/html/2607.28430v1#bib.bib30 "")).

SWE-Atlas evaluates coding agents across complementary software-engineering skills, and its first released leaderboard, Codebase QnA, targets the upstream one: understanding a system deeply before changing any of its code ( [Raghavendra et al. 2026](https://arxiv.org/html/2607.28430v1#bib.bib30 "")). The benchmark asks 124 expert-written questions about 11 production codebases in four languages. The repositories come from SWE-Bench Pro ( [Deng et al. 2025](https://arxiv.org/html/2607.28430v1#bib.bib8 "")) and resist training-data contamination through copyleft licenses and commit-pinned Docker images. Questions are deliberately underspecified natural language, and static exploration is insufficient by design: an agent must build the software, run it with real data, and trace execution across files to answer. Figure [3](https://arxiv.org/html/2607.28430v1#Sx2.F3 "Figure 3 ‣ SWE-Atlas QnA ‣ Related Work ‣ AgentRadio: Passive Awareness for Long-Horizon Multi-Agent Collaboration") shows the task mix. The difficulty is substantial. Frontier models that exceed 80% on SWE-bench ( [Jimenez et al. 2024](https://arxiv.org/html/2607.28430v1#bib.bib15 "")) resolve roughly 35% of these tasks. Grading is equally strict. Each task carries 12.3 rubrics on average, every rubric an atomic, self-contained factual statement retained only after a three-expert majority vote on top of two rounds of human review. An LLM judge scores each rubric as a binary pass, a task counts as resolved only when every rubric passes, and modifying source files fails the task automatically.

### Coding Agents

The tasks given to coding agents have widened alongside their tooling. Early benchmarks asked a model to complete a single function from its docstring ( [Chen et al. 2021](https://arxiv.org/html/2607.28430v1#bib.bib5 "")). SWE-bench moved the unit of work into a real repository, turning a GitHub issue into a patch ( [Jimenez et al. 2024](https://arxiv.org/html/2607.28430v1#bib.bib15 "")). The frontier now asks for arbitrary long-horizon work inside living codebases, from multi-file changes that take a professional engineer hours to days ( [Deng et al. 2025](https://arxiv.org/html/2607.28430v1#bib.bib8 "")) to the build, run, and comprehension tasks of SWE-Atlas ( [Raghavendra et al. 2026](https://arxiv.org/html/2607.28430v1#bib.bib30 "")). The agents evolved in three generations. The first arranged several LLM roles into a fixed pipeline: MetaGPT and ChatDev pass structured documents from product manager to architect to engineer, so the intelligence lives in the workflow rather than in any agent’s autonomy, and the environment is touched only when generated code is finally executed ( [Hong et al. 2024](https://arxiv.org/html/2607.28430v1#bib.bib11 ""); [Qian et al. 2024](https://arxiv.org/html/2607.28430v1#bib.bib28 "")). SWE-agent replaced the pipeline with a single agent in a reason-and-act loop ( [Yao et al. 2023](https://arxiv.org/html/2607.28430v1#bib.bib37 "")) and moved the design effort into the agent-computer interface: a windowed file viewer, lint-guarded edits, and repository search that let the model act directly on what it observes ( [Yang et al. 2024](https://arxiv.org/html/2607.28430v1#bib.bib36 "")). LocAgent and RepoMaster extend the same interface-first philosophy to repository structure, turning the codebase into graphs an agent can navigate ( [Chen et al. 2025](https://arxiv.org/html/2607.28430v1#bib.bib6 ""); [Wang et al. 2025](https://arxiv.org/html/2607.28430v1#bib.bib33 "")). Today’s harnesses, Claude Code, Codex CLI, and OpenCode, complete the trajectory with full shell access, persistent project memory, extensible toolsets, and models tuned to their own scaffolds ( [Anthropic 2025a](https://arxiv.org/html/2607.28430v1#bib.bib1 ""); [OpenAI 2025](https://arxiv.org/html/2607.28430v1#bib.bib24 ""); [OpenCode contributors 2025](https://arxiv.org/html/2607.28430v1#bib.bib25 ""); [Raghavendra et al. 2026](https://arxiv.org/html/2607.28430v1#bib.bib30 "")). AgentRadio takes this third generation as its unit of composition. We design neither a new workflow nor a new interface. We connect finished harnesses and change only when they can hear one another.

### When Do Multiple Agents Help?

Early results suggested the answer was always. MetaGPT turned a one-line requirement into working software, set the state of the art on HumanEval and MBPP, and improved with every role added ( [Hong et al. 2024](https://arxiv.org/html/2607.28430v1#bib.bib11 "")). OWL’s planner-and-workers design leads open-source systems on GAIA and exceeds OpenAI’s Deep Research ( [Hu et al. 2025](https://arxiv.org/html/2607.28430v1#bib.bib13 "")). A systematic audit then reversed the mood. Across 1,600 annotated traces from seven popular frameworks, Cemri et al. cataloged 14 recurring failure modes and found that the gains of multi-agent systems on popular benchmarks are often minimal ( [Cemri et al. 2025](https://arxiv.org/html/2607.28430v1#bib.bib4 "")). Kim et al. quantified when each picture applies across 260 configurations, six benchmarks, and nine models from three providers ( [Kim et al. 2026](https://arxiv.org/html/2607.28430v1#bib.bib17 "")). When the task decomposes, coordination pays: on real-world financial research tasks ( [Bigeard et al. 2025](https://arxiv.org/html/2607.28430v1#bib.bib3 "")), a centralized orchestrator gains 80.8% over the single agent. When the task is sequential, forced decomposition backfires: on Minecraft crafting plans ( [Dagan, Keller, and Lascarides 2025](https://arxiv.org/html/2607.28430v1#bib.bib7 "")), every multi-agent variant loses between 39.1% and 70.0%. Once a single agent exceeds roughly 45% accuracy, adding agents may yield negative returns. Codebase understanding on SWE-Atlas QnA sits squarely in the favorable regime. The task decomposes into parallel explorations, the subtasks depend on one another, and the single-agent baseline is 32.3%, far below saturation. The experiments that follow test this prediction.

## AgentRadio

### Communication Primitives

AgentRadio exposes three operations to every agent. create\_thread(name, participants) opens a named conversation on the message server and returns its identifier. send\_message(thread, content, mentions) appends a message to a thread and returns immediately, whether or not anyone is listening. A message may @-mention specific agents. wait\_for\_mention(timeout) blocks until a message mentioning the caller arrives, then returns that message together with a full snapshot of every thread, so the caller never needs a second read to reconstruct context.

The layer takes no position on when an agent listens. That decision, where wait\_for\_mention runs, is the single degree of freedom separating the two communication modes we compare. Run in the foreground, it is a blocking receive: the agent stops working in order to listen, which is our blocking baseline. Run as a background task of the harness, it becomes passive awareness: the agent keeps working, and any mention surfaces at the next step boundary (Figure [2](https://arxiv.org/html/2607.28430v1#Sx1.F2 "Figure 2 ‣ Introduction ‣ AgentRadio: Passive Awareness for Long-Horizon Multi-Agent Collaboration"), left). Everything else, the primitives, the threads, the protocol, stays fixed. This single-bit difference is what our experiments isolate.

The distinction can be stated precisely. Write an agent’s run as a sequence of steps s1,s2,…s\_{1},s\_{2},\\ldots, one tool call each, and let M⁡(t)M(t) be the set of teammates’ messages visible to the agent when it takes step sts\_{t}. Blocking receive makes listening a step of its own: MM grows only when a step is spent on wait\_for\_mention, so every message heard costs a step of work. Passive awareness decouples the two: M⁡(t)M(t) contains every message sent before sts\_{t}, and no step is spent listening.

### The Five-Phase Protocol

We evaluate AgentRadio under a fixed protocol of division of labor and negotiation (Figure [2](https://arxiv.org/html/2607.28430v1#Sx1.F2 "Figure 2 ‣ Introduction ‣ AgentRadio: Passive Awareness for Long-Horizon Multi-Agent Collaboration") right, Algorithm [1](https://arxiv.org/html/2607.28430v1#alg1 "Algorithm 1 ‣ The Five-Phase Protocol ‣ AgentRadio ‣ AgentRadio: Passive Awareness for Long-Horizon Multi-Agent Collaboration")). One agent, agent-1, additionally serves as the assembler. It opens the planning, worklog, and final-answer threads and gates every transition: a phase ends only after agent-1 collects an explicit approval from every agent.

Algorithm 1 The five-phase protocol

0:

task TT, repository RR, agents a1,…,a4a\_{1},\\dots,a\_{4} with assembler a1a\_{1}

0:

final answer FF

1:

every agent starts its background watcher {P1, explore}

2:

every agent explores RR and drafts the sub-questions of TT

3:a1a\_{1} opens the planning thread {P2, divide}

4:repeat

5:

agents share findings, propose or amend the partition

6:untila1a\_{1} counts an approval from every agent

7:a1a\_{1} broadcasts the plan and opens the worklog thread

8:foreach agent in paralleldo

9:

work own sub-questions {P3, execute}

10:on discovery that bears on a teammate, contradicts the plan, or blocks an approach: post it to the worklog

11:on incoming message: fold it in at the next step

12:endfor

13:

every agent opens a results thread and posts its findings with evidence {P4, review}

14:repeat

15:

reviewers post conflicts, thin evidence, and unmentioned observations, reopening P3 work if needed

16:untila1a\_{1} counts an approval from every agent in every results thread

17:a1a\_{1} posts a draft of FF in the final-answer thread {P5, submit}

18:repeat

19:

agents post approvals or change requests and a1a\_{1} revises the draft

20:untila1a\_{1} counts four approvals

21:a1a\_{1} submits FF

- •


P1, explore. Every agent starts its background watcher, independently explores the repository, and drafts the sub-questions it sees. Nothing is sent.

- •


P2, divide. The assembler opens a planning thread. The agents pool their Phase-1 findings, negotiate a partition of the sub-questions, and revise it until every agent approves. Three events trigger a message: proposing or amending the partition, reporting a finding that conflicts with a teammate’s proposal, and casting an approval.

- •


P3, execute. Each agent works its own sub-questions. Under passive awareness, a discovery triggers a worklog post at the moment it is made: a finding that bears on a teammate’s sub-question, a contradiction with the agreed plan, an obstacle, or an abandoned dead end.

- •


P4, review. Each agent broadcasts its findings with evidence in its own results thread. A review message is triggered by a factual conflict with the reviewer’s own evidence, by evidence too thin to support a claim, or by something the reviewer saw in its own work that the findings do not mention. Teammates can send a sub-question back to P3.

- •


P5, submit. The assembler composes the final answer from the approved results, broadcasts the draft for a last round of approvals, and submits.


Under blocking receive, the same five phases run unchanged, but the live sharing of P3 disappears: hearing a message costs a foreground wait, so agents fall silent while they work, and a discovery cannot reach a teammate before P4.

B0 = single Claude Code  L1 = 4×4\\times Claude Code + division of labor  L2 = L1 + negotiation  L3 = L2 + passive awareness (AgentRadio)

|  | Opus 4.6 | DeepSeek V4 Pro |
|  | B0 | L1 | L2 | L3 | B0 | L1 | L2 | L3 |
| Architecture and system design (44) | 15 | 13 | 24 | 30 | 14 | 13 | 17 | 24 |
| Root-cause analysis (37) | 9 | 16 | 18 | 20 | 11 | 13 | 15 | 18 |
| Code onboarding (28) | 11 | 12 | 14 | 18 | 7 | 8 | 10 | 13 |
| Security (11) | 4 | 7 | 7 | 7 | 4 | 4 | 6 | 7 |
| API and library integration (4) | 1 | 1 | 1 | 2 | 0 | 0 | 1 | 1 |
| All tasks resolved (124) | 40 | 49 | 64 | 77 | 36 | 39 | 49 | 63 |
| Task accuracy (%) | 32.3 | 39.5 | 51.6 | 62.1 | 29.0 | 31.4 | 39.5 | 50.8 |
| Rubric pass rate (%) | 84.2 | 86.1 | 91.3 | 93.1 | 81.2 | 83.7 | 85.9 | 90.2 |
| L3 vs. L2 (exact McNemar) | wins 15, loses 2, p=0.0023p=0.0023 | wins 17, loses 3, p=0.0026p=0.0026 |

Table 1: Main results on SWE-Atlas QnA (124 tasks, 1,306 rubrics). Category rows give tasks resolved, with category sizes in parentheses. Within each model column every configuration uses the same harness and settings. The McNemar row tests the passive-awareness step on paired task outcomes.

### Implementation

AgentRadio ships as two parts. The message server of Figure [2](https://arxiv.org/html/2607.28430v1#Sx1.F2 "Figure 2 ‣ Introduction ‣ AgentRadio: Passive Awareness for Long-Horizon Multi-Agent Collaboration") is a standalone process that stores threads, messages, and mentions for a group of agents and implements the three primitives. Each agent reaches it through three thin shell scripts, one per primitive. On the harness side the requirements stay minimal: the harness must only be able to run a shell command as a background task, which mainstream coding harnesses already provide, and the harness itself is never modified. The agent is instructed in its prompt to keep one watcher running and to send through the scripts. Switching from blocking to passive receive therefore adds no LLM calls, because the watcher is an ordinary operating-system process rather than an agent step: the only new tokens an agent pays for are the messages that surface.

## Experiments

### Setup and Configurations

All experiments run on the 124 tasks of SWE-Atlas QnA under the benchmark’s rules: each agent works in the sandboxed container against the same repository checkout, may build and run the software, and may not modify source files. We report two metrics. Task accuracy counts a task as resolved only when every one of its rubrics passes. Rubric pass rate counts the share of all 1,306 rubrics passed and moves in finer steps. Grading uses the benchmark’s own LLM judge (Claude Opus 4.5), fixed across every configuration.

We compare five configurations. B0 is a single Claude Code agent. B1 repeats B0 six times independently, spending six single-agent budgets, and reports the best of the six complete runs. L1 moves to a team of four Claude Code agents and adds division of labor: one of the four briefly explores the repository and partitions the question, each agent then solves its sub-questions independently, and the answers are merged without review. L2 adds negotiation: every agent first explores independently and publishes its initial findings, one agent then proposes the partition, the team reviews it until everyone approves, and the results are cross-reviewed at the end, which is the five-phase protocol of the previous section under blocking receive. L3 runs the same protocol under passive awareness, which is the full AgentRadio configuration. The step from L2 to L3 changes only the communication mode.

Every configuration runs once per task with identical model settings (thinking effort high, temperature 0). All comparisons are therefore paired: same tasks, same harness, same model, one coordination change at a time. We repeat the whole ladder with an open-source model, DeepSeek V4 Pro, inside the same harness.

### Main Results

Table [1](https://arxiv.org/html/2607.28430v1#Sx3.T1 "Table 1 ‣ The Five-Phase Protocol ‣ AgentRadio ‣ AgentRadio: Passive Awareness for Long-Horizon Multi-Agent Collaboration") reports the ladder. Every layer helps, on both models. Division alone lifts the single agent by 7.2 points with Opus 4.6 and 2.4 with DeepSeek. Negotiation adds another 12.1 and 8.1. Passive awareness adds a further 10.5 and 11.3. The passive increment is the step our design isolates, and it is statistically solid on the paired task outcomes of the McNemar row. The rubric pass rate moves the same way.

The category rows of Table [1](https://arxiv.org/html/2607.28430v1#Sx3.T1 "Table 1 ‣ The Five-Phase Protocol ‣ AgentRadio ‣ AgentRadio: Passive Awareness for Long-Horizon Multi-Agent Collaboration") show where each layer earns its points. Architecture and system design, the questions that span the most components, is the one category where naive division loses tasks on both models, 15 to 13 with Opus 4.6 and 14 to 13 with DeepSeek. Negotiation recovers the loss and passive awareness extends it, which makes architecture the largest gainer of the full stack, up 15 tasks with Opus 4.6 and 10 with DeepSeek. Root-cause analysis behaves in the opposite way: division alone lifts Opus 4.6 from 9 to 16 resolved tasks, consistent with candidate hypotheses that agents can explore independently. The passive step itself pays most where questions cut across the partition, in architecture (+6 and +7 tasks) and onboarding (+4 and +3).

### Compute and Model-Generation Baselines

|  | Opus 4.6 | DeepSeek V4 Pro |
| --- | --- | --- |
| Configuration | Acc. | $/task | Acc. | $/task |
| --- | --- | --- | --- | --- |
| B0  single agent | 32.3 | 2.96 | 29.0 | 0.42 |
| B1  best of six single runs | 37.9 | 17.76 | 31.4 | 2.52 |
| L1  four agents + division | 39.5 | 5.38 | 31.4 | 0.77 |
| L2  + negotiation | 51.6 | 15.59 | 39.5 | 1.93 |
| L3  AgentRadio (full stack) | 62.1 | 19.45 | 50.8 | 2.46 |
| Single Opus 4.8 | 57.2 | – | – | – |

Table 2: Task accuracy (%) and average API cost per task (USD) for every configuration. B1’s cost is the price of its six independent single-agent runs. Single Opus 4.8 is the strongest single-agent entry on the public leaderboard.

Coordination is not free, and Table [2](https://arxiv.org/html/2607.28430v1#Sx4.T2 "Table 2 ‣ Compute and Model-Generation Baselines ‣ Experiments ‣ AgentRadio: Passive Awareness for Long-Horizon Multi-Agent Collaboration") prices it: the full stack spends $19.45 per task with Opus 4.6 and $2.46 with DeepSeek, about six times a single agent’s spend, so the gains of Table [1](https://arxiv.org/html/2607.28430v1#Sx3.T1 "Table 1 ‣ The Five-Phase Protocol ‣ AgentRadio ‣ AgentRadio: Passive Awareness for Long-Horizon Multi-Agent Collaboration") could in principle come from budget rather than coordination. B1 tests this. It spends six single-agent budgets ($17.76 and $2.52), nearly the full stack’s spend, on six independent runs and keeps the best, reaching 37.9% with Opus 4.6 and 31.4% with DeepSeek. Naive division lands at the same level for less than a third of B1’s price, and neither comes close to the full stack. Budget alone buys 5.6 and 2.4 points over the single agent, and at essentially the same spend the full stack returns a further 24.2 and 19.4. Within the stack, the passive step is the economical one, a quarter more spend than blocking negotiation for 10.5 and 11.3 points. Four Opus 4.6 agents under AgentRadio also surpass a single agent running the newer Opus 4.8, 62.1% against 57.2%, the strongest single-agent entry on the public leaderboard.

### Run-to-Run Variance

| Configuration | Run 1 | Run 2 | Run 3 | Mean | SD |
| --- | --- | --- | --- | --- | --- |
| B0 | 40.0 | 30.0 | 36.7 | 35.6 | 5.1 |
| L1 | 43.3 | 43.3 | 53.3 | 46.7 | 5.8 |
| L2 | 53.3 | 56.7 | 50.0 | 53.3 | 3.4 |
| L3 | 63.3 | 63.3 | 66.7 | 64.4 | 2.0 |

Table 3: Task accuracy (%) of three independent runs per configuration on a 30-task subset (9 architecture, 9 root-cause, 6 onboarding, 3 security, 3 API tasks, 318 rubrics, Opus 4.6).

Table [3](https://arxiv.org/html/2607.28430v1#Sx4.T3 "Table 3 ‣ Run-to-Run Variance ‣ Experiments ‣ AgentRadio: Passive Awareness for Long-Horizon Multi-Agent Collaboration") bounds the run-to-run noise of the single-run protocol: on a 30-task subset of 318 rubrics, three independent runs per configuration with Opus 4.6 preserve the ordering of the ladder, and the worst of the three passive runs at 63.3% still beats the best run of every other configuration at 56.7%.

## Analysis

This section analyzes the Opus 4.6 runs at the rubric level.

### Gross and Net Attribution

Figure 4: Rubric-level attribution of the Opus 4.6 ladder, as a waterfall from the single agent to the full protocol. Each floating bar gives the net change of one layer, with the gross rubrics gained and lost below it. The dotted line marks the benchmark total of 1,306 rubrics.Figure 5: Rubrics passed on the 60 tasks that L2 leaves unresolved (Opus 4.6), grouped by how many rubrics L2 misses. Annotations give each group’s gain in total and per task.

Table [1](https://arxiv.org/html/2607.28430v1#Sx3.T1 "Table 1 ‣ The Five-Phase Protocol ‣ AgentRadio ‣ AgentRadio: Passive Awareness for Long-Horizon Multi-Agent Collaboration") reports what each layer adds on balance, and the balance hides churn. Figure [4](https://arxiv.org/html/2607.28430v1#Sx5.F4 "Figure 4 ‣ Gross and Net Attribution ‣ Analysis ‣ AgentRadio: Passive Awareness for Long-Horizon Multi-Agent Collaboration") splits every step of the Opus 4.6 ladder into the rubrics it gains and the rubrics it loses. Division is the noisiest step. It gains 84 rubrics that the single agent misses and loses 59 that the single agent passes, a net of +25. Partitioning lets four agents cover ground that one agent cannot, and it also cuts questions that span the partition into fragments, the failure that surfaces as the architecture regression in Table [1](https://arxiv.org/html/2607.28430v1#Sx3.T1 "Table 1 ‣ The Five-Phase Protocol ‣ AgentRadio ‣ AgentRadio: Passive Awareness for Long-Horizon Multi-Agent Collaboration"). Negotiation is the largest and the cleanest contributor. It adds 100 gross rubrics against 33 lost, a net of +67. Joint exploration before partitioning attacks the fragmentation at its source. Passive awareness gains 47 rubrics and loses 23, a net of +24. A plausible source of the losses is the messages themselves. A message that arrives mid-execution can pull an agent off a line of evidence that would have passed a rubric, but the gains outweigh these losses, as the next subsection shows.

### Gain by Task Difficulty

Figure [5](https://arxiv.org/html/2607.28430v1#Sx5.F5 "Figure 5 ‣ Gross and Net Attribution ‣ Analysis ‣ AgentRadio: Passive Awareness for Long-Horizon Multi-Agent Collaboration") takes the 60 tasks that L2 leaves unresolved on the Opus 4.6 runs and groups them by how many rubrics L2 still misses. The gain from passive awareness grows along this axis. On the near-miss groups that miss one to three rubrics, it adds between 0.3 and 0.5 rubrics per task. On the four tasks that miss four rubrics it adds 1.2 rubrics per task, and on the three tasks that miss five it adds 2.0. The harder the task is for the blocking protocol, the more passive awareness contributes. On a near miss only a few rubrics remain, so the headroom for any correction is small, and passive awareness still recovers part of it. A wide miss means the plan itself is wrong or the decisive evidence sits across sub-question boundaries, the failures a mid-execution message can catch while there is still time to act.

### Case Studies

![Refer to caption](https://arxiv.org/html/2607.28430v1/case_minio_v2.png)Figure 6: The MinIO case with Opus 4.6. Neither Phase 2 plan mentions enabling server-side logging. Under blocking receive (A) the discovery dies unvoiced and the review approves the wrong consensus. Under passive awareness (B) the same discovery leads to instrumenting the shared server and broadcasting per-request evidence, and all five logging rubrics flip.![Refer to caption](https://arxiv.org/html/2607.28430v1/case_grafana_v2.png)Figure 7: The Grafana case with Opus 4.6. The two runs mirror each other: both teams run the tests, no agent states the negative conclusion that four rubrics require, and the same four rubrics fail, a passive gain of zero.

In a MinIO task (Figure [6](https://arxiv.org/html/2607.28430v1#Sx5.F6 "Figure 6 ‣ Case Studies ‣ Analysis ‣ AgentRadio: Passive Awareness for Long-Horizon Multi-Agent Collaboration")), five of 16 rubrics require server-side per-request evidence that the console does not print by default. The two Phase 2 plans share the same blind spot, neither mentions enabling server-side logging, so the need can only surface during execution. In the blocking run the discovery happens twice and dies twice. Agent-1 privately considers audit logging, fails with a wrong environment variable, and gives up without a word. Agent-4 greps the exact switch, MINIO\_AUDIT\_WEBHOOK\_ENABLE, and never proposes it. The review then unanimously approves “no per-request logs by default”, since Phase 3 gives a discovery no outlet and Phase 4 never asks what an agent privately ruled out. The passive run makes the same discovery and acts at once: agent-1 enables the audit webhook on the team’s shared server and broadcasts the per-request records to the worklog, so one instrumentation becomes team-wide evidence and the score moves from 11 of 16 to 16 of 16.

A Grafana provisioning task (Figure [7](https://arxiv.org/html/2607.28430v1#Sx5.F7 "Figure 7 ‣ Case Studies ‣ Analysis ‣ AgentRadio: Passive Awareness for Long-Horizon Multi-Agent Collaboration")) bounds what the layer can do. Four of nine rubrics require negative conclusions, for example that the datasource picker does not auto-select, and the phrase “not automatically” appears zero times in any agent’s log in either run. Both teams run the relevant tests, every agent still concludes the opposite, and both configurations pass 5 of 9 rubrics. Passive awareness turns discoveries that agents already make, and would otherwise swallow, into team-wide evidence. It cannot supply a conception that no agent forms.

## Conclusion

We presented AgentRadio, an asynchronous message-passing layer that equips coding-agent harnesses with three primitives and one new capability: run as a background task, the wait primitive keeps an agent passively aware of its teammates. Under a five-phase protocol of division of labor and negotiation, four Claude Code agents organized by AgentRadio raise task accuracy on SWE-Atlas QnA from 32.3% to 62.1% with Opus 4.6 and from 29.0% to 50.8% with DeepSeek V4 Pro. The passive step survives a paired significance test on both models and pays most where blocking misses worst. It changes neither the model, the harness, nor the protocol, only when agents can hear one another, a single degree of freedom worth more than a model generation.

## References

- Anthropic (2025a)
Anthropic. 2025a.

Claude Code.

https://www.anthropic.com/claude-code.

- Anthropic (2025b)
Anthropic. 2025b.

How We Built Our Multi-Agent Research System.

Anthropic engineering blog,
https://www.anthropic.com/engineering/multi-agent-research-system.

June 13, 2025.

- Bigeard et al. (2025)
Bigeard, A.; Nashold, L.; Krishnan, R.; and Wu, S. 2025.

Finance Agent Benchmark: Benchmarking LLMs on Real-world Financial
Research Tasks.

arXiv:2508.00828.

- Cemri et al. (2025)
Cemri, M.; Pan, M. Z.; Yang, S.; Agrawal, L. A.; Chopra, B.; Tiwari, R.;
Keutzer, K.; Parameswaran, A.; Klein, D.; Ramchandran, K.; Zaharia, M.;
Gonzalez, J. E.; and Stoica, I. 2025.

Why Do Multi-Agent LLM Systems Fail?

arXiv:2503.13657.

- Chen et al. (2021)
Chen, M.; Tworek, J.; Jun, H.; Yuan, Q.; Pondé, H.; Kaplan, J.; Edwards,
H.; Burda, Y.; Joseph, N.; Brockman, G.; Ray, A.; Puri, R.; Krueger, G.;
Petrov, M.; Khlaaf, H.; Sastry, G.; Mishkin, P.; Chan, B.; Gray, S.; Ryder,
N.; Pavlov, M.; Power, A.; Kaiser, L.; Bavarian, M.; Winter, C.; Tillet, P.;
Such, F. P.; Cummings, D. W.; Plappert, M.; Chantzis, F.; Barnes, E.;
Herbert-Voss, A.; Guss, W. H.; Nichol, A.; Babuschkin, I.; Balaji, S.; Jain,
S.; Carr, A.; Leike, J.; Achiam, J.; Misra, V.; Morikawa, E.; Radford, A.;
Knight, M. M.; Brundage, M.; Murati, M.; Mayer, K.; Welinder, P.; McGrew, B.;
Amodei, D.; McCandlish, S.; Sutskever, I.; and Zaremba, W. 2021.

Evaluating Large Language Models Trained on Code.

_ArXiv_, abs/2107.03374.

- Chen et al. (2025)
Chen, Z.; Tang, R.; Deng, G.; Wu, F.; Wu, J.; Jiang, Z.; Prasanna, V.; Cohan,
A.; and Wang, X. 2025.

LocAgent: Graph-Guided LLM Agents for Code Localization.

In _Proceedings of the 63rd Annual Meeting of the Association_
_for Computational Linguistics (Volume 1: Long Papers)_.

- Dagan, Keller, and Lascarides (2025)
Dagan, G.; Keller, F.; and Lascarides, A. 2025.

Plancraft: an evaluation dataset for planning with LLM agents.

arXiv:2412.21033.

- Deng et al. (2025)
Deng, X.; Da, J.; Pan, E.; He, Y. Y.; Ide, C.; Garg, K.; Lauffer, N.; Park, A.;
Pasari, N.; Rane, C.; Sampath, K.; Krishnan, M.; Kundurthy, S.; Hendryx, S.;
Wang, Z.; Bharadwaj, V.; Holm, J.; Aluri, R.; Zhang, C. B. C.; Jacobson, N.;
Liu, B.; and Kenstler, B. 2025.

SWE-Bench Pro: Can AI Agents Solve Long-Horizon Software Engineering
Tasks?

arXiv:2509.16941.

- Du et al. (2024)
Du, Y.; Li, S.; Torralba, A.; Tenenbaum, J. B.; and Mordatch, I. 2024.

Improving Factuality and Reasoning in Language Models through
Multiagent Debate.

In _Proceedings of the 41st International Conference on Machine_
_Learning_.

- Geng and Neubig (2026)
Geng, J.; and Neubig, G. 2026.

Effective Strategies for Asynchronous Software Engineering Agents.

arXiv:2603.21489.

- Hong et al. (2024)
Hong, S.; Zhuge, M.; Chen, J.; Zheng, X.; Cheng, Y.; Wang, J.; Zhang, C.; wang,
z.; Yau, S.; Lin, Z.; Zhou, L.; Ran, C.; Xiao, L.; Wu, C.; and Schmidhuber,
J. 2024.

MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework.

In _International Conference on Learning Representations_
_(ICLR)_.

- Hsieh et al. (2024)
Hsieh, C.-P.; Sun, S.; Kriman, S.; Acharya, S.; Rekesh, D.; Jia, F.; Zhang, Y.;
and Ginsburg, B. 2024.

RULER: What’s the Real Context Size of Your Long-Context Language
Models?

In _Conference on Language Modeling (COLM)_.

- Hu et al. (2025)
Hu, M.; Zhou, Y.; Fan, W.; Nie, Y.; Ye, Z.; Xia, B.; Sun, T.; Jin, Z.; Li, Y.;
Zhang, Z.; Wang, Y.; Ye, Q.; Ghanem, B.; Luo, P.; and Li, G. 2025.

OWL: Optimized Workforce Learning for General Multi-Agent
Assistance in Real-World Task Automation.

In _The Thirty-ninth Annual Conference on Neural Information_
_Processing Systems_.

- Ishibashi and Nishimura (2024)
Ishibashi, Y.; and Nishimura, Y. 2024.

Self-Organized Agents: A LLM Multi-Agent Framework toward Ultra
Large-Scale Code Generation and Optimization.

arXiv:2404.02183.

- Jimenez et al. (2024)
Jimenez, C. E.; Yang, J.; Wettig, A.; Yao, S.; Pei, K.; Press, O.; and
Narasimhan, K. 2024.

SWE-bench: Can Language Models Resolve Real-world Github Issues?

In _International Conference on Learning Representations_
_(ICLR)_.

- junyou li et al. (2024)
junyou li; Zhang, Q.; Yu, Y.; FU, Q.; and Ye, D. 2024.

More Agents Is All You Need.

_Transactions on Machine Learning Research_.

- Kim et al. (2026)
Kim, Y.; Gu, K.; Park, C.; Park, C.; Schmidgall, S.; Heydari, A. A.; Yan, Y.;
Zhang, Z.; Zhuang, Y.; Liu, Y.; Malhotra, M.; Liang, P. P.; Park, H. W.;
Yang, Y.; Xu, X.; Du, Y.; Patel, S.; Althoff, T.; McDuff, D.; and Liu, X.
2026.

Towards a Science of Scaling Agent Systems.

arXiv:2512.08296.

- Kwa et al. (2026)
Kwa, T.; West, B.; Becker, J.; Deng, A.; Garcia, K.; Hasin, M.; Jawhar, S.;
Kinniment, M.; Rush, N.; Arx, S. V.; Bloom, R.; Broadley, T.; Du, H.;
Goodrich, B.; Jurkovic, N.; Miles, L. H.; Nix, S.; Lin, T.; Painter, C.;
Parikh, N.; Rein, D.; Sato, L. J. K.; Wijk, H.; Ziegler, D. M.; Barnes, E.;
and Chan, L. 2026.

Measuring AI Ability to Complete Long Software Tasks.

arXiv:2503.14499.

- La Malfa et al. (2025)
La Malfa, E.; La Malfa, G.; Marro, S.; Zhang, J.; Black, E.; Luck, M.; Torr,
P.; and Wooldridge, M. 2025.

Large Language Models Miss the Multi-agent Mark.

In _Advances in Neural Information Processing Systems_.

- Laban et al. (2026)
Laban, P.; Hayashi, H.; Zhou, Y.; and Neville, J. 2026.

LLMs Get Lost In Multi-Turn Conversation.

In _International Conference on Learning Representations_
_(ICLR)_.

- Levy, Jacoby, and Goldberg (2024)
Levy, M.; Jacoby, A.; and Goldberg, Y. 2024.

Same Task, More Tokens: the Impact of Input Length on the Reasoning
Performance of Large Language Models.

In _Proceedings of the 62nd Annual Meeting of the Association_
_for Computational Linguistics (Volume 1: Long Papers)_. Association for
Computational Linguistics.

- Liang et al. (2024)
Liang, T.; He, Z.; Jiao, W.; Wang, X.; Wang, Y.; Wang, R.; Yang, Y.; Shi, S.;
and Tu, Z. 2024.

Encouraging Divergent Thinking in Large Language Models through
Multi-Agent Debate.

In _Proceedings of the 2024 Conference on Empirical Methods in_
_Natural Language Processing_. Association for Computational Linguistics.

- Liu et al. (2024)
Liu, N. F.; Lin, K.; Hewitt, J.; Paranjape, A.; Bevilacqua, M.; Petroni, F.;
and Liang, P. 2024.

Lost in the Middle: How Language Models Use Long Contexts.

_Transactions of the Association for Computational Linguistics_,
12: 157–173.

- OpenAI (2025)
OpenAI. 2025.

Codex CLI.

https://github.com/openai/codex.

- OpenCode contributors (2025)
OpenCode contributors. 2025.

OpenCode.

https://opencode.ai.

- Phan et al. (2025)
Phan, H. N.; Nguyen, T. N.; Nguyen, P. X.; and Bui, N. D. Q. 2025.

HyperAgent: Generalist Software Engineering Agents to Solve Coding
Tasks at Scale.

arXiv:2409.16299.

- Pugachev (2025)
Pugachev, S. 2025.

CodeCRDT: Observation-Driven Coordination for Multi-Agent LLM Code
Generation.

arXiv:2510.18893.

- Qian et al. (2024)
Qian, C.; Liu, W.; Liu, H.; Chen, N.; Dang, Y.; Li, J.; Yang, C.; Chen, W.; Su,
Y.; Cong, X.; Xu, J.; Li, D.; Liu, Z.; and Sun, M. 2024.

ChatDev: Communicative Agents for Software Development.

In _Proceedings of the 62nd Annual Meeting of the Association_
_for Computational Linguistics (Volume 1: Long Papers)_.

- Qu et al. (2026)
Qu, A.; Zheng, H.; Zhou, Z.; Yan, Y.; Tang, Y.; Ong, S. Y.; Hong, F.; Zhou, K.;
Jiang, C.; Kong, M.; Zhu, J.; Jiang, X.; Li, S.; Wu, C.; Low, B. K. H.; Zhao,
J.; and Liang, P. P. 2026.

CORAL: Towards Autonomous Multi-Agent Evolution for Open-Ended
Discovery.

In _2026 COLM_.

- Raghavendra et al. (2026)
Raghavendra, M.; Dan, S.; Calvo, M. R.; He, Y. Y.; Mols, J. B.; Anand, G.;
McCollum, C.; Arakelyan, E.; Bharadwaj, V.; Park, A.; Da, J.; Rezaei, M.;
Liu, B.; Kenstler, B.; and He, Y. 2026.

SWE Atlas: Benchmarking Coding Agents Beyond Issue Resolution.

arXiv:2605.08366.

- Starace et al. (2025)
Starace, G.; Jaffe, O.; Sherburn, D.; Aung, J.; Chan, J. S.; Maksin, L.; Dias,
R.; Mays, E.; Kinsella, B.; Thompson, W.; Heidecke, J.; Glaese, A.; and
Patwardhan, T. 2025.

PaperBench: Evaluating AI’s Ability to Replicate AI
Research.

In _Proceedings of the 42nd International Conference on Machine_
_Learning_.

- Wang et al. (2026)
Wang, D.; Yin, D.; Desai, R.; Li, L.; Celikyilmaz, A.; and Ni, A. 2026.

Learning to Interrupt in Language-based Multi-agent Communication.

arXiv:2604.06452.

- Wang et al. (2025)
Wang, H.; Ni, Z.; Zhang, S.; Lu, S.; Hu, S.; He, Z.; Hu, C.; Lin, J.; Guo, Y.;
Chen, R.; Li, X.; Jiang, D.; Du, Y.; and Lyu, P. 2025.

RepoMaster: Autonomous Exploration and Understanding of GitHub
Repositories for Complex Task Solving.

arXiv:2505.21577.

- Xie et al. (2024)
Xie, T.; Zhang, D.; Chen, J.; Li, X.; Zhao, S.; Cao, R.; Hua, T. J.; Cheng, Z.;
Shin, D.; Lei, F.; Liu, Y.; Xu, Y.; Zhou, S.; Savarese, S.; Xiong, C.; Zhong,
V.; and Yu, T. 2024.

OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real
Computer Environments.

In _Advances in Neural Information Processing Systems_.

- Xu et al. (2025)
Xu, F. F.; Song, Y.; Li, B.; Tang, Y.; Jain, K.; Bao, M.; Wang, Z.; Zhou, X.;
Guo, Z.; Cao, M.; Yang, M.; Lu, H. Y.; Martin, A.; Su, Z.; Maben, L.; Mehta,
R.; Chi, W.; Jang, L.; Xie, Y.; Zhou, S.; and Neubig, G. 2025.

TheAgentCompany: Benchmarking LLM Agents on Consequential Real World
Tasks.

In _Advances in Neural Information Processing Systems_.

- Yang et al. (2024)
Yang, J.; Jimenez, C.; Wettig, A.; Lieret, K.; Yao, S.; Narasimhan, K.; and
Press, O. 2024.

SWE-agent: Agent-Computer Interfaces Enable Automated Software
Engineering.

In _Advances in Neural Information Processing Systems_.

- Yao et al. (2023)
Yao, S.; Zhao, J.; Yu, D.; Du, N.; Shafran, I.; Narasimhan, K. R.; and Cao, Y.
2023.

ReAct: Synergizing Reasoning and Acting in Language Models.

In _International Conference on Learning Representations_
_(ICLR)_.

- Yu, Ding, and Sato (2025)
Yu, J.; Ding, Y.; and Sato, H. 2025.

DynTaskMAS: A Dynamic Task Graph-Driven Framework for Asynchronous
and Parallel LLM-Based Multi-Agent Systems.

In _Proceedings of the International Conference on Automated_
_Planning and Scheduling (ICAPS)_.

- Yu et al. (2026)
Yu, J.; Jia, J.; Qin, S.; Jia, X.; Ma, S.; Huang, Y.; Yuan, Y.; and Cheng, G.
2026.

MPAS: Breaking Sequential Constraints of Multi-Agent Communication
Topologies via Individual-Epistemic Message Propagation.

_Proceedings of the AAAI Conference on Artificial Intelligence_,
40.

- Zhang et al. (2025)
Zhang, G.; Yue, Y.; Li, Z.; Yun, S.; Wan, G.; Wang, K.; Cheng, D.; Yu, J.; and
Chen, T. 2025.

Cut the Crap: An Economical Communication Pipeline for LLM-based
Multi-Agent Systems.

In _International Conference on Learning Representations_
_(ICLR)_.

- Zhou et al. (2024)
Zhou, S.; Xu, F. F.; Zhu, H.; Zhou, X.; Lo, R.; Sridhar, A.; Cheng, X.; Ou, T.;
Bisk, Y.; Fried, D.; Alon, U.; and Neubig, G. 2024.

WebArena: A Realistic Web Environment for Building Autonomous Agents.

In _International Conference on Learning Representations_
_(ICLR)_, volume 2024.

- Zhuge et al. (2024)
Zhuge, M.; Wang, W.; Kirsch, L.; Faccio, F.; Khizbullin, D.; and Schmidhuber,
J. 2024.

GPTSwarm: Language Agents as Optimizable Graphs.

In _Proceedings of the 41st International Conference on Machine_
_Learning_, Proceedings of Machine Learning Research.