# distributed-rhizotechnics Requirements Interview

Authority: owner elicitation and explicit unknowns.
Mode: interview, with authorized documentation checkpoints.
Source: the current local conversation with Maria / Colette.

## Coverage rule

Track nine decision areas, not nine fixed questions.
Ask exactly one question per turn.
Follow the answer before moving to another area.

Count an area complete when owner intent and remaining unknowns are explicitly recorded.
Do not count an area complete merely because a question was asked.
Uncertainty, refusal, and deferral are valid answers.
Interview coverage does not establish implementation readiness.

Completed areas: 5 of 9.
Current area: 6, structured contribution contract.

## Decision-area map

| Area | Topic | Starting knowledge | Remaining elicitation | Status |
| --- | --- | --- | --- | --- |
| 1 | First dataset and demonstration question | SwarmTraces; user types the question at session start. | A specific demonstration example is deferred. | Complete |
| 2 | Source identity and sentence anchoring | Private snapshots; stable source anchors; graph attribution; expandable evidence on nodes and edges. | Revisit inspector density after use; exact anchor encoding is engineering detail. | Complete, with provisional UI |
| 3 | Retrieval and model context | Dataset retrieval, named Hermes references, whole-graph context, and on-demand evidence inspection. | Whole-graph action permissions continue in area 4; role execution continues in area 5. | Complete |
| 4 | Graph action semantics | Additive linked revisions; members propose strike-through and humans approve the status change. | Detailed UI remains revisitable; preserve all correction provenance. | Complete |
| 5 | Swarm execution | Baton passing; tunable node-count cadence; 12-node review; finish on Pause; three no-node passes trigger pause. | Monetary/token limits continue in area 8; exact scheduler mechanics remain engineering details. | Complete |
| 6 | Structured contribution contract | Provenance and structured conclusions precede register rendering. | Define output validation, evidence references, and confidence semantics. | In progress |
| 7 | Persistence and report scope | Two report kinds; JSON and Markdown; optional PDF; shared snapshot. | Define reopen state, report inclusion scope, and PDF priority. | Pending |
| 8 | Trust boundaries and failure behavior | Local files; no web research; request-only AI Village data excluded from demonstration and repository. | Define model privacy, credentials, exports, and failure handling. | Pending |
| 9 | Observable acceptance criteria | One complete gesture loop and inspectable provenance. | Define success, negative cases, and completion evidence. | Pending |

## Answer record

Existing collaborative decisions are preserved in PROJECT_BRIEF.md.

### Area 1 — dataset selection

Question: Which dataset should the first working Rhizomics demonstration use?
Owner answer: “ummm let's start with the ai village dataset”
Owner correction: “but no images”
Initially selected: AI Village, non-image data only.
Exclude dataset images and screenshot archives.
This selection is superseded by the owner revision below.

### Area 1 — question entry and dataset revision

Owner statement: “let me type the first question in to begin the session”
Confirmed interaction: the user supplies the question at session start.
Do not require a hard-coded research question for the application.

The owner then withdrew AI Village because access is request-only.
She excluded that restricted data from the demonstration and swarm-forensics repository.
Owner selection: “first lets do swarmtraces dataset since im most familiar with that one”
Current selection: SwarmTraces.
Deferred: a particular question for a scripted demonstration.
Area 1 elicitation is complete; importer and source anchoring remain area 2 topics.

The previously reported `colette-research/sources/ai-village-dataset` folder is absent on local inspection.
The agent moved or deleted no data.

### Area 2 — source ownership explanation requested

Question: Should dataset selection read the existing file or import a private workspace copy?
Owner response: “idk what does in place / import affect”
Explain source ownership, disk cost, missing-file behavior, and reproducibility before requesting a decision.
Source ownership was unselected at that point; the next answer resolves it.

### Area 2 — private import selected

Question: Would you prefer the private-snapshot approach?
Owner answer: “ah yes private import.”
Confirmed: import an unchanged source snapshot into private application data outside Git.
Keep saved investigations tied to the imported dataset version.
Source identity, source revisions, and sentence anchoring remain unresolved.

