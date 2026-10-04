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

Completed areas: 2 of 9.
Current area: 3, retrieval and model context.

## Decision-area map

| Area | Topic | Starting knowledge | Remaining elicitation | Status |
| --- | --- | --- | --- | --- |
| 1 | First dataset and demonstration question | SwarmTraces; user types the question at session start. | A specific demonstration example is deferred. | Complete |
| 2 | Source identity and sentence anchoring | Private snapshots; stable source anchors; graph attribution; expandable evidence on nodes and edges. | Revisit inspector density after use; exact anchor encoding is engineering detail. | Complete, with provisional UI |
| 3 | Retrieval and model context | Members retrieve additional dataset material and use the named Hermes research collection. | Clarify reference materialization, citations, and model-context boundaries. | In progress |
| 4 | Graph action semantics | Respond, expand, connect, challenge, summarize, and question. | Define resulting objects, relation types, and revision/adjudication behavior. | Pending |
| 5 | Swarm execution | Optional timed single-member contributions to a frontier. | Define selection, silence, budgets, pause/stop, and pending-work behavior. | Pending |
| 6 | Structured contribution contract | Provenance and structured conclusions precede register rendering. | Define output validation, evidence references, and confidence semantics. | Pending |
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
Still unresolved: how a reference used by a contribution becomes visible and cited in the graph.

### Evidence-inspection revision during area 3

The owner revises the earlier original-records-only edge inspection choice.
Owner statement: “the evidence should be expandable from clicking the edge/node.”
She requests a modifier gesture such as “shift click or ctrl click”.
Confirmed: evidence access belongs to both nodes and edges.
Still unresolved: exact modifier and where expansion appears.
Do not treat additional visible reference nodes as required by this answer.
The owner continues to treat inspection choices as revisitable after use.

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

One-third and two-thirds milestones have not been reached.
