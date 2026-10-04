# Status: Swarm Forensics

Last verified: 2026-10-04.
Branch: `morphology-hunter-integration`.
Integration base: `df265db`.
Authority: verified local checkpoint, not a deployment receipt.

## Verified checkpoint

- `make test`: 189 plugin Python tests, 39 plugin JavaScript tests, 91 Discord Swarm tests, and 7 synchronization tests passed.
- `make lint`: plugin Python checks and maintained JavaScript syntax checks passed.
- `make check`: plugin manifests, Python compilation, and ESM syntax passed.
- Main migrations 1–5 retain their original fingerprint. Migration 6 adds morphology candidates and review history.
- Synthetic v5 upgrade preserves session bindings, corpus observations, and mirror metadata.
- Unknown-pattern, adaptive-probe, transient-inspection, and exact API read-back tests passed.
- Discovery-generated cards, SQLite state, CLI stdout, and saved reports exclude the synthetic source-copy canary.
- Receiver tests verify key redaction, collision rejection, taint screening, safe field selectors, and page-boundary reconstruction.
- Held-response tests reject discovery persistence after reset. Two-thread tests preserve review transition history.
- CLI tests refuse exact, symlink, hardlink, and directory-member source-output collisions.
- Single-page, multi-page, and full-card tests preserve short-assignment JSON syntax.
- Jesse source hashes match the imported revision.

Final verification used a fresh Python environment and cached React dependencies.
Discord Swarm dependencies were installed from the offline npm cache.
Ambient Hermes session variables were removed for isolated tests.
Default root setup, test, lint, and check targets passed without setup suppression.

## Working now

- Session-native hunts, chat narration, corpus observation, and text mirrors remain available.
- Morphologies provides authorized raw-data discovery and audited candidate intake.
- Root Make targets delegate to the showcase plugin and Jesse experiment.
- The plugin owns its development manifest and lockfile.

## Incomplete or unverified

- Live Hermes desktop interaction is unverified. Render and request-handler tests use synthetic fixtures.
- Discovery measures recurrence, not verified coordination, causal dependence, or actor identity.
- Sequence shortlists are frequency-capped before null comparison.
- Joint support across observations and novelty remain unmeasured.
- Final-round probe requests can execute without another model feedback round.
- PostgreSQL integration and Jesse browser suites were not run during this integration.
- The generic documentation audit reports three inherited format findings: a template-token example, Approved status, and the spec index.
- Two independent reviews found six blockers. All fixes pass regression tests. The owner waived further review for submission.
- GitHub write authentication remains unavailable at the last push preflight.

## Next transition

Authenticate GitHub with repository write access.
Publish the integration branch. The owner controls the submission merge.
Required GitHub checks MUST pass before merge.
Read back the merged commit before claiming remote completion.
