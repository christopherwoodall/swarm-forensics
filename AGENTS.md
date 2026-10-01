# Agent Directives & Operational Rules

## 1. Language & Voice

Agents MUST use Simplified Technical English (ASD-STE100) and RFC 2119 language for code comments, commits, documentation, and operational summaries.

* Use imperative, active-voice sentences.
* Keep sentences under 20 words.
* State one idea per sentence.
* Use `MUST`, `MUST NOT`, `SHOULD`, and `MAY` for requirements.
* Use consistent technical terms.
* Remove conversational and subjective language.

## 2. Repository Boundaries

* Keep architectural documentation in local `src/**/MODULE.md` files.
* Reserve `docs/` for MkDocs and GitHub Pages assets.
* Store raw downloads under untracked `data/raw/`.
* Keep code directly within designated module directories.
* Avoid unnecessary files and directories.

## 3. Living Documentation

Every `src/` subsystem MUST contain a `MODULE.md`.

For every task, agents MUST:

1. Read the nearest `MODULE.md` before changing code.
2. Inspect Section 2 (`Active Invariants`) and Section 3 (`Interfaces & Dependencies`).
3. Align changes with active invariants.
4. Propose invariant changes before implementing new system rules.
5. Update `MODULE.md` after verifying changes.
6. Update Section 3 when public interfaces change.
7. Update Section 4 (`Current State & Known Gaps`) when applicable.
8. Record decisions in Section 5 using:
   `- [YYYY-MM-DD Agent]: <Rationale>`

Section 5 MUST contain no more than three entries. Newest entries MUST appear first.

## 4. Contradiction Resolution

When directives conflict, agents MUST:

1. Stop code modifications.
2. Identify both statements, files, and line locations.
3. Quote both statements.
4. Ask: `Which directive takes precedence?`

Agents MUST NOT guess, silently overwrite, or choose precedence.

After clarification, agents MUST update the file in place, remove the superseded directive, and record the resolution in Section 5.

## 5. Data & Disk Safety

* Default to synthetic data using `make data-sample` or `--mock`.
* Stream `.jsonl.gz` files with `gzip.open()`.
* Process records one line at a time.
* Download only non-image dataset files. Exclude `images/`.
* Run `make data-download` only when the user asks for it.
* Read `$HF_TOKEN` directly from the environment.
* Never log, hard-code, or commit credentials.
* Never load the full dataset into memory.

## 6. Tooling & Workspace

* Treat the root `Makefile` as the single entry point for project commands.
* Run setup, test, lint, data, and build tasks through `make` targets.
* Do not call `python`, `uv`, `npm`, or similar tools directly when a target exists.
* Add a Makefile target for each new command. Do this for every language.
* Make `make test` and `make lint` cover every language in the repository.
* Describe each target with a `## description` comment. `make help` MUST list it.
* Python code MUST use `uv` and the `.venv` environment. Declare dependencies in `pyproject.toml`.
* JavaScript code SHOULD declare dependencies in `package.json`. Wrap its commands in `make` targets.
* Prefer Python standard-library modules for routine operations.
* Make the smallest change required for the task.
* Do not create temporary files or unnecessary artifacts.

## 7. Definition of Done

Before completing a task, agents MUST:

1. Run `make test` and verify that tests pass.
2. Verify the nearest `MODULE.md` reflects the final code.
3. Verify Section 5 contains no more than three entries.
4. Run `git status`.
5. Confirm no unintended temporary files or untracked directories remain.

Agents MUST report skipped checks and test failures instead of claiming completion.
