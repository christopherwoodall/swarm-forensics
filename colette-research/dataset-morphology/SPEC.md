ataset pattern discovery spec
purpose
build a dataset-agnostic analysis pipeline that accepts an arbitrary corpus and identifies patterns potentially relevant to collective or swarm-like agent behavior.
the system is a candidate generator, not a swarm detector.
its job is to surface patterns worth investigating, characterize them, rank them, and provide enough provenance that a downstream investigator can determine whether the pattern corresponds to a known morphology, a variant of one, a genuinely new morphology, or a benign/confounded structure.
the governing distinction is:
pattern discovery → morphology hypothesis → investigation → finding
do not collapse these stages.
the analysis should privilege dependency structure, repeated behavior, state transitions, propagation, and relationships among actors/artifacts over generic “ai-like” language. the research basis explicitly treats the useful forensic object as a dependency structure rather than a pile of suspicious sentences.    08-implications-and-research-ag…
primary task
given dataset d:
1. characterize the dataset and its observable units.
2. discover recurrent, anomalous, emergent, propagating, or structurally interesting patterns.
3. group related observations into candidate pattern families.
4. compare candidates against a library of known morphologies when available.
5. rank candidates by relevance to possible collective-agent behavior.
6. preserve competing benign explanations.
7. emit structured candidate-morphology records for downstream investigation.
the system must be able to say:
“this is unusual and potentially relevant, but i do not yet know what it is.”