### Area 2 — graph attribution and edge inspection

Question: Should selecting a source sentence show its full original record in the inspector?
The owner prefers node information displayed directly in the graph.
Confirmed: author at the node head, timestamp at the bottom.
Owner wording: “selecting an edge might be where the source record should show”
Treat edge-based source inspection as tentative until its meaning is clarified.
This distinction is resolved provisionally by the next answer.

### Area 2 — original records selected provisionally

Question: Should edge inspection show endpoint records, relation-supporting evidence, or both?
Owner answer: “original records for now.”
Confirmed first-pass behavior: show the original records behind the connected nodes.
The owner expects some inspection choices to change after using the application.
She cannot judge useful-versus-cluttered presentation without seeing it.
Keep those UI choices provisional and revisitable.

Area 2 owner elicitation is complete for the initial slice.
Existing stable-ID, exact-span, unknown-time, and snapshot requirements remain in force.
Exact encoding and indexing mechanics remain engineering decisions, not unelicited owner preferences.

### Area 3 — dataset retrieval and Hermes reference research

Question: May members retrieve more dataset material or only analyze existing graph source nodes?
Owner answer: “yes definitely retrieve additional data from the dataset.”
Confirmed: members may retrieve beyond the materialized graph.

The owner also supplied the Hermes swarm-research root for reference context.
Root: `/home/resonatingloop/.resonance/exoresonance/swarm-forensics/colette-research/hermes-research/`.
Her requested scope covers stages 1 and 2, stage 3, stage 4, evidence, and support.
Local inventory verified `stage-1-&-2`, `stage-3-event-discovery`, `stage-4-trace-reservoirs`, `_evidence`, and `_support`.
No additional research folder was authorized by this statement.
No evidence bodies or source datasets were reviewed during this inventory.

Preserve reference provenance separately from selected-dataset observations.
The later inspection agreement makes supporting references inspectable without mandatory additional visible nodes.

### Evidence-inspection revision during area 3

The owner revises the earlier original-records-only edge inspection choice.
Owner statement: “the evidence should be expandable from clicking the edge/node.”
She requests a modifier gesture such as “shift click or ctrl click”.
Confirmed: evidence access belongs to both nodes and edges.
Exact modifier and expansion location were unselected at that point.
Do not treat additional visible reference nodes as required by this answer.
The owner continues to treat inspection choices as revisitable after use.

### Evidence-inspection interaction accepted

Question: Should evidence opened through Shift-click appear in the side inspector?
Owner answer: “ohhhh yeah i like that”
Confirmed: ordinary click selects; Shift-click opens supporting evidence for either node or edge.
Show that evidence in the side inspector.
Provide an “Inspect evidence” menu action too.
Keep supporting references attached without requiring each citation to become a visible node.
These interaction choices remain revisitable after use.
The next answer supplies the member's existing-graph context boundary.

### Area 3 — whole-graph context and optional interaction

Question: Should members see the whole graph or only their relevant branch and retrieved material?
Owner answer: “whole graph”
Owner addition: “it should be able to interact with the whole graph too as an option”
Confirmed: whole current session graph is available as context.
Confirmed: whole-graph interaction is an optional capability.
Do not assume this grants permission to modify every existing object.
Addition-versus-revision permissions continue in area 4.

Owner hypothesis: “mixing technical / systems / mythopoetic in various responses might lead to something novel”
Record that as an exploratory possibility, not an observed outcome.
Preserve the existing distinction between analytic contributions and invariant register rendering.
Area 3 owner elicitation is complete for the initial slice.

### Area 4 — revision meaning requires clarification

Question: May members revise existing analytic nodes and edges or only add new ones?
Owner asks what revision would mean and which objects would change.
No revision permission is selected yet.

