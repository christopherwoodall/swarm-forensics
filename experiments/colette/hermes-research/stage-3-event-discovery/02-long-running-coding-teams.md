# Long-running coding teams

Research cutoff: 2026-10-01. Citation IDs belong to the Stage 3 ledger, not the parent collection.

Retained as executed engineering investigations with concrete coordination and failure mechanics. Neither artifact is treated as a validated production deployment.

## S3-COMPILER — Anthropic: sixteen Claudes building a C compiler

Classification: executed provider capability stress test.

### 1. What happened

Nicholas Carlini’s February 5, 2026 disclosure describes sixteen Opus 4.6 agents constructing a Rust C compiler across two weeks and nearly 2,000 Claude Code sessions, at just under $20,000.[14]
Exact run boundaries are not supplied.[14]
Reported outputs include bootable Linux 6.9 builds on x86, ARM and RISC-V and approximately 99% pass rates on most compiler test suites.[14]
This is an executed capability stress test, not a production compiler deployment.[14]

### 2. Why it is relevant

The meaningful phenomenon is artifact-mediated task allocation among simultaneous writers, not 100,000 lines of generated code.[14]
Agents claim work, incorporate others’ commits and select subsequent tasks without an orchestration agent.[14]
The revealing collective failure came at the Linux build: all sixteen encountered the same blocking bug, duplicated its repair and overwrote one another.[14]
Increasing population did not help until the human changed the task’s decomposition.[14]

### 3. What evidence exists

The primary engineering account specifies locks, containers, merges, test sampling and interventions; the public repository provides task-lock directories and commit links.[14][21]
The repository’s human-authored disclaimer says the code has not been validated for correctness and that generated documentation may make false claims.[21]
No independent compiler conformance or security evaluation is present in this bundle.[14][21]
Build success is narrower than language correctness.[14][21]

### 4. Autonomy and control topology

A human specified the compiler goal and some architecture, designed and revised the verifier, introduced CI, assigned specialist roles and devised the GCC oracle.[14]
Within that environment, peer agents choose the next problem, implement fixes, resolve conflicts and maintain progress notes; no high-level orchestrator is used.[14]
The loop starts new sessions repeatedly, rather than one persistent agent thinking for two weeks.[14]
This is decentralized task selection on centrally provided infrastructure, with substantive human feedback engineering—not “humans never intervened.”[14]

### 5. Coordination substrate

Each Docker container clones a shared bare Git repository.[14]
An agent writes a task file under `current_tasks/`; Git synchronization makes a competing claimant select another task.[14]
It then works, pulls and merges upstream changes, pushes and releases its lock.[14]
READMEs, progress files and failed-approach notes help replacement sessions orient themselves.[14]
Tests provide the action–feedback–next-action loop; deterministic per-agent subsampling reduces wasted test time.[14]
Shared Git is therefore an operational coordination medium, not merely an evidentiary archive.[14]

### 6. Strong claims versus speculative claims

Strong as an operator disclosure: agents continued work, collided on a common blocker and benefited from a human-built GCC differential oracle that split kernel files across agents; some failures still required delta-debugging pairs of files.[14]
New features repeatedly regressed existing functionality.[14]
Remaining limits include a GCC fallback for x86 16-bit boot code, buggy assembler/linker work, poor generated-code efficiency and failure to be a drop-in compiler.[14]
Generated README claims of standalone tooling and drop-in compatibility must not override the human account or disclaimer; this bundle cannot establish that those limitations were subsequently resolved.[14][21]
Neither test pass rate nor autonomous code volume demonstrates emergent intelligence.[14]

### 7. Distinctness

A separate Anthropic engineering episode from the excluded August 13 emerging-multiagent experiments; a compiler-construction workload, not the excluded exfiltration, wiki-collusion or PixelLeak families.[14]
Distinct from Cursor in operator, model, activity episode and topology: peer task locks plus a human-engineered oracle, versus recursive planning and assigned workers.[14][15]
Earlier Claude compiler benchmarks mentioned in the same disclosure are not additional cases.[14]

## S3-FASTRENDER — Cursor: FastRender’s long-running many-agent browser experiment

Classification: executed provider research project with independent limited artifact check.

### 1. What happened

Cursor disclosed the experiment on January 14, 2026; Wilson Lin’s January 23 interview adds operational detail.[15][16]
FastRender originated as his November 2025 side project before becoming a Cursor research project.[16]
The January disclosure reports a browser run of close to a week; the interview places the longest uninterrupted autonomous run at about one week, within a research program of about three weeks.[15][16]
Do not turn the program duration into one continuous run.[16]