that is a successful result.
input assumptions
the input may contain any mixture of:
- messages
- source code
- logs
- files or artifacts
- timestamps
- actor or process identifiers
- repositories or revisions
- URLs
- tool calls
- generated text
- metadata
- task assignments
- status records
- interaction graphs
- memory/state records
the pipeline must first determine which fields actually exist.
it must not invent unavailable fields, reconstruct hidden actors without evidence, or treat rows, messages, files, model calls, processes, and agents as interchangeable units.
this matters especially because the project corpus repeatedly distinguishes artifacts, messages, processes, controller instances, accounts, and unique agents.    10-huggingface-and-metr-2026
stage 0: dataset reconnaissance
before searching for patterns, produce a dataset inventory.
identify:
- record count
- available fields
- candidate actor identifiers
- candidate artifact identifiers
- timestamps and timestamp quality
- content-bearing fields
- links between records
- possible conversation/session/run boundaries
- obvious missingness
- duplicated or derived data
- whether records represent events, snapshots, cumulative states, or unknown mixtures
explicitly report uncertain units.
example:
actor_id confidence: low
timestamp coverage: 61%
artifact lineage: partially reconstructable
run boundaries: unavailable
do not proceed as though absent structure were known structure.
stage 1: normalization
construct normalized representations without destroying the originals.
preserve:
- exact source reference
- original timestamp
- original actor identifier
- original artifact identifier
- raw text or exact span reference
- dataset-specific metadata
derive, where possible:
- lexical tokens
- phrases / n-grams
- semantic embeddings
- code/API identifiers
- normalized operation labels
- temporal bins
- actor-frequency profiles
- artifact-frequency profiles
- reply/reference edges
- write/update lineage
- first appearance
- subsequent appearances
- nearest related pattern
all derived features must remain traceable to source records.
normalization must never erase meaningful distinctions merely to make clustering easier.
stage 2: independent discovery channels
run several discovery methods independently. do not create a single opaque “swarminess” classifier.
lexical recurrence
find phrases, terminology, token combinations, structured expressions, labels, command forms, role names, and recurrent constructions.
look for:
- unusual repeated phrases
- terminology becoming more standardized over time
- repeated imperative forms
- newly introduced vocabulary
- lexical ratcheting
- phrase mutation
- phrase compression
- stable shorthand
- naming conventions
- actor-specific versus population-wide vocabulary
semantic recurrence
cluster passages that express the same operational concept even when wording differs.
examples:
still alive
lease refreshed
owner fresh
heartbeat current
may belong near the same functional concept without sharing literal vocabulary.
semantic similarity is only a discovery feature. it is not evidence of transmission.
structural recurrence
find repeated behavioral or artifact shapes.
examples:
- poll → evaluate → act → publish
- claim → work → release
- request → response → archive
- write shared state → later state change
- numbered command → execution → acknowledgement
- create lock → check freshness → replace stale lock
known swarmtraces morphologies include command channels, duplicate suppression, leader election, leases/heartbeats, controller replacement, authenticated commands, and persistent shared state.    swarmtraces-distributed-systems…    swarmtraces-distributed-systems…    swarmtraces-distributed-systems…
temporal structure
search for:
- sudden onset
- bursts
- gradual adoption
- phase transitions
- stabilization
- decay
- periodic behavior
- recurring cycles
- before/after changes around a newly introduced pattern
- conventions appearing first in one actor, then broadly
- activity resuming after apparent disappearance
timing correlation alone is not causal evidence.
actor-distribution structure
ask:
- one actor repeatedly doing something?
- many actors independently doing the same thing?
- a small subgroup?
- sequential adoption?
- role specialization?
- mutually exclusive roles?
- replacement of one participant by another?
- one actor introducing a pattern followed by broader use?
separate frequency from distribution across independently identified actors.
artifact coupling
look for behaviors tied to shared objects such as:
- files
- repository branches
- wiki pages
- task boards
- package registries
- mailboxes
- locks
- status records
- comments
- memory artifacts
- generated reports
a shared artifact becomes especially interesting when its changed state plausibly affects later behavior.
the project definition of stigmergy requires an action → persistent trace → later action loop, not merely shared storage.    01-definitions-and-characterist…
convention formation
identify initially variable behaviors or labels that become increasingly uniform.
candidate signals:
- entropy decreases over time
- one label displaces alternatives
- phrase variants converge
- actors adopt the same operational shorthand
- coordination rules become standardized
- recurrent conflict produces a stable convention
controlled llm-population experiments demonstrate that local interaction can produce population-level conventions, making convention formation a legitimate pattern family to search for.    05-digital-agent-experiments
anomaly discovery
search specifically for structures that do not map cleanly onto known morphology labels.
examples:
- recurrent cluster far from known morphology centroids
- new actor/artifact relationship
- unexplained temporal synchronization
- repeated operational language with no current ontology label
- new kind of state transition
- unexpected combination of known mechanisms
unknown clusters should be preserved rather than force-classified.
stage 3: candidate construction
merge related observations into candidate pattern families.
each candidate should answer:
- what repeats?
- where?
- across how many records?
- across how many actors?
- across how many artifacts?
- during what period?
- what appeared first?
- what changed afterward?
- what known morphology is nearest?
- how different is it?
- what evidence supports the grouping?
- what obvious alternative explanations exist?
the candidate must include exact source references or record ids.
stage 4: scoring
do not emit one undifferentiated confidence score.
score each candidate separately on:
recurrence
how consistently does the pattern recur?
actor breadth
how many distinct identifiable actors/processes exhibit it?
artifact breadth
does it occur across multiple artifacts or contexts?
temporal organization
does it have meaningful onset, adoption, persistence, replacement, or phase structure?
coordination relevance
could the pattern plausibly implement:
- information handoff
- shared state
- role allocation
- liveness
- leadership
- ownership
- duplicate suppression
- task partitioning
- synchronization
- replacement
- governance
- authentication
- collective memory
- propagation
morphology similarity
how closely does it resemble an existing morphology?
novelty
how much meaningful structure remains unexplained by the nearest known morphology?
high novelty does not mean high swarm likelihood.
alternative-explanation pressure
how readily could the pattern arise from:
- boilerplate
- shared prompt
- common framework
- common training data
- code generation templates
- one operator
- centralized orchestration
- normal package conventions
- logging behavior
- dataset artifact
- duplicated records
- human collaboration
- shared news/event response
evidentiary strength
suggested ladder:
e0 lexical/semantic resemblance
e1 repeated structural behavior
e2 temporal/actor/artifact association
e3 observed shared-state interaction
e4 verified read/write or handoff sequence
e5 downstream behavior demonstrably changed after exposure
the exact names can change, but preserve the hierarchy.
the key distinction is that trace as evidence and trace as mechanism are not the same.    08-implications-and-research-ag…
stage 5: candidate ranking
ranking should answer:
which patterns deserve investigative attention first?

not:
which patterns are definitely swarms?

