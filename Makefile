.DEFAULT_GOAL := help
.PHONY: help setup data-info data-download data-sample test lint watcher-client watcher-init watcher-read
.PHONY: help setup data-info data-schema data-download data-sample data-validate replay-mock replay-export replay-serve pivot-check pivot-serve test lint
.PHONY: watcher-poll watcher-pending watcher-ack watcher-status watcher-monitor

# The repository can sit on a different filesystem than the uv cache.
export UV_LINK_MODE := copy

RUN := uv run

# Raw downloads MUST go to the untracked data/raw/ directory.
RAW_DIR := data/raw

WATCHER_CLIENT := $(RAW_DIR)/fairystack/external-agent-client.py
WATCHER_PRIVATE_DIR := $(HOME)/.config/fairystack-watcher
WATCHER_CONFIG := $(WATCHER_PRIVATE_DIR)/ca8ffac066a4.json
WATCHER_AFTER ?= 0
WATCHER_DB ?= $(RAW_DIR)/fairystack/ca8ffac066a4/source.sqlite
WATCHER_LIMIT ?= 50
WATCHER_MAX_PAGES ?= 20
WATCHER_TOTAL_SECONDS ?= 30
WATCHER_RETRY_SECONDS ?= 900
WATCHER_RUN = $(RUN) $(if $(findstring --frozen,$(RUN)),,--frozen)
WATCHER_CMD = $(WATCHER_RUN) python -m swarm_forensics.watcher --db "$(WATCHER_DB)" --config "$(WATCHER_CONFIG)"

# Optional: TABLES="events chat_messages" and REVISION=<commit>.
DATA_DIR ?= $(RAW_DIR)/sample
LIMIT ?= 100

# Replay viewer defaults. The case file stays under data/raw/.
CASE ?= $(RAW_DIR)/replay/sample-case.json
PORT ?= 8000

# Pivot graph viewer (v3_transluce).
PIVOT_FILE ?= data/viz_mock/v3_transluce/data/graph.json
PIVOT_PORT ?= 8001

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

pivot-check: setup ## Check the pivot graph file shape (PIVOT_FILE=<json>)
	$(RUN) python -m swarm_forensics.pivot --file $(PIVOT_FILE)

pivot-serve: setup ## Serve the pivot graph viewer on 127.0.0.1 (PIVOT_PORT=8001)
	$(RUN) python data/viz_mock/v3_transluce/serve.py --port $(PIVOT_PORT)

test: setup ## Run the offline unit tests
	$(RUN) python -m unittest discover -s src -t src -p "test_*.py"

lint: setup ## Check code style with ruff
	$(RUN) ruff check src data/viz_mock/v2/serve.py data/viz_mock/v3_transluce/serve.py

watcher-client: $(WATCHER_CLIENT) ## Download the official FairyStack external-agent client

$(WATCHER_CLIENT):
	@mkdir -p "$(dir $(WATCHER_CLIENT))"
	@curl --fail --silent --show-error --location --proto '=https' --max-time 30 --output "$@" https://multi.fairystack.com/external-agent-client.py

watcher-init: watcher-client ## Create a private watcher credential and print public enrollment metadata
	@install -d -m 700 "$(WATCHER_PRIVATE_DIR)"
	$(RUN) python "$(WATCHER_CLIENT)" --config "$(WATCHER_CONFIG)" init --origin https://multi.fairystack.com --id hermes-maria-ca8ffac066a4 --name "Hermes Silent Watcher"

watcher-read: watcher-client ## Read the enrolled conversation with WATCHER_AFTER as its cursor
	@$(RUN) python "$(WATCHER_CLIENT)" --config "$(WATCHER_CONFIG)" read --after "$(WATCHER_AFTER)"

watcher-poll: ## Archive fresh source pages with bounded GET requests
	@$(WATCHER_CMD) poll --max-pages "$(WATCHER_MAX_PAGES)" --total-seconds "$(WATCHER_TOTAL_SECONDS)"

watcher-pending: ## Emit unprocessed source events as JSON (WATCHER_LIMIT=50)
	@$(WATCHER_CMD) pending --limit "$(WATCHER_LIMIT)"

watcher-ack: ## Acknowledge durable analysis (WATCHER_CURSOR required)
	@test -n "$(WATCHER_CURSOR)" || { printf '%s\n' 'Set WATCHER_CURSOR=<cursor>.' >&2; exit 1; }
	@$(WATCHER_CMD) ack --cursor "$(WATCHER_CURSOR)"

watcher-status: ## Emit archive cursors and pending count as JSON
	@$(WATCHER_CMD) status

watcher-monitor: ## Poll and emit WATCHER_IDLE or a backlog wake generation
	@$(WATCHER_CMD) monitor --max-pages "$(WATCHER_MAX_PAGES)" --total-seconds "$(WATCHER_TOTAL_SECONDS)" --retry-seconds "$(WATCHER_RETRY_SECONDS)"
