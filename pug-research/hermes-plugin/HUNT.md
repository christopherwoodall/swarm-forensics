# Hunt Brief: Report-Seeded Agent-Infrastructure Forensics

## Kickoff

Review the following [Transluce](https://transluce.org/agent-activity) report. Identify entry points, such as **urlquery** sessions (2026-05-01 → 06-30), that give you timestamped, structured records of what the agents actually fetched — URLs, hosts, and response metadata. Use these to seed your hunt for shared infrastructure and nonce grammars using the urlquery.net API.

## The hunt

1. **Extract** every IOC from the report and its urlquery sessions: URLs, domains, URL patterns, parameter shapes, relay/proxy hosts, file paths, and any behavioral claims (archiving, filter evasion, dead-drops).
2. **Verify each IOC locally** against the two corpora (incident traces + wiki, AI Village tables). For each one, decide:
   - **Confirmed** — present with matching structure (cite counts, layers, timestamps)
   - **Commodity** — present but generic infrastructure anyone would use
   - **Quotation** — present only inside agents *discussing* the incident after the fact (check timestamps against public reporting dates)
   - **Absent** — clean negative; record what you searched
3. **Go beyond the report.** The report is a seed, not a boundary. Mine the corpora for what it missed: relay hosts it didn't name, nesting patterns in proxied URLs, archive-creation behavior, nonce/parameter grammars, and domains both populations hit.
4. **Grade everything** on one scale: **shared** (same artifact, 2+ layers) vs **linkage** (artifact plus corroborating evidence) vs **correlation** (statistical only). Shared destinations that any research agent would hit are gravity wells, not linkage.

## Report format

- Per-IOC verdict table with evidence
- What the report missed, with reproduction steps
- Three cleanest negatives
- One paragraph: strongest finding, strongest limit, and whether this looks like one operation or two worlds

## Rules

- Stream large files; record sampling strides.
- A zero is a result.
- Mark verified vs inferred, every time.
- Agent infrastructure and public evidence only. No human attribution, ever.

---

Report in, IOCs out, corpora verify, and the hunt continues past the report's edges. urlquery first because it's timestamped and structured — the rest follows from what it surfaces.