Agent explanation: possible targets include generated interpretations, summaries, relation types, and supporting references.
These examples are illustrative, not observed dataset findings or accepted behavior.
Do not interpret revision as permission to modify imported source records.
Agent proposal: add a linked successor instead of silently overwriting an existing analytic object.
The next answer accepts additive revision and adds incorrect-inference marking.

### Area 4 — additive revision and incorrect-inference marking accepted

Owner answer: “additive revisions are a very good addition.”
Confirmed: revision produces a linked analytic successor rather than overwriting earlier content.
The owner also requires the ability to strike through an inference found incorrect.
Preserve that inference and record correction provenance rather than deleting history.
Treat incorrect status as part of the graph record and report basis.
The next answer assigns members proposal authority and reserves approval for the human.

### Area 4 — human approval for incorrect-inference marking

Question: May members strike through an inference directly or only propose it for approval?
Owner answer: “propose”
Confirmed: members submit correction proposals; the human approves any strike-through status change.
Preserve the inference, proposal, approval, timestamps, actors, and stated basis.
Area 4 owner elicitation is complete for the initial slice.

### Area 5 — node-count timing proposal

The owner wants contribution timing to scale with node count.
Owner proposal: “maybe start 20/20/30/30/40/40 etc, topping out at like 80sec?”
Record it as tentative timing rather than a finalized schedule.
Candidate continuation: `20,20,30,30,40,40,50,50,60,60,70,70,80,80...` seconds.
That continuation assumes two counted nodes per interval step.
The next answer provisionally selects swarm-added nodes as the counting population.
Member selection, pause/stop, budgets, and pending-work behavior remain open.

### Area 5 — tentative timing counter selected

Question: Should timing count all graph nodes or only swarm-added nodes?
Owner answer: “swarm-added i think”
Provisional preference: swarm-added node count.
Preserve “i think” as uncertainty; the timing remains adjustable rather than permanently settled.
Automatic stopping, contribution budgets, member selection, and pause behavior remain unresolved.

### Area 5 — optional continuation threshold requested

Question: Continue automatic additions until paused or stop after a configurable contribution count?
The owner tentatively prefers automation to become optional after a certain point.
She asks for a reasonable threshold.

Agent proposal: pause automatic growth after 12 swarm-added nodes and offer explicit continuation.
The current candidate cadence totals 540 seconds of timer intervals for those additions.
That is nine minutes of scheduled waiting, excluding model generation and retrieval time.
The next candidate interval would be 80 seconds.
This calculation is conditional on the provisional two-nodes-per-step cadence.
No application timing was exercised.
The next answer accepts this as an adjustable first-pass default.

### Area 5 — initial automatic growth and continuation accepted

Question: Would the proposed 12-node review threshold work as the first-pass default?
Owner answer: “yes”
Confirmed: pause automatic growth after 12 swarm-added nodes by default.
Make the threshold adjustable.
Offer “Add one” and “Continue automatically”.
Keep manual graph interactions active during the pause.
Do not treat the threshold as an evidence-sufficiency or completion verdict.
Member selection and pending-work behavior remain unresolved.

### Area 5 — member-selection options requested

Question: How should the next swarm member be chosen?
The owner suggests random selection or baton passing, but has not chosen a policy.
She requests an explanation of the options.

Agent options: fixed rotation, random or shuffled rounds, member nomination, or explicit human selection.
These are alternatives for consideration, not accepted implementation requirements.
For baton passing, distinguish a member's nomination from the scheduler's actual grant.
Validation and a fallback would prevent an invalid nomination from stranding the run.
The next answer selects baton passing with a random fallback.

### Area 5 — baton passing accepted

The agent recommended baton passing with a random fallback for the first version.
Owner answer: “agreed”
Confirmed: contributing members nominate the next member.
The scheduler validates the nomination and grants the next turn.
Use a random fallback for missing or invalid nominations.
Detailed pause and pending-work behavior remain unresolved.

### Area 5 — pending contribution finishes on Pause

