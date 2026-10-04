# Swarm Forensics Specification

## 1. Scope & Purpose

This document specifies the Swarm Forensics plugin for Hermes desktop and CLI environments.
The plugin enables autonomous intelligence hunting, artifact correlation, and interactive investigation.
All implementations MUST follow this specification.

## 2. Architecture & Concurrency Model

The system MUST maintain decoupled background execution and interactive user controls.
The backend MUST run as a persistent service inside the Hermes runtime.
The system MUST support concurrent worker threads for autonomous hunts.
Each active hunt MUST execute in its own worker thread.
A hunt MUST respect configured cycle limits.
A hunt MUST respect parent-child relationships up to the configured maximum depth.
The system MUST limit sub-hunt hierarchy depth to three levels by default.
Child hunts MUST inherit the session identifier and root trace context of their parent.
The system MUST provide thread-safe cancellation and pause mechanisms.
When an operator issues a stop command, the target worker MUST terminate gracefully.
When the host application closes, all active workers MUST transition to paused state.
Workers MUST NOT resume automatically after process restart without operator consent.

## 3. Database & Storage Specification

The system MUST persist all operational state in SQLite.
The database file MUST reside in the state directory with write-ahead logging enabled.
The schema version MUST be integer four.
All database migrations MUST execute incrementally and idempotently.

### 3.1 Entity Model

The entity table MUST store unique entities with their type, name, and metadata.
Allowed entity types MUST be `campaign`, `swarm`, `agent`, or `artifact`.
The system MUST enforce strict hierarchy rules.
An `artifact` MUST link to an `agent`.
An `agent` MUST link to a `swarm`.
A `swarm` MUST link to a `campaign`.
The system MUST support custom agent and swarm groups.
Entities MUST support user-defined tags.
The system MUST record provenance and confidence for each entity.

### 3.2 Indicators of Compromise

The system MUST record indicators of compromise with operational categories.
Allowed IOC categories MUST include `domain`, `ip`, `agent_hash`, `prompt_signature`, and `nonce_grammar`.
Indicators MUST maintain explicit lifecycle states: `proposed`, `active`, `inactive`, `rejected`, or `benign`.
Promotion to active status MUST default to manual operator review.
When automatic promotion is enabled, the system MUST require distinct host evidence.
When automatic promotion is enabled, the system MUST require untainted evidence.
Operators MUST be able to mark indicators as benign false positives.
The system MUST log all lifecycle transitions with actor and timestamp.

### 3.3 Discovered URLs & Triage

The system MUST record all discovered and predicted URLs in the `urls` table.
Each URL record MUST include the source, normalized host, discovery time, and triage status.
Allowed triage statuses MUST be `discovered`, `examined`, `benign`, or `suspicious`.
Operators MUST be able to mark any URL as benign or suspicious.
Operators MUST be able to capture any URL directly as an `artifact` entity.

### 3.4 Prompt Templates

The system MUST store prompt templates in the `prompt_templates` table.
The system MUST seed default templates on database initialization.
Operators MUST be able to modify prompt templates at runtime.
Operators MUST be able to reset any prompt template to its default content.
The system MUST support variable token interpolation using double curly braces.
The system MUST support export and import of prompt templates in JSON format.

### 3.5 OSINT Sources & Grammar

The system MUST maintain index sources in the `osint_sources` table.
Supported source kinds MUST include `cdx`, `crtsh`, and `arxiv`.
Each source record MUST specify whether the source is enabled.
The system MUST store URL expansion grammar rules in the `url_grammar` table.
The system MUST dynamically generate candidate indicators from enabled grammar rules.
All external index requests MUST validate against allowlisted endpoints.

## 4. Interactive Sessions & Dynamic Attachment

The system MUST bind each hunt to a Hermes chat session identifier.
When an operator starts a hunt via chat, the system MUST bind the current session.
Operators MUST be able to attach any chat session to any active hunt.
When attached, the system MUST display recent tool calls, queries, and analysis rationale.
Operators MUST be able to spawn child hunts directly from chat sessions.
The system MUST provide tool calls to inspect context, query knowledge, and record findings.

## 5. Agent Tools Specification

The plugin MUST register the following tool definitions with the Hermes runtime:

1. `sf_get_context`: Returns current hunt state, open leads, and active indicators.
2. `sf_search_index`: Queries enabled OSINT index sources for indicators.
3. `sf_record_evidence`: Records analyzed web page evidence with taint metadata.
4. `sf_propose_ioc`: Submits candidate indicator terms for analyst review.
5. `sf_manage_entity`: Creates or updates agents, swarms, campaigns, or artifacts.
6. `sf_link_entities`: Creates directional links between entities.
7. `sf_triage_item`: Assigns operational status to indicators or URLs.
8. `sf_query_knowledge`: Searches entities, links, indicators, and evidence text.
9. `sf_spawn_subhunt`: Launches a concurrent child hunt for targeted investigation.
10. `sf_attach_hunt`: Binds the current conversation context to an active hunt.

All tools MUST sanitize input arguments.
All tools MUST return structured JSON dictionaries.

## 6. Safety & Taint Analysis

The system MUST treat all external web content as untrusted.
Fetched content MUST undergo screening for prompt injection signatures.
When injection phrasing is detected, the system MUST flag the evidence as tainted.
Tainted evidence MUST NOT support automatic indicator promotion.
The system MUST redact sensitive authentication tokens before persistence.
The system MUST NOT record operator credentials or private environment tokens.

## 7. Desktop User Interface

The desktop user interface MUST provide operational views across dedicated tabs:

1. **Hunt Tab**: Displays hunt metrics, activity stream, open leads, live URLs, and sessions.
2. **Knowledge Tab**: Displays interactive graph, entity hierarchy, groups, tags, and notes.
3. **Evidence Tab**: Displays captured text excerpts, provenance data, and taint indicators.
4. **IOCs Tab**: Displays indicator catalog, audit history, and review controls.
5. **URLs Tab**: Displays discovered URLs with triage controls and artifact capture.
6. **Prompts Tab**: Displays editable prompt templates with token substitution helper chips.
7. **Sources Tab**: Displays index toggles, URL grammar rules, and wordlist import.
8. **Settings Tab**: Displays operational configuration, schedule arms, export, and reset controls.

### 7.1 Text Selection & Interaction

The interface MUST allow text selection and copying across all pages and cards.
Cards, monospaced text blocks, and inputs MUST enable standard user selection.

### 7.2 Live URL Feed & Artifact Capture

The Hunt tab MUST display a live feed of recently discovered URLs.
Each URL entry MUST show the host, timestamp, and status.
Each URL entry MUST provide a single-click action to create an artifact entity.
The URLs tab MUST provide equivalent single-click artifact creation actions.

### 7.3 Data Reset Mechanism

The Settings page MUST provide a data reset control at the bottom.
The reset action MUST require explicit confirmation by the operator.
The CLI MUST require the `--force` flag for data reset.
When reset is invoked, the system MUST stop and join all background workers.
The system MUST drop all tables and re-apply schema migrations.
The system MUST re-seed default golden indicators, OSINT sources, and prompt templates.
The system MUST wipe all custom entities, evidence, and discovered URLs.

## 8. Conformance & Verification

Implementations MUST pass all unit and integration test suites.
The test suite MUST verify all API endpoints and database operations.
The test suite MUST verify offline operation using synthetic data.
Desktop interface components MUST render without errors in test environments.
All code MUST satisfy project linter rules.
