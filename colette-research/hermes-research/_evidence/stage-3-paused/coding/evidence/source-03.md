Title:

Content selection saved. Describe the issue below:

Description:

![](https://arxiv.org/static/base/1.0.1/images/icons/smileybones-small.svg)arXiv is now an independent nonprofit! [Learn more](https://info.arxiv.org/about) ×

[License: CC BY-SA 4.0](https://info.arxiv.org/help/license/index.html#licenses-available)

arXiv:2606.27416v1 \[cs.MA\] 25 Jun 2026

# Glite ARF: Verifier-Driven Research with   Parallel LLM Coding Agents

Vassili Philippov
Affiliation: Glite, {vassili,pavel,dmitrii,igor}@glite.aiEmail: [a.nikolaev@sheffield.ac.uk](mailto:)Pavel Katunin
Affiliation: Glite, {vassili,pavel,dmitrii,igor}@glite.aiDmitry Andreev
Affiliation: Glite, {vassili,pavel,dmitrii,igor}@glite.aiIgor Ostanin
Affiliation: Glite, {vassili,pavel,dmitrii,igor}@glite.aiAnton Nikolaev
Affiliation: School of Biosciences, The University of Sheffield, Sheffield, UK

###### Abstract

LLM coding agents make it tempting to automate empirical research by
delegating experiments to them directly, but naive delegation does not
scale to large projects: low-rate instruction lapses compound into
broken, irreproducible artefacts. To address this problem, we present
Glite ARF, an open-source Python framework for running many
LLM coding agents in parallel on a research repository without
sacrificing reproducibility or auditability. The framework defines a
three-role stack: a
human researcher chooses which hypotheses to test, coding agents
(Claude Code, Codex CLI) implement individual tasks under a fixed
structure, and deterministic Python _verifier_ scripts enforce task isolation, immutability of completed
work, a corrections overlay, and a materialised project overview. We
call this
verifier-driven research: the rules of the research
process live in code that fails loudly when violated, not in prose
that agents are merely asked to follow. Using Glite ARF, we developed
our submission to the BEA 2026 vocabulary-difficulty shared task,
placing first in the closed track and second in the open track on all
three target languages (Spanish, German, Mandarin) and reducing the
official baseline RMSE by 29.9% (closed) and 35.9% (open). The
campaign comprised 273 tracked tasks (146 experiment runs) across 129
feature sets, run by up to twelve parallel agents orchestrated from a
single laptop — with some model training on rented A100s — at
∼$450{\\sim}\\$450 in LLM API spend (∼$498{\\sim}\\$498 total third-party cost),
and structured per-fold provenance let us catch and strip four
target-leaking feature sets, correcting an implausible 0.609 RMSE to
0.802. Across three campaigns in three domains, the framework’s
structural machinery adds only ∼1%{\\sim}1\\% of wall-clock time.
Framework and a public demo project accompany this paper.

## 1 Introduction

LLM coding agents make it natural to imagine research as many
delegated experiments running in parallel. Naive automation, however,
does not scale to large projects: agents follow most instructions, but
the few they skip compound into fabricated citations, contaminated
splits, stale summaries, out-of-scope edits, and irreproducible
provenance. Glite ARF addresses this failure mode by making the
research process itself executable. A human researcher proposes
hypotheses, agents implement isolated tasks, and deterministic Python
_verifiers_ enforce task structure, immutability, corrections,
and a materialised project overview (Figure [1](https://arxiv.org/html/2606.27416v1#S1.F1 "Figure 1 ‣ 1 Introduction ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents")).

We used Glite ARF to develop our submission to the BEA 2026
vocabulary-difficulty shared task ( [Felice and Skidmore, 2026](https://arxiv.org/html/2606.27416v1#bib.bib7 "")), detailed in
our case study (§ [4](https://arxiv.org/html/2606.27416v1#S4 "4 Case Study: BEA 2026 ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents")). The resulting system placed first
in the closed track and second in the open track on all three target
languages; we developed it across 273 tracked tasks (146 experiment
runs) inside the Python framework released with this paper. The campaign
covered 129 feature sets at approximately $450 in LLM API spend for
feature engineering ($498 total third-party cost, including rented
compute). We have
since run the framework across three campaigns in three domains; its
structural machinery adds only ∼1%{\\sim}1\\% of wall-clock time
(§ [5](https://arxiv.org/html/2606.27416v1#S5 "5 The framework in use ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents")).

HumanCoding agentsPython scriptssuggestiontaskartefactsuggestsproducesmaterialised overview/ feeds back

Figure 1: Glite ARF’s three-role stack. The human researcher writes
suggestions; coding agents execute tasks; deterministic Python scripts
verify artefacts and materialise the canonical view that the human
reads back. Each role works at a different unit of granularity.

The failure mode we target is visible once campaigns involve hundreds
of runs. Independent evaluation of fully autonomous research systems
has shown how the failure rate compounds:
[Beel et al. (2025)](https://arxiv.org/html/2606.27416v1#bib.bib3 "") found that 42% of experiments
generated by The AI Scientist v1 ( [Lu et al., 2024](https://arxiv.org/html/2606.27416v1#bib.bib20 "")) failed due
to coding errors. Our own audit of the BEA 2026 campaign repository
catalogues thirteen incidents of similar character, ranging from
train-data corruption affecting 38 feature sets to four feature sets
that leaked the target variable into LLM prompts
(Appendix [D](https://arxiv.org/html/2606.27416v1#A4 "Appendix D Observed failure modes ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents")).

The natural response is to write better prompts. We tried. Across
thousands of agent invocations the failure rate of prompt-encoded
rules does not go to zero — it stays in the low single digits,
which compounds to dozens of broken artefacts across a multi-week
campaign. We argue that rules in agentic research must live in
deterministic code: scripts that refuse to advance a step until an
artefact conforms to a versioned specification, scripts that detect
when files outside an agent’s task folder have been modified, scripts
that materialise the canonical view of cumulative results so no agent
ever needs to write a manual summary. The companion BEA 2026 system
paper describes the same mechanism in its framework-overview section
( [Philippov et al., 2026](https://arxiv.org/html/2606.27416v1#bib.bib22 "")).

Glite ARF defines a three-role stack for autonomous
research (Figure [1](https://arxiv.org/html/2606.27416v1#S1.F1 "Figure 1 ‣ 1 Introduction ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents")): the human researcher
chooses which hypotheses to test, coding agents implement individual
tasks under fixed structure, and deterministic Python scripts
enforce task isolation, immutability, a corrections overlay, and a
materialised project overview. We call this
verifier-driven research, by analogy with test-driven
development: the rules of the research process live in scripts that
fail loudly when violated, not in prose that agents are merely asked
to follow. Our contribution is the framework, used at scale across
three domains, with a refereed external shared task as one anchor and
measured campaign evidence (§ [5](https://arxiv.org/html/2606.27416v1#S5 "5 The framework in use ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents")) as another.

Section [2](https://arxiv.org/html/2606.27416v1#S2 "2 Related Work ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents") positions Glite ARF in the
autoresearch and AI-for-science landscape.
Section [3](https://arxiv.org/html/2606.27416v1#S3 "3 System ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents") describes the framework’s seven structural
principles and the verifier layer that enforces them.
Section [4](https://arxiv.org/html/2606.27416v1#S4 "4 Case Study: BEA 2026 ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents") reports our BEA 2026 case study,
including an example where structured per-fold provenance let us catch
and strip target leakage. Section [5](https://arxiv.org/html/2606.27416v1#S5 "5 The framework in use ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents") reports measured
evidence from running the framework across three campaigns.
Section [6](https://arxiv.org/html/2606.27416v1#S6 "6 Lessons and Limits ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents") discusses lessons and limits — most
importantly, we are explicit that role 1 (hypothesis selection)
remains human-driven by design.
Section [7](https://arxiv.org/html/2606.27416v1#S7 "7 Availability ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents") covers availability.

## 2 Related Work

#### Multi-agent orchestration.

AutoGen ( [Wu et al., 2023](https://arxiv.org/html/2606.27416v1#bib.bib30 "")), MetaGPT ( [Hong et al., 2024](https://arxiv.org/html/2606.27416v1#bib.bib11 "")),
CAMEL ( [Li et al., 2023](https://arxiv.org/html/2606.27416v1#bib.bib18 "")), smolagents ( [Roucher et al., 2025](https://arxiv.org/html/2606.27416v1#bib.bib24 "")),
and CrewAI ( [CrewAI Inc., 2023](https://arxiv.org/html/2606.27416v1#bib.bib6 "")) provide intra-task agent coordination and
may run inside an ARF task; ARF is orthogonal, structuring the
_campaign_-level lifecycle that wraps any of them.

#### Coding agents.

Coding agents like Claude Code ( [Anthropic, 2025](https://arxiv.org/html/2606.27416v1#bib.bib2 "")),
OpenAI Codex CLI ( [OpenAI, 2025](https://arxiv.org/html/2606.27416v1#bib.bib21 "")),
Aider ( [Gauthier, 2023](https://arxiv.org/html/2606.27416v1#bib.bib8 "")),
OpenHands ( [Wang et al., 2024](https://arxiv.org/html/2606.27416v1#bib.bib29 "")), and
SWE-agent ( [Yang et al., 2024](https://arxiv.org/html/2606.27416v1#bib.bib32 "")) execute the code-writing inside an
ARF task. SWE-bench ( [Jimenez et al., 2024](https://arxiv.org/html/2606.27416v1#bib.bib14 "")) is the closest
adjacent benchmark, evaluating single-issue resolution rather than
research-campaign integrity.

#### Autoresearch (practitioner side).

A practitioner community has formed around Karpathy’s autoresearch
pattern ( [Karpathy, 2026](https://arxiv.org/html/2606.27416v1#bib.bib15 "")) — short, single-metric
optimisation loops applied to one training script. Recent work makes
this approach more rigorous: CORAL ( [Qu et al., 2026](https://arxiv.org/html/2606.27416v1#bib.bib23 "")) introduces
multi-agent evolution with isolated worktrees and shared persistent
memory; EvoSkill ( [Alzubi et al., 2026](https://arxiv.org/html/2606.27416v1#bib.bib1 "")) discovers reusable agent
skills through failure-driven evolution with each agent program
represented as a git branch; autoreason
( [SHL0MS and Hermes Agent, 2026](https://arxiv.org/html/2606.27416v1#bib.bib27 "")) addresses iterative document refinement by
treating “do nothing” as a first-class option.

#### Autoresearch (academic side).

On the academic side, AI-Researcher ( [Tang et al., 2025](https://arxiv.org/html/2606.27416v1#bib.bib28 "")) and
Agent Laboratory ( [Schmidgall et al., 2025](https://arxiv.org/html/2606.27416v1#bib.bib25 "")) orchestrate full
literature-to-manuscript pipelines; The AI Scientist v1 and v2
( [Lu et al., 2024](https://arxiv.org/html/2606.27416v1#bib.bib20 ""); [Yamada et al., 2025](https://arxiv.org/html/2606.27416v1#bib.bib31 "")) generate workshop-level papers
end to end; ADAS ( [Hu et al., 2025](https://arxiv.org/html/2606.27416v1#bib.bib12 "")) automates the design of agentic
systems themselves. Independent evaluation has shown that fully
autonomous systems still produce substantial structural errors:
[Beel et al. (2025)](https://arxiv.org/html/2606.27416v1#bib.bib3 "") found that 42% of AI-Scientist-v1
experiments failed due to coding errors. For a survey of the field see
[Zheng et al. (2025)](https://arxiv.org/html/2606.27416v1#bib.bib33 "").

#### Evaluation regime.

Existing autoresearch systems are typically evaluated against
benchmarks constructed by the system’s own team or close
collaborators: MLE-Bench ( [Chan et al., 2025](https://arxiv.org/html/2606.27416v1#bib.bib4 "")),
MLAgentBench ( [Huang et al., 2024](https://arxiv.org/html/2606.27416v1#bib.bib13 "")),
MLR-Bench ( [Chen et al., 2025](https://arxiv.org/html/2606.27416v1#bib.bib5 "")),
AgentBench ( [Liu et al., 2024](https://arxiv.org/html/2606.27416v1#bib.bib19 "")), and Scientist-Bench inside
AI-Researcher itself. Glite ARF’s empirical anchor is different in
kind: a refereed external shared task (BEA 2026) whose test labels,
metric, and leaderboard adjudication are all outside the authors’
control, complemented by measured evidence from three author-run
campaigns (§ [5](https://arxiv.org/html/2606.27416v1#S5 "5 The framework in use ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents")).

#### Workflow, provenance, and experiment management.

Many of ARF’s mechanisms adapt established software- and
data-engineering patterns rather than inventing them. Experiment
trackers (MLflow, Weights & Biases, Sacred, ClearML, Aim),
data and model versioning (DVC, DataLad), workflow engines
(Snakemake, Nextflow, Kedro), and reproducibility tooling (ReproZip)
already provide provenance, lineage, and pipeline structure;
continuous integration, policy-as-code, and append-only or
event-sourced logs provide gating and immutable history. ARF’s
contribution is not any single one of these ideas but their
opinionated, repository-native combination for _parallel_
_LLM-agent research campaigns_, in which the actor producing artefacts
is a non-deterministic agent rather than a person.
Table [1](https://arxiv.org/html/2606.27416v1#S2.T1 "Table 1 ‣ Workflow, provenance, and experiment management. ‣ 2 Related Work ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents") positions ARF against representative
systems along the dimensions this setting stresses.

| Capability | Trackers | DVC/CI | Workflows | ARF |
| --- | --- | --- | --- | --- |
| Task-level worktree isolation | — | ∼\\sim | — | ✓ |
| Machine-checked artefact contracts | — | ∼\\sim | ∼\\sim | ✓ |
| Immutable corrections overlay | — | — | — | ✓ |
| Agent command/transcript logging | — | — | — | ✓ |
| Materialised human-facing overview | ∼\\sim | — | — | ✓ |
| Model / agent independence | ✓ | ✓ | ✓ | ✓ |

Table 1: ARF versus representative experiment trackers
(MLflow, W&B), versioning/CI (DVC, GitHub Actions), and workflow
engines (Snakemake). ✓ = provided; ∼\\sim = partial;
— = not provided.

#### Position.

Glite ARF is therefore neither an orchestrator nor an agent nor a
benchmark, but a structural envelope that wraps existing coding agents
and makes a multi-week, multi-agent research campaign auditable.

## 3 System

### 3.1 Architecture and seven principles

Glite ARF defines three roles. The human researcher works at the
level of _suggestions_: hypotheses to test, datasets to try,
libraries to evaluate. Coding agents (Claude Code, Codex CLI) work at
the level of _tasks_: each task is a folder under
tasks/tNNNN\_slug/, a git branch, and a pull request; large
artefacts such as datasets and model checkpoints live in that folder
under Git LFS by default, though a project can substitute external
object storage (e.g. Amazon S3).
Deterministic Python scripts work at the level of _artefacts_:
every file an agent writes conforms to a versioned specification
(arf/specifications/,
meta/asset\_types/<kind>/specification.md), enforced by a
_verifier_ before it is merged; ARF’s internal name for these
scripts is _verificator_. ARF
is semi-autonomous by design: role 1 (hypothesis selection) remains
human-driven because frontier models in mid-2026 do not reliably
perform research-direction selection at the timescale of a multi-week
campaign. We return to this design choice in § [6](https://arxiv.org/html/2606.27416v1#S6 "6 Lessons and Limits ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents").

The framework’s design crystallised over four research projects in
response to recurring failure modes catalogued in
Appendix [D](https://arxiv.org/html/2606.27416v1#A4 "Appendix D Observed failure modes ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents"). Seven structural principles emerged.

#### 1\. Task isolation.

Motivated by an incident in which a single agent step intended to
append 2,244 test rows instead recomputed train, dev, and test
features across 38 feature sets, corrupting 20,304 historical
training rows (Appendix [D](https://arxiv.org/html/2606.27416v1#A4 "Appendix D Observed failure modes ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents"), F02). Each task lives
in its own folder and git worktree, and may modify only that folder
plus a small allow-list of shared configuration files
(pyproject.toml, uv.lock, ruff.toml,
mypy.ini, .gitignore, .gitattributes). A
pre-merge verifier (PM-E003) rejects any commit that
touches anything else, so one task can never corrupt another’s data.

#### 2\. Immutability with a corrections overlay.

Motivated by the same incident: the repair was a separate downstream
task that restored 48 CSV files across 34 feature sets without
rewriting the original step’s record. Completed task folders are
immutable — a verifier rejects any branch that modifies a merged
task’s files; downstream tasks fix mistakes via correction files in
their own folders, applied at read time by aggregators.

#### 3\. Aggregators-only cross-task reading.

Motivated by F07, in which a hand-maintained tracker file reported
Completed Tasks (75 of 64) — an impossible count produced
by manual editing during a busy week. Skills must read through
arf/scripts/aggregators/, never by walking task folders
directly.

#### 4\. Materialised project overview for human observability.

Derived from the same observability problem (F07) and from two
further incidents (F08, F09) in which stale or missing per-feature
metrics misled human reviewers. A dedicated
arf/scripts/overview/materialize.py regenerates
overview/ — a committed, browsable, GitHub-renderable
dashboard of all aggregator output. The materialisation is
automatic, the artefact is static and reviewable, and
overview/ is the only human-facing summary in the repository.

#### 5\. Spec-verified artefacts.

Motivated by F01 and F04 (target leakage in generated feature code).
Every produced artefact has a versioned specification and a
corresponding verifier that checks it before commit. We elaborate
this principle in § [3.2](https://arxiv.org/html/2606.27416v1#S3.SS2 "3.2 Verifiers: enforcing the principles ‣ 3 System ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents").

#### 6\. Comprehensive logging.

Motivated by debugging pain across the campaign and bounded by F03 as
a limits example. Every CLI invocation in a task branch is wrapped in
arf/scripts/utils/run\_with\_logs.py, which records the command,
stdout, stderr, exit code, and timestamp; a verifier refuses to
mark a step complete if an expected command log is missing, so the
work that happened and the record of it cannot diverge.

#### 7\. Subagent isolation.

Motivated by context-window degradation in long-horizon agents.
Complex tasks run as a chain of subagents (research, planning,
implementation, analysis, reporting); each subagent has its own
context and sees only the inputs it needs.

Figure [2](https://arxiv.org/html/2606.27416v1#S3.F2 "Figure 2 ‣ 7. Subagent isolation. ‣ 3.1 Architecture and seven principles ‣ 3 System ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents") shows the lifecycle every task passes
through; §§ [3.2](https://arxiv.org/html/2606.27416v1#S3.SS2 "3.2 Verifiers: enforcing the principles ‣ 3 System ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents")– [3.4](https://arxiv.org/html/2606.27416v1#S3.SS4 "3.4 Subagent isolation and parallelism ‣ 3 System ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents")
describe how the principles above are enforced in practice.

1\. Papersread/summarize2\. Internetsearch/download3\. Codeprior tasks/libs6\. Analysismetrics/charts5\. Implementcode/train/eval4\. Planningapproach/budget7\. Lit. comparepublished work8\. Reportingresults/suggestions9\. PR & mergereview/correctlogged ⋅\\cdot spec-verified ⋅\\cdot corrected, not rewrittenFigure 2: The nine-step lifecycle every task passes through: papers
→\\rightarrow internet →\\rightarrow code →\\rightarrow planning
→\\rightarrow implementation →\\rightarrow analysis →\\rightarrow
literature comparison →\\rightarrow reporting →\\rightarrow PR & merge.
In complex tasks each step runs in its own subagent and writes to a
known place inside the task folder.

### 3.2 Verifiers: enforcing the principles

Rules are only rules if they are followed; structure is only real if
something checks it. Glite ARF’s verifier layer turns the
principles into deterministic Python scripts that fail loudly when
violated, so an agent cannot silently drift past a rule by claiming to
have followed it. Our companion BEA 2026 system paper describes the
same mechanism in its framework-overview section ( [Philippov et al., 2026](https://arxiv.org/html/2606.27416v1#bib.bib22 "")):
“task isolation (one directory, one branch, one pull request per
experiment), artefact specifications checked by verifiers before
commit, and an immutable log of every experiment step.”

Every artefact has a versioned specification. Framework-level
artefacts (task folders, results files, logs) live under
arf/specifications/. Asset-type artefacts (papers, datasets,
models, predictions, answers, suggestions, libraries) live under
meta/asset\_types/<kind>/specification.md. Specifications are
plain markdown with a numeric version field; files produced under a
spec carry a matching spec\_version field, so format
evolution is auditable rather than silent, and verifiers validate
each artefact against the version it was written under.

Each specification has a verifier script under
arf/scripts/verificators/ that parses the artefact and produces
error or warning diagnostics with stable codes (e.g. FD-E001: a mandatory task subdirectory is missing;
PM-E003: the task branch modified a file outside its folder).
Errors block commit and merge — enforced both by the
prestep/poststep lifecycle gate and as required pull-request checks —
while warnings surface concerns without blocking. Verifiers are
deliberately allowed to be noisy and duplicated: two verifiers
checking the same thing from different angles catch cases either alone
might miss.

What the verifiers deliberately do _not_ judge is semantic
validity — whether an experiment is well-designed or a baseline
appropriate. That judgement stays with the human researcher (role 1,
§ [6](https://arxiv.org/html/2606.27416v1#S6 "6 Lessons and Limits ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents")); the framework’s job is to make the structural
substrate trustworthy so that human judgement operates on a reliable
record.

### 3.3 Aggregators and the corrections overlay

Each datum has a single home — the task folder that produced it.
When the framework needs a combined view (every paper across every
task, every metric filtered by category, every cost summed across the
campaign), an aggregator script in arf/scripts/aggregators/
walks tasks/, applies filters and the corrections overlay, and
returns the canonical answer. Snapshot output is committed to
overview/ (principle 4) so humans can browse the materialised
view on GitHub without rerunning the scripts.

Completed task folders are immutable. When a downstream task discovers
an earlier result was wrong — a paper misclassified, a metric
mis-aggregated, a feature later determined to leak the target — it
does not reach back into the earlier task’s folder. It writes a small
correction file in its own corrections/ directory, and
aggregators apply the correction overlay at read time, returning the
effective view that incorporates every later fix while preserving the
original record.

This discipline addresses one of the campaign’s most concrete failure
modes (F07): a hand-maintained tracker/completed.md reporting
Completed Tasks (75 of 64) — an impossible count produced
by manual editing during a busy week. With aggregators replacing
manual cross-task summaries, the canonical answer is recomputable and
traceable.

### 3.4 Subagent isolation and parallelism

Complex tasks run as a chain of subagents — research, planning,
implementation, analysis, reporting — each with its own context
window and inputs scoped to what it needs. A research subagent that
has read fifty paper summaries does not pollute the planning
subagent that follows. This addresses a hard limit of current LLMs:
they degrade as context fills up. Splitting the work into
context-bounded stages keeps each one focused and gives the framework
a natural insertion point for verification between stages.

Tasks run in parallel by living in separate git worktrees on separate
branches (task/<task\_id>). The researcher opens a
coding-agent session per task; ARF supplies the worktree and branch
conventions, the verifier gates, and the merge discipline that let
many sessions run at once without interfering. Up to twelve sessions
ran simultaneously on a single 48 GB Mac during the BEA 2026 campaign
(Figure [3](https://arxiv.org/html/2606.27416v1#S3.F3 "Figure 3 ‣ 3.4 Subagent isolation and parallelism ‣ 3 System ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents")), and no merge conflict reached
main. The pattern matches concurrent prior work — EvoSkill
( [Alzubi et al., 2026](https://arxiv.org/html/2606.27416v1#bib.bib1 "")) frames each agent program as a git branch;
CORAL ( [Qu et al., 2026](https://arxiv.org/html/2606.27416v1#bib.bib23 "")) describes “isolated workspaces while
sharing access to the same evaluator and shared persistent memory” —
but in ARF the parallelism is at the _task_ granularity inside a
_campaign_, not at the agent granularity inside a single
optimisation problem. Section [5](https://arxiv.org/html/2606.27416v1#S5 "5 The framework in use ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents") quantifies this
concurrency across campaigns.

![Refer to caption](https://arxiv.org/html/2606.27416v1/figures/12_agents.png)Figure 3: Twelve agent sessions running in parallel on a single 48 GB
Mac during the BEA 2026 campaign; each tile is one
task/<task\_id> worktree. Figure [6](https://arxiv.org/html/2606.27416v1#S5.F6 "Figure 6 ‣ Parallelism, measured. ‣ 5 The framework in use ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents")
shows the analogous concurrency profile, measured over time, for the
WSD campaign (§ [5](https://arxiv.org/html/2606.27416v1#S5 "5 The framework in use ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents")).

## 4 Case Study: BEA 2026

This paper’s contribution is the framework; the companion BEA 2026
system paper ( [Philippov et al., 2026](https://arxiv.org/html/2606.27416v1#bib.bib22 "")) describes the prediction system, and
we summarise its results here only as the setting in which the
framework was exercised.

### 4.1 The shared task

BEA 2026 ( [Felice and Skidmore, 2026](https://arxiv.org/html/2606.27416v1#bib.bib7 "")) introduced an L1-aware
vocabulary-difficulty prediction task: given an English target word, a
partial-spelling clue, an L1 translation, and a context sentence in
the learner’s L1 (Spanish, German, or Mandarin), predict the word’s
psychometric difficulty as a continuous, GLMM-calibrated score.
Labels are derived from roughly 3.3M test responses produced by
100,000+100{,}000{+} test-takers on the British Council Knowledge-based
Vocabulary Lists ( [Schmitt et al., 2024](https://arxiv.org/html/2606.27416v1#bib.bib26 "")). The task scores by
RMSE (lower is better) and reports Pearson correlation as a secondary
metric. The closed track forbids generative LLMs, paid APIs, and
additional training data; the open track has no such restriction.

### 4.2 The campaign

We developed our submission inside Glite ARF over a multi-week
research campaign. The campaign comprised 273 tracked task folders
(146 of type experiment-run; 247 completed, 9 permanently
failed, 17 cancelled — App [F](https://arxiv.org/html/2606.27416v1#A6 "Appendix F Aggregator output snapshots ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents")) across 129 feature
sets totalling 1,161 numeric feature columns organised into seven
domain families plus a derived bucket. Every feature CSV, every
fold-level score, every commit message is visible in the project’s PR
history. Up to twelve agent sessions ran in parallel, orchestrated
from a single 48 GB Mac, with rented A100 instances used only for
scaled-encoder fine-tuning and decoder-LLM LoRA training. Third-party
cost was $449.69 in LLM API spend for feature engineering and model training (Anthropic $287.12, OpenAI
$162.57) plus $48.62 in rented A100 compute — $498.31 total — and
∼100{\\sim}100 wall-hours of local compute (App [C](https://arxiv.org/html/2606.27416v1#A3 "Appendix C Cost breakdown ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents")).
Aggregator snapshot excerpts appear in App [F](https://arxiv.org/html/2606.27416v1#A6 "Appendix F Aggregator output snapshots ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents").

### 4.3 Headline result

Our system placed first in the closed track on all three L1s and
second in the open track on all three L1s
(Table [2](https://arxiv.org/html/2606.27416v1#S4.T2 "Table 2 ‣ 4.3 Headline result ‣ 4 Case Study: BEA 2026 ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents")). The average RMSE reduction over the
official baseline was 29.9% closed-track (28.2% ES, 29.6% DE,
31.9% CN) and 35.9% open-track (37.1% ES, 34.5% DE, 36.2% CN).
The best single component is a LLaMA-3.1-8B LoRA regression head with
a K-fold RMSE of 0.831 at 0.13% trainable parameters.
Figure [4](https://arxiv.org/html/2606.27416v1#S4.F4 "Figure 4 ‣ 4.3 Headline result ‣ 4 Case Study: BEA 2026 ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents") shows best-so-far dev-set Pearson
across the campaign — from 0.78 at task t0001 to 0.91 by
task t0270, with most experiments producing no improvement
and a small number producing the large jumps that give the staircase
its shape. We show this only to illustrate the search dynamics: a
best-so-far curve is monotonic by construction, Pearson is the
secondary metric (the official objective is RMSE), and task index is
not wall-clock time in a parallel campaign.

![Refer to caption](https://arxiv.org/html/2606.27416v1/figures/progress_pearson_by_step_milestones.png)Figure 4: Best dev-set Pearson correlation across the BEA 2026
campaign, by step index (one step per tracked task). Most tracked
tasks leave the best-so-far value unchanged; a few produce a step.

| Track | System | ES (RMSE) | DE (RMSE) | CN (RMSE) | Avg |
| Closed | 1\. Ours | 0.903 | 0.885 | 0.776 | 0.855 |
| Closed | 2\. Best non-Glite, per L1† | 0.975 | 0.903 | 0.816 | — |
| Closed | Baseline | 1.257 | 1.258 | 1.140 | 1.218 |
| Open | 1\. Sakura | 0.742 | 0.723 | 0.630 | 0.698 |
| Open | 2\. Ours | 0.754 | 0.764 | 0.660 | 0.726 |
| Open | 3\. TeamXBC | 0.876 | 0.826 | 0.722 | 0.808 |
| Open | Baseline | 1.198 | 1.166 | 1.034 | 1.133 |

Table 2: Official BEA 2026 test-set leaderboard (RMSE, lower is
better). † The closed-track row is the
best _non-Glite_ result _per L1_ — uogal for ES
and DE, Sakura for CN — and is not a single system, so we
omit a cross-L1 average for it. Open-track rows are single teams.

### 4.4 Structured provenance caught the leakage

The campaign’s sharpest demonstration of verifier-driven research
is the leakage post-mortem reported in our BEA system paper
( [Philippov et al., 2026](https://arxiv.org/html/2606.27416v1#bib.bib22 "")). An intermediate ensemble (v13) scored an
implausibly strong K-fold RMSE of 0.609; because every feature CSV
carried a versioned specification and every fold-level score was
traceable to the code revision that produced it, we localised the
cause within minutes: four feature sets were leaking the target
variable.
outlier\_surgery passed the GLMM target into LLM prompts as
“actual difficulty.” cross\_l1\_oof used cross-L1
out-of-fold predictions with an item-id split shared across L1s.
heteroscedastic regressed on GLMM-score residuals.
annotation\_noise computed noise statistics from the GLMM
target. Each used the GLMM target that is available at
training/cross-validation time but not for hidden-test items, which is
precisely why they leaked. All four were quarantined into a
removed\_leaking\_features/ folder via the corrections overlay,
and the rebuilt v14 ensemble scored RMSE 0.802 — the corrected
estimate. The structural layer cannot judge that a feature is
_semantically_ leaking — that call was a human’s — but the
per-feature specifications and per-fold provenance turned what could
have been a silent contaminated submission into a fix made in minutes
and fully auditable after the fact. This is verifier-driven
research working as intended: structure makes the failure findable and
the correction trustworthy.

### 4.5 Compliance audit at scale

The closed track’s restrictions (no generative LLMs, no paid APIs, no
extra training data, no cross-L1 training) created a second governance
problem. These restrictions apply to the _submitted system_ —
its features and inference path — not to development assistance, so
using coding agents to author and run pipeline code is permitted while
LLM-derived features are not; keeping that line required per-feature
accounting. We developed a per-column compliance schema that records,
for each feature column, the external models, APIs, datasets, and
computation paths used to produce it, detailed in that paper’s
compliance-engineering section ( [Philippov et al., 2026](https://arxiv.org/html/2606.27416v1#bib.bib22 "")).
When the BEA organisers issued five rule clarifications in March
2026, the per-column metadata enabled a finer-grained audit than
feature-set-level checks would have: 17 features were reclassified
after the clarifications and our internal audit added two more,
leaving 57 of 129 feature sets (249 of 1,161 columns)
closed-track-eligible — a 56% rejection rate that forced a full
pipeline rebuild in the final week. We submitted a 469-line LLM-usage
disclosure with the closed-track system. The rebuilt closed-track
system retained its 1st-place ranking on every L1.

## 5 The framework in use

To characterise Glite ARF independently of any single result, we mined
the logs of two further ARF campaigns in different
domains: research-wsd (word-sense disambiguation; 167
completed tasks over 74 days) and research-ace-cefr (English
CEFR readability). Figures below derive from each campaign’s logs
(research-ace-cefr is public; the research-wsd logs
are author-held). Together with BEA, this is
three multi-week campaigns in
three domains driven by the same framework code
(Table [3](https://arxiv.org/html/2606.27416v1#S5.T3 "Table 3 ‣ 5 The framework in use ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents")).

|  | WSD | Ace-CEFR | BEA |
| Completed tasks | 167 | 35 | 247 |
| Experiment runs | 72 | 15 | 146 |
| Merged branches | 271 | 34 | — |
| Logged commands | 17,915 | 1,916 | — |
| Peak concurrency | 12 | 3 | 12 |
| Spend (USD) | 4,039 | 19 | 498 |

Table 3: Three ARF campaigns in three domains on identical framework
code. WSD and Ace-CEFR are mined from their campaign logs (Ace-CEFR
public; WSD author-held); BEA is from § [4](https://arxiv.org/html/2606.27416v1#S4 "4 Case Study: BEA 2026 ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents").

#### The structural machinery is cheap.

Classifying the 17,915 logged WSD commands, the framework’s own
scripts — verifiers, aggregators, run\_with\_logs, and the
lint/type/test gate — are about a quarter of all commands but only
∼1%{\\sim}1\\% of wall-clock time (Figure [5](https://arxiv.org/html/2606.27416v1#S5.F5 "Figure 5 ‣ The structural machinery is cheap. ‣ 5 The framework in use ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents"));
experiment work dominates runtime. Per-stage timing agrees: the
framework-administrative steps (branch creation, dependency checks,
folder init) take seconds, while implementation steps take tens of
minutes. Verifier-driven research buys its guarantees at negligible
time cost.

Figure 5: Command-level overhead (WSD): ARF’s own scripts are
∼25%{\\sim}25\\% of commands but ∼1%{\\sim}1\\% of wall-clock time.

#### Parallelism, measured.

Reconstructing in-flight tasks from their timestamps, the WSD campaign
sustained bursts of concurrent work peaking at twelve simultaneous
tasks (Figure [6](https://arxiv.org/html/2606.27416v1#S5.F6 "Figure 6 ‣ Parallelism, measured. ‣ 5 The framework in use ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents")), confirming the “up to twelve
agents” figure of § [3.4](https://arxiv.org/html/2606.27416v1#S3.SS4 "3.4 Subagent isolation and parallelism ‣ 3 System ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents") with data rather than
a screenshot. The profile is bursty, matching a human driving role 1
while many task agents run underneath.

Figure 6: Concurrent in-flight WSD tasks over the 74-day campaign;
peak twelve.

#### Isolation and portability hold across domains.

Across 305 merges in the two mined campaigns, no task corrupted
another task’s data or the shared main branch, and no merge
conflict reached main. The three campaigns span word-sense
disambiguation, readability, and vocabulary difficulty, yet the
framework code under arf/ is byte-for-byte identical: only
project/, tasks/, and meta/ differ. The framework
transfers across domains without modification.

## 6 Lessons and Limits

#### The structural layer is cheap.

A natural worry is that wrapping every command, verifying every
artefact, and re-reading specifications at each step is expensive. It
is not: across the campaigns the framework’s own machinery accounts for
about a quarter of all commands but only ∼1%{\\sim}1\\% of wall-clock time
(§ [5](https://arxiv.org/html/2606.27416v1#S5 "5 The framework in use ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents")). The BEA campaign cost approximately $450 in LLM
API spend ($498 total third-party) across 273 tracked tasks — low
per experiment. The overhead is intentional and well spent: when an
agent in week eight needs to know what an agent in week one actually
did, the answer comes from a recorded, verified artefact, not a guess.

#### Human-in-the-loop is intentional, not interim.

Role 1 in our three-role stack — choosing which hypotheses to test
next — is human-driven by design, not because we are waiting for
stronger models. The METR time-horizon study
( [Kwa et al., 2025](https://arxiv.org/html/2606.27416v1#bib.bib17 "")) measures the task length at which a model
succeeds half the time at roughly one hour for the strongest model it
evaluated, with the more reliable 80% horizon far shorter; a research
campaign runs for weeks. The AI Scientist v1 ( [Lu et al., 2024](https://arxiv.org/html/2606.27416v1#bib.bib20 "")) was
evaluated by [Beel et al. (2025)](https://arxiv.org/html/2606.27416v1#bib.bib3 ""), which found that 42% of its
generated experiments failed due to coding errors — exactly the
failure mode that emerges when the strategic-decision role is
delegated to current models. We make a different bet: keep role 1
human, delegate role 2 entirely, and put deterministic Python scripts
on role 3.

#### What verifiers do not catch.

Verifiers are deterministic; they catch structural errors
— files outside the task folder modified, logs missing, JSON
malformed against its spec, fold-level scores untraceable to a code
revision. They do not catch semantic errors — a wrong analysis, a
wrong baseline, a methodologically inappropriate but plausible-looking
experimental design. [Schmidgall et al. (2025)](https://arxiv.org/html/2606.27416v1#bib.bib25 "") report that
automated paper-quality evaluation overestimates human reviewer
scores by ∼2{\\sim}2 points; we expect the same gap in any
verifier-style evaluation of scientific merit. Glite ARF’s
contribution is that it makes a class of structural failures
_detectable and auditable_ while leaving semantic judgement where
it belongs — with the human researcher (role 1).

#### Limitations.

Two further limits are worth stating plainly. First, ARF assumes a
_single_ human operator: its task-index and merge conventions are
not designed for several people driving role 1 concurrently, which
would risk index collisions and duplicated work. Second, the
verifiers are not agent-proof — they are ordinary scripts in the
repository, so an agent explicitly instructed to bypass a rule can
weaken or rewrite the verifier that checks it. ARF targets
accidental agent drift in a non-adversarial setting, not a determined
or adversarial agent.

## 7 Availability

Glite ARF ( [Glite Tech Ltd et al., 2026](https://arxiv.org/html/2606.27416v1#bib.bib10 "")) is released under the Apache 2.0
licence (version 0.1.0) at
[https://github.com/GliteTech/glite-arf](https://github.com/GliteTech/glite-arf ""). A public ARF
demo project accompanies it: English CEFR readability
( [https://github.com/GliteTech/research-ace-cefr](https://github.com/GliteTech/research-ace-cefr "")). The
framework code under arf/ is identical across all three
campaigns; only project/, tasks/, and meta/ carry
project-specific content (§ [5](https://arxiv.org/html/2606.27416v1#S5 "5 The framework in use ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents")).
Appendix [D](https://arxiv.org/html/2606.27416v1#A4 "Appendix D Observed failure modes ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents") summarises the failure modes that
shaped the design.

#### Future work.

We plan automatic citation verification (motivated by F05), per-column
compliance audits as a reusable methodological contribution,
heartbeat-style periodic agent reflection adapted from CORAL
( [Qu et al., 2026](https://arxiv.org/html/2606.27416v1#bib.bib23 "")), and a controlled study — seeding the
Appendix [D](https://arxiv.org/html/2606.27416v1#A4 "Appendix D Observed failure modes ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents") incidents into test repositories —
to measure verifier detection rates directly. Replacing role 1 with
an autonomous brainstorming agent is not a near-term priority — see
above.

## Ethics Statement

Glite ARF runs LLM coding agents (Claude Code, Codex CLI)
autonomously on the operator’s machine, with shell execution, file
writes, git push permissions, and paid API calls. The
framework’s verifier layer enforces structural integrity, but it is
not a security sandbox: it does not constrain what an agent’s shell
commands can do to the host machine. The repository ships a permissive
.claude/settings.json suitable for research environments and
documents the security trade-offs in
arf/docs/explanation/safety.md;
operators on machines with sensitive data should narrow the
allow-list before running.

The BEA 2026 dataset is distributed under the British Council’s
Knowledge-based Vocabulary Lists licence
( [Schmitt et al., 2024](https://arxiv.org/html/2606.27416v1#bib.bib26 "")); we used it under the shared-task
agreement. No personally identifying information appears in any
artefact released with this paper. LLM API spend for the BEA campaign
was approximately $450 ($498 total third-party cost including rented
compute) and is itemised in Appendix [C](https://arxiv.org/html/2606.27416v1#A3 "Appendix C Cost breakdown ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents"). Our campaign ran
predominantly on a 48 GB Mac (CPU/GPU) and on rented A100 GPU hours;
we did not measure carbon emissions and therefore do not characterise
the campaign’s footprint.

The framework lowers the cost of running multi-agent research
campaigns. We acknowledge that the same lowered cost could be used
to run campaigns whose hypotheses are not socially beneficial; the
framework imposes structure on _how_ research is conducted, not
on _what_ is researched. Role 1 in the three-role stack
(hypothesis selection) remains human, in part for the structural
reasons argued in § [6](https://arxiv.org/html/2606.27416v1#S6 "6 Lessons and Limits ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents") and in part because the human
is where ethical accountability lives.

## References

- Alzubi et al. (2026)
Salaheddin Alzubi, Noah Provenzano, Jaydon Bingham, Weiyuan Chen, and Tu Vu.
2026.

[EvoSkill: Automated skill\\
discovery for multi-agent systems](https://arxiv.org/abs/2603.02766 "").

_Preprint_, arXiv:2603.02766.

- Anthropic (2025)
Anthropic. 2025.

Claude code.

[https://www.anthropic.com/claude-code](https://www.anthropic.com/claude-code "").

- Beel et al. (2025)
Joeran Beel, Min-Yen Kan, and Moritz Baumgart. 2025.

[Evaluating Sakana’s AI\\
scientist: Bold claims, mixed results, and a promising future?](https://arxiv.org/abs/2502.14297 "")_Preprint_, arXiv:2502.14297.

- Chan et al. (2025)
Jun Shern Chan, Neil Chowdhury, Oliver Jaffe, James Aung, Dane Sherburn, Evan
Mays, Giulio Starace, Kevin Liu, Leon Maksin, Tejal Patwardhan, Lilian Weng,
and Aleksander Mądry. 2025.

[MLE-bench: Evaluating\\
machine learning agents on machine learning engineering](https://arxiv.org/abs/2410.07095 "").

In _The Thirteenth International Conference on Learning_
_Representations (ICLR)_.

- Chen et al. (2025)
Hui Chen, Miao Xiong, Yujie Lu, Wei Han, Ailin Deng, Yufei He, Jiaying Wu, Yibo
Li, Yue Liu, and Bryan Hooi. 2025.

[MLR-Bench: Evaluating\\
AI agents on open-ended machine learning research](https://arxiv.org/abs/2505.19955 "").

_Preprint_, arXiv:2505.19955.

NeurIPS 2025 Datasets & Benchmarks Track.

- CrewAI Inc. (2023)
CrewAI Inc. 2023.

CrewAI: Framework for orchestrating role-playing, autonomous AI
agents.

GitHub: [https://github.com/crewAIInc/crewAI](https://github.com/crewAIInc/crewAI "").

- Felice and Skidmore (2026)
Mariano Felice and Lucy Skidmore. 2026.

Findings of the BEA 2026 shared task on vocabulary difficulty
prediction for English learners.

In _Proceedings of the 21st Workshop on Innovative Use of NLP_
_for Building Educational Applications (BEA 2026)_, San Diego, California.
Association for Computational Linguistics.

To appear; co-located with ACL 2026.

- Gauthier (2023)
Paul Gauthier. 2023.

Aider: AI pair programming in your terminal.

GitHub: [https://github.com/Aider-AI/aider](https://github.com/Aider-AI/aider "").

- Glite Tech Ltd (2026)
Glite Tech Ltd. 2026.

research-ace-cefr: A public Glite ARF demo project on
conversational-text CEFR difficulty prediction.

[https://github.com/GliteTech/research-ace-cefr](https://github.com/GliteTech/research-ace-cefr "").

Apache-2.0 license.

- Glite Tech Ltd et al. (2026)
Glite Tech Ltd, Vassili Philippov, Pavel Katunin, Dmitry Andreev, and Igor
Ostanin. 2026.

Glite autonomous research framework (glite arf).

[https://github.com/GliteTech/glite-arf](https://github.com/GliteTech/glite-arf "").

Version 0.1.0, Apache-2.0 license.

- Hong et al. (2024)
Sirui Hong, Mingchen Zhuge, Jiaqi Chen, Xiawu Zheng, Yuheng Cheng, Ceyao Zhang,
Jinlin Wang, Zili Wang, Steven Ka Shing Yau, Zijuan Lin, Liyang Zhou, Chenyu
Ran, Lingfeng Xiao, Chenglin Wu, and Jürgen Schmidhuber. 2024.

[MetaGPT: Meta programming\\
for a multi-agent collaborative framework](https://arxiv.org/abs/2308.00352 "").

In _The Twelfth International Conference on Learning_
_Representations (ICLR)_.

- Hu et al. (2025)
Shengran Hu, Cong Lu, and Jeff Clune. 2025.

[Automated design of agentic\\
systems](https://arxiv.org/abs/2408.08435 "").

_Preprint_, arXiv:2408.08435.

ICLR 2025.

- Huang et al. (2024)
Qian Huang, Jian Vora, Percy Liang, and Jure Leskovec. 2024.

[MLAgentBench: Evaluating\\
language agents on machine learning experimentation](https://arxiv.org/abs/2310.03302 "").

In _Proceedings of the 41st International Conference on Machine_
_Learning (ICML)_.

- Jimenez et al. (2024)
Carlos E. Jimenez, John Yang, Alexander Wettig, Shunyu Yao, Kexin Pei, Ofir
Press, and Karthik Narasimhan. 2024.

[SWE-bench: Can language\\
models resolve real-world GitHub issues?](https://arxiv.org/abs/2310.06770 "")In _The Twelfth International Conference on Learning_
_Representations (ICLR)_.

- Karpathy (2026)
Andrej Karpathy. 2026.

autoresearch: AI agents running research on single-GPU nanochat
training automatically.

GitHub: [https://github.com/karpathy/autoresearch](https://github.com/karpathy/autoresearch "").

- Kogan et al. (2025)
David Kogan, Max Schumacher, Sam Nguyen, Masanori Suzuki, Melissa Smith,
Chloe Sophia Bellows, and Jared Bernstein. 2025.

[Ace-CEFR: A dataset for\\
automated evaluation of the linguistic difficulty of conversational texts for\\
LLM applications](https://arxiv.org/abs/2506.14046 "").

_Preprint_, arXiv:2506.14046.

- Kwa et al. (2025)
Thomas Kwa, Ben West, Joel Becker, Amy Deng, Katharyn Garcia, Max Hasin, Sami
Jawhar, Megan Kinniment, Nate Rush, Sydney Von Arx, Ryan Bloom, Thomas
Broadley, Haoxing Du, Brian Goodrich, Nikola Jurkovic, Luke Harold Miles,
Seraphina Nix, Tao Lin, Neev Parikh, and 6 others. 2025.

[Measuring AI ability to\\
complete long software tasks](https://arxiv.org/abs/2503.14499 "").

_Preprint_, arXiv:2503.14499.

- Li et al. (2023)
Guohao Li, Hasan Abed Al Kader Hammoud, Hani Itani, Dmitrii Khizbullin, and
Bernard Ghanem. 2023.

[CAMEL: Communicative\\
agents for “mind” exploration of large language model society](https://arxiv.org/abs/2303.17760 "").

In _Advances in Neural Information Processing Systems_
_(NeurIPS)_.

- Liu et al. (2024)
Xiao Liu, Hao Yu, Hanchen Zhang, Yifan Xu, Xuanyu Lei, Hanyu Lai, Yu Gu,
Hangliang Ding, Kaiwen Men, Kejuan Yang, Shudan Zhang, Xiang Deng, Aohan
Zeng, Zhengxiao Du, Chenhui Zhang, Sheng Shen, Tianjun Zhang, Yu Su, Huan
Sun, and 3 others. 2024.

[AgentBench: Evaluating\\
LLMs as agents](https://arxiv.org/abs/2308.03688 "").

_Preprint_, arXiv:2308.03688.

ICLR 2024.

- Lu et al. (2024)
Chris Lu, Cong Lu, Robert Tjarko Lange, Jakob Foerster, Jeff Clune, and David
Ha. 2024.

[The AI scientist: Towards\\
fully automated open-ended scientific discovery](https://arxiv.org/abs/2408.06292 "").

_Preprint_, arXiv:2408.06292.

- OpenAI (2025)
OpenAI. 2025.

Codex CLI: a lightweight coding agent that runs in your terminal.

GitHub: [https://github.com/openai/codex](https://github.com/openai/codex "").

- Philippov et al. (2026)
Vassili Philippov, Dmitrii Andreev, Pavel Katunin, and Anton Nikolaev. 2026.

[Glite at BEA\\
2026 shared task 1: Holistic difficulty models dominate, feature engineering\\
closes the gap in L1-aware vocabulary difficulty prediction](https://aclanthology.org/2026.bea-1.78/ "").

In _Proceedings of the 21st Workshop on Innovative Use of NLP_
_for Building Educational Applications (BEA 2026)_. Association for
Computational Linguistics.

To appear.

- Qu et al. (2026)
Ao Qu, Han Zheng, Zijian Zhou, Yihao Yan, Yihong Tang, Shao Yong Ong, Fenglu
Hong, Kaichen Zhou, Chonghe Jiang, Minwei Kong, Jiacheng Zhu, Xuan Jiang,
Sirui Li, Cathy Wu, Bryan Kian Hsiang Low, Jinhua Zhao, and Paul Pu Liang.
2026.

[CORAL: Towards autonomous\\
multi-agent evolution for open-ended discovery](https://arxiv.org/abs/2604.01658 "").

_Preprint_, arXiv:2604.01658.

- Roucher et al. (2025)
Aymeric Roucher, Albert Villanova del Moral, Thomas Wolf, Leandro von Werra,
and Erik Kaunismäki. 2025.

smolagents: a barebones library for agents that think in code.

GitHub: [https://github.com/huggingface/smolagents](https://github.com/huggingface/smolagents "").

- Schmidgall et al. (2025)
Samuel Schmidgall, Yusheng Su, Ze Wang, Ximeng Sun, Jialian Wu, Xiaodong Yu,
Jiang Liu, Michael Moor, Zicheng Liu, and Emad Barsoum. 2025.

[Agent laboratory: Using\\
LLM agents as research assistants](https://arxiv.org/abs/2501.04227 "").

_Preprint_, arXiv:2501.04227.

- Schmitt et al. (2024)
Norbert Schmitt, Karen Dunn, Barry O’Sullivan, Laurence Anthony, and Benjamin
Kremmel. 2024.

[_Knowledge-based_\\
_Vocabulary Lists_](https://doi.org/10.3138/9781800504158 ""), volume 5 of _British Council Monographs on Modern_
_Language Testing_.

University of Toronto Press.

- SHL0MS and Hermes Agent (2026)
SHL0MS and Hermes Agent. 2026.

Autoreason: Self-refinement that knows when to stop.

Nous Research: [https://github.com/NousResearch/autoreason](https://github.com/NousResearch/autoreason "").

- Tang et al. (2025)
Jiabin Tang, Lianghao Xia, Zhonghang Li, and Chao Huang. 2025.

[AI-Researcher: Autonomous\\
scientific innovation](https://arxiv.org/abs/2505.18705 "").

_Preprint_, arXiv:2505.18705.

- Wang et al. (2024)
Xingyao Wang, Boxuan Li, Yufan Song, Frank F. Xu, Xiangru Tang, Mingchen Zhuge,
Jiayi Pan, Yueqi Song, Bowen Li, Jaskirat Singh, Hoang H. Tran, Fuqiang Li,
Ren Ma, Mingzhang Zheng, Bill Qian, Yanjun Shao, Niklas Muennighoff, Yizhe
Zhang, Binyuan Hui, and 5 others. 2024.

[OpenHands: An open\\
platform for AI software developers as generalist agents](https://arxiv.org/abs/2407.16741 "").

_Preprint_, arXiv:2407.16741.

Accepted at ICLR 2025.

- Wu et al. (2023)
Qingyun Wu, Gagan Bansal, Jieyu Zhang, Yiran Wu, Beibin Li, Erkang Zhu,
Li Jiang, Xiaoyun Zhang, Shaokun Zhang, Jiale Liu, Ahmed Hassan Awadallah,
Ryen W. White, Doug Burger, and Chi Wang. 2023.

[AutoGen: Enabling\\
next-gen LLM applications via multi-agent conversation](https://arxiv.org/abs/2308.08155 "").

_Preprint_, arXiv:2308.08155.

- Yamada et al. (2025)
Yutaro Yamada, Robert Tjarko Lange, Cong Lu, Shengran Hu, Chris Lu, Jakob
Foerster, Jeff Clune, and David Ha. 2025.

[The AI scientist-v2:\\
Workshop-level automated scientific discovery via agentic tree search](https://arxiv.org/abs/2504.08066 "").

_Preprint_, arXiv:2504.08066.

- Yang et al. (2024)
John Yang, Carlos E. Jimenez, Alexander Wettig, Kilian Lieret, Shunyu Yao,
Karthik Narasimhan, and Ofir Press. 2024.

[SWE-agent: Agent-computer\\
interfaces enable automated software engineering](https://arxiv.org/abs/2405.15793 "").

In _Advances in Neural Information Processing Systems_
_(NeurIPS)_.

- Zheng et al. (2025)
Tianshi Zheng, Zheye Deng, Hong Ting Tsang, Weiqi Wang, Jiaxin Bai, Zihao Wang,
and Yangqiu Song. 2025.

[From automation to\\
autonomy: A survey on large language models in scientific discovery](https://arxiv.org/abs/2505.13259 "").

_Preprint_, arXiv:2505.13259.

EMNLP 2025 Main.


## Appendix A Task folder structure

Every ARF task lives in tasks/tNNNN\_<slug>/ on a branch called
task/<task\_id>. The folder follows a fixed layout
(Listing [1](https://arxiv.org/html/2606.27416v1#LST1 "Listing 1 ‣ Appendix A Task folder structure ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents")); the verifier
verify\_task\_folder.py (prefix FD) rejects any commit
that adds a top-level file outside the listed set or omits a mandatory
subdirectory.

Listing 1: On-disk layout of a single ARF task
folder.

[⬇](data:text/plain;base64,dGFza3MvdDAwNDJfZXhhbXBsZV90YXNrLwogIHRhc2suanNvbiwgc3RlcF90cmFja2VyLmpzb24KICBwbGFuLywgcmVzZWFyY2gvCiAgYXNzZXRzL3twYXBlcnMsZGF0YXNldHMsbGlicmFyaWVzLGFuc3dlcnMsCiAgICAgICAgICBzdWdnZXN0aW9ucyxtb2RlbHMscHJlZGljdGlvbnN9LwogIHJlc3VsdHMve3N1bW1hcmllcyxtZXRyaWNzLGNvc3RzLGltYWdlc30vCiAgY29ycmVjdGlvbnMvLCBpbnRlcnZlbnRpb24vCiAgbG9ncy97Y29tbWFuZHMsc3RlcHMsc2VhcmNoZXMsc2Vzc2lvbnN9Lw==)

tasks/t0042\_example\_task/

task.json,step\_tracker.json

plan/,research/

assets/{papers,datasets,libraries,answers,

suggestions,models,predictions}/

results/{summaries,metrics,costs,images}/

corrections/,intervention/

logs/{commands,steps,searches,sessions}/

The public PR for the corresponding worked example
(tasks/t0042\_example\_task/) is linked from the framework
README. Reviewers can browse the actual task folder there to see
what each subdirectory contains in practice.

## Appendix B Verifier catalogue and log spec

### B.1 Verifier scripts

Verifiers live under arf/scripts/verificators/. Each script
parses a class of artefact and emits diagnostic codes of the form
<2-CHAR>-<E\|W>NNN. Errors block commit and merge (via the
prestep/poststep gate and required pull-request checks); warnings
surface concerns without blocking. A representative subset of the
shipped scripts:

- •


verify\_task\_folder.py (FD) — structural
integrity of tasks/<id>/: the mandatory subdirectory layout
and required files.

- •


verify\_task\_results.py (TR) and
verify\_metrics.py (MT) — presence and format of
results/ files (metrics.json,
results\_summary.md); cross-checks the step tracker against
produced artefacts.

- •


verify\_logs.py (LG) — log presence and
structure against arf/specifications/logs\_specification.md.

- •


verify\_pr\_premerge.py (PM) — the pre-merge
gate; PM-E003 rejects a commit that modifies files outside
the task folder beyond the allow-list, and the immutability check
rejects edits to merged tasks.

- •


verify\_corrections.py (CR) — every
correction file targets an existing earlier task and follows the
correction schema.

- •


Asset-type verifiers under
meta/asset\_types/<kind>/verificator.py — per-asset-type
specifications for papers, datasets, models, predictions, answers,
suggestions, and libraries.


Every specification has a corresponding verifier, so each artefact
class an agent can produce is checked before it is committed.

### B.2 Per-step log format

Logs live under the task’s logs/ directory in four mandatory
subdirectories (logs specification v5), summarised in
Table [4](https://arxiv.org/html/2606.27416v1#A2.T4 "Table 4 ‣ B.2 Per-step log format ‣ Appendix B Verifier catalogue and log spec ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents").

| Subdirectory | Contents |
| commands/ | one JSON record per CLI invocation |
|  | (command, exit\_code, |
|  | timestamp) plus .stdout.txt |
|  | and .stderr.txt side-files |
| steps/ | one folder per step; step\_log.md |
|  | with YAML frontmatter |
| searches/ | one record per internet search query |
| sessions/ | agent session-capture outputs |

Table 4: Log directory layout (specification v5). Command logs are
auto-generated by run\_with\_logs.py, which wraps every CLI
invocation in a task branch.

## Appendix C Cost breakdown

Total third-party cost for the BEA 2026 campaign was $498.31, of
which LLM API spend was $449.69 (Anthropic $287.12, OpenAI $162.57)
and rented A100 compute (Vast.ai) was $48.62; on top of this the
campaign used ∼100{\\sim}100 wall-hours of local compute on a 48 GB Mac
(see App [F](https://arxiv.org/html/2606.27416v1#A6 "Appendix F Aggregator output snapshots ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents") for the aggregator snapshot these
figures come from). Table [5](https://arxiv.org/html/2606.27416v1#A3.T5 "Table 5 ‣ Appendix C Cost breakdown ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents") reports the
highest-LLM-cost feature experiments, drawn from the campaign’s
per-task cost aggregator (App [F](https://arxiv.org/html/2606.27416v1#A6 "Appendix F Aggregator output snapshots ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents")).

| Feature experiment | Cost ($) | Δ\\DeltaRMSE |
| --- | --- | --- |
| LLM rubric (4o-mini, full pool) | 1.93 | −0.015-0.015 |
| LLM rubric (4o-mini, ablation) | 9.72 | −0.012-0.012 |
| LLM-WSD (gpt-4o) | 36.14 | −0.008-0.008 |
| Polysemy contrast (LLM) | 22.47 | −0.004-0.004 |
| Counterfactual cue sensitivity | 41.38 | −0.011-0.011 |
| Annotation-noise LLM (leaking) | 14.52 | —† |

Table 5: Highest-cost LLM-API feature experiments and their effect
on full-system K-fold RMSE. † The
annotation\_noise feature was one of the four leaking
sets quarantined by the audit described in
§ [4.4](https://arxiv.org/html/2606.27416v1#S4.SS4 "4.4 Structured provenance caught the leakage ‣ 4 Case Study: BEA 2026 ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents") and was excluded from the final
ensemble.

We distinguish two cost categories.

#### Per-experiment cost.

The cost of running a feature experiment itself — LLM-rubric
queries, decoder-LLM LoRA training calls, paid embedding lookups.
This is what Table [5](https://arxiv.org/html/2606.27416v1#A3.T5 "Table 5 ‣ Appendix C Cost breakdown ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents") reports and what drives the
$449.69 LLM API total. These figures cover paid LLM _API_ calls
for feature engineering and model training only; the Claude Code and
Codex coding agents that authored and ran the pipeline operated under
flat-rate subscriptions during the campaign, so their token usage
carried no per-task marginal cost and is not part of the $449.69.
Teams paying metered per-token rates for the agents should budget for
that separately.

#### Framework overhead.

The structural machinery — run\_with\_logs command wrapping,
spec checks, verifier runs, aggregator materialisation, and the
subagent pipeline — is cheap in wall-clock terms: across campaigns it
is about a quarter of all commands but only ∼1%{\\sim}1\\% of wall-clock
time (§ [5](https://arxiv.org/html/2606.27416v1#S5 "5 The framework in use ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents"), Fig. [5](https://arxiv.org/html/2606.27416v1#S5.F5 "Figure 5 ‣ The structural machinery is cheap. ‣ 5 The framework in use ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents")). The added
token cost per task is modest relative to the experiment work itself,
and is the intended price of a fully recorded, verifiable research
trail.

## Appendix D Observed failure modes

Table [D](https://arxiv.org/html/2606.27416v1#A4 "Appendix D Observed failure modes ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents") summarises five representative failure
classes observed during the BEA 2026 campaign and the framework
principle each one motivated
(App [F](https://arxiv.org/html/2606.27416v1#A6 "Appendix F Aggregator output snapshots ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents") excerpts the campaign snapshots). Several
incidents occurred under earlier versions of the framework and
motivated specific later additions; the per-feature-CSV
specifications added in response to F01 are what later made the
leakage in § [4.4](https://arxiv.org/html/2606.27416v1#S4.SS4 "4.4 Structured provenance caught the leakage ‣ 4 Case Study: BEA 2026 ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents") _auditable_ — the
audit itself was human-driven, not triggered by a verifier.

| Class (ref.) | Concrete example | Motivated principle |
| --- | --- | --- |
| Data corruption (F02) | Step 146 reran train+dev+test; 38 feature sets<br>corrupted | Task isolation; immutability |
| Semantic invalidity (F01, F04) | outlier\_surgery leaked<br>target labels; v13 RMSE 0.609 →\\rightarrow v14 0.802 | Spec-verified artefacts; corrections overlay |
| Stale summaries (F07) | Completed Tasks (75 of 64) from manual<br>tracker editing | Aggregators-only reading; materialised overview |
| Citation hallucination (F05) | RemBERT BibTeX had 3 of 5 coauthors<br>hallucinated | Future citation verifier |
| Resource state drift (F06) | A100 status left as “Running step 323”<br>after no result report | Future teardown verifier |

Table 6: Five representative failure modes and the framework
principles each one motivated. References in parentheses resolve to
the full incident catalogue.

We adopt the deliberately bounded language “motivated” rather than
“prevented” or “solved.” Verifiers catch a class of
structural error; semantic errors such as F01 and F04 (target
leakage in generated feature code) become _auditable_ once the
artefact is spec-verified, but the audit itself is run by a
human. § [6](https://arxiv.org/html/2606.27416v1#S6 "6 Lessons and Limits ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents") returns to this distinction.

## Appendix E Secondary case study: Ace-CEFR

| Task type | Tasks |
| --- | --- |
| experiment-run | 11 |
| build-model | 6 |
| baseline-evaluation | 4 |
| download-paper | 3 |
| comparative-analysis | 3 |
| feature-engineering | 2 |
| download-dataset | 2 |
| literature-survey | 2 |
| data-analysis | 2 |
| others (8 task types) | 3 |
| Total | 38 |

Table 7: Public Ace-CEFR task-type breakdown.
All counts use generic ARF template types; the project adds no
project-specific task types. These counts assign each task a single
type and sum to 38; the experiment-run figure in
Table [3](https://arxiv.org/html/2606.27416v1#S5.T3 "Table 3 ‣ 5 The framework in use ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents") (15) instead counts every task
_tagged_ experiment-run, as a task may carry several
types.

We illustrate reuse with a public ARF project in a related
domain. research-ace-cefr( [Glite Tech Ltd, 2026](https://arxiv.org/html/2606.27416v1#bib.bib9 "")) is
author-run and still in progress, so it shows reuse rather than
independent adoption. It targets English CEFR readability on the
Ace-CEFR benchmark ( [Kogan et al., 2025](https://arxiv.org/html/2606.27416v1#bib.bib16 "")): 890 conversational
passages labelled on the CEFR 1–6 scale, split 445 train / 445 test.
The project aims to beat the published BERT + PaLM ensemble baseline
(0.33 MSE) under a stratified split that does not tune on test.

The snapshot contains 38 task folders across 17 task types
(Table [E](https://arxiv.org/html/2606.27416v1#A5 "Appendix E Secondary case study: Ace-CEFR ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents")); 35 have executed and 3 are
queued as planned next steps. The materialised overview/
dashboard is committed to the repository, so readers can browse
metrics, per-task status, and corrections on GitHub without rerunning
code. Ace-CEFR shares no project-specific code with the BEA campaign:
arf/ is identical, while project/, tasks/, and
meta/ carry project-specific content.

## Appendix F Aggregator output snapshots

Aggregator output snapshots were taken on 2026-05-06;
Listing [2](https://arxiv.org/html/2606.27416v1#LST2 "Listing 2 ‣ Appendix F Aggregator output snapshots ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents") shows representative excerpts.
Every quantitative claim in
§ [4](https://arxiv.org/html/2606.27416v1#S4 "4 Case Study: BEA 2026 ‣ Glite ARF: Verifier-Driven Research withParallel LLM Coding Agents") traces to one of these files.

Listing 2: Aggregator snapshot excerpts.

[⬇](data:text/plain;base64,ZGF0ZT0yMDI2LTA1LTA2OyB0YXNrcz0yNzMvMjQ3LzkvMTcKdHlwZXM9ZXhwZXJpbWVudC1ydW46MTQ2LCBmZWF0dXJlLWVuZ2luZWVyaW5nOjU0LCBidWlsZC1tb2RlbDoxOQpjb3N0PSQ0OTguMzE7IG1ldHJpY3MgdDAwMDE9Ljc4MS8xLjE0MyAtPiB0MDI3MD0uOTExLy44MDI=)

date=2026-05-06;tasks=273/247/9/17

types=experiment-run:146,feature-engineering:54,build-model:19

cost=$498.31;metricst0001=.781/1.143->t0270=.911/.802