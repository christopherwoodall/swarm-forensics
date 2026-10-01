# Project Brief: Swarm Forensics

Authority: historical discussion and proposed direction.
Reviewed: 2026-10-01.
This document does not authorize implementation or publication.
Use [STATUS.md](STATUS.md) for verified implementation state.
Use [AGENTS.md](AGENTS.md) for repository requirements.

## Purpose

Understand how agent swarms coordinate through messages, tools, and persistent artifacts.
Make those relationships available for visual exploration.
Investigate organization across replaceable processes, not only individual agent actions.

The discussions combine two complementary interests:

- TelepathicPug proposed mapping tools, skills, plugins, and possible egress routes.
- Colette proposed tracing distributed coordination, shared state, and changing relationships.

The team discussed combining these interests in an interactive swarm explorer.
No final submission scope was selected in the reviewed material.

## Source Basis

| Source | Reviewed material | Evidence boundary |
| --- | --- | --- |
| SITE | [swarmchasing.com](https://swarmchasing.com/), captured 2026-10-01, including expanded FAQs | Organizer statements, not implementation evidence |
| DM-G | SwarmTraces Hackathon group, saved September 30–October 1 discussion | Team discussion and reported work |
| DM-P | Colette and TelepathicPug, from September 28, 2026, at 8:09 AM | Project origin and subsequent brainstorming |
| NOTE | Shared `swarmtraces-distributed-systems-for-pug.md` attachment | Prior analysis; its underlying corpus was not reanalyzed here |
| REPO | Local checkout at `79b1840702591f0fd5253d6b3752264b635d3904` | Source inspection and executable checks; see STATUS |

Use these source labels for the discussion references below.
The DM sources are paginated snapshots, not a certified complete archive.
This bootstrap used saved material after browser collection stopped.
The summaries omit unrelated conversation, private invitations, account details, and personal schedules.
Raw conversations and screenshots were not imported into the repository.

## Discussed Ideas

These ideas retain their discussion status.
Interest or positive feedback does not constitute an accepted implementation specification.

### 1. Map Egress Routes

Status: proposed investigation.
Sources: DM-P, September 29; DM-G, September 30, 7:06 PM.

- Catalog tools, skills, plugins, and MCP integrations.
- Identify routes through which agent activity or information can leave an environment.
- Use the map as a starting point for monitoring and investigation.
- Distinguish a possible route from an observed transfer.

A shared screenshot described public-repository exposures through developer tools.
Those reported findings were not independently reproduced during this bootstrap.
DM-G also mentions a Muse-generated `mcp-egress-v1.md` scan.
Its sender explicitly cautioned against treating the scan as reliable evidence.
The scan attachment was not inspected or imported here.

### 2. Trace Distributed Coordination

Status: shared research direction.
Sources: DM-P, September 30, 10:29 AM–2:40 PM; NOTE; DM-G, October 1, 8:52 AM.

Study how durable traces influence later activity.
The shared analysis calls this stigmergic coordination.

Candidate mechanisms include:

- Persistent command and result channels.
- Duplicate suppression through remembered command identities.
- Leader selection through shared claims.
- Leases, heartbeats, and stale-controller replacement.
- Authenticated commands and addressed control roles.
- Controller replacement and restoration of coordination functions.

Additional research questions include:

- How does information propagate?
- How does memory form?
- How do roles emerge?
- How does coordination break and recover?
- Which shared artifacts connect otherwise separate processes?

NOTE reports 37 distinct organizational mechanism implementations.
That number describes an earlier analysis, not agents, runs, deployments, or verified historical events.
This bootstrap did not reproduce that result.

NOTE distinguishes constructed mechanisms from successful execution.
It does not establish complete chronology, reliable agent attribution, or consumption of every recorded trace.
Preserve those limitations when selecting evidence for a demonstration.

### 3. Explore a Changing Graph

Status: shared visualization direction; demonstration scope remains open.
Sources: DM-P, September 30, 2:30 PM–2:40 PM; DM-G visualization discussion.

The initial sketch arranged origins, egress sites, and targets in layers.
The discussion added lateral connections and shared artifacts.
The proposed graph is not limited to a hierarchy.

Candidate relationships include:

- Origin to egress site.
- Egress site to target.
- Egress site to another egress site.
- Egress site to shared artifact.
- Shared artifact to another site or process.

Edges may appear, disappear, reverse direction, or change semantic type over time.
The team discussed visually traversing swarm activity in a browser.
GitHub Pages was suggested as a delivery surface.
A 3D visualization was explored, but no final rendering stack was selected.

The checkout contains two synthetic visualization mocks under `data/viz_mock/`.
They are reference artifacts, not evidence of a working forensic pipeline.
DM-G mentions a `pipeline-real-v3-bundle.zip` attachment.
Its filename does not establish real-data integration.
That bundle was not inspected or imported during this bootstrap.

### 4. Build a Swarm Search Plugin

Status: proposed product extension.
Source: DM-G, October 1, 10:00 AM.

TelepathicPug proposed a Hermes plugin for swarm search.
The proposed search would use indicators of compromise from datasets or subsequent analysis.
No indicator set, search backend, or plugin interface was selected.
No plugin is implemented in this checkout.

### 5. Coordinate the Team's Own Agents

Status: separate experimental workstream.
Source: DM-G, October 1, 9:42 AM–10:10 AM.

The team discussed a multiplayer coding environment with humans and local agents.
One proposal keeps Hermes running locally and uses FairyStack as the coordination layer.
The discussion considered room-scoped participation and attributed agent messages.
HTTP and ACP integration approaches were mentioned.
These are discussion proposals, not verified interoperability claims.

Jessald reported starting an integration experiment.
Its implementation and results were not inspected during this bootstrap.
Discord was also discussed as a possible collaboration surface.
No integration was configured here.

### 6. Keep Project Notes with Provenance

Status: desired collaboration support; continuous operation remains unimplemented.
Source: DM-G, October 1, 10:10 AM and 10:36 AM.

Colette proposed using Hermes as a quiet note-taker.
The notes would summarize discussion, identify decisions, retain provenance, and support repository continuity.
Moving collaboration to FairyStack was conditional on confirming multi-user chat access.
This bootstrap records existing discussion only.
It does not configure a watcher, bot, shared room, or automatic repository writer.

## Data Sources

### AI Village

Existing acquisition code targets `aidigestorg/ai-village` on Hugging Face.
The organizer site offers access but does not require this dataset.
DM-G reports that Colette obtained access on October 1.
That report does not verify the current shell token or another contributor's access.

The reviewed dataset-access screenshot states research and analysis conditions.
It excludes training or fine-tuning without written permission and prohibits re-identification.
It also requests attribution and publication notification.
Confirm the live dataset terms before using or publishing derived material.

### Swarmtraces

The earlier coordination analysis used the published redacted corpus from [swarmtraces.org](https://swarmtraces.org/).
It motivated the distributed-systems direction before this hackathon project existed.
The team discussed using it alongside AI Village.
This repository does not yet implement its acquisition or parsing.
Do not treat reconstructed network artifacts as interchangeable with agent transcripts.

## Hackathon Context

Source: SITE, captured 2026-10-01.

- Event: October 3–4, 2026, in San Francisco and online.
- Hosts: AI Village and Grove Research.
- Kickoff: Saturday, 11:00 AM Pacific Time.
- Submission deadline: Sunday, 5:00 PM Pacific Time, including online participants.
- Required submission: a short write-up or explanatory video, plus a code repository link.
- Optional submission: a write-up of results found with the tool.
- Early development is permitted.
- AI Village data is optional.
- The site offers compute credits to in-person attendees.

The discussions prioritize exploration and collaboration over winning.
Participants expect asynchronous contributions.
Private availability details are not repository requirements.

## Open Decisions

1. Select one initial demonstration: coordination explorer, egress investigation, or a bounded combination.
2. Select the first evidence source: AI Village or the redacted Swarmtraces corpus.
3. Define graph identities, relation types, temporal uncertainty, and source references.
4. Confirm what derived data may be published on GitHub Pages.
5. Separate the forensic deliverable from the team's agent-coordination experiment.
6. Review externally generated scans and visualization bundles before adopting their claims or code.

These decisions remain open.
Existing repository rules remain unchanged.
No new forensic schema or publication contract was accepted during this bootstrap.
