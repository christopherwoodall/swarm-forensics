---

name: living-docs
description: Mandatory pre-flight and post-flight procedure for code changes.

---

# Living Docs Procedure
Execute this procedure when creating, modifying, or deleting code in a subsystem.

## 1. Pre-Flight
Execute before writing code.

1. **Locate the Blackboard**
   * Identify the source file planned for modification.
   * Traverse upward to locate the nearest `MODULE.md`.
2. **Detect Contradictions**
   * Scan `MODULE.md` for duplicate or conflicting rules.
   * If conflicting rules exist, HALT code modifications.
   * Quote the conflicting statements and identify their locations.
   * Ask: `Which statement takes precedence?`
   * Await operator instruction before continuing.
3. **Inspect Active Invariants**
   * Read Section 2 (`Active Invariants`).
   * Code changes MUST NOT violate active invariants.
   * If a task conflicts with an invariant, HALT and request an invariant change.
4. **Inspect Interfaces**
   * Read Section 3 (`Interfaces & Dependencies`).
   * Identify relevant exports, schemas, and dependencies.
   * Align the implementation with these contracts.

## 2. Post-Flight
Execute after tests pass.

1. **Update the Blackboard**
   * Reopen the `MODULE.md` inspected during pre-flight.
   * Update Section 3 when exports or schemas change.
   * Update Section 4 (`Current State & Known Gaps`) when state changes.
   * Update Section 2 ONLY when system rules intentionally change.

2. **Record Decisions**
   * Add decisions to Section 5 using:
     `- [YYYY-MM-DD Agent]: <Rationale>`
   * Keep the newest entry first.
   * Section 5 MUST contain no more than three entries.
   * Remove the oldest entries when the limit is exceeded.
