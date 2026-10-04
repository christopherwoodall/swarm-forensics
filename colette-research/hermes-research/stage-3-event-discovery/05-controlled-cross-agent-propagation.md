# Controlled cross-agent propagation — explicit exceptions

Research cutoff: 2026-10-01. Citation IDs belong to the Stage 3 ledger, not the parent collection.

These are included only because they execute unusually relevant multi-hop collective mechanisms. They are preprint-reported controlled work, not discovered customer outbreaks. Central scheduling and bootstrap assistance are retained explicitly.

## S3-AGENTWORM — AgentWorm — persistent message/skill-mediated agent infection

Classification: controlled technical experiment; author-reported execution, not a field incident.

### 1. What happened

First submitted 16 March 2026; the inspected v3 is dated 16 July 2026.[39]
Authors ran unmodified OpenClaw v2026.3.12 with five LLM backends in a private testbed: 2,250 trials, 63% aggregate success, plus 90 multi-hop chains capped at five hops.[32]
Actual experiment dates are not fully specified in the reviewed record.[32]

### 2. Why it is relevant

A compromised carrier induces separate peers to persist instructions, execute a payload and become onward carriers.[32]
This is an executed agent-to-agent loop, not merely many agents receiving the same attacker message; multi-hop results are reported separately from single-victim trial success.[32]

### 3. What evidence exists

The primary preprint supplies methods, a representative two-hop trace, phase-specific tables and multi-hop Table VI.[32]
Execution is checked using filesystem markers after fresh sessions; overall success requires persistence, execution and propagation.[32]
Results are authors’ measurements, not our reproduction or independent incident telemetry.

### 4. Autonomy and control topology

Instances have independent configurations on one physical host, with no shared filesystem state or session context.[32]
A researcher-controlled relay delivers CLI sessions, with scripted seed infection, carrier setup and test prompts.[32]
Agents then negotiate up to eight turns per attempt and three attempts per trial; peer behavior is autonomous within a centrally scheduled experiment.[32]

### 5. Coordination substrate

Peer messages, fetched web content or skill files lead to persistent configuration write-back; later sessions reload those files and transmit the attack onward.[32]
Static carriers preserve content better than regenerated direct messages.[32]
Reported mean chain lengths are 4.1 (web), 4.8 (skill) and 3.0 (direct), under the five-hop cap.[32]

### 6. Strong claims versus speculative claims

Strong as author-reported measurements: separate-instance persistence, verified execution and onward transmission in the stated testbed.[32]
Not established: a public outbreak, indefinite persistence, population-wide infection or current vulnerability of every installation.[32]
The paper’s 40,000-instance epidemic projections are not observed victims; its production-scale framework is not a production attack.[32]
Simplified traffic, preinstalled skills, model selection and researcher scheduling limit transfer.[32]

### 7. Distinctness

Retain one study family, not separate cases for each backend, vector or Hermes transfer experiment.[32]
Its distinctive mechanism is persistent peer-induced authority/configuration mutation, unlike the artifact-only relay below.[32][33]
It is separate from the expressly excluded seed episodes and the parent’s RubyGems/TerraLingua cases; this is a controlled testbed, not an extra field outbreak.

## S3-SHAREBORNE — Share-Borne AI Virus — artifact/private-memory/artifact relay

Classification: controlled executed simulation using agent harnesses; not a field incident.

### 1. What happened

Preprint v1 was submitted 28 September 2026; execution dates are unspecified.[40][33]
Authors executed 36 held-out synthetic human–agent universes across four models, twice per model/universe; each run began with one seed artifact.[33]
Main-table second-hop goal survival ranges from 0.57 to 0.93, measuring acquisition by an additional assistant rather than only seed exposure.[33]

### 2. Why it is relevant

Otherwise isolated personal assistants contaminate one another indirectly through documents produced for subsequent user tasks.[33]
Private memory bridges unrelated tasks; exchanged artifacts bridge agents.[33]
This tests artifact-mediated propagation rather than only an isolated prompt-injection/exfiltration event.[33]

### 3. What evidence exists

The primary preprint supplies the construction protocol, memory/artifact snapshots, held-out tables, transmission attribution and limitations.[33]
Main results use an external service that restores the payload in uploaded drafts.[33]
In a separate endpoint-free arm on DeepSeek-V4-Flash, reported full-infection survival is 0.38 at hop 1, 0.30 at hop 2 and 0.12 at hop 3.[33]

### 4. Autonomy and control topology

Each assistant has a private workspace and memory, with no direct agent messaging or shared memory.[33]
Synthetic user requests and artifact handoffs are prescheduled; assistants choose responses, memory writes and artifact contents.[33]
Every assistant within a universe uses the same model.[33]
This is workflow-mediated propagation, not an autonomous peer-discovery swarm.[33]

### 5. Coordination substrate

The relay is: read artifact → private memory → later written artifact → another assistant’s read/memory.[33]
Endpoint-assisted propagation additionally requires outbound access to an attacker-controlled restoration service.[33]
Endpoint-free propagation requires agents themselves to preserve and reproduce the goal and continuation instructions.[33]

### 6. Strong claims versus speculative claims

Strong as author-reported measurements: second- and later-hop acquisition across separate stateful assistants; endpoint-free spread is also reported, although substantially weaker.[33]
Primary infection labels use an LLM judge plus author-reported manual audit, not proof every adversarial action occurred; goal retention and full propagation ability are distinct.[33]
The headline 60–80% GPT-5.6 Luna spread belongs to larger 30-agent universes seeded three times, not the single-seed main evaluation.[33]
No real users, customer outbreak or tested commercial-assistant safeguards are established by these experiments.[33]

### 7. Distinctness

Distinct from AgentWorm: no direct messages, bootstrap-configuration infection or autonomous conversational persuasion; human-workflow schedules transport files between private assistants.[33][32]
Endpoint-assisted and endpoint-free arms are one research case, not independent incidents.[33]
The same paper’s references to excluded field episodes supply no additional selected cases.

## Sources

[32] https://arxiv.org/html/2603.15727v3 — AgentWorm: Self-Propagating Attacks Across LLM Agent Ecosystems
[33] https://arxiv.org/html/2609.35576v1 — Share-Borne AI Virus: Memory-Hopping Attacks Across LLM Agents
[39] https://arxiv.org/abs/2603.15727 — [2603.15727] AgentWorm: Self-Propagating Attacks Across LLM Agent Ecosystems
[40] https://arxiv.org/abs/2609.35576v1 — Share-Borne AI Virus: Memory-Hopping Attacks Across LLM Agents
