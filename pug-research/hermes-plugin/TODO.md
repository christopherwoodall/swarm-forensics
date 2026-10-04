# TODO: Extend the Swarm Forensics desktop plugin

Work queue for [PLAN.md](PLAN.md). Delete a task line when it is done and verified.
Delete this file and PLAN.md when the queue is empty and the Definition of Done passes.

## Handoff rules

- Read [MODULE.md](MODULE.md) Sections 2 and 3 before you change code.
- Work top to bottom. Each phase depends on the phases above it.
- Run `make test` after each phase. Do not start the next phase while tests fail.
- Record a partial task under "In progress" with the exact file and step.
- The operator has not answered the open questions. Use the defaults in PLAN.md.
- Do not put files in `plugins/swarm-forensics/` unless they ship with the plugin. `make install` copies that folder.

## In progress

- (none)

## Operator decisions

- 2026-10-04: The operator approved the invariant 16 change and the hierarchy invariant. Record them in MODULE.md Section 5 during Phase 6.
- 2026-10-04: Seed several index sources. Each source gets an enable toggle in the plugin Sources tab. Seeds: Wayback CDX (on), arquivo.pt (on), urlquery (off, 404), Common Crawl index (off, the collection id needs updates).

## Phase 1: Storage (schema v2) - COMPLETE

## Phase 2: Registries

- [ ] `iocs.py`: extract `parse_wordlist(lines)`, and use it in `seed()`.
- [ ] NEW `registry.py`: `Registry` with source CRUD, `allowed_hosts`, grammar CRUD, `grammar_bundle`, `import_wordlist`, validation, `registry` events, and seeding of `DEFAULT_*` rows.
- [ ] `predict.py`: move the constants to `DEFAULT_GRAMMAR`. `generate_candidates(bundle)` and `matches_observed(url, patterns)` take rows.
- [ ] `sources.py`: remove the constants. Rows drive `queries_for` and `candidate_query`. `curl_get` checks `allowed_hosts`.
- [ ] `service.py`: build `Registry`, and seed it after migration.
- [ ] NEW `tests/test_registry.py`: validation, allowlist follows `enabled`, disabled host refused, seeded grammar matches old candidates, wordlist import, audit events.

## Phase 3: Entity hierarchy

- [ ] `safety.py`: new `ENTITY_TYPES`, `HIERARCHY`, `LINK_KINDS`, legacy maps. `parse_analysis` reads `campaigns` (alias `cases`).
- [ ] `entities.py`: `part_of` direction normalization, `parents`/`children` in `view()`, `rank` in `graph()`.
- [ ] `prompts.py`: new analysis schema and the hierarchy rule.
- [ ] `research.py`: artifact entity, `part_of` to agents (or swarms), sweep over enabled source rows, cursor key `src:<id>`, candidate probe through the `probe_candidates` row, `Parts.registry`.
- [ ] `tests/test_research.py` and `tests/test_store.py`: artifact `part_of` agent, enabled-only sweep, direction flip.

## Phase 4: Ledger, export, API

- [ ] `ledger.py`: `events()` filters `kind` and `level`. `close_lead()` accepts `dismissed` and returns bool.
- [ ] NEW `export.py`: `export_all()` writes streamed JSON and the Markdown vault to `state_dir()/exports/<stamp>/`.
- [ ] `plugin_api.py`: routes for events filters, `/leads/{id}/close`, `/sources`, `/grammar`, `/grammar/regenerate`, `/iocs/import`, `/export`. Map `RegistryError` to 400.
- [ ] `tests/test_api.py`: new routes, lead dismissal, event filters, export to a temp state dir.

## Phase 5: Desktop UI (`desktop/plugin.js`)

- [ ] `useApi(..., enabled)`. IocRow and EvidencePage fetch detail only when open.
- [ ] Rename `Error` to `ErrorNote`.
- [ ] GraphView: memoize on a signature, warm-start positions, rank force, new type shapes.
- [ ] Hunt tab: activity filters, Leads card with Dismiss, HuntDetail panel.
- [ ] Knowledge tab: new types and link kinds, Hierarchy card.
- [ ] NEW Sources tab: index sources, URL grammar, Regenerate, wordlist import.
- [ ] Settings tab: Export card. Palette: export command.
- [ ] `tests/js/sdk-stub.mjs`: honor `enabled: false`, record paths.
- [ ] `tests/render.test.mjs`: fixtures and tests for Sources, HuntDetail, Leads, Hierarchy. Assert no `/iocs/1` request while closed.

## Phase 6: Docs and Definition of Done

- [ ] MODULE.md: Sections 1 to 4 updated. Section 5 has a new entry and at most three entries.
- [ ] README.md and `skills/swarm-forensics/SKILL.md`: pages, vocabulary, export, Sources tab.
- [ ] `make test`, `make lint`, `make check` pass.
- [ ] `git status`: no stray files (`__pycache__`, exports, `.bak`).
- [ ] Manual desktop checks listed in PLAN.md "Manual Verification". The operator runs these.
- [ ] Delete PLAN.md and TODO.md.
