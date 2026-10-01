# Status: Swarm Forensics

Last verified: 2026-10-01.
Branch: `colette-help-peer`.
Base revision: `79b1840702591f0fd5253d6b3752264b635d3904`.
Authority: verified local checkpoint, not an implementation specification.

## Verified checkpoint

- `make help`: listed the existing project commands.
- `make test`: passed all 16 offline tests.
- `make lint`: passed Ruff checks on Python source.
- `make data-sample`: wrote three synthetic tables under `data/raw/sample/`.
- Streaming inspection: parsed every sample line as JSON.
- Sample records: 3 agent goals, 20 chat messages, and 50 events.
- Ignore verification: all three sample files are excluded from Git.
- Documentation checker: seven project documents checked, with no findings. Unrelated logs were excluded.
- Module decision logs: core contains three entries; ingest contains one.
- Local `HEAD` and `main` remain at the base revision above.

The bootstrap changed documentation only.
No commit, push, or real dataset download was performed.
No browser collection was restarted to complete this documentation pass.

## Working now

- Acquire non-image AI Village files through the existing downloader.
- Inspect dataset metadata with `make data-info`, after configuring approved access.
- Generate synthetic acquisition samples offline.
- Find project discussion and evidence limits in [PROJECT_BRIEF.md](PROJECT_BRIEF.md).
- Find setup instructions and the authority map in [README.md](README.md).

The downloader's network path was not exercised during this pass.
Source inspection and offline tests support its documented interfaces.
The existing 3D mocks use synthetic data and external CDN imports.
Their browser behavior was not checked during this bootstrap.

## Incomplete or broken

- No unified forensic schema, timeline parser, or graph pipeline is implemented.
- No anomaly analysis engine or Swarmtraces parser is implemented.
- No real-data graph integration is verified.
- No Hermes swarm-search plugin is implemented.
- No FairyStack or Discord integration was inspected or configured.
- Existing test and lint targets do not exercise the HTML/JavaScript mocks.
- Referenced egress-scan and visualization-bundle attachments remain unreviewed.
- Saved chat snapshots do not establish complete conversation coverage.
- Prior analysis results are attributed reports, not results reproduced here.

The earlier remote fetch failed because GitHub authentication was unavailable.
This bootstrap uses local `main`; newer remote changes remain unverified.

## Active work

The documentation bootstrap is complete.
No implementation slice has been accepted in this pass.
The project brief separates research interests, product ideas, and collaboration experiments.
Existing active invariants remain unchanged.

## Next useful action

Select one initial demonstration and its evidence source.
Read the open decisions in [PROJECT_BRIEF.md](PROJECT_BRIEF.md#open-decisions).
Then define a bounded implementation specification before building the forensic pipeline.

The temporal coordination explorer is a discussed direction, not an approved construction task.
The agent-coordination experiment is separate from the forensic deliverable.

## Re-entry notes

Run `make setup`, `make test`, `make lint`, and `make data-sample` from the repository root.
Start with synthetic data; real downloads require explicit user approval.

During validation, `uv sync` removed the lockfile's `exclude-newer` options.
That unrelated lockfile change was restored after inspecting its diff.
Review future lockfile changes rather than including validation churn in documentation work.

The pre-existing untracked `hermes-log/` directory was left untouched.
No raw conversation, screenshot, private invitation, or credential was added by this bootstrap.
Changes remain uncommitted on `colette-help-peer` for review and selective integration.
