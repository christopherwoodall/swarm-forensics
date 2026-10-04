# Hunt Brief: Report-Seeded Agent-Infrastructure Forensics

This brief instructs Hermes agents during report-seeded swarm investigations.
Agents receive this brief when starting a hunt seeded by an incident report.
Operators can load or edit this prompt in the Prompts tab.

---

## 1. Kickoff

Review the target incident report (for example, the Transluce report).
Identify entry points such as recorded web sessions.
Extract timestamped records of URLs, hosts, and response metadata.
Use these entries to seed your hunt for shared infrastructure and nonce grammars.

## 2. Investigation Steps

1. **Extract Indicators**:
   Extract every indicator of compromise from the report.
   Capture URLs, domains, URL patterns, parameter shapes, and relay hosts.
   Capture file paths, archive actions, and filter evasion claims.

2. **Verify Indicators Locally**:
   Cross-reference each indicator against available corpora and public indexes.
   Classify each indicator into one category:
   - **Confirmed**: Present with matching structure, cite counts, and timestamps.
   - **Commodity**: Present but generic public infrastructure.
   - **Quotation**: Present only in commentary discussing the incident after publication.
   - **Absent**: Clean negative result. Record search parameters.

3. **Expand Beyond the Seed Report**:
   The initial report is a seed, not a boundary.
   Search the corpus for indicators that the report missed.
   Identify unmentioned relay hosts and nesting patterns in proxied URLs.
   Detect archive-creation actions, parameter nonce grammars, and co-occurring domains.

4. **Grade Relationships**:
   Grade every relationship on the standard scale:
   - **Shared**: Same artifact across two or more layers.
   - **Linkage**: Artifact supported by corroborating evidence.
   - **Correlation**: Statistical co-occurrence only.
   Shared destinations that research agents routinely query are gravity wells, not linkage.

## 3. Report Format

Structure the final hunt findings with the following sections:

- **Per-IOC Verdict Table**: Include evidence, counts, and classification for each indicator.
- **Novel Findings**: Document discoveries that the seed report missed, with reproduction steps.
- **Clean Negatives**: List the three cleanest negative search results with exact queries.
- **Synthesis Paragraph**: Summarize the strongest finding, strongest limitation, and operational unity.

## 4. Epistemic Rules

- Stream large files line by line.
- Record all sampling strides.
- Treat a zero count as a valid result.
- Mark findings as verified or inferred every time.
- Restrict scope to agent infrastructure and public evidence.
- Never pursue human or operator attribution.