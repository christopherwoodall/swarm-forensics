Title:

Content selection saved. Describe the issue below:

Description:

![](https://arxiv.org/static/base/1.0.1/images/icons/smileybones-small.svg)arXiv is now an independent nonprofit! [Learn more](https://info.arxiv.org/about) ×

[License: arXiv.org perpetual non-exclusive license](https://info.arxiv.org/help/license/index.html#licenses-available)

arXiv:2603.21489v2 \[cs.CL\] 08 Jul 2026

# Effective Strategies for    Asynchronous Software Engineering Agents

Jiayi Geng
Affiliation: Carnegie Mellon University, Language Technologies Institute
Graham Neubig
Email: [{ogeng, gneubig}@cs.cmu.edu](mailto:%20%CB%9C%20%CB%9C%20%CB%9C) [![[Uncaptioned image]](https://arxiv.org/html/2603.21489v2/logo/github.png)https://github.com/JiayiGeng/CAID](https://github.com/JiayiGeng/async-swe-agents "") ˜ ˜ ˜
Affiliation: Carnegie Mellon University, Language Technologies Institute

###### Abstract

AI agents have become increasingly capable at isolated software engineering (SWE) tasks such as resolving issues on Github.
Yet long-horizon tasks involving multiple interdependent subtasks still pose challenges both with respect to accuracy, and with respect to timely completion.
A natural approach to solving these long-horizon tasks in a timely manner is asynchronous multi-agent collaboration, where multiple agents work on different parts of the task at the same time.
But effective application of multi-agent systems has proven surprisingly difficult: concurrent edits by multiple agents interfere with each other, dependencies are difficult to synchronize, and combining partial progress into a coherent whole is challenging.
On the other hand, human developers have long relied on mature collaboration infrastructure to manage these challenges in large software projects.
Inspired by these collaboration primitives, we introduce Centralized Asynchronous Isolated Delegation (CAID), a structured multi-agent coordination paradigm grounded in three core SWE primitives: centralized task delegation, asynchronous execution, and isolated workspaces. CAID constructs dependency-aware task plans through a central manager, executes subtasks concurrently in isolated workspaces, and consolidates progress via structured integration with executable test-based verification. In empirical evaluation, we find that CAID improves accuracy over single-agent baselines by 25.6% absolute on paper reproduction tasks (PaperBench) and 14.7% on Python library development tasks (Commit0).
Through systematic analysis, we find that branch-and-merge is a central coordination mechanism for multi-agent collaboration, and that SWE primitives such as git worktree, git commit, and git merge enable it to be realized in a reliable and executable manner.

![Refer to caption](https://arxiv.org/html/2603.21489v2/multi-agent-teaser.png)Figure 1: Overview of CAID Workflow. The Manager explores the SWE tasks, builds a dependency graph to decompose tasks into parallelizable groups, and creates isolated git worktrees for every onboarded engineer. In the asynchronous loop, engineers independently implement, self-verify, and make a commit. Upon any engineer’s completion, the Manager merges to main and dynamically updates the task delegation plan before reassigning the next task. After the asynchronous loop, the manager does a final review before submitting the final product.

|     |
| --- |
|  |

## 1 Introduction

As LLM-based software engineering agents improve, we have come to expect more of them.
Whereas fixing isolated github issues on real-world repositories was a major challenge a few years ago ( [Jimenez et al., 2023](https://arxiv.org/html/2603.21489v2#bib.bib2 ""); [Yang et al., 2024](https://arxiv.org/html/2603.21489v2#bib.bib1 ""); [Wang et al., 2024](https://arxiv.org/html/2603.21489v2#bib.bib3 "")), we are now asking agents to build large apps from scratch ( [Zhao et al., 2024](https://arxiv.org/html/2603.21489v2#bib.bib6 "")) or implement entire research papers ( [Starace et al., 2025](https://arxiv.org/html/2603.21489v2#bib.bib5 "")). One method for performing this implementation is tasking a single agent with a large task, and hoping that it can execute on it from start to finish.
While task-completion horizons of agents continue to grow rapidly ( [Kwa et al., 2025](https://arxiv.org/html/2603.21489v2#bib.bib9 "")), these systems are still limited in the scope of tasks they can perform reliably, and a single agent performing a large task also takes significant wall-clock time.
To this end, in this paper, we study the question: “how can multiple agents be coordinated to asynchronously collaborate over a shared artifact in an effective way?”

While much research has focused on coordinating multiple agents, ranging from role-based pipelines that mirror human software engineering teams ( [Hong et al., 2023](https://arxiv.org/html/2603.21489v2#bib.bib11 ""); [Qian et al., 2024a](https://arxiv.org/html/2603.21489v2#bib.bib12 "")), to hierarchical managers that decompose and delegate subtasks ( [Benkovich and Valkov, 2026](https://arxiv.org/html/2603.21489v2#bib.bib8 "")), to include verification mechanisms in multi-agent systems ( [Venkataramani et al., 2026](https://arxiv.org/html/2603.21489v2#bib.bib46 "")), and to automated searches over communication topologies ( [Zhang et al., 2025a](https://arxiv.org/html/2603.21489v2#bib.bib13 ""))—most of these approaches primarily address how tasks are decomposed and allocated across agents.
However, the core challenges of _asynchronous_ multi-agent collaboration over shared artifacts remain unsolved.
Agents operating in this setting face a myriad of challenges such as locally reasonably but globally consistent edits ( [Khatua et al., 2026](https://arxiv.org/html/2603.21489v2#bib.bib14 "")), lack of shared state ( [Cemri et al., 2025](https://arxiv.org/html/2603.21489v2#bib.bib10 "")), and late discovery of any conflicts ( [Cognition AI, 2025](https://arxiv.org/html/2603.21489v2#bib.bib15 "")).

Human software engineering teams face these coordination failures routinely, and they have developed a mature infrastructure to mitigate them.
Developers work in isolated copies of the repository (e.g., via git worktrees), so parallel edits do not overwrite one another.
When changes are ready, version-control integration protocols (e.g., merge-based workflows) consolidate contributions and conflicts explicitly, rather than allowing silent interference. Test suites verify each change automatically, so correctness does not rely solely on any single developer’s judgment.

With this in mind, we build CAID ( [Figure 1](https://arxiv.org/html/2603.21489v2#S0.F1 "Figure 1 ‣ Abstract ‣ Effective Strategies for Asynchronous Software Engineering Agents")), a multi-agent system grounded in SWE primitives, in which a manager agent dynamically decomposes and delegates tasks to multiple engineer agents who execute concurrently in isolated workspaces.
In particular, each engineer operates in its own git worktree, a fully isolated workspace with a versioned copy of the repository and when an engineer finishes, its changes are integrated back through git merge.
As in human software teams, each engineer is responsible not only for implementation, but also for executable self-verification and conflict resolution at commit time.
Communication between the manager and engineers uses structured JSON instructions and git commits rather than free-form dialog, avoiding the inter-agent misalignment that has been identified as the primary failure mode in multi-agent systems ( [Cemri et al., 2025](https://arxiv.org/html/2603.21489v2#bib.bib10 "")).
We provide further details on the design of CAID in [section 2](https://arxiv.org/html/2603.21489v2#S2 "2 Branch-and-Merge Multi-Agent Coordination with SWE Primitives ‣ Effective Strategies for Asynchronous Software Engineering Agents").

We evaluate CAID on two long-horizon, complex software engineering tasks that provide a natural testbed for _shared-artifact_ collaboration. Specifically, we use Commit0 ( [Zhao et al., 2024](https://arxiv.org/html/2603.21489v2#bib.bib6 "")), which requires agents to implement Python libraries from scratch (e.g., tinydb, minitorch, jinja), and on PaperBench ( [Starace et al., 2025](https://arxiv.org/html/2603.21489v2#bib.bib5 "")), where agents reproduce a conference paper. Together, these benchmarks allow us to evaluate CAID with the lens of branch-and-merge coordination in long-horizon multi-agent software engineering. Based on these experiments, we show that CAID consistently improves the performance of Commit0 and PaperBench across multiple models.

## 2 Branch-and-Merge Multi-Agent Coordination with SWE Primitives

|     |     |     |
| --- | --- | --- |
| SWE Primitive | Coordination Mechanism | Role in Caid |
| Dependency graph | Scheduling constraints | Dependency order determines safe task delegation |
| git worktree | Workspace isolation | Each agent works in an independent worktree |
| git commit / git pull request | Structured signaling | Agents report completion by making the commits |
| git merge | Output integration | Completed changes are merged into the main |
| Merge conflict resolution | Conflict handling | Engineer resolves integration conflicts by themselves |
| Code review | Verification | Engineer does the self-verification |
| asyncio parallel execution | Concurrent execution | Multiple agents run concurrently |
| Event loop + await | Coordination cycle | Await completion →\\rightarrow integrate →\\rightarrow reassign tasks |
| git reset −⁣−--hard HEAD | State synchronization | Worktrees sync to latest integrated state |

Table 1: Mapping between concrete SWE primitives and multi-agent coordination mechanisms in CAID. Each primitive serves as an operational building block for isolation, delegation, asynchronous execution, and integration.

CAID’s coordination architecture is based on SWE primitives, which support operations such as task decomposition, isolated development, integration, and verification. In [Table 1](https://arxiv.org/html/2603.21489v2#S2.T1 "Table 1 ‣ 2 Branch-and-Merge Multi-Agent Coordination with SWE Primitives ‣ Effective Strategies for Asynchronous Software Engineering Agents"), we associate concrete SWE primitives (e.g., git worktree, git merge, dependency graphs, and test suites) and their corresponding coordination roles in CAID.
CAID consists of task specification and dependency modeling ( [subsection 2.1](https://arxiv.org/html/2603.21489v2#S2.SS1 "2.1 Task Specification and Dependency Graph ‣ 2 Branch-and-Merge Multi-Agent Coordination with SWE Primitives ‣ Effective Strategies for Asynchronous Software Engineering Agents")), dependency-aware task delegation ( [subsection 2.2](https://arxiv.org/html/2603.21489v2#S2.SS2 "2.2 Dependency-Aware Task Delegation ‣ 2 Branch-and-Merge Multi-Agent Coordination with SWE Primitives ‣ Effective Strategies for Asynchronous Software Engineering Agents")), workspace isolation and integration ( [subsection 2.3](https://arxiv.org/html/2603.21489v2#S2.SS3 "2.3 Workspace Isolation and Integration ‣ 2 Branch-and-Merge Multi-Agent Coordination with SWE Primitives ‣ Effective Strategies for Asynchronous Software Engineering Agents")), structured communication with asynchronous execution ( [subsection 2.4](https://arxiv.org/html/2603.21489v2#S2.SS4 "2.4 Communication and Asynchronous Execution ‣ 2 Branch-and-Merge Multi-Agent Coordination with SWE Primitives ‣ Effective Strategies for Asynchronous Software Engineering Agents")), and self-verification with termination control ( [subsection 2.5](https://arxiv.org/html/2603.21489v2#S2.SS5 "2.5 Self-Verification and Termination ‣ 2 Branch-and-Merge Multi-Agent Coordination with SWE Primitives ‣ Effective Strategies for Asynchronous Software Engineering Agents")).

### 2.1 Task Specification and Dependency Graph

To perform multi-agent delegation, we need to split the overall task into ordered sub-tasks. In our preliminary experience, allowing agents to split tasks arbitrarily causes them to miss important parts as they proceed.
Therefore, to proceed with task delegation in a structured way, we instead have the manager create a dependency graph of the repository to organize the work to be done. The repository structure is represented as a directed graph G=(V,E)G=(V,E), where each node v∈Vv\\in V corresponds to a unit of work and each directed edge (vi,vj)∈E(v\_{i},v\_{j})\\in E indicates that vjv\_{j} depends on viv\_{i}.
Let 𝒞t⊆V\\mathcal{C}\_{t}\\subseteq V denote the set of units that have been completed and successfully integrated into the main branch at round tt. A unit vjv\_{j} is eligible for delegation only if all its dependencies have been satisfied:
Readyt​(vj)⇔∀(vi,vj)∈E,vi∈𝒞t\\texttt{Ready}\_{t}(v\_{j})\\iff\\forall(v\_{i},v\_{j})\\in E,\\;v\_{i}\\in\\mathcal{C}\_{t}.
At each round, the manager selects executable units from the ready set {v∈V∣Readyt​(v)}\\{v\\in V\\mid\\texttt{Ready}\_{t}(v)\\} and converts them into task assignments.
Depending on the task, the unit of work and dependency analysis method is defined differently. In [subsection 3.1](https://arxiv.org/html/2603.21489v2#S3.SS1 "3.1 Evaluation Benchmarks ‣ 3 Main Results ‣ Effective Strategies for Asynchronous Software Engineering Agents"), we describe these definitions for Commit0 and PaperBench respectively. Although granularity differs across benchmarks, in both settings the manager constructs a dependency structure before delegating, and engineers are assigned tasks only after it is established.

### 2.2 Dependency-Aware Task Delegation

We prompt (see Appendix [A.1](https://arxiv.org/html/2603.21489v2#A1.SS1 "A.1 Commit0 Prompts ‣ Appendix A Prompt Engineering for Multi-Agent Task Delegation ‣ Effective Strategies for Asynchronous Software Engineering Agents") and [A.2](https://arxiv.org/html/2603.21489v2#A1.SS2 "A.2 PaperBench Prompts ‣ Appendix A Prompt Engineering for Multi-Agent Task Delegation ‣ Effective Strategies for Asynchronous Software Engineering Agents")) the manager to convert the dependency structure from Section [2.1](https://arxiv.org/html/2603.21489v2#S2.SS1 "2.1 Task Specification and Dependency Graph ‣ 2 Branch-and-Merge Multi-Agent Coordination with SWE Primitives ‣ Effective Strategies for Asynchronous Software Engineering Agents") into small executable task units assigned to each engineer. The manager splits implementation work into at most NN major task groups, where NN is the maximum number of parallel engineers, activating up to NN engineers whose dependencies are satisfied (not all NN are necessarily activated). Files with strong or circular dependencies are grouped together and assigned to the same engineer to reduce cross-agent coordination.

At each delegation step, the manager selects next tasks with top priority from the major task group, prioritized based on tasks that enable earlier test execution, expose more evaluation signals, or lie closer to the upstream end of the dependency chain. We suggest to the manager that engineers typically start with simpler functions before moving on to more complex ones. The manager dynamically updates dependency state after an engineer merges code and decides whether to assign the next task or keep the engineer idle. We define one round as a complete cycle of delegation, implementation, and dependency update. The process continues until no executable task groups remain or execution limits are reached.

### 2.3 Workspace Isolation and Integration

We use git worktree to ensure that each engineer modifies files only within its workspace, which is always derived from the main branch. Before delegation, we ask the manager to set up the repository in an executable state, including preparing the runtime environment, organizing entry points, or adding minimal function stubs when required by the task. These preparatory changes are committed to the main branch so that all subsequent engineer branches are created from a consistent base state. Certain shared files, such as package initialization files (e.g., \_\_init\_\_.py), are marked as restricted, and engineers are explicitly instructed not to commit changes to them. Worktrees are deleted after all assigned tasks are completed or when the engineer reaches the predefined iteration limit.
Integration is performed through standard git commit and git merge operations. After completing implementation and self-verification, an engineer submits a commit from its branch. The manager attempts to merge this branch into the main branch. If a merge conflict occurs, the engineer who produced the conflicting commit is responsible for resolving it. To solve the conflict, we ask the engineer to pull the latest main branch into its worktree, resolve conflicts locally, and resubmit the updated commit. As a result, the main branch remains the single source of integrated state throughout execution. We observe that this branch-based isolation, combined with explicit merge responsibilities, prevents parallel development from corrupting the shared codebase.

### 2.4 Communication and Asynchronous Execution

We use a structured JSON protocol as the communication interface between the manager and the engineer agents. When delegated the task, the manager outputs a JSON specification that defines task assignments, file paths, target functions, and dependency information to ensure that the task boundaries, responsibilities, and outputs are explicitly defined and can be programmatically validated. We provide the details in Appendix [A.1](https://arxiv.org/html/2603.21489v2#A1.SS1 "A.1 Commit0 Prompts ‣ Appendix A Prompt Engineering for Multi-Agent Task Delegation ‣ Effective Strategies for Asynchronous Software Engineering Agents").

The execution is organized around an asynchronous manager-controlled event loop. Once tasks are delegated, each engineer operates as an independent coroutine. Engineers invoke language model calls, modify code in their worktrees, and execute verification commands such as running tests. These operations are executed concurrently up to a predefined maximum number of active engineers. The manager listens for completion signals and dynamically updates the dependency state when commits are submitted. Engineers who finish early can be assigned new executable task units, while engineers whose dependencies are not yet satisfied remain idle. To manage context growth, the manager maintains a compressed execution history. We use LLMSummarizingCondenser to periodically summarize prior interaction rounds while preserving key structured artifacts such as the dependency graph, completed tasks, and unresolved errors. This separation prevents unnecessary context expansion while preserving execution traceability.

### 2.5 Self-Verification and Termination

To ensure implementation quality, we require each engineer to perform verification before submitting a commit. If executable tests are available, the engineer runs the subset of tests that directly import or reference the modified files. If there is no explicit mapping, the engineer runs the repository’s default test command or a minimally runnable entry point. Any failed test or runtime exception must be resolved before submission, and engineers iteratively refine the implementation using concrete error logs and tracebacks. After a verified commit is submitted, the manager integrates it into the main branch and updates the dependency state. The manager does not perform a detailed code review at every step, but monitors the overall progress and remaining implementation units. We terminate execution when all units in the dependency structure have been completed and integrated, or when predefined limits, such as maximum rounds or iteration budgets, are reached.

## 3 Main Results

### 3.1 Evaluation Benchmarks

We evaluate CAID on two long-horizon software engineering benchmarks.

#### Commit0

( [Zhao et al., 2024](https://arxiv.org/html/2603.21489v2#bib.bib6 "")) tests whether agents can implement a Python library from scratch given a repository skeleton and a suite of unit tests. The task is considered successful only if all tests pass, making it a repository-level integration problem rather than a collection of independent code completions.
We use Commit0-Lite as our primary evaluation set.
In Commit0, the manager receives an instruction and a repository path containing executable tests (Appendix [A.1](https://arxiv.org/html/2603.21489v2#A1.SS1 "A.1 Commit0 Prompts ‣ Appendix A Prompt Engineering for Multi-Agent Task Delegation ‣ Effective Strategies for Asynchronous Software Engineering Agents")). It first checks import statements for file-level dependencies, collects test cases, and examines which files those tests exercise. The manager is instructed to first consider file-level delegation, but if a single file contains many unimplemented functions it can further divide work at the function level. After assigning initial tasks to multiple engineers, the manager continues exploring the repository until one engineer completes its tasks, submits a commit for merge, and is ready for the next task.

#### PaperBench

( [Starace et al., 2025](https://arxiv.org/html/2603.21489v2#bib.bib5 "")) evaluates an agent’s ability to reproduce the main contributions of a published conference paper, typically involving multi-step implementation, experimental setup, and result verification. The benchmark emphasizes long-horizon reasoning and structured execution over complex codebases. Due to computational cost constraints, we adopt the Code-Dev evaluation protocol instead of running the full evaluation pipeline. Following the benchmark’s evaluation paradigm, we use gpt-5-mini( [OpenAI, 2025](https://arxiv.org/html/2603.21489v2#bib.bib42 "")) as the judge model to assess functional correctness and completion quality. As an open-ended task, explicit test-to-file mappings are not always available. The manager reads the paper, considers the main contribution as the central implementation objective, and infers the required implementation order from it. We provide the prompt in Appendix [A.2](https://arxiv.org/html/2603.21489v2#A1.SS2 "A.2 PaperBench Prompts ‣ Appendix A Prompt Engineering for Multi-Agent Task Delegation ‣ Effective Strategies for Asynchronous Software Engineering Agents").

### 3.2 Experimental Setup

We build CAID using the open-source OpenHands agent SDK ( [Wang et al., 2024](https://arxiv.org/html/2603.21489v2#bib.bib3 ""); [Wang et al., 2025b](https://arxiv.org/html/2603.21489v2#bib.bib4 "")) (v1.11.0), instantiating a centralized manager for dependency-aware task delegation and multiple software-engineer agents in isolated workspaces. We evaluate with three language models: two open-source (GLM 4.7( [Zeng et al., 2025](https://arxiv.org/html/2603.21489v2#bib.bib40 "")) and MiniMax 2.5( [MiniMax, 2024](https://arxiv.org/html/2603.21489v2#bib.bib43 ""))) and one closed-source (Claude-4.5-Sonnet( [Anthropic, 2024](https://arxiv.org/html/2603.21489v2#bib.bib41 ""))).
Following the Commit0 leaderboard111 [https://commit-0.github.io/](https://commit-0.github.io/ "") configuration, we use a single-agent setup with max\_iterations=100\\texttt{max\\\_iterations}=100 on both Commit0 and PaperBench. For multi-agent runs, we set max\_iterations=50\\texttt{max\\\_iterations}=50 for the manager and max\_iterations=80\\texttt{max\\\_iterations}=80 for each engineer agent, with 22 implementation rounds. In the main results, we use one manager with 22 engineers on PaperBench and 44 on Commit0. Detailed analysis of configuration choices is in Section [4](https://arxiv.org/html/2603.21489v2#S4 "4 Analysis ‣ Effective Strategies for Asynchronous Software Engineering Agents").222







All configurations are fixed prior to experimentation to balance correctness and runtime efficiency.

### 3.3 Baselines

Our primary baseline is a single-agent system built on the same OpenHands agent, isolating the effect of branch-and-merge coordination while holding the underlying framework fixed. This controlled comparison measures the incremental contribution of dependency-aware delegation, isolated workspaces, and merge-and-branch integration without introducing variation from framework-level differences such as prompting structure, tool interfaces, memory mechanisms, or execution policies. In Section [4](https://arxiv.org/html/2603.21489v2#S4 "4 Analysis ‣ Effective Strategies for Asynchronous Software Engineering Agents"), we further vary coordination and isolation mechanisms to compare different multi-agent architecture design choices.

### 3.4 Branch-and-Merge Based Coordination Improves Multi-Agent Performance

|     |     |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PaperBench |
|  |  | Single-Agent | CAID (2 Engineers) | Single-Agent + CAID |
| Model | SDK | Score | Runtime | Cost | Score | Runtime | Cost | Score | Runtime | Cost |
| Claude Sonnet 4.5 | v1.11.0 | 57.2 | 1803.5 | 3.3 | 63.3 | 2080.4 | 6.5 | 66.8 | 3883.9 | 9.7 |
| MiniMax 2.5 | v1.11.0 | 10.5 | 2525.3 | 1.1 | 36.1 | 3042.4 | 2.6 | 36.7 | 5567.7 | 3.7 |
| GLM 4.7 | v1.11.0 | 38.0 | 1177.6 | 2.8 | 45.4 | 1449.4 | 4.7 | 48.5 | 2627.0 | 7.5 |
| Commit0-Lite |
|  |  | Single-Agent | CAID (4 Engineers) | Single-Agent + CAID |
| Model | SDK | Score | Runtime | Cost | Score | Runtime | Cost | Score | Runtime | Cost |
| Claude Sonnet 4.5 | v1.11.0 | 53.1 | 692.6 | 1.9 | 59.1 | 1583.2 | 8.1 | 59.5 | 2275.8 | 10.0 |
| MiniMax 2.5 | v1.11.0 | 42.3 | 752.1 | 1.6 | 57.0 | 1908.7 | 4.5 | 57.0 | 2660.7 | 6.2 |
| GLM 4.7 | v1.11.0 | 42.9 | 871.0 | 2.5 | 46.5 | 1387.8 | 7.3 | 46.5 | 2258.8 | 9.8 |

Table 2: Main results on Commit0 and PaperBench. We compare single-agent baselines with CAID (2 engineers on PaperBench and 4 engineers on Commit0) under the same underlying model and fixed per-configuration iteration budgets.

We compare CAID with the single-agent baseline in Table [2](https://arxiv.org/html/2603.21489v2#S3.T2 "Table 2 ‣ 3.4 Branch-and-Merge Based Coordination Improves Multi-Agent Performance ‣ 3 Main Results ‣ Effective Strategies for Asynchronous Software Engineering Agents") and observe a consistent advantage for the branch-and-merge-based multi-agent system across both benchmarks and three LLMs. On PaperBench, we observe that multi-agent coordination yields large gains for weaker single-agent runs: MiniMax 2.5 reaches 36.1% under multi-agent execution, while its single-agent score is only 10.5%. The improvement is not limited to weaker models. With Claude 4.5, multi-agent execution achieves 63.3% compared to 57.2% for single-agent. In Commit0-Lite, we find the same pattern. Claude 4.5 improves from 53.1% to 59.1%, and MiniMax 2.5 reaches 57.0% under multi-agent execution. These results indicate that the performance gap is not explained by changing the underlying model, but by changing the execution method. In CAID, engineers work in separate branches and changes enter the main branch only through explicit merge and test validation. This makes parallel work usable by separating implementation from integration: engineers can iterate locally without overwriting each other’s intermediate states, while integration failures are surfaced at merge time with concrete test signals tied to specific updates. Our results in Table [2](https://arxiv.org/html/2603.21489v2#S3.T2 "Table 2 ‣ 3.4 Branch-and-Merge Based Coordination Improves Multi-Agent Performance ‣ 3 Main Results ‣ Effective Strategies for Asynchronous Software Engineering Agents") are consistent with the benefit of making integration explicit and test-gated under long-horizon execution. We provide one-sided t-tests in Appendix [C](https://arxiv.org/html/2603.21489v2#A3 "Appendix C One-sided t-test ‣ Effective Strategies for Asynchronous Software Engineering Agents").

Table [2](https://arxiv.org/html/2603.21489v2#S3.T2 "Table 2 ‣ 3.4 Branch-and-Merge Based Coordination Improves Multi-Agent Performance ‣ 3 Main Results ‣ Effective Strategies for Asynchronous Software Engineering Agents") further reveals an important strategic implication. In long-horizon shared-artifact tasks, multi-agent coordination should not be treated as a fallback after single-agent failure. The Single-Agent + Multi-Agent setting approximates a practical strategy in which a single agent is first attempted, followed by coordinated execution if necessary. However, this sequential strategy incurs nearly additive runtime and cost, while the final performance remains close to the direct multi-agent result. For example, on PaperBench with Claude Sonnet 4.5, the combined strategy reaches 66.8%, only slightly above the multi-agent score of 63.3%, yet runtime increases from 2080.4s to 3883.9s and cost rises from 6.5 to 9.7. On Commit0-Lite with MiniMax 2.5, the multi-agent score is 57.0%, and the combined strategy remains 57.0%, while both runtime and cost increase substantially. These results give us a clear strategy insight for long-horizon shared-artifact tasks.
Treating multi-agent coordination as a fallback after a single-agent attempt is inefficient. A more cost-effective strategy is to adopt coordinated multi-agent execution from the outset rather than switching only after failure.

### 3.5 Single Agents Fail to Utilize More Iterations

![Refer to caption](https://arxiv.org/html/2603.21489v2/delta_hori_paperbench.png)Figure 2: CAID effectively utilizes iteration budgets. We compare the final score and the iteration utilization between single-agent runs with different iteration limits and CAID.

Can a single agent overcome long-horizon shared-artifact challenges simply by running longer?
To study this, we run a single agent with m​a​x​\_​i​t​e​r​a​t​i​o​n​s=100max\\\_iterations=100 and m​a​x​\_​i​t​e​r​a​t​i​o​n​s=200max\\\_iterations=200. We control computation through a max iteration budget rather than enforcing a fixed runtime, which better reflects practical agent deployment where iteration-based control is commonly used.
As shown in Figure [2](https://arxiv.org/html/2603.21489v2#S3.F2 "Figure 2 ‣ 3.5 Single Agents Fail to Utilize More Iterations ‣ 3 Main Results ‣ Effective Strategies for Asynchronous Software Engineering Agents"), doubling the iteration limit yields only marginal improvements and, in some cases, even degraded results. In PaperBench, Δ\\Delta from 100 to 200 iterations remains small for GLM 4.7 and MiniMax 2.5, and becomes negative for Claude Sonnet 4.5. In Commit0-Lite, the improvement is similarly limited, and MiniMax 2.5 shows a negative delta. This trend is consistent with the findings in PaperBench, where forcing the agent to run until a time limit does not reliably improve the judge score ( [Starace et al., 2025](https://arxiv.org/html/2603.21489v2#bib.bib5 "")). In Figure [2](https://arxiv.org/html/2603.21489v2#S3.F2 "Figure 2 ‣ 3.5 Single Agents Fail to Utilize More Iterations ‣ 3 Main Results ‣ Effective Strategies for Asynchronous Software Engineering Agents"), we also show the score gain of CAID relative to the 100-iteration single-agent baseline. Across both benchmarks, these gains are substantially larger than those from increasing the iteration budget. For example, on PaperBench the multi-agent improvement for MiniMax 2.5 exceeds 25 percentage points, while doubling iterations yields only a small change. A similar gap appears in Commit0-Lite. These results show that extending the iteration budget alone does not resolve the fundamental bottleneck of a single agent on long-horizon tasks, whereas multi-agent coordination produces significantly larger gains.

## 4 Analysis

### 4.1 Git worktree Isolation

|     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- |
| PaperBench |
| single agent | CAID(worktree isolation) | multi-agent(soft isolation) |
| score | iterations | score | iterations | score | iterations |
| 57.2 | 66.8 | 63.3 | 168.3 | 55.5 | 190.0 |
| Commit0-Lite |
| single agent | CAID(worktree isolation) | multi-agent(soft isolation) |
| score | iterations | score | iterations | score | iterations |
| 53.1 | 84.5 | 59.1 | 313.3 | 56.1 | 335.9 |

Table 3: We compare soft context isolation and worktree isolation on PaperBench and Commit0-Lite.

In Table [3](https://arxiv.org/html/2603.21489v2#S4.T3 "Table 3 ‣ 4.1 Git worktree Isolation ‣ 4 Analysis ‣ Effective Strategies for Asynchronous Software Engineering Agents"), we study whether our proposed method of “worktree isolation” is necessary, comparing it with “soft isolation”, where all engineers share one workspace, and the central manager attempts to prevent conflicts through instruction-level constraints, such as assigning non-overlapping files and explicitly warning against interference.
On Commit0-Lite, soft isolation improves over single-agent from 53.1% to 56.1%, showing that central manager-driven delegation alone already helps when repository structure and file dependencies are explicit. Worktree isolation further increases performance to 59.1%, indicating that instruction-level separation is not sufficient to fully eliminate interference over longer trajectories. In contrast, on PaperBench soft isolation drops to 55.5%, below the single-agent score of 57.2%, while worktree isolation reaches 63.3%. Unlike Commit0, PaperBench does not provide explicit file structure or dependency graphs, and the manager must first infer the global implementation plan from the paper itself. In this case, sharing a workspace causes miscoordination, whereas worktree isolation stabilizes parallel execution.

### 4.2 Choosing the Degree of Parallel Execution

Figure 3: Effect of the number of engineer agents on runtime, pass rate, and cost for Commit0-Lite and PaperBench. We provide the single-agent baselines here for comparison.

We analyze how the number of asynchronous engineer agents affects the performance in Figure [3](https://arxiv.org/html/2603.21489v2#S4.F3 "Figure 3 ‣ 4.2 Choosing the Degree of Parallel Execution ‣ 4 Analysis ‣ Effective Strategies for Asynchronous Software Engineering Agents"). We find that increasing the number of engineers does not monotonically improve the performance, which aligns with the results in ( [Yang et al., 2026](https://arxiv.org/html/2603.21489v2#bib.bib47 "")). The optimal degree of parallelism depends on two factors: the intrinsic parallel structure of the task and the delegation capacity of the central manager. First, tasks differ in how many components can be implemented independently. In Commit0-Lite, performance improves when increasing engineers from 2 to 4, but decreases when expanding to 8 engineers. Although more agents increase theoretical parallelism, overly fine-grained task delegation introduces integration overhead and conflict resolution cost, especially when multiple engineers modify closely related modules. However, too few engineers can exploit the independent files available in clear-structured repositories, limiting progress within a fixed iteration budget. Second, scalability is constrained by the manager’s coordination ability. The central manager must track dependency states, monitor the progress of engineers, and dynamically assign tasks. When the number of engineers increases, delegation errors or delayed synchronization can propagate and destabilize the overall trajectory. This effect is visible in Commit0-Lite at 8 engineers, where performance declines despite higher computation cost. On PaperBench, where task decomposition is less structurally explicit, increasing engineers beyond 2 yields minimal gain in score while runtime and cost increase steadily. These results show that the number of subagents should be matched to both the inherent modularity of the task and the effective delegation capacity of the manager. Excess parallelism without reliable coordination degrades stability, rather than improving performance. We provide examples of failure in the Appendix [D](https://arxiv.org/html/2603.21489v2#A4 "Appendix D Failure on Scaling the Parallel Execution ‣ Effective Strategies for Asynchronous Software Engineering Agents").

### 4.3 Delegation Shapes Execution Trajectory

Figure 4: Execution timelines on the minitorch repository for a single-agent run and two CAID runs. The bars in the Gantt plot indicate file-level implementation intervals and manager phases. The runs differ in which modules are assigned and actively developed, resulting in distinct execution trajectories and pass rates.

In Figure [4](https://arxiv.org/html/2603.21489v2#S4.F4 "Figure 4 ‣ 4.3 Delegation Shapes Execution Trajectory ‣ 4 Analysis ‣ Effective Strategies for Asynchronous Software Engineering Agents"), we show two CAID runs and one single-agent run in the Commit0-Lite minitorch repository to study how task delegation affects execution outcomes. We find that the performance difference between CAID Run 1 (8.7% pass rate) and CAID Run 2 (34.3%) is not simply due to the number of modules implemented, but to which modules are assigned and actively pursued. In Run 2, the manager assigns an engineer to autodiff.py, a file that is critical for passing tests, and sustained effort on this file is followed by broader progress across dependent components. In contrast, Run 1 assigns engineers to several other files, but never assigns work to autodiff.py. Although multiple engineers are active, the absence of this key dependency limits the overall pass rate. We observe that the single-agent run touches autodiff.py during exploration and implements part of the logic, but the file remains incomplete and the final pass rate reaches only 17.4%. This example shows that the manager’s delegation ability, particularly the ability to identify and assign high-impact dependencies, is critical for the success of long-horizon SWE tasks.

### 4.4 Scaling Asynchronous Parallelism

Figure 5: Runtime (s) vs. pass rate (%) of a subset of the Commit0 under three coordination prompts (1) Round-Manager Review: the manager reviews each round before integration; (2) Engineer Self-Verification: engineers verify locally without repeated managerial review; and (3) Efficiency-Prioritized: all agents are instructed to prioritize runtime efficiency.

During our exploration of the multi-agent design, we experimented with different prompt engineering strategies that emphasize distinct objectives, such as prioritizing correctness or efficiency. Figure [5](https://arxiv.org/html/2603.21489v2#S4.F5 "Figure 5 ‣ 4.4 Scaling Asynchronous Parallelism ‣ 4 Analysis ‣ Effective Strategies for Asynchronous Software Engineering Agents") shows the results on a subset of eight repositories (i.e., _babel, chardet, cookiecutter, imapclient, jinja, minitorch, simpy, tinydb_) of Commit0-Lite. In Round-Manager Review, the manager explicitly reviews code quality at every implementation round before integration for each engineer, placing stronger emphasis on correctness. In Engineer Self-Verification, engineers conduct self-review without repeated managerial inspection, which is closest to the main results we report in Section [3](https://arxiv.org/html/2603.21489v2#S3 "3 Main Results ‣ Effective Strategies for Asynchronous Software Engineering Agents"). In Efficiency-Prioritized, both manager and engineer agents are explicitly instructed to prioritize runtime efficiency and are reminded that execution time will be evaluated, thereby assigning higher weight to the runtime of implementation in the user instruction. We observe a clear pattern: Round-Manager Review achieves the highest pass rate (60.2%) but also incurs the longest runtime (3689.1s), Self-Verification yields intermediate performance (55.1%) with moderate runtime (2243.9s), and Efficiency-Prioritized runs fastest (1908.6s) but achieves the lowest pass rate (54.0%). This development-stage result suggests a trade-off between verification intensity and execution efficiency: emphasizing efficiency can shorten runtime but may reduce integration robustness, while stricter review improves stability at additional computational cost.

## 5 Related Work

### 5.1 Multi-Agent Architectures

Recent studies have explored diverse architectural choices for LLM-based multi-agent systems, spanning from static, predefined role-playing topologies to dynamic, task-adaptive orchestrations. Early frameworks such as CAMEL ( [Li et al., 2023](https://arxiv.org/html/2603.21489v2#bib.bib16 "")) and Generative Agents ( [Park et al., 2023](https://arxiv.org/html/2603.21489v2#bib.bib19 "")) established the foundation for communicative interaction, which was later structured into a natural language communication pipeline from ChatDev ( [Qian et al., 2024a](https://arxiv.org/html/2603.21489v2#bib.bib12 "")). To enhance flexibility, EvoMAC [Hu et al. (2024)](https://arxiv.org/html/2603.21489v2#bib.bib48 "")
explores self-evolving collaboration and AutoAgents [Chen et al. (2023)](https://arxiv.org/html/2603.21489v2#bib.bib20 "") focuses on automated agent generation. Advanced orchestrators like AgentOrchestra [Zhang et al. (2025b)](https://arxiv.org/html/2603.21489v2#bib.bib18 "") introduce standardized protocols (e.g., TEA), while MASS ( [Zhou et al., 2025](https://arxiv.org/html/2603.21489v2#bib.bib21 "")) and DyLAN ( [Liu et al., 2023](https://arxiv.org/html/2603.21489v2#bib.bib22 "")) optimize inter-agent topologies for adaptive task decomposition. Despite achieving higher autonomy in personnel allocation, these architectures still struggle with high-density communication and cognitive overload in long-horizon tasks. To address this, MegaAgent [Wang et al. (2025a)](https://arxiv.org/html/2603.21489v2#bib.bib23 "") and subsequent scaling laws ( [Qian et al., 2024b](https://arxiv.org/html/2603.21489v2#bib.bib24 "")) examine the decay of efficiency in large clusters, leading to optimization strategies such as sequential aggregation in Chain-of-Agents ( [Zhang et al., 2024](https://arxiv.org/html/2603.21489v2#bib.bib26 "")), and memory abstractions in MemGPT ( [Packer et al., 2023](https://arxiv.org/html/2603.21489v2#bib.bib25 "")). Many open-source agents such as OpenHands ( [Wang et al., 2024](https://arxiv.org/html/2603.21489v2#bib.bib3 "")) further reduce context explosion through history condensation.

Although many multi-agent systems optimize information flow, they largely rely on "standardized operating procedures" to maintain agent coordination ( [Hong et al., 2023](https://arxiv.org/html/2603.21489v2#bib.bib11 ""); [Nguyen et al., 2025](https://arxiv.org/html/2603.21489v2#bib.bib17 "")) and incorporate agile methodologies for lifecycle management. Deeper coordination is studied through implicit co-player inference ( [Meulemans et al., 2024](https://arxiv.org/html/2603.21489v2#bib.bib27 "")), consensus-based evaluation in agent-as-judge ( [Zhuge et al., 2024](https://arxiv.org/html/2603.21489v2#bib.bib28 "")). However, in shared-artifact environments like software engineering, these linguistically-governed architectures frequently encounter execution conflicts when multiple agents concurrently modify the codebase. [Khatua et al. (2026)](https://arxiv.org/html/2603.21489v2#bib.bib14 "") suggest that this critical bottleneck for multi-agent execution remains under-explored. This gap reveals that we need an architectural design that physically coordinates multiple agents in an execution-aware paradigm.

### 5.2 Multi-Agent Coordination Challenges

Despite advances in multi-agent architectures, coordination stability remains constrained by communication workflows, which is directly reflected in task delegation under the uncertainty of complex tasks and explicit conflicts within shared workspaces. In dialogue-driven systems ( [Wu et al., 2024](https://arxiv.org/html/2603.21489v2#bib.bib35 "")), delegation typically emerges implicitly through conversational interaction rather than explicit authority modeling, which can lead to redundant effort or delayed escalation. While recent studies propose more structured approaches—including orchestrator-executor handoffs and hierarchical organizations ( [Song et al., 2025](https://arxiv.org/html/2603.21489v2#bib.bib36 ""); [Xu et al., 2025](https://arxiv.org/html/2603.21489v2#bib.bib37 "")) to regulate task delegation, scaling analyses ( [Qian et al., 2024b](https://arxiv.org/html/2603.21489v2#bib.bib24 ""); [Li et al., 2024c](https://arxiv.org/html/2603.21489v2#bib.bib38 "")) demonstrate that increasing the agent population without disciplined delegation amplifies communication overhead and may degrade overall performance. Another critical challenge caused by unstructured communication is physical interference: planning-oriented analyses ( [Li et al., 2024a](https://arxiv.org/html/2603.21489v2#bib.bib39 "")) report severe task overlap and inconsistent action sequences, while empirical scaling results ( [Qian et al., 2024b](https://arxiv.org/html/2603.21489v2#bib.bib24 ""); [Li et al., 2024c](https://arxiv.org/html/2603.21489v2#bib.bib38 "")) quantify a "coordination tax" in which synchronization costs grow superlinearly with agent count. These findings indicate that linguistic alignment can harmonize intent but cannot inherently serialize concurrent state transitions or guarantee integration consistency. To address these challenges, we use a central manager to explicitly delegate tasks and physically isolate the workspaces of concurrent agents to prevent integration conflicts.

### 5.3 Software Engineering for Multi-Agent Coordination

Before the emergence of LLM-based agents, software engineering had already developed mechanisms for coordinating parallel work over shared artifacts, including branching and merging, dependency management, continuous integration, and code review. These mechanisms treat coordination as explicit control over versioned artifacts and their integration. Recent multi-agent work has begun to implicitly adopt parts of the SWE paradigm. Process-driven frameworks such as MetaGPT ( [Hong et al., 2023](https://arxiv.org/html/2603.21489v2#bib.bib11 "")) and AgileCoder ( [Nguyen et al., 2025](https://arxiv.org/html/2603.21489v2#bib.bib17 "")) mirror role decomposition and lifecycle management. Sandbox-based systems, including the SWE-agent [Yang et al. (2024)](https://arxiv.org/html/2603.21489v2#bib.bib1 ""), incorporate build–test feedback loops analogous to continuous integration. However, recent empirical studies [Khatua et al. (2026)](https://arxiv.org/html/2603.21489v2#bib.bib14 "") still report that concurrent modification and merge conflicts remain a primary failure mode when these engineering primitives are not explicitly modeled. These observations suggest that, in shared repositories, the central issue is not only how agents are organized into roles or workflows, but also how concurrent work is isolated, integrated, and verified. In this paper, we focus on branch-and-merge coordination and the SWE primitives that support it in multi-agent software engineering.

### 5.4 Software Engineering Evaluation Benchmarks

Software Engineering (SWE) tasks, which evaluate agents on their ability to autonomously carry out diverse real-world development activities across complex codebases, have become the core benchmarks for measuring the practical capabilities of LLM-based coding agents. SWE-bench [Jimenez et al. (2023)](https://arxiv.org/html/2603.21489v2#bib.bib2 "") provides the initial benchmark for autonomous issue resolution. SWE-bench Verified [Chowdhury et al. (2024)](https://arxiv.org/html/2603.21489v2#bib.bib29 "") refines the evaluation methodology to enhance fidelity and robustness, whereas SWE-bench Pro [Deng et al. (2025)](https://arxiv.org/html/2603.21489v2#bib.bib7 "") expands the task design to include professionally curated, multi-step engineering problems that better approximate complex real-world development workflows. To move beyond issue-level resolution, several benchmarks isolate specific capabilities of software engineering agents. TerminalBench [Merrill et al. (2026)](https://arxiv.org/html/2603.21489v2#bib.bib30 "") and InterCode [Yang et al. (2023)](https://arxiv.org/html/2603.21489v2#bib.bib31 "") evaluate the use of terminal-based tools, while DevBench [Li et al. (2024b)](https://arxiv.org/html/2603.21489v2#bib.bib32 "") extends the assessment to the broader software development lifecycle. For long-horizon and reasoning-intensive scenarios, SciCode ( [Tian et al., 2024](https://arxiv.org/html/2603.21489v2#bib.bib33 "")) and LongCLI ( [Feng et al., 2026](https://arxiv.org/html/2603.21489v2#bib.bib34 "")) introduce multi-step algorithmic or decentralized workflows. At a larger granularity, Commit0 [Zhao et al. (2024)](https://arxiv.org/html/2603.21489v2#bib.bib6 "") and PaperBench [Starace et al. (2025)](https://arxiv.org/html/2603.21489v2#bib.bib5 "") introduce long-horizon SWE tasks that move beyond localized reasoning. Long-horizon, complex SWE tasks naturally constitute a rigorous testbed for multi-agent systems, as coordinated multi-file modifications, interdependent subtasks, and explicit merge conflicts systematically expose challenges in synchronization, consistency maintenance, and progress integration across agents. In this paper, we evaluate CAID on Commit0 and PaperBench.

## 6 Limitations and Future Directions

#### Cost and Runtime.

Although CAID improves success rates on long-horizon shared-artifact tasks, it introduces non-trivial coordination overhead. In our experiments, multi-agent execution consistently incurs higher API cost than single-agent baselines, and wall-clock runtime is not substantially reduced despite parallel execution. This reflects a fundamental trade-off: structured isolation, integration, and verification improve stability, but require additional communication rounds, merge operations, and test executions. In particular, while engineers operate concurrently, integration remains sequential and test-gated, limiting end-to-end acceleration. Prior analyses of multi-agent systems have similarly noted that coordination complexity can offset gains from specialization and parallelism when not carefully optimized ( [Radar, 2024](https://arxiv.org/html/2603.21489v2#bib.bib44 "")). For the long-horizon shared-artifact tasks we study, however, such coordination may still be necessary, since simply extending single-agent execution does not reliably achieve comparable gains. Therefore, promising next steps include improving scheduling efficiency, reducing redundant verification cycles, and learning when to merge or prune intermediate states. Optimizing the cost–performance frontier of structured multi-agent execution remains an important area for future work.

#### Isolated Task Delegation Capabilities of Agents.

A second limitation lies in the central manager’s task decomposition and delegation capability. In the current implementation, task assignment relies primarily on prompt engineering heuristics rather than learned delegation policies. While our results indicate that architectural isolation and integration are the dominant factors for stability, weak or suboptimal task decomposition can still reduce overall effectiveness. Existing analyses of multi-agent systems identify imprecise task handoffs and underspecified subgoals as major sources of coordination failure ( [Bhavsar, 2026](https://arxiv.org/html/2603.21489v2#bib.bib45 "")).
Our findings align with this observation: when delegation is coarse-grained or misaligned with dependency structure, engineers may produce locally correct outputs that are globally inefficient to integrate. Future work may explore reinforcement learning–based delegation policies, dependency-aware planning modules, or adaptive subtask refinement strategies that improve alignment between global objectives and isolated execution. Strengthening delegation capability would allow the architectural benefits of isolation and structured integration to scale more reliably.

#### Generalization Beyond Software Engineering Tasks.

Finally, our evaluation focuses on software engineering benchmarks, which provide a natural testbed for structured multi-agent execution due to explicit workspace boundaries, version control infrastructure, and executable test suites. These properties make software development uniquely suitable for studying isolation, integration, and dependency-aware coordination. However, not all long-horizon shared-artifact tasks possess such clearly defined boundaries or objective verification mechanisms. Extending CAID to non-coding domains—such as document synthesis, research planning, or multimodal artifact construction—will require adapting isolation mechanisms and designing alternative forms of integration and validation. Evaluating the framework in such settings is necessary to determine whether the architectural principles demonstrated here generalize beyond SWE-specific workflows.

## 7 Conclusion

In this paper, we introduce CAID, a branch-and-merge based multi-agent system for long-horizon software engineering tasks. We use a manager to break a task into dependency-aware units, assign them to engineers, and keep each engineer working in an isolated branch and worktree. Progress is integrated only through git commit and git merge on the main branch, with tests used as the executable check for whether an update should be kept. Across Commit0 and PaperBench, our CAID consistently improves over single-agent baselines, even when the underlying model is unchanged. Our results also show that simply increasing the single agent iteration budget does not reliably improve outcomes, and a fallback strategy that runs a single agent first and then switches to multi-agent mainly wastes runtime and cost. Overall, we show that branch-and-merge is important for effective multi-agent software engineering and that SWE primitives provide a practical way to support it. For complex long-horizon, dependency-aware software engineering tasks, CAID is the default paradigm for structuring solutions to enable parallel and coordinated development.

## Acknowledgments

This paper was supported by grants from Fujitsu. We thank Apurva Gandhi, Lintang Sutawika, Emmy Liu, and Howard Chen for their valuable feedback and discussion.

## References

- Anthropic (2024)AnthropicClaude 4.5 sonnet.
Note: [https://www.anthropic.com](https://www.anthropic.com/ "") Large language model developed by AnthropicCited by: [§3.2](https://arxiv.org/html/2603.21489v2#S3.SS2.p1.1 "3.2 Experimental Setup ‣ 3 Main Results ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Benkovich and Valkov (2026)N. Benkovich and V. ValkovAgyn: a multi-agent system for team-based autonomous software engineering.
arXiv preprint arXiv:2602.01465.
Cited by: [§1](https://arxiv.org/html/2603.21489v2#S1.p2.1 "1 Introduction ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Bhavsar (2026)P. BhavsarWhy do multi-agent systems fail even when agents work perfectly in isolation?.
Note: Galileo BlogExternal Links: [Link](https://galileo.ai/blog/why-multi-agent-systems-fail "")Cited by: [§6](https://arxiv.org/html/2603.21489v2#S6.SS0.SSS0.Px2.p1.1 "Isolated Task Delegation Capabilities of Agents. ‣ 6 Limitations and Future Directions ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Cemri et al. (2025)M. Cemri, M. Z. Pan, S. Yang, L. A. Agrawal, B. Chopra, R. Tiwari, K. Keutzer, A. Parameswaran, D. Klein, K. Ramchandran, et al.Why do multi-agent llm systems fail?.
arXiv preprint arXiv:2503.13657.
Cited by: [§1](https://arxiv.org/html/2603.21489v2#S1.p2.1 "1 Introduction ‣ Effective Strategies for Asynchronous Software Engineering Agents"),
[§1](https://arxiv.org/html/2603.21489v2#S1.p4.1 "1 Introduction ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Chen et al. (2023)G. Chen, S. Dong, Y. Shu, G. Zhang, J. Sesay, B. F. Karlsson, J. Fu, and Y. ShiAutoagents: a framework for automatic agent generation.
arXiv preprint arXiv:2309.17288.
Cited by: [§5.1](https://arxiv.org/html/2603.21489v2#S5.SS1.p1.1 "5.1 Multi-Agent Architectures ‣ 5 Related Work ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Chowdhury et al. (2024)N. Chowdhury, J. Aung, C. J. Shern, O. Jaffe, D. Sherburn, G. Starace, E. Mays, R. Dias, M. Aljubeh, M. Glaese, C. E. Jimenez, J. Yang, L. Ho, T. Patwardhan, K. Liu, and A. MadryIntroducing swe-bench verified.
External Links: [Link](https://openai.com/index/introducing-swe-bench-verified/ "")Cited by: [§5.4](https://arxiv.org/html/2603.21489v2#S5.SS4.p1.1 "5.4 Software Engineering Evaluation Benchmarks ‣ 5 Related Work ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Cognition AI (2025)Cognition AIDon’t build multi-agents.
Note: [https://cognition.ai/blog/dont-build-multi-agents](https://cognition.ai/blog/dont-build-multi-agents "") Accessed: 2026-02-20Cited by: [§1](https://arxiv.org/html/2603.21489v2#S1.p2.1 "1 Introduction ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Deng et al. (2025)X. Deng, J. Da, E. Pan, Y. Y. He, C. Ide, K. Garg, N. Lauffer, A. Park, N. Pasari, C. Rane, et al.Swe-bench pro: can ai agents solve long-horizon software engineering tasks?.
arXiv preprint arXiv:2509.16941.
Cited by: [§5.4](https://arxiv.org/html/2603.21489v2#S5.SS4.p1.1 "5.4 Software Engineering Evaluation Benchmarks ‣ 5 Related Work ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Feng et al. (2026)Y. Feng, J. Sun, Z. Yang, J. Ai, C. Li, Z. Li, F. Zhang, K. He, R. Ma, J. Lin, et al.LongCLI-bench: a preliminary benchmark and study for long-horizon agentic programming in command-line interfaces.
arXiv preprint arXiv:2602.14337.
Cited by: [§5.4](https://arxiv.org/html/2603.21489v2#S5.SS4.p1.1 "5.4 Software Engineering Evaluation Benchmarks ‣ 5 Related Work ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Hong et al. (2023)S. Hong, M. Zhuge, J. Chen, X. Zheng, Y. Cheng, J. Wang, C. Zhang, Z. Wang, S. K. S. Yau, Z. Lin, et al.MetaGPT: meta programming for a multi-agent collaborative framework.
In The twelfth international conference on learning representations,
Cited by: [§1](https://arxiv.org/html/2603.21489v2#S1.p2.1 "1 Introduction ‣ Effective Strategies for Asynchronous Software Engineering Agents"),
[§5.1](https://arxiv.org/html/2603.21489v2#S5.SS1.p2.1 "5.1 Multi-Agent Architectures ‣ 5 Related Work ‣ Effective Strategies for Asynchronous Software Engineering Agents"),
[§5.3](https://arxiv.org/html/2603.21489v2#S5.SS3.p1.1 "5.3 Software Engineering for Multi-Agent Coordination ‣ 5 Related Work ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Hu et al. (2024)Y. Hu, Y. Cai, Y. Du, X. Zhu, X. Liu, Z. Yu, Y. Hou, S. Tang, and S. ChenSelf-evolving multi-agent collaboration networks for software development.
arXiv preprint arXiv:2410.16946.
Cited by: [§5.1](https://arxiv.org/html/2603.21489v2#S5.SS1.p1.1 "5.1 Multi-Agent Architectures ‣ 5 Related Work ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Jimenez et al. (2023)C. E. Jimenez, J. Yang, A. Wettig, S. Yao, K. Pei, O. Press, and K. NarasimhanSwe-bench: can language models resolve real-world github issues?.
arXiv preprint arXiv:2310.06770.
Cited by: [§1](https://arxiv.org/html/2603.21489v2#S1.p1.1 "1 Introduction ‣ Effective Strategies for Asynchronous Software Engineering Agents"),
[§5.4](https://arxiv.org/html/2603.21489v2#S5.SS4.p1.1 "5.4 Software Engineering Evaluation Benchmarks ‣ 5 Related Work ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Khatua et al. (2026)A. Khatua, H. Zhu, P. Tran, A. Prabhudesai, F. Sadrieh, J. K. Lieberwirth, X. Yu, Y. Fu, M. J. Ryan, J. Pei, et al.CooperBench: why coding agents cannot be your teammates yet.
arXiv preprint arXiv:2601.13295.
Cited by: [§1](https://arxiv.org/html/2603.21489v2#S1.p2.1 "1 Introduction ‣ Effective Strategies for Asynchronous Software Engineering Agents"),
[§5.1](https://arxiv.org/html/2603.21489v2#S5.SS1.p2.1 "5.1 Multi-Agent Architectures ‣ 5 Related Work ‣ Effective Strategies for Asynchronous Software Engineering Agents"),
[§5.3](https://arxiv.org/html/2603.21489v2#S5.SS3.p1.1 "5.3 Software Engineering for Multi-Agent Coordination ‣ 5 Related Work ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Kwa et al. (2025)T. Kwa, B. West, J. Becker, A. Deng, K. Garcia, M. Hasin, S. Jawhar, M. Kinniment, N. Rush, S. Von Arx, et al.Measuring ai ability to complete long tasks.
arXiv preprint arXiv:2503.14499.
Cited by: [§1](https://arxiv.org/html/2603.21489v2#S1.p1.1 "1 Introduction ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Li et al. (2024a)A. Li, Y. Xie, S. Li, F. Tsung, B. Ding, and Y. LiAgent-oriented planning in multi-agent systems.
arXiv preprint arXiv:2410.02189.
Cited by: [§5.2](https://arxiv.org/html/2603.21489v2#S5.SS2.p1.1 "5.2 Multi-Agent Coordination Challenges ‣ 5 Related Work ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Li et al. (2024b)B. Li, W. Wu, Z. Tang, L. Shi, J. Yang, J. Li, S. Yao, C. Qian, B. Hui, Q. Zhang, et al.Devbench: a comprehensive benchmark for software development.
arXiv preprint arXiv:2403.086043.
Cited by: [§5.4](https://arxiv.org/html/2603.21489v2#S5.SS4.p1.1 "5.4 Software Engineering Evaluation Benchmarks ‣ 5 Related Work ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Li et al. (2023)G. Li, H. Hammoud, H. Itani, D. Khizbullin, and B. GhanemCamel: communicative agents for" mind" exploration of large language model society.
Advances in neural information processing systems36, pp. 51991–52008.
Cited by: [§5.1](https://arxiv.org/html/2603.21489v2#S5.SS1.p1.1 "5.1 Multi-Agent Architectures ‣ 5 Related Work ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Li et al. (2024c)J. Li, Q. Zhang, Y. Yu, Q. Fu, and D. YeMore agents is all you need.
arXiv preprint arXiv:2402.05120.
Cited by: [§5.2](https://arxiv.org/html/2603.21489v2#S5.SS2.p1.1 "5.2 Multi-Agent Coordination Challenges ‣ 5 Related Work ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Liu et al. (2023)Z. Liu, Y. Zhang, P. Li, Y. Liu, and D. YangDynamic llm-agent network: an llm-agent collaboration framework with agent team optimization.
arXiv preprint arXiv:2310.02170.
Cited by: [§5.1](https://arxiv.org/html/2603.21489v2#S5.SS1.p1.1 "5.1 Multi-Agent Architectures ‣ 5 Related Work ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Merrill et al. (2026)M. A. Merrill, A. G. Shaw, N. Carlini, B. Li, H. Raj, I. Bercovich, L. Shi, J. Y. Shin, T. Walshe, E. K. Buchanan, et al.Terminal-bench: benchmarking agents on hard, realistic tasks in command line interfaces.
arXiv preprint arXiv:2601.11868.
Cited by: [§5.4](https://arxiv.org/html/2603.21489v2#S5.SS4.p1.1 "5.4 Software Engineering Evaluation Benchmarks ‣ 5 Related Work ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Meulemans et al. (2024)A. Meulemans, S. Kobayashi, J. von Oswald, N. Scherrer, E. Elmoznino, B. Richards, G. Lajoie, J. Sacramento, et al.Multi-agent cooperation through learning-aware policy gradients.
arXiv preprint arXiv:2410.18636.
Cited by: [§5.1](https://arxiv.org/html/2603.21489v2#S5.SS1.p2.1 "5.1 Multi-Agent Architectures ‣ 5 Related Work ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- MiniMax (2024)MiniMaxMiniMax 2.5.
Note: [https://www.minimaxi.com](https://www.minimaxi.com/ "") Large language model developed by MiniMaxCited by: [§3.2](https://arxiv.org/html/2603.21489v2#S3.SS2.p1.1 "3.2 Experimental Setup ‣ 3 Main Results ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Nguyen et al. (2025)M. H. Nguyen, T. P. Chau, P. X. Nguyen, and N. D. BuiAgilecoder: dynamic collaborative agents for software development based on agile methodology.
In 2025 IEEE/ACM Second International Conference on AI Foundation Models and Software Engineering (Forge),
pp. 156–167.
Cited by: [§5.1](https://arxiv.org/html/2603.21489v2#S5.SS1.p2.1 "5.1 Multi-Agent Architectures ‣ 5 Related Work ‣ Effective Strategies for Asynchronous Software Engineering Agents"),
[§5.3](https://arxiv.org/html/2603.21489v2#S5.SS3.p1.1 "5.3 Software Engineering for Multi-Agent Coordination ‣ 5 Related Work ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- OpenAI (2025)OpenAIGPT-5-mini.
Note: [https://www.openai.com](https://www.openai.com/ "") Large language model developed by OpenAICited by: [§3.1](https://arxiv.org/html/2603.21489v2#S3.SS1.SSS0.Px2.p1.1 "PaperBench ‣ 3.1 Evaluation Benchmarks ‣ 3 Main Results ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Packer et al. (2023)C. Packer, V. Fang, S. Patil, K. Lin, S. Wooders, and J. GonzalezMemGPT: towards llms as operating systems..
Cited by: [§5.1](https://arxiv.org/html/2603.21489v2#S5.SS1.p1.1 "5.1 Multi-Agent Architectures ‣ 5 Related Work ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Park et al. (2023)J. S. Park, J. O’Brien, C. J. Cai, M. R. Morris, P. Liang, and M. S. BernsteinGenerative agents: interactive simulacra of human behavior.
In Proceedings of the 36th annual acm symposium on user interface software and technology,
pp. 1–22.
Cited by: [§5.1](https://arxiv.org/html/2603.21489v2#S5.SS1.p1.1 "5.1 Multi-Agent Architectures ‣ 5 Related Work ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Qian et al. (2024a)C. Qian, W. Liu, H. Liu, N. Chen, Y. Dang, J. Li, C. Yang, W. Chen, Y. Su, X. Cong, et al.Chatdev: communicative agents for software development.
In Proceedings of the 62nd annual meeting of the association for computational linguistics (volume 1: Long papers),
pp. 15174–15186.
Cited by: [§1](https://arxiv.org/html/2603.21489v2#S1.p2.1 "1 Introduction ‣ Effective Strategies for Asynchronous Software Engineering Agents"),
[§5.1](https://arxiv.org/html/2603.21489v2#S5.SS1.p1.1 "5.1 Multi-Agent Architectures ‣ 5 Related Work ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Qian et al. (2024b)C. Qian, Z. Xie, Y. Wang, W. Liu, K. Zhu, H. Xia, Y. Dang, Z. Du, W. Chen, C. Yang, et al.Scaling large language model-based multi-agent collaboration.
arXiv preprint arXiv:2406.07155.
Cited by: [§5.1](https://arxiv.org/html/2603.21489v2#S5.SS1.p1.1 "5.1 Multi-Agent Architectures ‣ 5 Related Work ‣ Effective Strategies for Asynchronous Software Engineering Agents"),
[§5.2](https://arxiv.org/html/2603.21489v2#S5.SS2.p1.1 "5.2 Multi-Agent Coordination Challenges ‣ 5 Related Work ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Radar (2024)O. RadarDesigning effective multi-agent architectures.
Note: [https://www.oreilly.com/radar/designing-effective-multi-agent-architectures/](https://www.oreilly.com/radar/designing-effective-multi-agent-architectures/ "") Accessed 2026Cited by: [§6](https://arxiv.org/html/2603.21489v2#S6.SS0.SSS0.Px1.p1.1 "Cost and Runtime. ‣ 6 Limitations and Future Directions ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Song et al. (2025)L. Song, Y. Dai, V. Prabhu, J. Zhang, T. Shi, L. Li, J. Li, S. Savarese, Z. Chen, J. Zhao, et al.Coact-1: computer-using agents with coding as actions.
arXiv preprint arXiv:2508.03923.
Cited by: [§5.2](https://arxiv.org/html/2603.21489v2#S5.SS2.p1.1 "5.2 Multi-Agent Coordination Challenges ‣ 5 Related Work ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Starace et al. (2025)G. Starace, O. Jaffe, D. Sherburn, J. Aung, J. S. Chan, L. Maksin, R. Dias, E. Mays, B. Kinsella, W. Thompson, et al.PaperBench: evaluating ai’s ability to replicate ai research.
arXiv preprint arXiv:2504.01848.
Cited by: [§1](https://arxiv.org/html/2603.21489v2#S1.p1.1 "1 Introduction ‣ Effective Strategies for Asynchronous Software Engineering Agents"),
[§1](https://arxiv.org/html/2603.21489v2#S1.p5.1 "1 Introduction ‣ Effective Strategies for Asynchronous Software Engineering Agents"),
[§3.1](https://arxiv.org/html/2603.21489v2#S3.SS1.SSS0.Px2.p1.1 "PaperBench ‣ 3.1 Evaluation Benchmarks ‣ 3 Main Results ‣ Effective Strategies for Asynchronous Software Engineering Agents"),
[§3.5](https://arxiv.org/html/2603.21489v2#S3.SS5.p1.1 "3.5 Single Agents Fail to Utilize More Iterations ‣ 3 Main Results ‣ Effective Strategies for Asynchronous Software Engineering Agents"),
[§5.4](https://arxiv.org/html/2603.21489v2#S5.SS4.p1.1 "5.4 Software Engineering Evaluation Benchmarks ‣ 5 Related Work ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Tian et al. (2024)M. Tian, L. Gao, S. D. Zhang, X. Chen, C. Fan, X. Guo, R. Haas, P. Ji, K. Krongchon, Y. Li, et al.Scicode: a research coding benchmark curated by scientists.
Advances in Neural Information Processing Systems37, pp. 30624–30650.
Cited by: [§5.4](https://arxiv.org/html/2603.21489v2#S5.SS4.p1.1 "5.4 Software Engineering Evaluation Benchmarks ‣ 5 Related Work ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Venkataramani et al. (2026)V. Venkataramani, H. Shi, Z. Ke, A. Xu, X. He, Y. Zhou, S. Yavuz, H. Wang, and S. JotyMAS-prove: understanding the process verification of multi-agent systems.
arXiv preprint arXiv:2602.03053.
Cited by: [§1](https://arxiv.org/html/2603.21489v2#S1.p2.1 "1 Introduction ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Wang et al. (2025a)Q. Wang, T. Wang, Z. Tang, Q. Li, N. Chen, J. Liang, and B. HeMegaAgent: a large-scale autonomous llm-based multi-agent system without predefined sops.
In Findings of the Association for Computational Linguistics: ACL 2025,
pp. 4998–5036.
Cited by: [§5.1](https://arxiv.org/html/2603.21489v2#S5.SS1.p1.1 "5.1 Multi-Agent Architectures ‣ 5 Related Work ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Wang et al. (2024)X. Wang, B. Li, Y. Song, F. F. Xu, X. Tang, M. Zhuge, J. Pan, Y. Song, B. Li, J. Singh, et al.Openhands: an open platform for ai software developers as generalist agents.
arXiv preprint arXiv:2407.16741.
Cited by: [§1](https://arxiv.org/html/2603.21489v2#S1.p1.1 "1 Introduction ‣ Effective Strategies for Asynchronous Software Engineering Agents"),
[§3.2](https://arxiv.org/html/2603.21489v2#S3.SS2.p1.1 "3.2 Experimental Setup ‣ 3 Main Results ‣ Effective Strategies for Asynchronous Software Engineering Agents"),
[§5.1](https://arxiv.org/html/2603.21489v2#S5.SS1.p1.1 "5.1 Multi-Agent Architectures ‣ 5 Related Work ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Wang et al. (2025b)X. Wang, S. Rosenberg, J. Michelini, C. Smith, H. Tran, E. Nyst, R. Malhotra, X. Zhou, V. Chen, R. Brennan, et al.The openhands software agent sdk: a composable and extensible foundation for production agents.
arXiv preprint arXiv:2511.03690.
Cited by: [§3.2](https://arxiv.org/html/2603.21489v2#S3.SS2.p1.1 "3.2 Experimental Setup ‣ 3 Main Results ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Wu et al. (2024)Q. Wu, G. Bansal, J. Zhang, Y. Wu, B. Li, E. Zhu, L. Jiang, X. Zhang, S. Zhang, J. Liu, et al.Autogen: enabling next-gen llm applications via multi-agent conversations.
In First conference on language modeling,
Cited by: [§5.2](https://arxiv.org/html/2603.21489v2#S5.SS2.p1.1 "5.2 Multi-Agent Coordination Challenges ‣ 5 Related Work ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Xu et al. (2025)I. Xu, G. Zeng, Z. He, C. Jin, A. Pareja, D. Gutfreund, C. Gan, and Z. HongBOAD: discovering hierarchical software engineering agents via bandit optimization.
arXiv preprint arXiv:2512.23631.
Cited by: [§5.2](https://arxiv.org/html/2603.21489v2#S5.SS2.p1.1 "5.2 Multi-Agent Coordination Challenges ‣ 5 Related Work ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Yang et al. (2024)J. Yang, C. E. Jimenez, A. Wettig, K. Lieret, S. Yao, K. Narasimhan, and O. PressSwe-agent: agent-computer interfaces enable automated software engineering.
Advances in Neural Information Processing Systems37, pp. 50528–50652.
Cited by: [§1](https://arxiv.org/html/2603.21489v2#S1.p1.1 "1 Introduction ‣ Effective Strategies for Asynchronous Software Engineering Agents"),
[§5.3](https://arxiv.org/html/2603.21489v2#S5.SS3.p1.1 "5.3 Software Engineering for Multi-Agent Coordination ‣ 5 Related Work ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Yang et al. (2023)J. Yang, A. Prabhakar, K. Narasimhan, and S. YaoIntercode: standardizing and benchmarking interactive coding with execution feedback.
Advances in Neural Information Processing Systems36, pp. 23826–23854.
Cited by: [§5.4](https://arxiv.org/html/2603.21489v2#S5.SS4.p1.1 "5.4 Software Engineering Evaluation Benchmarks ‣ 5 Related Work ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Yang et al. (2026)Y. Yang, C. Qu, M. Wen, L. Shi, Y. Wen, W. Zhang, A. Wierman, and S. GuUnderstanding agent scaling in llm-based multi-agent systems via diversity.
arXiv preprint arXiv:2602.03794.
Cited by: [§4.2](https://arxiv.org/html/2603.21489v2#S4.SS2.p1.1 "4.2 Choosing the Degree of Parallel Execution ‣ 4 Analysis ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Zeng et al. (2025)A. Zeng, X. Lv, Q. Zheng, Z. Hou, B. Chen, C. Xie, C. Wang, D. Yin, H. Zeng, J. Zhang, et al.Glm-4.5: agentic, reasoning, and coding (arc) foundation models.
arXiv preprint arXiv:2508.06471.
Cited by: [§3.2](https://arxiv.org/html/2603.21489v2#S3.SS2.p1.1 "3.2 Experimental Setup ‣ 3 Main Results ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Zhang et al. (2025a)G. Zhang, L. Niu, J. Fang, K. Wang, L. Bai, and X. WangMulti-agent architecture search via agentic supernet.
arXiv preprint arXiv:2502.04180.
Cited by: [§1](https://arxiv.org/html/2603.21489v2#S1.p2.1 "1 Introduction ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Zhang et al. (2025b)W. Zhang, L. Zeng, Y. Xiao, Y. Li, Y. Zhao, C. Cui, Y. Liu, and B. AnAgentOrchestra: orchestrating hierarchical multi-agent intelligence with the tool-environment-agent (tea) protocol.
Cited by: [§5.1](https://arxiv.org/html/2603.21489v2#S5.SS1.p1.1 "5.1 Multi-Agent Architectures ‣ 5 Related Work ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Zhang et al. (2024)Y. Zhang, R. Sun, Y. Chen, T. Pfister, R. Zhang, and S. ArikChain of agents: large language models collaborating on long-context tasks.
Advances in Neural Information Processing Systems37, pp. 132208–132237.
Cited by: [§5.1](https://arxiv.org/html/2603.21489v2#S5.SS1.p1.1 "5.1 Multi-Agent Architectures ‣ 5 Related Work ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Zhao et al. (2024)W. Zhao, N. Jiang, C. Lee, J. T. Chiu, C. Cardie, M. Gallé, and A. M. RushCommit0: library generation from scratch.
arXiv preprint arXiv:2412.01769.
Cited by: [§1](https://arxiv.org/html/2603.21489v2#S1.p1.1 "1 Introduction ‣ Effective Strategies for Asynchronous Software Engineering Agents"),
[§1](https://arxiv.org/html/2603.21489v2#S1.p5.1 "1 Introduction ‣ Effective Strategies for Asynchronous Software Engineering Agents"),
[§3.1](https://arxiv.org/html/2603.21489v2#S3.SS1.SSS0.Px1.p1.1 "Commit0 ‣ 3.1 Evaluation Benchmarks ‣ 3 Main Results ‣ Effective Strategies for Asynchronous Software Engineering Agents"),
[§5.4](https://arxiv.org/html/2603.21489v2#S5.SS4.p1.1 "5.4 Software Engineering Evaluation Benchmarks ‣ 5 Related Work ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Zhou et al. (2025)H. Zhou, X. Wan, R. Sun, H. Palangi, S. Iqbal, I. Vulić, A. Korhonen, and S. Ö. ArıkMulti-agent design: optimizing agents with better prompts and topologies.
arXiv preprint arXiv:2502.02533.
Cited by: [§5.1](https://arxiv.org/html/2603.21489v2#S5.SS1.p1.1 "5.1 Multi-Agent Architectures ‣ 5 Related Work ‣ Effective Strategies for Asynchronous Software Engineering Agents").

- Zhuge et al. (2024)M. Zhuge, C. Zhao, D. Ashley, W. Wang, D. Khizbullin, Y. Xiong, Z. Liu, E. Chang, R. Krishnamoorthi, Y. Tian, et al.Agent-as-a-judge: evaluate agents with agents.
arXiv preprint arXiv:2410.10934.
Cited by: [§5.1](https://arxiv.org/html/2603.21489v2#S5.SS1.p2.1 "5.1 Multi-Agent Architectures ‣ 5 Related Work ‣ Effective Strategies for Asynchronous Software Engineering Agents").


## Appendix A Prompt Engineering for Multi-Agent Task Delegation

We provide the user instruction and task delegation prompts for both Commit0 in Section [A.1](https://arxiv.org/html/2603.21489v2#A1.SS1 "A.1 Commit0 Prompts ‣ Appendix A Prompt Engineering for Multi-Agent Task Delegation ‣ Effective Strategies for Asynchronous Software Engineering Agents") and PaperBench in [A.2](https://arxiv.org/html/2603.21489v2#A1.SS2 "A.2 PaperBench Prompts ‣ Appendix A Prompt Engineering for Multi-Agent Task Delegation ‣ Effective Strategies for Asynchronous Software Engineering Agents").

### A.1 Commit0 Prompts

[⬇](data:text/plain;base64,PHVwbG9hZGVkX2ZpbGVzPgovd29ya3NwYWNlL3t7IHdvcmtzcGFjZV9kaXJfbmFtZSB9fQo8L3VwbG9hZGVkX2ZpbGVzPgpJJ3ZlIHVwbG9hZGVkIGEgUHl0aG9uIGNvZGUgcmVwb3NpdG9yeSBpbiB0aGUgZGlyZWN0b3J5IHt7IHdvcmtzcGFjZV9kaXJfbmFtZSB9fS4KCkhlcmUgaXMgeW91ciB0YXNrOgogIFlvdSBhcmUgYSBzb2Z0d2FyZSBlbmdpbmVlcmluZyBtYW5hZ2VyIGFuZCBoYXZlIHttYXhfYWdlbnRzfSBlbmdpbmVlcnMgaW4geW91ciB0ZWFtLgogIFlvdXIgcmVzcG9uc2liaWxpdHkgaXMgdG8gbWF4aW1pemUgdGhlIHV0aWxpemF0aW9uIG9mIHRoZSBlbmdpbmVlcnMgYnkgZGVsZWdhdGluZwogIHRoZSBpbXBsZW1lbnRhdGlvbiB0YXNrcyAoaS5lLiwgdGhlIGZ1bmN0aW9ucyB3aXRoIGBwYXNzYCBzdGF0ZW1lbnRzKSB0byB0aGVzZQogIGVuZ2luZWVycyBhbmQgZ3VpZGUgdGhlbSB0byBlZmZpY2llbnRseSBhbmQgZWZmZWN0aXZlbHkgY29tcGxldGUgdGhlIGltcGxlbWVudGF0aW9uCiAgYW5kIHBhc3MgQUxMIHRoZSB1bml0IHRlc3RzLiBFeGNlcHQgZm9yIHRoZSBmdW5jdGlvbnMgd2l0aCBgcGFzc2Agc3RhdGVtZW50cywgdGhlCiAgcmVwb3NpdG9yeSBtaWdodCBhbHNvIGNvbnRhaW4gc29tZSBtaXNzaW5nIGZ1bmN0aW9ucyB0aGF0IGFyZSBub3QgZGVmaW5lZCBpbiBhbnkKICBmaWxlcy4gWW91IG5lZWQgdG8gYWRkIHRoZW0gd2l0aCBjbGVhciBkb2NzdHJpbmdzIGFuZCBgcGFzc2Agc3RhdGVtZW50cyBpbnRvIHRoZQogIGZpbGVzIGZvciB0aGUgZW5naW5lZXJzIHRvIGltcGxlbWVudC4gTWFrZSBzdXJlIHlvdSBzdWJtaXQgYSBsb2NhbCBjb21taXQgb2YKICB5b3VyIGNoYW5nZXMuIFJlbWVtYmVyIHlvdSBhcmUgTk9UIGFsbG93ZWQgdG8gZ2VuZXJhdGUgYW55IGNvZGUgZm9yIHRoZSBleGlzdGluZwogIGZ1bmN0aW9ucyBvciBjbGFzc2VzIHdpdGggYHBhc3NgIHN0YXRlbWVudHMuIFlvdSBjYW4gb25seSBhZGQgdW5kZWZpbmVkCiAgZnVuY3Rpb25zIGFzIG5lZWRlZC4KCiAgRE8gTk9UIGNoYW5nZSB0aGUgbmFtZXMgb2YgZXhpc3RpbmcgdmFyaWFibGVzLCBmdW5jdGlvbnMsIG9yIGNsYXNzZXMsIGFzIHRoZXkgbWF5CiAgYmUgcmVmZXJlbmNlZCBmcm9tIG90aGVyIGNvZGUgbGlrZSB1bml0IHRlc3RzLiBEbyBub3QgY29tbWVudCBvdXQgYW55IGV4aXN0aW5nIGNvZGUuCgogIFdoZW4gdGhlIGVuZ2luZWVycyBnZW5lcmF0ZSBjb2RlLCB5b3UgbmVlZCB0byBtYWtlIHN1cmUgdGhleSBtYWludGFpbiB0aGUgb3JpZ2luYWwKICBmb3JtYXR0aW5nIG9mIHRoZSBmdW5jdGlvbiBzdHVicyAoc3VjaCBhcyB3aGl0ZXNwYWNlcyksIG90aGVyd2lzZSB3ZSB3aWxsIG5vdCBiZQogIGFibGUgdG8gc2VhcmNoL3JlcGxhY2UgYmxvY2tzIGZvciBjb2RlIG1vZGlmaWNhdGlvbnMsIGFuZCB0aGVyZWZvcmUgeW91ciB0ZWFtIHdpbGwKICByZWNlaXZlIGEgc2NvcmUgb2YgMCBmb3IgdGhlIGdlbmVyYXRlZCBjb2RlLgoKSGVyZSBpcyB0aGUgY29tbWFuZCB0byBydW4gdGhlIHVuaXQgdGVzdHM6Cjx0ZXN0X2NvbW1hbmQ+Cnt0ZXN0X2NtZH0ge3Rlc3RfZGlyfQo8L3Rlc3RfY29tbWFuZD4KCkVhY2ggZW5naW5lZXIgaXMgZXhwZWN0ZWQgdG8gcHJvYWN0aXZlbHkgc3VibWl0IGEgbG9jYWwgZ2l0IGNvbW1pdCB0byB5b3Ugb25jZSB0aGVpcgphc3NpZ25lZCB0YXNrIGlzIGNvbXBsZXRlLiBUaGUgZW5naW5lZXJzIGFyZSByZXNwb25zaWJsZSBmb3IgdmVyaWZ5aW5nIHRoZWlyIG93bgppbXBsZW1lbnRhdGlvbiBxdWFsaXR5IGFuZCBydW5uaW5nIHRlc3RzIGJlZm9yZSBzdWJtaXR0aW5nLiBJZiBubyBjb21taXQgaXMgc3VibWl0dGVkLAp5b3Ugc2hvdWxkIGFzc3VtZSB0aGUgdGFzayBtYXkgYmUgcGFydGlhbGx5IGNvbXBsZXRlLiBJbiB0aGF0IGNhc2UsIG1hbnVhbGx5IGluc3BlY3QKdGhlIGVuZ2luZWVyJ3Mgd29ya3RyZWUsIGRldGVybWluZSB3aGljaCBwYXJ0cyBoYXZlIGFscmVhZHkgYmVlbiBpbXBsZW1lbnRlZCwgc3luYwphbmQgbWVyZ2UgdGhvc2UgY29tcGxldGVkIGFydGlmYWN0cyBpbnRvIHRoZSBtYWluIGRpcmVjdG9yeSwgYW5kIG1ha2UgYSBjb21taXQgb24KdGhlaXIgYmVoYWxmLgoKV2hlbiBhbiBlbmdpbmVlciBoYXMgY29tcGxldGVkIHRoZWlyIHRhc2sgd2l0aCBhIHN1Y2Nlc3NmdWwgY29tbWl0LCB5b3UgbmVlZCB0bwpkZWNpZGUgdGhlIG5leHQgdGFzayB0byBhc3NpZ24sIGZvbGxvd2luZyB0aGVzZSBzdGVwczoKICAxLiBCYXNlZCBvbiB0aGUgY3VycmVudCBwcm9ncmVzcywgYXNzaWduIHRoZSBoaWdoZXN0IHByaW9yaXR5IGZpbGUgdG8gdGhpcyBlbmdpbmVlci4KICAyLiBNYWtlIHN1cmUgdGhlIGFzc2lnbmVkIGZpbGVzIGRvIG5vdCBjb250YWluIG9yIGRlcGVuZCBvbiBhbnkgbWlzc2luZyAodW5kZWZpbmVkKSBmdW5jdGlvbnM7IGlmIHNvLCBhZGQgdGhlbSB3aXRoIGNsZWFyIGRvY3N0cmluZ3MgYW5kIGBwYXNzYCBzdGF0ZW1lbnRzIGludG8gdGhlIGZpbGVzIGFuZCBzdWJtaXQgYSBsb2NhbCBjb21taXQgb2YgeW91ciBjaGFuZ2VzLgogIDMuIEV4cGxhaW4gdGhlIG92ZXJhbGwgcHJvZ3Jlc3Mgb2YgdGhlIGltcGxlbWVudGF0aW9uIGFuZCBwcm92aWRlIGEgZGV0YWlsZWQgZXhwbGFuYXRpb24gb2YgdGhlIHB1cnBvc2Ugb2YgdGhlIGltcGxlbWVudGF0aW9uIHRvIGluc3RydWN0IHRoZSBlbmdpbmVlcgogICAgIHRvIGNvbXBsZXRlIHRoZSB0YXNrLgogIDQuIElmIG5vIG5ldyBpbXBsZW1lbnRhdGlvbiBpcyBuZWVkZWQgZm9yIG5vdyAoZS5nLiwgdGhlIGZpbGUgaXMgYWxyZWFkeSBpbXBsZW1lbnRlZCBvciBuZWVkcyB0byB3YWl0IGZvciBvdGhlciBlbmdpbmVlcnMgdG8gY29tcGxldGUgdGhlIGRlcGVuZGVuY2llcyksIHlvdSBjYW4gc2ltcGx5IHNheSAiVGhhbmsgeW91IGZvciB5b3VyIHdvcmsuIEkgd2lsbCBhc3NpZ24gYSBuZXcgdGFzayB0byB5b3UgbGF0ZXIuIgogIDUuIFlvdSBjYW4gYWxzbyBhc3NpZ24gdGFza3MgdG8gaWRsZSBvciBpbmFjdGl2ZSBlbmdpbmVlcnMgaWYgeW91IG5lZWQgbW9yZSBjYXBhY2l0eSB0byBiZXR0ZXIgdXRpbGl6ZSB0aGUgZW5naW5lZXJzLgoKRW5naW5lZXJzIGFyZSByZXNwb25zaWJsZSBmb3IgdmVyaWZ5aW5nIHRoZWlyIG93biBpbXBsZW1lbnRhdGlvbiBxdWFsaXR5IGJlZm9yZQpzdWJtaXR0aW5nIHRoZWlyIGNvbW1pdHM7IHlvdSBkbyBOT1QgbmVlZCB0byByZXZpZXcgdGhlaXIgY29kZSBxdWFsaXR5IG9yIHJ1biB0ZXN0cwp5b3Vyc2VsZi4gT25seSBmb2N1cyBvbiBkZWxlZ2F0aW5nIHRhc2tzIChpLmUuLCBtYXhpbWl6aW5nIHRoZSB1dGlsaXphdGlvbiBvZiB0aGUKZW5naW5lZXJzIHRvIHBhc3MgbW9yZSB1bml0IHRlc3RzKS4KCk1ha2Ugc3VyZSB5b3UgRE8gTk9UIGl0ZXJhdGl2ZWx5IG92ZXJjaGVjayBvciBmaXggbWlzc2luZyBmdW5jdGlvbnMuClByb3ZpZGUgYSBjbGVhciBhbmQgY29uY2lzZSByZXNwb25zZSBpbiB0aGUgSlNPTiBmb3JtYXQgYmVsb3cuClBsZWFzZSBzdHJ1Y3R1cmUgeW91ciByZXNwb25zZSBhcyBKU09OOgoKewogICJhc3NpZ25fdGFzayI6IHsKICAgICJyZWFzb25pbmciOiAiRXhwbGFpbiB5b3VyIGRlY2lzaW9uIiwKICAgICJhc3NpZ25tZW50cyI6IFsKICAgICAgewogICAgICAgICJlbmdpbmVlcl9pZCI6ICJlbmdpbmVlcl9pZCIsCiAgICAgICAgInRhc2tfaWQiOiAidGFzay11bmlxdWUtaWQgb3IgJ2ZpeC08b3JpZ2luYWwtdGFzay1pZD4nIiwKICAgICAgICAiZmlsZV9wYXRoIjogInBhdGgvdG8vZmlsZS5weSIsCiAgICAgICAgImZ1bmN0aW9uc190b19pbXBsZW1lbnQiOiBbImZ1bmMxIiwgImZ1bmMyIl0sCiAgICAgICAgImluc3RydWN0aW9uIjogIkRldGFpbGVkIGV4cGxhbmF0aW9uIG9mIHRoZSBwdXJwb3NlIG9mIHRoZSBpbXBsZW1lbnRhdGlvbi4iLAogICAgICAgICJjb21wbGV4aXR5IjogInNpbXBsZXxtZWRpdW18Y29tcGxleCIKICAgICAgfQogICAgXQogIH0KfQoKSWYgbm8gdGFza3Mgc2hvdWxkIGJlIGFzc2lnbmVkLCB1c2UgYW4gZW1wdHkgYXNzaWdubWVudHMgYXJyYXku)

<uploaded\_files>

/workspace/{{workspace\_dir\_name}}

</uploaded\_files>

I’veuploadedaPythoncoderepositoryinthedirectory{{workspace\_dir\_name}}.

Hereisyourtask:

Youareasoftwareengineeringmanagerandhave{max\_agents}engineersinyourteam.

Yourresponsibilityistomaximizetheutilizationoftheengineersbydelegating

theimplementationtasks(i.e.,thefunctionswith‘pass‘statements)tothese

engineersandguidethemtoefficientlyandeffectivelycompletetheimplementation

andpassALLtheunittests.Exceptforthefunctionswith‘pass‘statements,the

repositorymightalsocontainsomemissingfunctionsthatarenotdefinedinany

files.Youneedtoaddthemwithcleardocstringsand‘pass‘statementsintothe

filesfortheengineerstoimplement.Makesureyousubmitalocalcommitof

yourchanges.RememberyouareNOTallowedtogenerateanycodefortheexisting

functionsorclasseswith‘pass‘statements.Youcanonlyaddundefined

functionsasneeded.

DONOTchangethenamesofexistingvariables,functions,orclasses,astheymay

bereferencedfromothercodelikeunittests.Donotcommentoutanyexistingcode.

Whentheengineersgeneratecode,youneedtomakesuretheymaintaintheoriginal

formattingofthefunctionstubs(suchaswhitespaces),otherwisewewillnotbe

abletosearch/replaceblocksforcodemodifications,andthereforeyourteamwill

receiveascoreof0forthegeneratedcode.

Hereisthecommandtoruntheunittests:

<test\_command>

{test\_cmd}{test\_dir}

</test\_command>

Eachengineerisexpectedtoproactivelysubmitalocalgitcommittoyouoncetheir

assignedtaskiscomplete.Theengineersareresponsibleforverifyingtheirown

implementationqualityandrunningtestsbeforesubmitting.Ifnocommitissubmitted,

youshouldassumethetaskmaybepartiallycomplete.Inthatcase,manuallyinspect

theengineer’sworktree,determinewhichpartshavealreadybeenimplemented,sync

andmergethosecompletedartifactsintothemaindirectory,andmakeacommiton

theirbehalf.

Whenanengineerhascompletedtheirtaskwithasuccessfulcommit,youneedto

decidethenexttasktoassign,followingthesesteps:

1.Basedonthecurrentprogress,assignthehighestpriorityfiletothisengineer.

2.Makesuretheassignedfilesdonotcontainordependonanymissing(undefined)functions;ifso,addthemwithcleardocstringsand‘pass‘statementsintothefilesandsubmitalocalcommitofyourchanges.

3.Explaintheoverallprogressoftheimplementationandprovideadetailedexplanationofthepurposeoftheimplementationtoinstructtheengineer

tocompletethetask.

4.Ifnonewimplementationisneededfornow(e.g.,thefileisalreadyimplementedorneedstowaitforotherengineerstocompletethedependencies),youcansimplysay"Thankyouforyourwork.Iwillassignanewtasktoyoulater."

5.Youcanalsoassigntaskstoidleorinactiveengineersifyouneedmorecapacitytobetterutilizetheengineers.

Engineersareresponsibleforverifyingtheirownimplementationqualitybefore

submittingtheircommits;youdoNOTneedtoreviewtheircodequalityorruntests

yourself.Onlyfocusondelegatingtasks(i.e.,maximizingtheutilizationofthe

engineerstopassmoreunittests).

MakesureyouDONOTiterativelyovercheckorfixmissingfunctions.

ProvideaclearandconciseresponseintheJSONformatbelow.

PleasestructureyourresponseasJSON:

{

"assign\_task":{

"reasoning":"Explainyourdecision",

"assignments":\[\
\
{\
\
"engineer\_id":"engineer\_id",\
\
"task\_id":"task-unique-idor’fix-<original-task-id>’",\
\
"file\_path":"path/to/file.py",\
\
"functions\_to\_implement":\["func1","func2"\],\
\
"instruction":"Detailedexplanationofthepurposeoftheimplementation.",\
\
"complexity":"simple\|medium\|complex"\
\
}\
\
\]

}

}

Ifnotasksshouldbeassigned,useanemptyassignmentsarray.

[⬇](data:text/plain;base64,WW91ciBlbmdpbmVlcnMgYXJlIHdhaXRpbmcgZm9yIHlvdXIgaW5zdHJ1Y3Rpb25zIHRvIHN0YXJ0IHRoZWlyIGZpcnN0IGltcGxlbWVudGF0aW9uIHRhc2tzLiBOb3cgeW91IG5lZWQgdG86CgogIDEuIENoZWNrIGZvciB1bmNvbW1pdHRlZCBjaGFuZ2VzIGFuZCBjb21taXQgaWYgbmVlZGVkOgogICAgIGdpdCBzdGF0dXMKICAgICBnaXQgYWRkIC1BICYmIGdpdCBjb21taXQgLW0gIkFkZCBtaXNzaW5nIHN0dWJzIGZyb20gc2NhbiBwaGFzZSIgfHwgdHJ1ZQoKICAyLiBTdXNwZW5kIGV4cGxvcmF0aW9uIGFuZCBzeXN0ZW1hdGljYWxseSBkZWxlZ2F0ZSB0aGUgaW1wbGVtZW50YXRpb24gd29yawogICAgIGJ5IG91dHB1dHRpbmcgYSBkZWxlZ2F0aW9uIEpTT04gYmFzZWQgb24geW91ciBjdXJyZW50IHVuZGVyc3RhbmRpbmcKICAgICBvZiB0aGUgcmVwb3NpdG9yeSBzdHJ1Y3R1cmUgYW5kIGl0cyBkZXBlbmRlbmNpZXMuCiAgICAgWW91IGhhdmUgdXAgdG8ge21heF9hZ2VudHN9IGVuZ2luZWVycyBhdmFpbGFibGUuCgpTdWdnZXN0aW9ucyBmb3IgZWZmZWN0aXZlIGRlbGVnYXRpb24gaW4gdGhlIGZpcnN0IHJvdW5kOgoKICAtIEZpcnN0LCBkaXZpZGUgdGhlIG92ZXJhbGwgaW1wbGVtZW50YXRpb24gd29yayBpbnRvIHVwIHRvIHttYXhfYWdlbnRzfQogICAgbWFqb3IgdGFza3MsIGJhbGFuY2luZyBjb21wbGV4aXR5IGFuZCBlc3RpbWF0ZWQgZWZmb3J0IGFzIGV2ZW5seSBhcyBwb3NzaWJsZS4gS2VlcCBoaWdobHkgaW50ZXJkZXBlbmRlbnQgZmlsZXMgd2l0aGluIHRoZSBzYW1lIG1ham9yIHRhc2suIFByZWZlciBzcGxpdHRpbmcgYXQgdGhlIGZpbGUgbGV2ZWwuIElmIG9uZSBmaWxlIGNvbnRhaW5zIGEgZGlzcHJvcG9ydGlvbmF0ZWx5IGxhcmdlIG51bWJlciBvZiBmdW5jdGlvbnMgd2l0aCBwYXNzIHN0YXRlbWVudHMsIHlvdSBtYXkgc3BsaXQgYnkgZnVuY3Rpb24gYW5kIGFzc2lnbiBub24tb3ZlcmxhcHBpbmcgc2V0cyB0byBtdWx0aXBsZSBlbmdpbmVlcnMuCgogIC0gRm9yIGVhY2ggZW5naW5lZXIsIGFzc2lnbiB0aGUgaGlnaGVzdC1wcmlvcml0eSBmaWxlIHdpdGhpbiB0aGVpciBtYWpvciB0YXNrLiBJZiB0d28gZmlsZXMgYXJlIGNpcmN1bGFybHkgZGVwZW5kZW50LCBhc3NpZ24gdGhlbSB0byB0aGUgc2FtZSBlbmdpbmVlci4gRW5naW5lZXJzIGFyZSBnZW5lcmFsbHkgbW9yZSBjb21mb3J0YWJsZSBzdGFydGluZyBmcm9tIHNpbXBsZXIgdGFza3MgYmVmb3JlIG1vdmluZyB0byBtb3JlIGNvbXBsZXggb25lcy4KCiAgLSBFbmdpbmVlcnMgYXJlIG9ubHkgcmVzcG9uc2libGUgZm9yIGltcGxlbWVudGluZyBmdW5jdGlvbnMgd2l0aCBwYXNzCiAgICBzdGF0ZW1lbnRzLiBEbyBub3QgYXNzaWduIHRoZW0gdG8gaW1wbGVtZW50IG1pc3NpbmcgZnVuY3Rpb25zIHRoYXQgYXJlIG5vdCBkZWZpbmVkIGluIGFueSBmaWxlLiBJZiB5b3UgcHJldmlvdXNseSBhZGRlZCB1bmRlZmluZWQgZnVuY3Rpb25zIHdpdGggcGFzcyBzdGF0ZW1lbnRzLCBpbmNsdWRlIHRoZW0gaW4gdGhlIGFzc2lnbm1lbnQgaW5zdHJ1Y3Rpb25zLgoKICAtIEluIGVhY2ggYXNzaWdubWVudCwgYnJpZWZseSBzdW1tYXJpemUgdGhlIHJlbGV2YW50IHJlcG9zaXRvcnkgc3RydWN0dXJlIGFuZCBkZXBlbmRlbmNpZXMgc28gZW5naW5lZXJzIGRvIG5vdCBuZWVkIHRvIHJlLWV4cGxvcmUgdGhlIGNvZGViYXNlLiBDbGVhcmx5IHNwZWNpZnkgd2hpY2ggZmlsZSBhbmQgd2hpY2ggZnVuY3Rpb25zIHRvIGltcGxlbWVudC4gRXhwbGFpbiB0aGUgcHVycG9zZSBhbmQgZXhwZWN0ZWQgYmVoYXZpb3Igb2YgZWFjaCBmdW5jdGlvbi4gSWYgYXNzaWduZWQgZnVuY3Rpb25zIGRlcGVuZCBvbiBvdGhlciBzdHViIGZ1bmN0aW9ucyBub3QgYXNzaWduZWQgdG8gdGhlIHNhbWUgZW5naW5lZXIsIHByb3ZpZGUgYSBzaG9ydCBkZXNjcmlwdGlvbiBvZiB0aG9zZSBkZXBlbmRlbmNpZXMgdG8gYXZvaWQgY29uZnVzaW9uLgoKTm90ZTogRG8gTk9UIHByb3ZpZGUgYW55IGNvZGUgc25pcHBldHMgb3IgcHNldWRvLWNvZGUuCk91dHB1dCB5b3VyIGRlbGVnYXRpb24gcGxhbiBzdHJpY3RseSBpbiB0aGUgZm9sbG93aW5nIEpTT04gZm9ybWF0OgoKewogICJkZWxlZ2F0aW9uX3BsYW4iOiB7CiAgICAiZmlyc3Rfcm91bmQiOiB7CiAgICAgICJudW1fYWdlbnRzIjogPGludGVnZXIgKDEgdG8ge21heF9hZ2VudHN9KT4sCiAgICAgICJyZWFzb25pbmciOiAiRXhwbGFpbiB3aHkgdGhlc2UgZmlsZXMgYXJlIGFzc2lnbmVkIGZpcnN0IGFuZCB3aHkgdGhpcyBudW1iZXIgb2YgZW5naW5lZXJzIGlzIHVzZWQuIiwKICAgICAgInRhc2tzIjogWwogICAgICAgIHsKICAgICAgICAgICJlbmdpbmVlcl9pZCI6ICJlbmdpbmVlcl9pZCIsCiAgICAgICAgICAidGFza19pZCI6ICJ0YXNrLXVuaXF1ZS1pZCIsCiAgICAgICAgICAiZmlsZV9wYXRoIjogInBhdGgvdG8vZmlsZS5weSIsCiAgICAgICAgICAiZnVuY3Rpb25zX3RvX2ltcGxlbWVudCI6IFsiZnVuYzEiLCAiZnVuYzIiXSwKICAgICAgICAgICJjb21wbGV4aXR5IjogInNpbXBsZXxtZWRpdW18Y29tcGxleCIsCiAgICAgICAgICAiaW5zdHJ1Y3Rpb24iOiAiU3VtbWFyaXplIHRoZSByZXBvc2l0b3J5IHN0cnVjdHVyZSBhbmQgZGVwZW5kZW5jaWVzLiBUaGVuIHByb3ZpZGUgZGV0YWlsZWQgaW5zdHJ1Y3Rpb25zIGZvciB0aGUgaW1wbGVtZW50YXRpb24sIGluY2x1ZGluZyB0aGUgZXhwZWN0ZWQgYmVoYXZpb3Igb2YgdGhlIGFzc2lnbmVkIGZ1bmN0aW9ucyBhbmQgZGVzY3JpcHRpb25zIG9mIGFueSBkZXBlbmRlbnQgc3R1YiBmdW5jdGlvbnMuIgogICAgICAgIH0KICAgICAgXQogICAgfSwKICAgICJyZW1haW5pbmdfdGFza3MiOiBbCiAgICAgIHsKICAgICAgICAidGFza19pZCI6ICJ0YXNrLXVuaXF1ZS1pZCIsCiAgICAgICAgImZpbGVfcGF0aCI6ICJwYXRoL3RvL2ZpbGUucHkiLAogICAgICAgICJmdW5jdGlvbnNfdG9faW1wbGVtZW50IjogWyJmdW5jMSIsICJmdW5jMiJdLAogICAgICAgICJjb21wbGV4aXR5IjogInNpbXBsZXxtZWRpdW18Y29tcGxleCIsCiAgICAgICAgImRlcGVuZHNfb24iOiBbImZpbGVfcGF0aF8xIiwgImZpbGVfcGF0aF8yIl0KICAgICAgfQogICAgXQogIH0KfQ==)

Yourengineersarewaitingforyourinstructionstostarttheirfirstimplementationtasks.Nowyouneedto:

1.Checkforuncommittedchangesandcommitifneeded:

gitstatus

gitadd-A&&gitcommit-m"Addmissingstubsfromscanphase"\|\|true

2.Suspendexplorationandsystematicallydelegatetheimplementationwork

byoutputtingadelegationJSONbasedonyourcurrentunderstanding

oftherepositorystructureanditsdependencies.

Youhaveupto{max\_agents}engineersavailable.

Suggestionsforeffectivedelegationinthefirstround:

-First,dividetheoverallimplementationworkintoupto{max\_agents}

majortasks,balancingcomplexityandestimatedeffortasevenlyaspossible.Keephighlyinterdependentfileswithinthesamemajortask.Prefersplittingatthefilelevel.Ifonefilecontainsadisproportionatelylargenumberoffunctionswithpassstatements,youmaysplitbyfunctionandassignnon-overlappingsetstomultipleengineers.

-Foreachengineer,assignthehighest-priorityfilewithintheirmajortask.Iftwofilesarecircularlydependent,assignthemtothesameengineer.Engineersaregenerallymorecomfortablestartingfromsimplertasksbeforemovingtomorecomplexones.

-Engineersareonlyresponsibleforimplementingfunctionswithpass

statements.Donotassignthemtoimplementmissingfunctionsthatarenotdefinedinanyfile.Ifyoupreviouslyaddedundefinedfunctionswithpassstatements,includethemintheassignmentinstructions.

-Ineachassignment,brieflysummarizetherelevantrepositorystructureanddependenciessoengineersdonotneedtore-explorethecodebase.Clearlyspecifywhichfileandwhichfunctionstoimplement.Explainthepurposeandexpectedbehaviorofeachfunction.Ifassignedfunctionsdependonotherstubfunctionsnotassignedtothesameengineer,provideashortdescriptionofthosedependenciestoavoidconfusion.

Note:DoNOTprovideanycodesnippetsorpseudo-code.

OutputyourdelegationplanstrictlyinthefollowingJSONformat:

{

"delegation\_plan":{

"first\_round":{

"num\_agents":<integer(1to{max\_agents})>,

"reasoning":"Explainwhythesefilesareassignedfirstandwhythisnumberofengineersisused.",

"tasks":\[\
\
{\
\
"engineer\_id":"engineer\_id",\
\
"task\_id":"task-unique-id",\
\
"file\_path":"path/to/file.py",\
\
"functions\_to\_implement":\["func1","func2"\],\
\
"complexity":"simple\|medium\|complex",\
\
"instruction":"Summarizetherepositorystructureanddependencies.Thenprovidedetailedinstructionsfortheimplementation,includingtheexpectedbehavioroftheassignedfunctionsanddescriptionsofanydependentstubfunctions."\
\
}\
\
\]

},

"remaining\_tasks":\[\
\
{\
\
"task\_id":"task-unique-id",\
\
"file\_path":"path/to/file.py",\
\
"functions\_to\_implement":\["func1","func2"\],\
\
"complexity":"simple\|medium\|complex",\
\
"depends\_on":\["file\_path\_1","file\_path\_2"\]\
\
}\
\
\]

}

}

### A.2 PaperBench Prompts

[⬇](data:text/plain;base64,WW91IGFyZSB0YXNrZWQgd2l0aCByZXByb2R1Y2luZyBhIHJlc2VhcmNoIHBhcGVyLgoKWW91IGhhdmUgYmVlbiBwcm92aWRlZCB3aXRoIGEgcmVzZWFyY2ggcGFwZXIgbG9jYXRlZCBhdCBgL3dvcmtzcGFjZS9wYXBlcmAuIFRoZSBkaXJlY3RvcnkgY29udGFpbnMgdGhlIHBhcGVyIGluIGJvdGggUERGIGFuZCBtYXJrZG93biBmb3JtYXQuCgpIZXJlIGlzIHlvdXIgdGFzazoKWW91IGFyZSBhIHNvZnR3YXJlIGVuZ2luZWVyaW5nIG1hbmFnZXIgZm9yIGEgcmVzZWFyY2ggdGVhbSBhbmQgaGF2ZSB7bWF4X2FnZW50c30gZW5naW5lZXJzIGluIHlvdXIgdGVhbS4gRWFjaCBlbmdpbmVlciBoYXMgYSB0b3RhbCBvZiB7bWF4X3JvdW5kc30gcm91bmRzIHRvIGNvbXBsZXRlIHRoZWlyIGFzc2lnbmVkIHRhc2tzLiBZb3VyIHJlc3BvbnNpYmlsaXR5IGlzIHRvIGRlbGVnYXRlIHRoZSByZXByb2R1Y3Rpb24gdGFza3MgdG8gdGhlc2UgZW5naW5lZXJzIGFuZCBndWlkZSB0aGVtIHRvIGVmZmljaWVudGx5IHJlcGxpY2F0ZSBhcyBtYW55IG9mIHRoZSBjb3JlIGNvbnRyaWJ1dGlvbnMgYW5kIHJlc3VsdHMgb2YgdGhpcyBwYXBlciBhcyBwb3NzaWJsZS4gWW91ciB0ZWFtIG1heSBub3QgYmUgYWJsZSB0byBjb21wbGV0ZSBldmVyeXRoaW5nIHdpdGhpbiB0aGUgYWxsb3R0ZWQgdGltZTsgeW91IHNob3VsZCBwcmlvcml0aXplIHRhc2tzIGluIG9yZGVyIHRvIGFjY29tcGxpc2ggYXMgbXVjaCBhcyBwb3NzaWJsZSB3aXRoaW4gbGltaXRlZCB0aW1lLiBZb3UgbWF5IHByZXBhcmUgdGhlIGVudmlyb25tZW50IGZvciB0aGUgcmVwcm9kdWN0aW9uLCBidXQgeW91IGFyZSBOT1QgYWxsb3dlZCB0byBnZW5lcmF0ZSBhbnkgY29kZSBmb3IgdGhlIHJlcHJvZHVjdGlvbi4gWW91IG1heSBvbmx5IGRlbGVnYXRlIHJlcHJvZHVjdGlvbiB0YXNrcyB0byB5b3VyIGVuZ2luZWVycy4gRG8gTk9UIGNyZWF0ZSBjb2RlIHNjYWZmb2xkcywgc2tlbGV0b24gZmlsZXMsIG9yIG1hcmtkb3duIGZpbGVzIC0tIHlvdXIgZW5naW5lZXJzIHdpbGwgY3JlYXRlIHRoZWlyIG93biBpbXBsZW1lbnRhdGlvbiBmaWxlcy4KCkRvIG5vdCB3b3JyeSBpZiB5b3VyIHRlYW0gZmFpbHMgdG8gY29tcGxldGVseSByZXByb2R1Y2UgY2VydGFpbiBwYXJ0cyBvZiB0aGUgcGFwZXIuIFBhcnRpYWwgY3JlZGl0IHdpbGwgYmUgYXNzaWduZWQuIElmIGEgc3BlY2lmaWMgcGFydCBvZiB0aGUgcmVwcm9kdWN0aW9uIGlzIGluY29ycmVjdCwgb25seSB0aGF0IHBhcnQgd2lsbCBmYWlsIHRvIHJlY2VpdmUgY3JlZGl0LCB3aGlsZSBjb3JyZWN0bHkgaW1wbGVtZW50ZWQgcGFydHMgd2lsbCBiZSBtYXJrZWQgYXMgc3VjY2Vzc2Z1bC4gVGhlIHBhcnRpYWwgY3JlZGl0IHdpbGwgYmUgd2VpZ2h0ZWQgYnkgaW1wb3J0YW5jZSB0byB0aGUgcGFwZXIncyBtYWluIGNvbnRyaWJ1dGlvbnMgYW5kIHJlc3VsdHMuIFVzZSB5b3VyIGp1ZGdtZW50IHRvIGRldGVybWluZSB3aGljaCBwYXJ0cyBvZiB0aGUgcGFwZXIgYXJlIG1vcmUgaW1wb3J0YW50IHRvIHJlcHJvZHVjZS4gV2Ugd2lsbCBjaGVjayB0aGF0IHlvdXIgcmVzdWx0cyBtYXRjaCB0aGUgZ2VuZXJhbCB0cmVuZHMgb2YgdGhlIG9yaWdpbmFsIHBhcGVyIHdpdGhpbiBhIHJlYXNvbmFibGUgbWFyZ2luIG9mIGVycm9yLgoKRXhwZXJpbWVudHMgaW50cm9kdWNlZCBvbmx5IGluIHRoZSBBcHBlbmRpeCBhcmUgbm90IGNvbnNpZGVyZWQgY29yZSBjb250cmlidXRpb25zIGFuZCBhcmUgb3V0IG9mIHNjb3BlLCBldmVuIGlmIHJlZmVyZW5jZWQgaW4gdGhlIG1haW4gdGV4dC4gSG93ZXZlciwgaWYgYW4gZXhwZXJpbWVudCBpcyBkZXNjcmliZWQgaW4gdGhlIG1haW4gYm9keSBidXQgc29tZSBpbXBsZW1lbnRhdGlvbiBkZXRhaWxzIChlLmcuLCBwcm9tcHRzIG9yIGxvbmcgbWF0aGVtYXRpY2FsIGV4cHJlc3Npb25zKSBhcmUgcGxhY2VkIGluIHRoZSBBcHBlbmRpeCwgdGhhdCBleHBlcmltZW50IGlzIHN0aWxsIGluIHNjb3BlLgoKUkVTT1VSQ0VTCi0tLQpZb3UgbWF5IGJlIHByb3ZpZGVkIHdpdGggYSBydWJyaWMgZmlsZSBsb2NhdGVkIGF0IGAvd29ya3NwYWNlL3BhcGVyL3J1YnJpYy5qc29uYC4gVGhlIHJ1YnJpYyBoYXMgYSBoaWVyYXJjaGljYWwgdHJlZSBzdHJ1Y3R1cmUgdGhhdCBicmVha3MgZG93biB0aGUgcGFwZXIgaW50byBmaW5lLWdyYWluZWQgdGFza3MuIFlvdSBtYXkgcmVjZWl2ZSBvbmx5IGEgc3Vic2V0IG9mIHRoZSBmdWxsIGhpZXJhcmNoeSwgb3IgYSBzaW5nbGUgcm9vdC1sZXZlbCB0YXNrLiBJbiB0aGF0IGNhc2UsIHVzZSB5b3VyIGp1ZGdtZW50IHRvIGRlY29tcG9zZSB0aGUgcmVwcm9kdWN0aW9uIGludG8gYXBwcm9wcmlhdGUgc3ViLXRhc2tzIGFuZCBhc3NpZ24gdGhlbSB0byB5b3VyIGVuZ2luZWVycy4gRG8gTk9UIGRlbGVnYXRlIGRpcmVjdGx5IGF0IHJ1YnJpYyBub2RlIGxldmVsOyB0aGUgcnVicmljIGlzIG9ubHkgYSByZWZlcmVuY2UgZm9yIGV4cGVjdGVkIG91dGNvbWVzLgoKQW4gYWRkZW5kdW0gZmlsZSBtYXkgYWxzbyBiZSBhdmFpbGFibGUgYXQgYC93b3Jrc3BhY2UvcGFwZXIvYWRkZW5kdW0ubWRgLCBwcm92aWRpbmcgYWRkaXRpb25hbCBjb250ZXh0IG9yIGNsYXJpZmljYXRpb25zIHJlZ2FyZGluZyBzY29wZS4KCllvdXIgdGVhbSBtYXkgYnJvd3NlIGFuZCB1c2UgcHVibGljbHkgYXZhaWxhYmxlIHJlc291cmNlcyBvbmxpbmUuIEhvd2V2ZXIsIHlvdXIgdGVhbSBtdXN0IE5PVCBhY2Nlc3MgdGhlIG9yaWdpbmFsIHBhcGVyJ3MgY29kZWJhc2Ugb3IgYW55IHJlc291cmNlcyBsaXN0ZWQgaW4gYGJsYWNrbGlzdC50eHRgLgoKU1VCTUlTU0lPTgotLS0KWW91ciB0ZWFtIG11c3QgcHJvZHVjZSBhIGdpdCByZXBvc2l0b3J5IGxvY2F0ZWQgYXQgYC93b3Jrc3BhY2Uvc3VibWlzc2lvbi9gLiBPbmx5IHNvdXJjZSBjb2RlIGFuZCBuZWNlc3Nhcnkgc2NyaXB0cyBzaG91bGQgYmUgY29tbWl0dGVkOyB0aGUgdG90YWwgY29tbWl0dGVkIHNpemUgbXVzdCBub3QgZXhjZWVkIDFHQi4gV2Ugd2lsbCBydW4gYGdpdCBjbGVhbiAtZmRgIGJlZm9yZSBncmFkaW5nLCBzbyBhbnkgdW50cmFja2VkIGZpbGVzIHdpbGwgYmUgcmVtb3ZlZC4KClRoZSBzdWJtaXNzaW9uIE1VU1QgaW5jbHVkZSBhIHJlcHJvZHVjdGlvbiBzY3JpcHQgYXQ6CiAgL3dvcmtzcGFjZS9zdWJtaXNzaW9uL3JlcHJvZHVjZS5zaAoKV2Ugd2lsbCBjb3B5IHlvdXIgc3VibWlzc2lvbiBpbnRvIGEgZnJlc2ggVWJ1bnR1IDI0LjA0IExUUyBEb2NrZXIgY29udGFpbmVyIGFuZCBydW46CiAgYmFzaCByZXByb2R1Y2Uuc2gKClRoZSBtYXhpbXVtIHJ1bnRpbWUgaXMgNyBkYXlzLiBEbyBub3QgcmVseSBvbiBoYXJkY29kZWQgYWJzb2x1dGUgcGF0aHMuIFRoZSBjb250YWluZXIgd2lsbCBpbmNsdWRlIGFuIE5WSURJQSBBMTAgR1BVIHdpdGggdGhlIE5WSURJQSBjb250YWluZXIgdG9vbGtpdCBpbnN0YWxsZWQuCgpBbGwgZ3JhZGVkIGFydGlmYWN0cyBtdXN0IGJlIGdlbmVyYXRlZCBieSB0aGUgcmVwcm9kdWN0aW9uIHNjcmlwdC4KCllvdSBzaG91bGQgcmVndWxhcmx5IHVwZGF0ZSBhbmQgdGVzdCB5b3VyIHJlcHJvZHVjdGlvbiBzY3JpcHQgdGhyb3VnaG91dCBkZXZlbG9wbWVudC4KCkZpbmFsbHksIGluY2x1ZGUgYSBSRUFETUUubWQgZmlsZSBhZnRlciBhbGwgcmVwcm9kdWN0aW9uIHRhc2tzIGFyZSBjb21wbGV0ZWQgKG9yIHdoZW4gZW5naW5lZXJzIHJlYWNoIHRoZWlyIG1heGltdW0gcm91bmRzKS4gVGhlIFJFQURNRSBzaG91bGQgc3VtbWFyaXplIGFjaGlldmVkIHJlc3VsdHMsIGV4cGxhaW4gdGhlIHJlcG9zaXRvcnkgc3RydWN0dXJlLCBhbmQgZGVzY3JpYmUgZXhwZWN0ZWQgb3V0cHV0cyBmcm9tIHJ1bm5pbmcgcmVwcm9kdWNlLnNoLgoKRU5HSU5FRVIgU1VCTUlTU0lPTlMKLS0tCkVhY2ggZW5naW5lZXIgbXVzdCBzdWJtaXQgYSBsb2NhbCBnaXQgY29tbWl0IHVwb24gY29tcGxldGluZyB0aGVpciBhc3NpZ25lZCB0YXNrLiBJZiBubyBjb21taXQgaXMgc3VibWl0dGVkLCBhc3N1bWUgcGFydGlhbCBjb21wbGV0aW9uLgoKQWZ0ZXIgcmV2aWV3aW5nIGEgc3VibWlzc2lvbjoKICAxLiBWZXJpZnkgd2hldGhlciB0aGUgZXhwZWN0ZWQgb3V0cHV0cyBhcmUgcHJvZHVjZWQuCiAgMi4gSWYgaW5jb21wbGV0ZSwgcmVhc3NpZ24gdGhlIHNhbWUgdGFzayB3aXRoIGNvcnJlY3RpdmUgZ3VpZGFuY2UuCiAgMy4gSWYgY29tcGxldGUsIGFzc2lnbiB0aGUgbmV4dCBoaWdoZXN0LXByaW9yaXR5IHJlbWFpbmluZyB0YXNrLgogIDQuIFlvdSBtYXkgYXNzaWduIHRhc2tzIHRvIGlkbGUgZW5naW5lZXJzIHRvIG1heGltaXplIHByb2R1Y3Rpdml0eS4KICA1LiBBbHdheXMgc3VtbWFyaXplIG92ZXJhbGwgcHJvZ3Jlc3MgYW5kIHByb3ZpZGUgZGV0YWlsZWQgaW5zdHJ1Y3Rpb25zIGZvciB0aGUgbmV4dCB0YXNrLgogIDYuIElmIG9uYm9hcmRpbmcgYSBuZXcgZW5naW5lZXIsIHByb3ZpZGUgYSBkZXRhaWxlZCBleHBsYW5hdGlvbiBvZiB0aGUgcGFwZXIgYW5kIGN1cnJlbnQgcmVwcm9kdWN0aW9uIGdvYWxzLgoKT3V0cHV0IHlvdXIgcmVzcG9uc2Ugc3RyaWN0bHkgaW4gdGhlIGZvbGxvd2luZyBKU09OIGZvcm1hdDoKCnsKICAiYXNzaWduX3Rhc2siOiB7CiAgICAicmVhc29uaW5nIjogIkV4cGxhaW4geW91ciBkZWNpc2lvbiIsCiAgICAidGFza3MiOiBbCiAgICAgIHsKICAgICAgICAiZW5naW5lZXJfaWQiOiAiZW5naW5lZXJfaWQiLAogICAgICAgICJ0YXNrX2lkIjogInRhc2stdW5pcXVlLWlkIiwKICAgICAgICAidGFza19ub2RlX2lkIjogInJ1YnJpYyB0YXNrIG5vZGUgaWQgaWYgYXZhaWxhYmxlIiwKICAgICAgICAicmVxdWlyZW1lbnRzIjogIlNwZWNpZmljIHJlcXVpcmVtZW50IHRvIGltcGxlbWVudCIsCiAgICAgICAgInRhc2tfY2F0ZWdvcnkiOiAiQ29kZSBEZXZlbG9wbWVudHxFeHBlcmltZW50IFJ1bm5pbmd8UmVzdWx0cyBBbmFseXNpc3xPdGhlciIsCiAgICAgICAgImVzdGltYXRlZF9jb21wbGV4aXR5IjogInNpbXBsZXxtZWRpdW18Y29tcGxleCIsCiAgICAgICAgImluc3RydWN0aW9uIjogIlByb3ZpZGUgZGV0YWlsZWQgZXhwbGFuYXRpb24gb2YgY3VycmVudCBwcm9ncmVzcyBhbmQgZGV0YWlsZWQgaW5zdHJ1Y3Rpb25zIGZvciB0aGlzIHRhc2ssIGluY2x1ZGluZyBleHBlY3RlZCBiZWhhdmlvciBhbmQgb3V0cHV0cywgcmVsZXZhbnQgcGFwZXIgZGV0YWlscywgYW5kIHJlcXVpcmVkIGRlcGVuZGVuY2llcy4iCiAgICAgIH0KICAgIF0KICB9Cn0KCklmIG5vIHRhc2tzIHNob3VsZCBiZSBhc3NpZ25lZCwgdXNlIGFuIGVtcHR5IHRhc2tzIGFycmF5Lg==)

Youaretaskedwithreproducingaresearchpaper.

Youhavebeenprovidedwitharesearchpaperlocatedat‘/workspace/paper‘.ThedirectorycontainsthepaperinbothPDFandmarkdownformat.

Hereisyourtask:

Youareasoftwareengineeringmanagerforaresearchteamandhave{max\_agents}engineersinyourteam.Eachengineerhasatotalof{max\_rounds}roundstocompletetheirassignedtasks.Yourresponsibilityistodelegatethereproductiontaskstotheseengineersandguidethemtoefficientlyreplicateasmanyofthecorecontributionsandresultsofthispaperaspossible.Yourteammaynotbeabletocompleteeverythingwithintheallottedtime;youshouldprioritizetasksinordertoaccomplishasmuchaspossiblewithinlimitedtime.Youmaypreparetheenvironmentforthereproduction,butyouareNOTallowedtogenerateanycodeforthereproduction.Youmayonlydelegatereproductiontaskstoyourengineers.DoNOTcreatecodescaffolds,skeletonfiles,ormarkdownfiles--yourengineerswillcreatetheirownimplementationfiles.

Donotworryifyourteamfailstocompletelyreproducecertainpartsofthepaper.Partialcreditwillbeassigned.Ifaspecificpartofthereproductionisincorrect,onlythatpartwillfailtoreceivecredit,whilecorrectlyimplementedpartswillbemarkedassuccessful.Thepartialcreditwillbeweightedbyimportancetothepaper’smaincontributionsandresults.Useyourjudgmenttodeterminewhichpartsofthepaperaremoreimportanttoreproduce.Wewillcheckthatyourresultsmatchthegeneraltrendsoftheoriginalpaperwithinareasonablemarginoferror.

ExperimentsintroducedonlyintheAppendixarenotconsideredcorecontributionsandareoutofscope,evenifreferencedinthemaintext.However,ifanexperimentisdescribedinthemainbodybutsomeimplementationdetails(e.g.,promptsorlongmathematicalexpressions)areplacedintheAppendix,thatexperimentisstillinscope.

RESOURCES

\-\-\-

Youmaybeprovidedwitharubricfilelocatedat‘/workspace/paper/rubric.json‘.Therubrichasahierarchicaltreestructurethatbreaksdownthepaperintofine-grainedtasks.Youmayreceiveonlyasubsetofthefullhierarchy,orasingleroot-leveltask.Inthatcase,useyourjudgmenttodecomposethereproductionintoappropriatesub-tasksandassignthemtoyourengineers.DoNOTdelegatedirectlyatrubricnodelevel;therubricisonlyareferenceforexpectedoutcomes.

Anaddendumfilemayalsobeavailableat‘/workspace/paper/addendum.md‘,providingadditionalcontextorclarificationsregardingscope.

Yourteammaybrowseandusepubliclyavailableresourcesonline.However,yourteammustNOTaccesstheoriginalpaper’scodebaseoranyresourceslistedin‘blacklist.txt‘.

SUBMISSION

\-\-\-

Yourteammustproduceagitrepositorylocatedat‘/workspace/submission/‘.Onlysourcecodeandnecessaryscriptsshouldbecommitted;thetotalcommittedsizemustnotexceed1GB.Wewillrun‘gitclean-fd‘beforegrading,soanyuntrackedfileswillberemoved.

ThesubmissionMUSTincludeareproductionscriptat:

/workspace/submission/reproduce.sh

WewillcopyyoursubmissionintoafreshUbuntu24.04LTSDockercontainerandrun:

bashreproduce.sh

Themaximumruntimeis7days.Donotrelyonhardcodedabsolutepaths.ThecontainerwillincludeanNVIDIAA10GPUwiththeNVIDIAcontainertoolkitinstalled.

Allgradedartifactsmustbegeneratedbythereproductionscript.

Youshouldregularlyupdateandtestyourreproductionscriptthroughoutdevelopment.

Finally,includeaREADME.mdfileafterallreproductiontasksarecompleted(orwhenengineersreachtheirmaximumrounds).TheREADMEshouldsummarizeachievedresults,explaintherepositorystructure,anddescribeexpectedoutputsfromrunningreproduce.sh.

ENGINEERSUBMISSIONS

\-\-\-

Eachengineermustsubmitalocalgitcommituponcompletingtheirassignedtask.Ifnocommitissubmitted,assumepartialcompletion.

Afterreviewingasubmission:

1.Verifywhethertheexpectedoutputsareproduced.

2.Ifincomplete,reassignthesametaskwithcorrectiveguidance.

3.Ifcomplete,assignthenexthighest-priorityremainingtask.

4.Youmayassigntaskstoidleengineerstomaximizeproductivity.

5.Alwayssummarizeoverallprogressandprovidedetailedinstructionsforthenexttask.

6.Ifonboardinganewengineer,provideadetailedexplanationofthepaperandcurrentreproductiongoals.

OutputyourresponsestrictlyinthefollowingJSONformat:

{

"assign\_task":{

"reasoning":"Explainyourdecision",

"tasks":\[\
\
{\
\
"engineer\_id":"engineer\_id",\
\
"task\_id":"task-unique-id",\
\
"task\_node\_id":"rubrictasknodeidifavailable",\
\
"requirements":"Specificrequirementtoimplement",\
\
"task\_category":"CodeDevelopment\|ExperimentRunning\|ResultsAnalysis\|Other",\
\
"estimated\_complexity":"simple\|medium\|complex",\
\
"instruction":"Providedetailedexplanationofcurrentprogressanddetailedinstructionsforthistask,includingexpectedbehaviorandoutputs,relevantpaperdetails,andrequireddependencies."\
\
}\
\
\]

}

}

Ifnotasksshouldbeassigned,useanemptytasksarray.

[⬇](data:text/plain;base64,VGhlIGVuZ2luZWVycyBvbiB5b3VyIHRlYW0gYXJlIHdhaXRpbmcgZm9yIGluc3RydWN0aW9ucyB0byBiZWdpbiB0aGVpciBmaXJzdCByZXByb2R1Y3Rpb24gdGFza3MuIFlvdSBtdXN0IG5vdyBkZWxlZ2F0ZSB0aGUgcmVwcm9kdWN0aW9uIHdvcmsgc3lzdGVtYXRpY2FsbHkgYnkgb3V0cHV0dGluZyBhIGRlbGVnYXRpb24gSlNPTiBiYXNlZCBvbiB5b3VyIGN1cnJlbnQgdW5kZXJzdGFuZGluZyBvZiB0aGUgcGFwZXIuIFlvdSBoYXZlIHVwIHRvIHttYXhfYWdlbnRzfSBlbmdpbmVlcnMgYXZhaWxhYmxlLgoKU3RyYXRlZ2llcyBmb3IgZWZmZWN0aXZlIGZpcnN0LXJvdW5kIGRlbGVnYXRpb246CgotIEZpcnN0LCBkaXZpZGUgdGhlIG92ZXJhbGwgcmVwcm9kdWN0aW9uIGVmZm9ydCBpbnRvIHVwIHRvIHttYXhfYWdlbnRzfSBtYWpvciB0YXNrIGdyb3VwcyBiYXNlZCBvbiB5b3VyIHVuZGVyc3RhbmRpbmcgb2YgdGhlIHBhcGVyLiBCYWxhbmNlIGNvbXBsZXhpdHkgYW5kIGVzdGltYXRlZCBlZmZvcnQgYXMgZXZlbmx5IGFzIHBvc3NpYmxlLiBHcm91cCByZWxhdGVkIHRhc2tzIHRvZ2V0aGVyIGFuZCBjYXJlZnVsbHkgY29uc2lkZXIgZGVwZW5kZW5jaWVzIGJldHdlZW4gdGFza3MgKGkuZS4sIHdoaWNoIGNvbXBvbmVudHMgZGVwZW5kIG9uIG90aGVycykuIERvIE5PVCBkZWxlZ2F0ZSBkaXJlY3RseSBhdCB0aGUgcnVicmljIG5vZGUgbGV2ZWw7IHRoZSBydWJyaWMgKGlmIHByb3ZpZGVkKSBpcyBvbmx5IGEgcmVmZXJlbmNlIGZvciBleHBlY3RlZCBvdXRjb21lcy4gUmVtZW1iZXIgdGhhdCByZXByb2R1Y3Rpb24gaW5jbHVkZXMgbm90IG9ubHkgaW1wbGVtZW50YXRpb24gYnV0IGFsc28gZXhwZXJpbWVudCBleGVjdXRpb24gbmVlZGVkIHRvIGdlbmVyYXRlIGV4cGVjdGVkIG91dHB1dHMuIFdoZW4gZm9ybWluZyB0YXNrIGdyb3VwcywgY29uc2lkZXIgaG93IGV4cGVyaW1lbnQgb3JjaGVzdHJhdGlvbiB3aWxsIGJlIHN0cnVjdHVyZWQuCgotIEZvciBlYWNoIGVuZ2luZWVyLCBhc3NpZ24gdGhlIGhpZ2hlc3QtcHJpb3JpdHkgcmVwcm9kdWN0aW9uIHRhc2sgd2l0aGluIHRoZWlyIHRhc2sgZ3JvdXAgKGkuZS4sIHRoZSB0YXNrIHRoYXQgcmVwcm9kdWNlcyB0aGUgbW9zdCBpbXBvcnRhbnQgcmVzdWx0cykuCgotIFNpbmNlIHRoaXMgaXMgdGhlIGZpcnN0IGFzc2lnbm1lbnQgcm91bmQsIHByb3ZpZGUgZW5naW5lZXJzIHdpdGggYSBjbGVhciBleHBsYW5hdGlvbiBvZiB0aGUgb3ZlcmFsbCBzdHJ1Y3R1cmUgb2YgdGhlIHBhcGVyIGFuZCBhIGRldGFpbGVkIHN1bW1hcnkgb2YgdGhlIHBhcGVyIGJhc2VkIG9uIHlvdXIgZXhwbG9yYXRpb24uIFRoaXMgZW5zdXJlcyB0aGV5IGRvIG5vdCBuZWVkIHRvIHJlLWV4cGxvcmUgdGhlIHBhcGVyIGluZGVwZW5kZW50bHkuCgotIFByb3ZpZGUgZGV0YWlsZWQgaW5zdHJ1Y3Rpb25zIGZvciBlYWNoIGFzc2lnbmVkIHRhc2suIENsZWFybHkgc3BlY2lmeSB3aGljaCBwYXJ0IG9mIHRoZSBwYXBlciBpcyBiZWluZyByZXByb2R1Y2VkIGFuZCB3aGF0IG91dHB1dHMgYXJlIGV4cGVjdGVkLiBJbmNsdWRlIHJlbGV2YW50IGNvbnRleHQgZnJvbSB0aGUgcGFwZXIgYW5kIGFkZGVuZHVtLiBFeHBsaWNpdGx5IG1lbnRpb24gd2hpY2ggZGVwZW5kZW5jaWVzIGFyZSBhbHJlYWR5IGF2YWlsYWJsZSBhbmQgd2hpY2ggbXVzdCBiZSBpbnN0YWxsZWQuIEVuc3VyZSB0aGF0IGVhY2ggZW5naW5lZXIgY3JlYXRlcyBhbmQgbW9kaWZpZXMgb25seSB0aGVpciBvd24gZmlsZXMuIERvIE5PVCBhc3NpZ24gbXVsdGlwbGUgZW5naW5lZXJzIHRvIG1vZGlmeSB0aGUgc2FtZSBmaWxlLCBhcyB0aGlzIHdpbGwgY2F1c2UgbWVyZ2UgY29uZmxpY3RzLgoKLSBEbyBub3QgYXNzaWduIHRoZSByZXByb2R1Y2Uuc2ggc2NyaXB0IHRvIGFueSBlbmdpbmVlci4gWW91IHdpbGwgY3JlYXRlIGl0IHlvdXJzZWxmIGFmdGVyIGFsbCBlbmdpbmVlcnMgaGF2ZSBjb21wbGV0ZWQgdGhlaXIgdGFza3Mgb3IgcmVhY2hlZCB0aGVpciBtYXhpbXVtIHJvdW5kcy4KCi0gUmVwcm9kdWN0aW9uIGludm9sdmVzIGJvdGggaW1wbGVtZW50YXRpb24gYW5kIGV4cGVyaW1lbnQgZXhlY3V0aW9uLiBFbmdpbmVlcnMgbXVzdCBydW4gZXhwZXJpbWVudHMgYW5kIGdlbmVyYXRlIGNvbmNyZXRlIG91dHB1dHMgKGUuZy4sIHRhYmxlcywgZmlndXJlcywgQ1NWIGZpbGVzKS4gRWFjaCB0YXNrIGdyb3VwIHNob3VsZCBpbmNsdWRlIGJvdGggaW1wbGVtZW50YXRpb24gYW5kIGV4ZWN1dGlvbiBzdGVwcyBuZWNlc3NhcnkgdG8gcHJvZHVjZSBtZWFzdXJhYmxlIHJlc3VsdHMuIFRoZSBvYmplY3RpdmUgaXMgdG8gcmVwcm9kdWNlIGFzIG1hbnkgb2YgdGhlIHBhcGVyJ3MgY29yZSBjb250cmlidXRpb25zIGFuZCByZXN1bHRzIGFzIHBvc3NpYmxlIHdpdGhpbiBsaW1pdGVkIHRpbWUuCgpOb3RlOiBEbyBOT1QgcHJvdmlkZSBhbnkgY29kZSBzbmlwcGV0cyBvciBwc2V1ZG8tY29kZS4gT3V0cHV0IHlvdXIgZGVsZWdhdGlvbiBwbGFuIHN0cmljdGx5IGluIHRoZSBmb2xsb3dpbmcgSlNPTiBmb3JtYXQ6Cgp7CiAgImRlbGVnYXRpb25fcGxhbiI6IHsKICAgICJmaXJzdF9yb3VuZCI6IHsKICAgICAgIm51bV9hZ2VudHMiOiA8aW50ZWdlciBiZXR3ZWVuIDEgYW5kIHttYXhfYWdlbnRzfT4sCiAgICAgICJyZWFzb25pbmciOiAiRXhwbGFpbiB3aHkgdGhlc2UgdGFza3MgYXJlIHByaW9yaXRpemVkIGFuZCB3aHkgdGhpcyBudW1iZXIgb2YgZW5naW5lZXJzIGlzIHVzZWQuIiwKICAgICAgInRhc2tzIjogWwogICAgICAgIHsKICAgICAgICAgICJlbmdpbmVlcl9pZCI6ICJlbmdpbmVlcl9pZCIsCiAgICAgICAgICAidGFza19pZCI6ICJ0YXNrLXVuaXF1ZS1pZCIsCiAgICAgICAgICAidGFza19ub2RlX2lkIjogInJ1YnJpYyB0YXNrIG5vZGUgaWQgaWYgYXZhaWxhYmxlIiwKICAgICAgICAgICJyZXF1aXJlbWVudHMiOiAiU3BlY2lmaWMgcmVxdWlyZW1lbnQgZnJvbSB0aGUgcnVicmljIHRvIGltcGxlbWVudCIsCiAgICAgICAgICAidGFza19jYXRlZ29yeSI6ICJDb2RlIERldmVsb3BtZW50fEV4cGVyaW1lbnQgUnVubmluZ3xSZXN1bHRzIEFuYWx5c2lzfE90aGVyIiwKICAgICAgICAgICJlc3RpbWF0ZWRfY29tcGxleGl0eSI6ICJzaW1wbGV8bWVkaXVtfGNvbXBsZXgiLAogICAgICAgICAgImluc3RydWN0aW9uIjogIlByb3ZpZGUgYSBkZXRhaWxlZCBleHBsYW5hdGlvbiBvZiB0aGUgcGFwZXIgYW5kIGRldGFpbGVkIGluc3RydWN0aW9ucyBmb3IgdGhlIGN1cnJlbnQgcmVwcm9kdWN0aW9uIHRhc2suIEV4cGxhaW4gdGhlIGV4cGVjdGVkIGJlaGF2aW9yIGFuZCBvdXRwdXRzLiBJbmNsdWRlIHJlbGV2YW50IGRldGFpbHMgZnJvbSB0aGUgcGFwZXIgb3IgYWRkZW5kdW0uIEV4cGxpY2l0bHkgbWVudGlvbiBhdmFpbGFibGUgZGVwZW5kZW5jaWVzIGFuZCByZXF1aXJlZCBpbnN0YWxsYXRpb25zLiBQcm92aWRlIGNsZWFyLCBzdHJ1Y3R1cmVkIGd1aWRhbmNlIHRvIGVuc3VyZSBjb3JyZWN0IGltcGxlbWVudGF0aW9uLiIKICAgICAgICB9CiAgICAgIF0KICAgIH0sCiAgICAicmVtYWluaW5nX3Rhc2tzIjogWwogICAgICB7CiAgICAgICAgInRhc2tfaWQiOiAidGFzay11bmlxdWUtaWQiLAogICAgICAgICJ0YXNrX25vZGVfaWQiOiAicnVicmljIHRhc2sgbm9kZSBpZCBpZiBhdmFpbGFibGUiLAogICAgICAgICJyZXF1aXJlbWVudHMiOiAiU3BlY2lmaWMgcmVxdWlyZW1lbnQgdG8gaW1wbGVtZW50IiwKICAgICAgICAidGFza19jYXRlZ29yeSI6ICJDb2RlIERldmVsb3BtZW50fEV4cGVyaW1lbnQgUnVubmluZ3xSZXN1bHRzIEFuYWx5c2lzfE90aGVyIiwKICAgICAgICAiZXN0aW1hdGVkX2NvbXBsZXhpdHkiOiAic2ltcGxlfG1lZGl1bXxjb21wbGV4IiwKICAgICAgICAiZGVwZW5kc19vbiI6IFsibGlzdCBvZiB0YXNrX2lkcyB0aGlzIGRlcGVuZHMgb24sIG9yIGVtcHR5Il0KICAgICAgfQogICAgXQogIH0KfQ==)

Theengineersonyourteamarewaitingforinstructionstobegintheirfirstreproductiontasks.YoumustnowdelegatethereproductionworksystematicallybyoutputtingadelegationJSONbasedonyourcurrentunderstandingofthepaper.Youhaveupto{max\_agents}engineersavailable.

Strategiesforeffectivefirst-rounddelegation:

-First,dividetheoverallreproductioneffortintoupto{max\_agents}majortaskgroupsbasedonyourunderstandingofthepaper.Balancecomplexityandestimatedeffortasevenlyaspossible.Grouprelatedtaskstogetherandcarefullyconsiderdependenciesbetweentasks(i.e.,whichcomponentsdependonothers).DoNOTdelegatedirectlyattherubricnodelevel;therubric(ifprovided)isonlyareferenceforexpectedoutcomes.Rememberthatreproductionincludesnotonlyimplementationbutalsoexperimentexecutionneededtogenerateexpectedoutputs.Whenformingtaskgroups,considerhowexperimentorchestrationwillbestructured.

-Foreachengineer,assignthehighest-priorityreproductiontaskwithintheirtaskgroup(i.e.,thetaskthatreproducesthemostimportantresults).

-Sincethisisthefirstassignmentround,provideengineerswithaclearexplanationoftheoverallstructureofthepaperandadetailedsummaryofthepaperbasedonyourexploration.Thisensurestheydonotneedtore-explorethepaperindependently.

-Providedetailedinstructionsforeachassignedtask.Clearlyspecifywhichpartofthepaperisbeingreproducedandwhatoutputsareexpected.Includerelevantcontextfromthepaperandaddendum.Explicitlymentionwhichdependenciesarealreadyavailableandwhichmustbeinstalled.Ensurethateachengineercreatesandmodifiesonlytheirownfiles.DoNOTassignmultipleengineerstomodifythesamefile,asthiswillcausemergeconflicts.

-Donotassignthereproduce.shscripttoanyengineer.Youwillcreateityourselfafterallengineershavecompletedtheirtasksorreachedtheirmaximumrounds.

-Reproductioninvolvesbothimplementationandexperimentexecution.Engineersmustrunexperimentsandgenerateconcreteoutputs(e.g.,tables,figures,CSVfiles).Eachtaskgroupshouldincludebothimplementationandexecutionstepsnecessarytoproducemeasurableresults.Theobjectiveistoreproduceasmanyofthepaper’scorecontributionsandresultsaspossiblewithinlimitedtime.

Note:DoNOTprovideanycodesnippetsorpseudo-code.OutputyourdelegationplanstrictlyinthefollowingJSONformat:

{

"delegation\_plan":{

"first\_round":{

"num\_agents":<integerbetween1and{max\_agents}>,

"reasoning":"Explainwhythesetasksareprioritizedandwhythisnumberofengineersisused.",

"tasks":\[\
\
{\
\
"engineer\_id":"engineer\_id",\
\
"task\_id":"task-unique-id",\
\
"task\_node\_id":"rubrictasknodeidifavailable",\
\
"requirements":"Specificrequirementfromtherubrictoimplement",\
\
"task\_category":"CodeDevelopment\|ExperimentRunning\|ResultsAnalysis\|Other",\
\
"estimated\_complexity":"simple\|medium\|complex",\
\
"instruction":"Provideadetailedexplanationofthepaperanddetailedinstructionsforthecurrentreproductiontask.Explaintheexpectedbehaviorandoutputs.Includerelevantdetailsfromthepaperoraddendum.Explicitlymentionavailabledependenciesandrequiredinstallations.Provideclear,structuredguidancetoensurecorrectimplementation."\
\
}\
\
\]

},

"remaining\_tasks":\[\
\
{\
\
"task\_id":"task-unique-id",\
\
"task\_node\_id":"rubrictasknodeidifavailable",\
\
"requirements":"Specificrequirementtoimplement",\
\
"task\_category":"CodeDevelopment\|ExperimentRunning\|ResultsAnalysis\|Other",\
\
"estimated\_complexity":"simple\|medium\|complex",\
\
"depends\_on":\["listoftask\_idsthisdependson,orempty"\]\
\
}\
\
\]

}

}

## Appendix B Full Results

We provide the full results for each repository on Commit0-Lite and each paper on PaperBench across three LLMs.

|     |     |     |     |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | Single-Agent (100 iters) | CAID (4 engineers) | Single+CAID |
| repo\_id | Pass | Time | Cost | Iter | Pass | Time | Cost | Iter | Pass | Time | Cost | Iter |
| babel | 0.00.0 | 955.3955.3 | 1.25001.2500 | 100100 | 1.51.5 | 1749.41749.4 | 13.991413.9914 | 267267 | 1.51.5 | 2704.72704.7 | 15.241415.2414 | 367367 |
| cachetools | 100.0100.0 | 284.3284.3 | 0.99260.9926 | 4444 | 100.0100.0 | 863.1863.1 | 3.32883.3288 | 206206 | 100.0100.0 | 1147.41147.4 | 4.32144.3214 | 250250 |
| chardet | 6.46.4 | 598.0598.0 | 2.26392.2639 | 3131 | 2.42.4 | 1112.41112.4 | 7.48947.4894 | 259259 | 6.46.4 | 1710.41710.4 | 9.75339.7533 | 290290 |
| cookiecutter | 35.135.1 | 615.8615.8 | 1.87141.8714 | 100100 | 40.240.2 | 1246.91246.9 | 6.97276.9727 | 288288 | 40.240.2 | 1862.71862.7 | 8.84418.8441 | 388388 |
| deprecated | 100.0100.0 | 444.3444.3 | 0.98120.9812 | 4747 | 100.0100.0 | 1197.21197.2 | 4.24084.2408 | 165165 | 100.0100.0 | 1641.51641.5 | 5.22205.2220 | 212212 |
| imapclient | 28.828.8 | 596.6596.6 | 1.91161.9116 | 100100 | 42.342.3 | 1463.01463.0 | 9.08529.0852 | 405405 | 42.342.3 | 2059.62059.6 | 10.996810.9968 | 505505 |
| jinja | 0.00.0 | 647.2647.2 | 1.70511.7051 | 9999 | 5.15.1 | 1483.91483.9 | 9.97079.9707 | 428428 | 5.15.1 | 2131.12131.1 | 11.675811.6758 | 527527 |
| marshmallow | 23.123.1 | 600.6600.6 | 2.03932.0393 | 100100 | 43.843.8 | 1981.01981.0 | 10.998710.9987 | 444444 | 43.843.8 | 2581.62581.6 | 13.038013.0380 | 544544 |
| minitorch | 17.417.4 | 689.7689.7 | 1.98251.9825 | 100100 | 34.434.4 | 1436.21436.2 | 8.68748.6874 | 374374 | 34.434.4 | 2125.92125.9 | 10.669910.6699 | 474474 |
| parsel | 73.873.8 | 782.2782.2 | 2.23792.2379 | 9797 | 72.372.3 | 1609.41609.4 | 7.27027.2702 | 275275 | 73.873.8 | 2391.62391.6 | 9.50819.5081 | 372372 |
| portalocker | 79.079.0 | 1180.61180.6 | 1.70701.7070 | 7878 | 100.0100.0 | 2098.52098.5 | 7.43217.4321 | 275275 | 100.0100.0 | 3279.13279.1 | 9.13919.1391 | 353353 |
| pyjwt | 61.061.0 | 721.7721.7 | 2.41652.4165 | 9999 | 62.262.2 | 1513.41513.4 | 8.03668.0366 | 330330 | 62.262.2 | 2235.12235.1 | 10.453110.4531 | 429429 |
| simpy | 77.977.9 | 745.2745.2 | 2.11962.1196 | 100100 | 92.192.1 | 2424.92424.9 | 10.743210.7432 | 387387 | 92.192.1 | 3170.13170.1 | 12.862812.8628 | 487487 |
| tinydb | 91.091.0 | 838.6838.6 | 2.52072.5207 | 100100 | 94.094.0 | 1730.01730.0 | 7.13277.1327 | 285285 | 94.094.0 | 2568.62568.6 | 9.65349.6534 | 385385 |
| voluptuous | 56.456.4 | 747.5747.5 | 2.50852.5085 | 100100 | 55.755.7 | 1801.31801.3 | 9.21309.2130 | 422422 | 56.456.4 | 2548.82548.8 | 11.721511.7215 | 522522 |
| wcwidth | 100.0100.0 | 634.4634.4 | 1.69381.6938 | 5757 | 100.0100.0 | 1620.21620.2 | 5.51455.5145 | 203203 | 100.0100.0 | 2254.62254.6 | 7.20837.2083 | 260260 |
| AVERAGE | 53.153.1 | 692.6692.6 | 1.88761.8876 | 84.584.5 | 59.159.1 | 1583.21583.2 | 8.13178.1317 | 313.3313.3 | 59.559.5 | 2275.82275.8 | 10.019310.0193 | 397.8397.8 |

Table 4: Claude 4.5 Sonnet results on Commit0-Lite across different configurations.

|     |     |     |     |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | Single-Agent (100 iters) | Multi-Agent (4 engineers) | Single+Multi-Agent (100 iters) |
| repo\_id | Pass | Time | Cost | Iter | Pass | Time | Cost | Iter | Pass | Time | Cost | Iter |
| babel | 0.40.4 | 865.6865.6 | 3.63.6 | 100100 | 0.70.7 | 1658.41658.4 | 11.811.8 | 395395 | 0.70.7 | 2524.02524.0 | 15.415.4 | 495495 |
| cachetools | 100.0100.0 | 314.5314.5 | 1.51.5 | 6868 | 100.0100.0 | 2131.22131.2 | 4.14.1 | 179179 | 100.0100.0 | 2445.72445.7 | 5.65.6 | 247247 |
| chardet | 0.00.0 | 438.0438.0 | 4.14.1 | 100100 | 0.00.0 | 1654.11654.1 | 8.48.4 | 269269 | 0.00.0 | 2092.12092.1 | 12.512.5 | 369369 |
| cookiecutter | 22.122.1 | 3817.73817.7 | 3.23.2 | 100100 | 29.029.0 | 2047.82047.8 | 6.46.4 | 287287 | 29.029.0 | 5865.55865.5 | 9.69.6 | 387387 |
| deprecated | 100.0100.0 | 210.1210.1 | 0.90.9 | 4444 | 100.0100.0 | 2749.62749.6 | 5.15.1 | 190190 | 100.0100.0 | 2959.72959.7 | 6.06.0 | 234234 |
| imapclient | 23.223.2 | 550.4550.4 | 2.62.6 | 100100 | 24.324.3 | 1615.11615.1 | 13.213.2 | 510510 | 24.324.3 | 2165.52165.5 | 15.715.7 | 610610 |
| jinja | 0.00.0 | 419.0419.0 | 2.42.4 | 100100 | 0.00.0 | 509.2509.2 | 2.62.6 | 150150 | 0.00.0 | 928.2928.2 | 5.05.0 | 250250 |
| marshmallow | 17.017.0 | 392.6392.6 | 2.32.3 | 100100 | 38.738.7 | 2256.22256.2 | 18.718.7 | 592592 | 38.738.7 | 2648.82648.8 | 21.021.0 | 692692 |
| minitorch | 17.417.4 | 555.5555.5 | 2.32.3 | 100100 | 20.020.0 | 744.7744.7 | 9.29.2 | 372372 | 20.020.0 | 1300.21300.2 | 11.511.5 | 472472 |
| parsel | 39.839.8 | 486.3486.3 | 2.62.6 | 100100 | 47.647.6 | 552.8552.8 | 5.35.3 | 240240 | 47.647.6 | 1039.11039.1 | 7.97.9 | 340340 |
| portalocker | 68.468.4 | 2957.42957.4 | 1.31.3 | 5656 | 71.171.1 | 1287.81287.8 | 5.65.6 | 264264 | 71.171.1 | 4245.24245.2 | 6.86.8 | 320320 |
| pyjwt | 49.449.4 | 1039.51039.5 | 3.13.1 | 100100 | 59.559.5 | 527.4527.4 | 1.51.5 | 5454 | 59.559.5 | 1566.91566.9 | 4.64.6 | 154154 |
| simpy | 34.334.3 | 672.4672.4 | 2.62.6 | 100100 | 65.065.0 | 1558.81558.8 | 7.07.0 | 270270 | 65.065.0 | 2231.22231.2 | 9.69.6 | 370370 |
| tinydb | 82.182.1 | 458.9458.9 | 3.23.2 | 100100 | 71.671.6 | 1124.91124.9 | 5.95.9 | 244244 | 82.182.1 | 1583.81583.8 | 9.19.1 | 344344 |
| voluptuous | 42.342.3 | 419.4419.4 | 3.23.2 | 100100 | 32.232.2 | 1052.41052.4 | 6.26.2 | 246246 | 42.342.3 | 1471.81471.8 | 9.49.4 | 346346 |
| wcwidth | 89.589.5 | 338.9338.9 | 0.80.8 | 3030 | 84.284.2 | 734.2734.2 | 5.55.5 | 181181 | 89.589.5 | 1073.11073.1 | 6.36.3 | 211211 |
| AVERAGE | 42.942.9 | 871.0871.0 | 2.52.5 | 87.487.4 | 46.546.5 | 1387.81387.8 | 7.37.3 | 277.7277.7 | 46.546.5 | 2258.82258.8 | 9.89.8 | 365.1365.1 |

Table 5: GLM 4.7 results on Commit0-Lite across different configurations.

|     |     |     |     |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | Single-Agent (100 iters) | Multi-Agent (4 engineers) | Single+Multi-Agent (100 iters) |
| repo\_id | Pass | Time | Cost | Iter | Pass | Time | Cost | Iter | Pass | Time | Cost | Iter |
| babel | 0.30.3 | 578.6578.6 | 1.41.4 | 100100 | 1.21.2 | 3972.73972.7 | 9.49.4 | 514514 | 1.21.2 | 4551.34551.3 | 10.810.8 | 614614 |
| cachetools | 100.0100.0 | 408.2408.2 | 0.90.9 | 3838 | 100.0100.0 | 469.2469.2 | 0.70.7 | 8181 | 100.0100.0 | 877.4877.4 | 1.71.7 | 119119 |
| chardet | 3.53.5 | 612.3612.3 | 1.71.7 | 6464 | 31.731.7 | 2804.72804.7 | 4.74.7 | 327327 | 31.731.7 | 3417.03417.0 | 6.36.3 | 391391 |
| cookiecutter | 42.342.3 | 901.5901.5 | 1.61.6 | 5454 | 47.347.3 | 3593.63593.6 | 6.86.8 | 407407 | 47.347.3 | 4495.14495.1 | 8.48.4 | 461461 |
| deprecated | 100.0100.0 | 551.5551.5 | 0.80.8 | 3333 | 100.0100.0 | 758.1758.1 | 1.71.7 | 147147 | 100.0100.0 | 1309.61309.6 | 2.52.5 | 180180 |
| imapclient | 18.018.0 | 443.9443.9 | 1.11.1 | 100100 | 16.916.9 | 871.1871.1 | 1.51.5 | 3131 | 18.018.0 | 1315.01315.0 | 2.52.5 | 131131 |
| jinja | 0.00.0 | 419.5419.5 | 3.63.6 | 100100 | 0.00.0 | 1213.11213.1 | 1.81.8 | 150150 | 0.00.0 | 1632.61632.6 | 5.35.3 | 250250 |
| marshmallow | 15.515.5 | 469.4469.4 | 1.21.2 | 100100 | 23.223.2 | 1217.81217.8 | 5.45.4 | 242242 | 23.223.2 | 1687.21687.2 | 6.66.6 | 342342 |
| minitorch | 0.00.0 | 461.2461.2 | 1.21.2 | 5555 | 40.040.0 | 1164.61164.6 | 2.02.0 | 112112 | 40.040.0 | 1625.81625.8 | 3.23.2 | 167167 |
| parsel | 52.952.9 | 857.6857.6 | 1.81.8 | 5252 | 100.0100.0 | 1690.31690.3 | 5.15.1 | 317317 | 100.0100.0 | 2547.92547.9 | 6.96.9 | 369369 |
| portalocker | 76.376.3 | 978.6978.6 | 1.71.7 | 7070 | 97.497.4 | 3394.03394.0 | 8.38.3 | 424424 | 97.497.4 | 4372.64372.6 | 10.010.0 | 494494 |
| pyjwt | 51.751.7 | 793.4793.4 | 1.81.8 | 5050 | 51.751.7 | 2385.22385.2 | 7.97.9 | 424424 | 51.751.7 | 3178.63178.6 | 9.79.7 | 474474 |
| simpy | 0.00.0 | 1031.01031.0 | 1.41.4 | 6161 | 68.668.6 | 1578.11578.1 | 5.65.6 | 138138 | 68.668.6 | 2609.12609.1 | 7.07.0 | 199199 |
| tinydb | 86.186.1 | 679.0679.0 | 1.51.5 | 5151 | 95.095.0 | 2817.12817.1 | 6.16.1 | 171171 | 95.095.0 | 3496.13496.1 | 7.67.6 | 222222 |
| voluptuous | 37.637.6 | 919.5919.5 | 1.51.5 | 6969 | 38.338.3 | 1172.61172.6 | 2.72.7 | 235235 | 38.338.3 | 2092.12092.1 | 4.24.2 | 304304 |
| wcwidth | 92.192.1 | 1927.91927.9 | 2.82.8 | 3939 | 100.0100.0 | 1436.51436.5 | 3.03.0 | 213213 | 100.0100.0 | 3364.43364.4 | 5.85.8 | 252252 |
| AVERAGE | 42.342.3 | 752.1752.1 | 1.61.6 | 64.864.8 | 57.057.0 | 1908.71908.7 | 4.54.5 | 245.8245.8 | 57.057.0 | 2660.72660.7 | 6.26.2 | 310.6310.6 |

Table 6: MiniMax 2.5 results on Commit0-Lite across different configurations.

|     |     |     |     |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | Single-Agent (100 iters) | CAID (2 engineers) | Single+CAID |
| paper\_id | Scores | Time | Cost | Iter | Scores | Time | Cost | Iter | Scores | Time | Cost | Iter |
| adaptive-pruning | 33.433.4 | 1043.51043.5 | 3.03.0 | 70.070.0 | 56.056.0 | 2463.02463.0 | 7.47.4 | 191.0191.0 | 56.056.0 | 3506.53506.5 | 10.510.5 | 261.0261.0 |
| all-in-one | 68.468.4 | 3124.03124.0 | 3.93.9 | 98.098.0 | 50.250.2 | 1946.91946.9 | 6.06.0 | 146.0146.0 | 68.468.4 | 5070.95070.9 | 9.99.9 | 244.0244.0 |
| bam | 57.957.9 | 3601.63601.6 | 3.43.4 | 87.087.0 | 64.764.7 | 2577.72577.7 | 7.27.2 | 223.0223.0 | 64.764.7 | 6179.36179.3 | 10.610.6 | 310.0310.0 |
| bbox | 38.638.6 | 3397.53397.5 | 4.04.0 | 80.080.0 | 68.868.8 | 1856.01856.0 | 9.19.1 | 163.0163.0 | 68.868.8 | 5253.55253.5 | 13.113.1 | 243.0243.0 |
| bridging-data-gaps | 43.243.2 | 1409.71409.7 | 2.92.9 | 78.078.0 | 40.540.5 | 2078.02078.0 | 6.66.6 | 166.0166.0 | 43.243.2 | 3487.73487.7 | 9.59.5 | 244.0244.0 |
| fre | 56.956.9 | 1198.61198.6 | 3.33.3 | 92.092.0 | 69.669.6 | 2193.62193.6 | 7.67.6 | 213.0213.0 | 69.669.6 | 3392.23392.2 | 10.910.9 | 305.0305.0 |
| ftrl | 34.634.6 | 1499.61499.6 | 3.23.2 | 14.014.0 | 61.961.9 | 1943.01943.0 | 7.37.3 | 184.0184.0 | 61.961.9 | 3442.63442.6 | 10.510.5 | 198.0198.0 |
| lbcs | 79.579.5 | 1451.91451.9 | 3.33.3 | 50.050.0 | 82.982.9 | 2508.92508.9 | 6.36.3 | 170.0170.0 | 82.982.9 | 3960.83960.8 | 9.69.6 | 220.0220.0 |
| lca-on-the-line | 59.359.3 | 1754.11754.1 | 3.33.3 | 18.018.0 | 48.848.8 | 2011.92011.9 | 4.74.7 | 205.0205.0 | 59.359.3 | 3766.03766.0 | 8.08.0 | 223.0223.0 |
| mechanistic-understanding | 75.075.0 | 1771.81771.8 | 3.03.0 | 77.077.0 | 63.163.1 | 1936.51936.5 | 6.56.5 | 175.0175.0 | 75.075.0 | 3708.33708.3 | 9.59.5 | 252.0252.0 |
| pinn | 53.953.9 | 2272.62272.6 | 3.93.9 | 44.044.0 | 68.468.4 | 2222.52222.5 | 5.35.3 | 112.0112.0 | 68.468.4 | 4495.14495.1 | 9.29.2 | 156.0156.0 |
| rice | 33.233.2 | 2239.42239.4 | 3.43.4 | 72.072.0 | 30.030.0 | 1870.71870.7 | 6.46.4 | 150.0150.0 | 33.233.2 | 4110.14110.1 | 9.89.8 | 222.0222.0 |
| robust-clip | 42.942.9 | 1343.81343.8 | 3.43.4 | 83.083.0 | 57.257.2 | 1899.51899.5 | 6.46.4 | 151.0151.0 | 57.257.2 | 3243.33243.3 | 9.79.7 | 234.0234.0 |
| sample-specific-masks | 85.685.6 | 1110.31110.3 | 2.72.7 | 22.022.0 | 86.386.3 | 2081.02081.0 | 6.26.2 | 165.0165.0 | 86.386.3 | 3191.33191.3 | 8.98.9 | 187.0187.0 |
| sapg | 28.028.0 | 1551.11551.1 | 3.33.3 | 99.099.0 | 64.264.2 | 1934.81934.8 | 8.08.0 | 139.0139.0 | 64.264.2 | 3485.93485.9 | 11.411.4 | 238.0238.0 |
| sequential-neural-score-estimation | 86.586.5 | 2011.62011.6 | 3.23.2 | 100.0100.0 | 86.786.7 | 2097.52097.5 | 4.74.7 | 164.0164.0 | 86.786.7 | 4109.14109.1 | 7.97.9 | 264.0264.0 |
| stay-on-topic-with-classifier-free-guidance | 66.266.2 | 1468.21468.2 | 3.03.0 | 62.062.0 | 78.578.5 | 1829.01829.0 | 4.24.2 | 140.0140.0 | 78.578.5 | 3297.23297.2 | 7.27.2 | 202.0202.0 |
| stochastic-interpolants | 85.885.8 | 1260.41260.4 | 3.53.5 | 100.0100.0 | 74.174.1 | 2105.32105.3 | 6.66.6 | 217.0217.0 | 85.885.8 | 3365.73365.7 | 10.110.1 | 317.0317.0 |
| test-time-model-adaptation | 62.762.7 | 1165.91165.9 | 2.82.8 | 16.016.0 | 51.351.3 | 1966.11966.1 | 6.26.2 | 165.0165.0 | 62.762.7 | 3132.03132.0 | 9.09.0 | 181.0181.0 |
| what-will-my-model-forget | 52.452.4 | 1394.81394.8 | 3.03.0 | 74.074.0 | 63.263.2 | 2086.12086.1 | 6.56.5 | 126.0126.0 | 63.263.2 | 3480.93480.9 | 9.59.5 | 200.0200.0 |
| AVERAGE | 57.257.2 | 1803.51803.5 | 3.33.3 | 66.866.8 | 63.363.3 | 2080.42080.4 | 6.56.5 | 168.3168.3 | 66.866.8 | 3883.93883.9 | 9.79.7 | 235.1235.1 |

Table 7: Claude 4.5 Sonnet results on PaperBench Code-Dev across different configurations.

|     |     |     |     |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | Single-Agent (100 iters) | Multi-Agent (2 engineers) | Single+Multi-Agent |
| paper\_id | Scores | Time | Cost | Iter | Scores | Time | Cost | Iter | Scores | Time | Cost | Iter |
| adaptive-pruning | 44.944.9 | 1130.01130.0 | 2.52.5 | 72.072.0 | 60.360.3 | 1473.61473.6 | 6.16.1 | 187.0187.0 | 60.360.3 | 2603.62603.6 | 8.68.6 | 259.0259.0 |
| all-in-one | 19.919.9 | 1430.01430.0 | 3.63.6 | 100.0100.0 | 25.825.8 | 1532.01532.0 | 3.33.3 | 140.0140.0 | 25.825.8 | 2962.02962.0 | 6.96.9 | 240.0240.0 |
| bam | 63.563.5 | 681.6681.6 | 2.52.5 | 53.053.0 | 75.375.3 | 1315.11315.1 | 4.94.9 | 184.0184.0 | 75.375.3 | 1996.71996.7 | 7.47.4 | 237.0237.0 |
| bbox | 15.115.1 | 1186.01186.0 | 2.72.7 | 75.075.0 | 40.140.1 | 1227.91227.9 | 4.44.4 | 163.0163.0 | 40.140.1 | 2413.92413.9 | 7.17.1 | 238.0238.0 |
| bridging-data-gaps | 25.625.6 | 603.0603.0 | 2.12.1 | 68.068.0 | 33.533.5 | 1227.11227.1 | 4.84.8 | 190.0190.0 | 33.533.5 | 1830.11830.1 | 6.96.9 | 258.0258.0 |
| fre | 42.342.3 | 2429.62429.6 | 2.62.6 | 55.055.0 | 42.842.8 | 1349.61349.6 | 4.44.4 | 177.0177.0 | 42.842.8 | 3779.23779.2 | 7.07.0 | 232.0232.0 |
| ftrl | 15.415.4 | 1326.41326.4 | 3.13.1 | 95.095.0 | 32.732.7 | 1850.01850.0 | 5.25.2 | 182.0182.0 | 32.732.7 | 3176.43176.4 | 8.38.3 | 277.0277.0 |
| lbcs | 75.075.0 | 539.7539.7 | 3.33.3 | 87.087.0 | 38.238.2 | 1213.21213.2 | 4.54.5 | 145.0145.0 | 75.075.0 | 1752.91752.9 | 7.87.8 | 232.0232.0 |
| lca-on-the-line | 34.734.7 | 675.7675.7 | 2.92.9 | 58.058.0 | 30.230.2 | 1974.91974.9 | 3.23.2 | 112.0112.0 | 34.734.7 | 2650.62650.6 | 6.16.1 | 170.0170.0 |
| mechanistic-understanding | 0.00.0 | 3601.73601.7 | 3.33.3 | 90.090.0 | 47.747.7 | 1904.21904.2 | 3.63.6 | 164.0164.0 | 47.747.7 | 5505.95505.9 | 6.96.9 | 254.0254.0 |
| pinn | 61.061.0 | 1158.61158.6 | 2.42.4 | 43.043.0 | 43.243.2 | 832.6832.6 | 4.34.3 | 155.0155.0 | 61.061.0 | 1991.21991.2 | 6.76.7 | 198.0198.0 |
| rice | 28.528.5 | 867.8867.8 | 3.43.4 | 96.096.0 | 30.030.0 | 1870.71870.7 | 3.63.6 | 131.0131.0 | 30.030.0 | 2738.52738.5 | 7.07.0 | 227.0227.0 |
| robust-clip | 22.322.3 | 728.7728.7 | 3.73.7 | 87.087.0 | 29.329.3 | 1288.91288.9 | 7.17.1 | 191.0191.0 | 29.329.3 | 2017.62017.6 | 10.910.9 | 278.0278.0 |
| sample-specific-masks | 50.450.4 | 793.3793.3 | 2.42.4 | 58.058.0 | 54.654.6 | 1123.51123.5 | 5.55.5 | 217.0217.0 | 54.654.6 | 1916.81916.8 | 7.97.9 | 275.0275.0 |
| sapg | 29.429.4 | 836.0836.0 | 4.54.5 | 100.0100.0 | 27.027.0 | 952.0952.0 | 6.06.0 | 204.0204.0 | 29.429.4 | 1788.01788.0 | 10.510.5 | 304.0304.0 |
| sequential-neural-score-estimation | 58.858.8 | 1248.61248.6 | 2.82.8 | 92.092.0 | 79.979.9 | 1136.11136.1 | 4.44.4 | 176.0176.0 | 79.979.9 | 2384.72384.7 | 7.27.2 | 268.0268.0 |
| stay-on-topic-with-classifier-free-guidance | 49.749.7 | 807.1807.1 | 2.62.6 | 81.081.0 | 59.359.3 | 1769.41769.4 | 4.84.8 | 157.0157.0 | 59.359.3 | 2576.52576.5 | 7.47.4 | 238.0238.0 |
| stochastic-interpolants | 70.870.8 | 1376.51376.5 | 3.03.0 | 67.067.0 | 71.071.0 | 1586.81586.8 | 6.76.7 | 228.0228.0 | 71.071.0 | 2963.32963.3 | 9.79.7 | 295.0295.0 |
| test-time-model-adaptation | 10.310.3 | 1106.91106.9 | 1.01.0 | 92.092.0 | 32.932.9 | 1547.61547.6 | 3.23.2 | 133.0133.0 | 32.932.9 | 2654.52654.5 | 4.24.2 | 225.0225.0 |
| what-will-my-model-forget | 42.642.6 | 1023.91023.9 | 1.91.9 | 61.061.0 | 53.653.6 | 1812.91812.9 | 4.64.6 | 76.076.0 | 53.653.6 | 2836.82836.8 | 6.46.4 | 137.0137.0 |
| AVERAGE | 38.038.0 | 1177.61177.6 | 2.82.8 | 76.576.5 | 45.445.4 | 1449.41449.4 | 4.74.7 | 165.6165.6 | 48.548.5 | 2627.02627.0 | 7.57.5 | 242.3242.3 |

Table 8: GLM 4.7 results on PaperBench Code-Dev across different configurations.

|     |     |     |     |     |     |     |     |     |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | Single-Agent (100 iters) | Multi-Agent (2 engineers) | Single+Multi-Agent |
| paper\_id | Scores | Time | Cost | Iter | Scores | Time | Cost | Iter | Scores | Time | Cost | Iter |
| adaptive-pruning | 15.115.1 | 3601.53601.5 | 0.90.9 | 50.050.0 | 15.215.2 | 3558.33558.3 | 3.13.1 | 223.0223.0 | 15.215.2 | 7159.87159.8 | 4.04.0 | 273.0273.0 |
| all-in-one | 0.00.0 | 2461.62461.6 | 1.21.2 | 35.035.0 | 22.322.3 | 3635.13635.1 | 2.72.7 | 198.0198.0 | 22.322.3 | 6096.76096.7 | 3.93.9 | 233.0233.0 |
| bam | 49.949.9 | 2434.82434.8 | 1.31.3 | 11.011.0 | 38.538.5 | 1852.41852.4 | 2.62.6 | 216.0216.0 | 49.949.9 | 4287.24287.2 | 3.83.8 | 227.0227.0 |
| bbox | 0.00.0 | 1491.01491.0 | 0.50.5 | 41.041.0 | 28.028.0 | 1257.81257.8 | 1.31.3 | 136.0136.0 | 28.028.0 | 2748.82748.8 | 1.91.9 | 177.0177.0 |
| bridging-data-gaps | 29.429.4 | 970.1970.1 | 0.80.8 | 57.057.0 | 33.533.5 | 2610.42610.4 | 2.72.7 | 181.0181.0 | 33.533.5 | 3580.53580.5 | 3.53.5 | 238.0238.0 |
| fre | 0.00.0 | 2128.32128.3 | 2.52.5 | 100.0100.0 | 29.029.0 | 2955.02955.0 | 4.34.3 | 284.0284.0 | 29.029.0 | 5083.35083.3 | 6.86.8 | 384.0384.0 |
| ftrl | 0.00.0 | 3601.23601.2 | 0.90.9 | 55.055.0 | 7.17.1 | 4130.44130.4 | 2.42.4 | 193.0193.0 | 7.17.1 | 7731.67731.6 | 3.43.4 | 248.0248.0 |
| lbcs | 0.00.0 | 3601.13601.1 | 0.60.6 | 36.036.0 | 0.40.4 | 2933.22933.2 | 3.03.0 | 189.0189.0 | 42.042.0 | 6534.36534.3 | 3.63.6 | 225.0225.0 |
| lca-on-the-line | 11.811.8 | 1045.41045.4 | 0.60.6 | 45.045.0 | 0.20.2 | 3294.73294.7 | 3.33.3 | 239.0239.0 | 24.924.9 | 4340.14340.1 | 3.93.9 | 284.0284.0 |
| mechanistic-understanding | 0.00.0 | 3600.73600.7 | 1.11.1 | 64.064.0 | 0.30.3 | 3129.23129.2 | 1.31.3 | 131.0131.0 | 34.034.0 | 6729.96729.9 | 2.42.4 | 195.0195.0 |
| pinn | 0.00.0 | 1906.91906.9 | 1.21.2 | 67.067.0 | 0.60.6 | 2714.22714.2 | 2.62.6 | 192.0192.0 | 56.056.0 | 4621.14621.1 | 3.83.8 | 259.0259.0 |
| rice | 0.00.0 | 3601.63601.6 | 0.80.8 | 53.053.0 | 0.20.2 | 2509.72509.7 | 2.22.2 | 173.0173.0 | 20.620.6 | 6111.36111.3 | 3.03.0 | 226.0226.0 |
| robust-clip | 0.00.0 | 2474.92474.9 | 1.41.4 | 75.075.0 | 0.20.2 | 3668.23668.2 | 3.23.2 | 250.0250.0 | 23.923.9 | 6143.16143.1 | 4.64.6 | 325.0325.0 |
| sample-specific-masks | 0.00.0 | 3601.13601.1 | 0.60.6 | 46.046.0 | 0.60.6 | 4419.14419.1 | 1.81.8 | 78.078.0 | 58.758.7 | 8020.28020.2 | 2.42.4 | 124.0124.0 |
| sapg | 8.48.4 | 1780.21780.2 | 0.60.6 | 46.046.0 | 0.30.3 | 1934.81934.8 | 0.90.9 | 150.0150.0 | 29.929.9 | 3715.03715.0 | 1.51.5 | 196.0196.0 |
| sequential-neural-score-estimation | 47.447.4 | 2511.22511.2 | 1.01.0 | 75.075.0 | 0.70.7 | 3759.23759.2 | 3.03.0 | 137.0137.0 | 71.171.1 | 6270.46270.4 | 4.04.0 | 212.0212.0 |
| stay-on-topic-with-classifier-free-guidance | 0.50.5 | 2882.92882.9 | 1.21.2 | 71.071.0 | 0.50.5 | 3029.03029.0 | 3.23.2 | 176.0176.0 | 0.50.5 | 5911.95911.9 | 4.54.5 | 247.0247.0 |
| stochastic-interpolants | 0.00.0 | 2426.32426.3 | 2.12.1 | 100.0100.0 | 0.70.7 | 3608.03608.0 | 4.84.8 | 279.0279.0 | 0.70.7 | 6034.36034.3 | 6.86.8 | 379.0379.0 |
| test-time-model-adaptation | 0.00.0 | 2990.12990.1 | 1.51.5 | 93.093.0 | 0.50.5 | 1989.61989.6 | 1.61.6 | 137.0137.0 | 0.50.5 | 4979.74979.7 | 3.13.1 | 230.0230.0 |
| what-will-my-model-forget | 0.00.0 | 1395.71395.7 | 0.90.9 | 45.045.0 | 0.20.2 | 3859.73859.7 | 2.02.0 | 49.049.0 | 0.20.2 | 5255.45255.4 | 2.92.9 | 94.094.0 |
| AVERAGE | 10.510.5 | 2525.32525.3 | 1.11.1 | 58.358.3 | 36.136.1 | 3042.43042.4 | 2.62.6 | 180.6180.6 | 36.736.7 | 5567.75567.7 | 3.73.7 | 238.8238.8 |

Table 9: MiniMax 2.5 results on PaperBench Code-Dev across different configurations.

## Appendix C One-sided t-test

|     |     |     |     |     |
| --- | --- | --- | --- | --- |
| Benchmark | Model | Δ\\Delta | tt | pp |
| Commit0 | Claude 4.5 | +6.0 | 2.87 | 0.006 |
| GLM 4.7 | +3.6 | 1.37 | 0.095 |
| MiniMax 2.5 | +14.7 | 2.81 | 0.007 |
| PaperBench | Claude 4.5 | +6.1 | 1.78 | 0.046 |
| GLM 4.7 | +7.4 | 1.93 | 0.034 |
| MiniMax 2.5 | +25.6 | 5.27 | <0.0001 |

Table 10: One-sided paired tt-test (H1H\_{1}: CAID>> Single-Agent). Δ\\Delta: mean score improvement. Bold: p<0.05p<0.05.

We compute one-sided paired tt-tests (H1H\_{1}: CAID>> Single-Agent) across all repositories or papers for each model in Table [10](https://arxiv.org/html/2603.21489v2#A3.T10 "Table 10 ‣ Appendix C One-sided t-test ‣ Effective Strategies for Asynchronous Software Engineering Agents"). On Commit0-Lite, the improvement is significant for Claude Sonnet 4.5 (t=2.87t=2.87, p=0.006p=0.006) and MiniMax 2.5 (t=2.81t=2.81, p=0.007p=0.007), with mean gains of 6.0 and 14.7 percentage points respectively. GLM 4.7 improves by 3.6 points on average but does not reach significance (p=0.095p=0.095), largely because the per-repository variance is high: CAID brings large gains on some repositories (e.g., +30.7 on simpy) but regresses on others (e.g., −10.5-10.5 on tinydb), which inflates the standard error with only 16 paired samples. On PaperBench, all three models, Claude Sonnet 4.5 (t=1.78t=1.78, p=0.046p=0.046), GLM 4.7 (t=1.93t=1.93, p=0.034p=0.034) and MiniMax 2.5 (t=5.27t=5.27, p<0.0001p<0.0001) are significant.
As discussed in Section [4.3](https://arxiv.org/html/2603.21489v2#S4.SS3 "4.3 Delegation Shapes Execution Trajectory ‣ 4 Analysis ‣ Effective Strategies for Asynchronous Software Engineering Agents"), CAID’s effectiveness depends on the manager’s ability to construct accurate dependency graphs and delegate tasks accordingly. A weaker base model produces less reliable task decomposition on the open-ended PaperBench tasks, limiting the gains that multi-agent coordination can deliver.

## Appendix D Failure on Scaling the Parallel Execution

Figure 6: Gantt plot on the simpy repository for CAID with different number of engineers, where N=2,4,8N=2,4,8.

We provide an example to show why scaling parallel execution does not always help. Figure [6](https://arxiv.org/html/2603.21489v2#A4.F6 "Figure 6 ‣ Appendix D Failure on Scaling the Parallel Execution ‣ Effective Strategies for Asynchronous Software Engineering Agents") shows the execution timelines on the simpy repository under different numbers of engineers (N=2,4,8N=2,4,8). The performance difference is not solely explained by the number of files touched, but by how the manager structures delegation across engineers. For N=4N=4, delegation remains clean and non-overlapping. Each engineer is assigned distinct files (e.g., events.py, core.py, container.py, resource.py), and their implementations proceed largely without interference. The manager avoids assigning closely coupled modules to different engineers simultaneously, and no two engineers work on the same file at the same time. As a result, integration remains stable and the run reaches a pass rate of 92.1%.

For N=8N=8, although more files are modified and parallel activity increases, the delegation becomes less disciplined. Multiple engineers are assigned different functions within the same file (notably events.py), creating overlapping write regions within a shared module. While these edits are logically separable at the function level, they introduce integration risk at the file level. The main branch receives competing updates on the same module, increasing the likelihood of merge conflicts or inconsistent intermediate states. This fragmentation of responsibility prevents clean consolidation and ultimately limits performance to 44.3%. The degradation in N=8N=8 therefore does not arise from excessive parallelism alone, but from a delegation that ignores the ownership boundaries of the file-level. When parallel execution exceeds the manager’s ability to enforce coherent task partitioning, local productivity no longer translates into stable global progress. This example illustrates that scaling the number of engineers requires disciplined delegation, not simply increasing concurrency.