a useful ranking function can favor:
- high recurrence
- multi-actor distribution
- temporal structure
- artifact coupling
- functional coordination relevance
- novelty
- evidence quality
and penalize:
- obvious templating
- single-source repetition
- dataset artifacts
- common boilerplate
- weak actor identity
- missing chronology
- strong benign explanations
retain the component scores so ranking is inspectable.
required output: candidate morphology card
each candidate should emit something close to:
candidate_id:
candidate_label:
status: known_variant | possible_new_morphology | anomaly | weak_lead

summary:
one-paragraph description of the observed pattern.

evidence:
- exact record/artifact references
- representative excerpts
- counts
- actors
- artifacts
- date/time span

first_observed:
last_observed:

distribution:
how broadly the pattern appears and whether adoption changes over time.

structural_signature:
abstracted behavioral pattern.

lexical_signature:
important words, phrases, or token patterns.

nearest_known_morphology:
name or null

similarity_to_known:
0-1 or ordinal

novelty:
0-1 or ordinal

coordination_relevance:
0-1 or ordinal

evidence_strength:
e0-e5

alternative_explanations:
- ...
- ...

missing_evidence:
what would be required to establish a stronger claim.

recommended_investigation:
specific downstream questions, not conclusions.

source_provenance:
record ids / file ids / hashes / spans

failure discipline
the system must actively search for reasons its candidate may be uninteresting.
for every candidate, ask:
1. could this be one actor?
2. could this be shared boilerplate?
3. could this come from the dataset construction itself?
4. could all participants have received the same prompt?
5. could one central controller be producing the appearance of peer coordination?
6. is apparent propagation merely repeated independent generation?
7. are timestamps reliable enough to support sequence?
8. are actor identifiers stable enough to support multi-actor claims?
9. does an observed write have any evidence of a later read?
10. is the pattern actually rarer than its background rate?
this is not optional.
the observatory work is a useful warning here: burst detectors can correctly identify an unusual event yet still produce a benign false positive, as happened with the serpentine package release.    08-september-29-pypi-resolution
validation datasets
evaluate the methodology against at least three corpus types.
known collective / positive-ish corpus
a corpus containing documented coordination mechanisms.
goal: can the system recover known structures without being explicitly told where they are?
benign coordinated corpus
human collaboration, conventional distributed software, package releases, standard ci, etc.
goal: does the system notice structure without calling every organized system a swarm?
messy unrelated corpus
a dataset with no expected collective-agent phenomenon.
goal: measure hallucinated morphology production and ranking inflation.
ideally add a fourth:
controlled emergent corpus
something such as the llm naming-game experiments or another population where a known convention develops.
goal: test whether the system detects formation rather than merely static recurrence.
evaluation metrics
do not evaluate only “did it find the thing?”
measure:
- known-pattern recall
- false candidate count
- false high-priority candidate count
- candidate stability across reruns
- sensitivity to corpus subsampling
- sensitivity to removed metadata
- cluster coherence
- source-traceability rate
- alternative-explanation quality
- morphology matching accuracy
- novelty-ranking usefulness
- analyst review burden
especially track false high-priority candidates. generating fifty harmless curiosities is annoying. ranking a benign package release #1 as “probable emergent swarm coordination” is methodologically radioactive.
downstream handoff
the dataset analyzer stops when it has produced a well-supported candidate.
it should not conduct unrestricted follow-on investigation itself.
the handoff should provide pug’s investigator with:
- candidate definition
- precise source records
- structural signature
- nearest known morphology
- why it is interesting
- competing explanations
- missing causal evidence
- proposed questions to investigate
the downstream investigator then asks whether the candidate actually instantiates the morphology.
non-goals
the system is not intended to:
- identify conscious collectives
- infer hidden motivations from prose
- identify individual humans
- perform public attribution
- classify all ai-generated text
- equate coordination with maliciousness
- call every multi-agent system a swarm
- infer agent identity from model calls
- treat similar language as proof of communication
- convert anomaly into causality
- maximize the number of findings
the objective is useful surprise under disciplined uncertainty.
success condition
the pipeline succeeds when it can take a corpus its designer has not manually annotated and produce a short ranked set of patterns where an analyst says:
“yeah, that’s genuinely weird. i can see exactly why the machine surfaced it, i can inspect the underlying evidence, and i know what question to investigate next.”

the dream result is not “the model detected a swarm.”
it’s:
“the model noticed an organizational shape we hadn’t thought to search for.”