### 2. Why it is relevant

The project documents a transition from flat self-coordination to hierarchical task generation, together with failure modes of both.[15]
Initially, agents claimed work through a shared file and locks: forgotten or long-held locks reduced twenty agents to the effective throughput of two or three.[15]
Optimistic concurrency helped mechanics but not risk aversion: agents made safe small changes while no one owned hard end-to-end problems.[15]
These are actual reported collective pathologies, not merely a large repository.[15]

### 3. What evidence exists

Cursor’s account provides the architecture and public artifact link.[15]
The published Lin interview includes a harness demo, precise mechanisms and concessions.[16]
Approximately 2,000 concurrent agents at the peak is Lin’s later operator report; January 14 described hundreds, and the figures must not be added or treated as independently verified counts.[15][16]
Simon Willison independently followed build instructions and obtained a working browser window with recognizable Google and blog pages, but visible rendering glitches.[17]
Fortune interviewed Cursor and OpenAI personnel and reported that the system remained incomplete and nonproduction-ready.[18]

### 4. Autonomy and control topology

Planners continually inspect the codebase and create tasks, recursively spawning sub-planners; workers complete assigned tasks and push changes without coordinating directly with other workers.[15]
A judge decides whether another cycle should run, followed by fresh starts.[15]
Humans designed prompts, selected models and divided browser workstreams across harnesses.[15][16]
Lin says they could stop a running execution but did not steer its trajectory.[16]
This is substantial ongoing model decision authority inside an engineered hierarchy, not a flat decentralized swarm.[15][16]

### 5. Coordination substrate

Planner task trees and the shared Git branch mediate work allocation and integration.[15][16]
Scope partitioning and modular code reportedly minimize overlapping edits; an integrator role was removed because it bottlenecked work.[15][16]
Specification submodules, Rust compilation and screenshot comparison against golden samples supply grounding and feedback.[16]
Screenshots are part of the disclosed feedback design, not an independent guarantee of browser correctness.[16]
Multiple harnesses on separate large machines handled workstreams such as CSS; Lin described roughly 300 concurrent agents per machine.[16]

### 6. Strong claims versus speculative claims

Strongest result: a coordinated autonomous run produced an artifact that an independent developer could build and use for limited page rendering.[15][17]
Initial public CI failed and build instructions were missing; later instructions enabled Willison’s build.[17]
JavaScript was not working in the January 23 demo and agents had disabled it behind a feature flag.[16]
They autonomously chose dependencies—including Taffy and a QuickJS workaround to unblock work while other agents built the JavaScript engine—complicating “from scratch.” Lin explicitly allowed transient compilation/API errors to avoid synchronization bottlenecks; his claim that errors stayed at a stable rate is not independently measured here.[16]
Cursor still required fresh starts against drift, and Lin said production software was never the goal.[15][16]
Repo size, commit rate and a screenshot establish neither completeness nor correctness.[15][16][17]

### 7. Distinctness

Separate operator and episode from Anthropic’s compiler and all excluded seed families.[14][15]
The January disclosure, January 19 build check and January 23 interview describe the same browser project, not three swarms.[15][16][17]
Its Solid-to-React migration, video-rendering improvement, Java LSP, emulator and spreadsheet listings are not split into independent collective cases: project outcome lists alone do not establish separate comparable many-agent runs.[15]

## Sources

[14] https://www.anthropic.com/engineering/building-c-compiler — Building a C compiler with a team of parallel Claudes
[15] https://cursor.com/blog/scaling-agents — Scaling long-running autonomous coding
[16] https://simonwillison.net/2026/Jan/23/fastrender — Wilson Lin on FastRender: a browser built by thousands of parallel agents
[17] https://simonwillison.net/2026/Jan/19/scaling-long-running-autonomous-coding — Scaling long-running autonomous coding (Simon Willison link post)
[18] https://fortune.com/2026/01/23/cursor-built-web-browser-with-swarm-ai-agents-powered-openai — Cursor used a swarm of AI agents powered by OpenAI to build and run a web browser for a week—with no human help. Here’s why developers are buzzing
[21] https://github.com/anthropics/claudes-c-compiler — CCC — Claude's C Compiler (anthropics/claudes-c-compiler)
