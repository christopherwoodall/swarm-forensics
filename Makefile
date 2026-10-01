.DEFAULT_GOAL := help
.PHONY: help setup data-info data-schema data-download data-sample data-validate replay-mock replay-export replay-serve test lint

# The repository can sit on a different filesystem than the uv cache.
export UV_LINK_MODE := copy

RUN := uv run

# Raw downloads MUST go to the untracked data/raw/ directory.
RAW_DIR := data/raw

# Optional: TABLES="events chat_messages" and REVISION=<commit>.
DATA_DIR ?= $(RAW_DIR)/sample
LIMIT ?= 100

# Replay viewer defaults. The case file stays under data/raw/.
CASE ?= $(RAW_DIR)/replay/sample-case.json
PORT ?= 8000

DOWNLOAD_ARGS := --dest $(RAW_DIR) $(if $(TABLES),--tables $(TABLES)) $(if $(REVISION),--revision $(REVISION))

help: ## Show this help
	@awk -F':.*## ' '/^[a-z-]+:.*## /{printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Create .venv and install dependencies with uv
	uv sync

data-info: setup ## List dataset files and sizes (no download; needs HF_TOKEN)
	$(RUN) python -m swarm_forensics.ingest.download info $(DOWNLOAD_ARGS)

data-schema: setup ## Download SCHEMA.md, CHANGELOG.md, manifest.json to data/raw/ (small; needs HF_TOKEN)
	$(RUN) python -m swarm_forensics.ingest.download download --schema-only --dest $(RAW_DIR) $(if $(REVISION),--revision $(REVISION))

data-download: setup ## Download all non-image files to data/raw/ (about 5.8 GB; needs HF_TOKEN)
	$(RUN) python -m swarm_forensics.ingest.download download $(DOWNLOAD_ARGS)

data-sample: setup ## Write synthetic sample tables to data/raw/sample/ (offline)
	$(RUN) python -m swarm_forensics.ingest.sample --dest $(RAW_DIR)/sample

data-validate: setup ## Validate tables against the JSON Schema (DATA_DIR, TABLES, LIMIT; default: sample, 100 rows)
	$(RUN) python -m swarm_forensics.ingest.schema --dir $(DATA_DIR) --limit $(LIMIT) $(if $(TABLES),--tables $(TABLES))

replay-mock: setup ## Write the synthetic replay case to data/raw/replay/ (offline)
	$(RUN) python -m swarm_forensics.replay --mock

replay-export: setup ## Export one real session as a replay case (SESSION=<uuid> required; reads data/raw/)
	@test -n "$(SESSION)" || { echo "Set SESSION=<uuid>."; exit 1; }
	$(RUN) python -m swarm_forensics.replay --session $(SESSION) --dir $(RAW_DIR)

replay-serve: setup ## Serve the 3D viz on 127.0.0.1 (CASE=<json>, PORT=8000)
	$(RUN) python data/viz_mock/v2/serve.py --case $(CASE) --port $(PORT)

test: setup ## Run the offline unit tests
	$(RUN) python -m unittest discover -s src -t src -p "test_*.py"

lint: setup ## Check code style with ruff
	$(RUN) ruff check src data/viz_mock/v2/serve.py
