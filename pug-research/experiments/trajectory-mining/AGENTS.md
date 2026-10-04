# Trajectory Mining: Agent Notes

The root `AGENTS.md` applies. This file adds local rules.

* Read `MODULE.md` in this directory before you change code.
* Run commands through `make` in this directory. The root `Makefile` does not cover this module.
* Use synthetic fixtures (`test_fixtures.py`) in tests. Tests MUST NOT read `data/raw/` or use the network.
* Run `make index` or `make index-sample` only when the user asks. Use `LIMIT` for first runs.
* Keep the default `DB_PATH`. The importer stages on a Linux path and moves the index into `data/raw/trajectories/`.
* Do not delete an index unless the user asks. `--rebuild` deletes only the file you name.
* Keep `llm.py` off by default. Never print or store API keys.
* Run `make test` and `make lint` before you finish.
* Update `MODULE.md` after verified changes.