Question: Should a running contribution finish or stop without adding a node when paused?
Owner answer: “finish”
Confirmed: finish the already-running contribution and add it to the graph.
Do not start another automatic contribution while paused.
No Pause implementation was exercised.
Still unresolved: whether a member may decline to add a node and simply pass the baton.

### Area 5 — passing without a node accepted

Question: May a member pass the baton without creating a node when it has nothing useful to add?
Owner answer: “yes”
Confirmed: passing without a graph contribution is legal.
Retain the handoff in activity history rather than creating a filler node.
A no-node pass does not advance the swarm-added-node counter.
The next answer supplies an automatic pause threshold for repeated no-node passes.

### Area 5 — stall-review threshold accepted

Question: Should three consecutive no-node passes automatically pause the swarm?
Owner answer: “yup”
Confirmed: pause after three consecutive passes without a new node.
Do not interpret this as consensus or proof that investigation is complete.
Area 5 owner elicitation is complete for the initial slice.
Money/token limits continue in area 8; precise scheduler mechanics remain engineering details.

### Project-name revision

The owner selected the name `distributed-rhizotechnics` and renamed the existing directory.
Local inspection verified the new documentation directory and absence of the old directory.
The agent did not perform the rename.

### Historical interface and aesthetic scope supplied

The owner supplied `/home/resonatingloop/Pictures/project-screenshots/rhizomics.png` as historical interface reference.
She said later responses were refined to 2-3 sentences.
The screenshot was viewed, not copied into the repository.

The owner supplied AESTHETIC.md as the current visual scope.
Read its tokens and semantic mappings directly rather than recreating them from memory.
Its insectile quality comes from abstract choreography, not literal bug imagery.
It specifies reduced motion, visible uncertainty, consent thresholds, and an append-only activity layer.

The later edge-inspection answer supplies the first-pass source-context behavior.
The aesthetic scope does not itself settle source identity or layout usefulness.

Record each answer with its question and source attribution.
Label any agent interpretation separately.
Preserve contradictions and changed answers with links to the earlier position.
Do not turn an unresolved preference into a default without the owner's agreement.

## Milestone protocol

At three completed areas, document the one-third checkpoint.
At six completed areas, document the two-thirds checkpoint.
At nine addressed areas, announce that elicitation coverage is complete.

For each checkpoint:

1. Update confirmed direction and explicit unknowns in PROJECT_BRIEF.md.
2. Update this coverage table and answer record.
3. Append a concise milestone record here.
4. Replace STATUS.md with the actual current checkpoint.
5. Tell the owner the checkpoint has been saved.

Do not create a build plan or start implementation automatically.
If blocking unknowns remain, identify them at completion.
If the owner wraps early, preserve partial coverage and report it accurately.

## Milestone record

### Initial checkpoint

Captured: 2026-10-03T15:54:32-07:00.
Completed interview areas: 0 of 9.
Product direction is documented before the first question.

### One-third checkpoint

Captured: 2026-10-03T17:06:22-07:00.
Completed areas: 3 of 9.
Current checkout: `colette-help-peer`.
Repository revision at capture: `e2456b88affe54b75efc6289bdcd9663e13aaf68`.

Settled for the first slice:

- SwarmTraces is the initial dataset; the user enters the question at session start.
- Import an unchanged private source snapshot outside Git.
- Preserve exact source anchors, source uncertainty, and independent node/edge provenance.
- Show node author at its head and timestamp at its bottom.
- Ordinary click selects; Shift-click or “Inspect evidence” opens evidence in the side inspector.
- Members retrieve additional dataset material and consult the named Hermes research directories.
- Members see the whole current graph and may use an optional whole-graph interaction mode.
- Mixed technical, systems, and mythopoetic responses are desired as an exploratory possibility.

Still provisional:

- Information density and inspection placement need actual use before permanent decisions.
- Whole-graph interaction permissions are not yet defined.
- Exact indexing, identity encoding, and context-packing mechanics remain engineering details.

The product brief and STATUS.md are updated with this checkpoint.
No application implementation is authorized or verified.
The two-thirds checkpoint remains due after six completed areas.
