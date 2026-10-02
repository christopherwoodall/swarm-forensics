.DEFAULT_GOAL := help
.PHONY: help setup data-info data-download data-sample test lint watcher-client watcher-init watcher-read

# The repository can sit on a different filesystem than the uv cache.
export UV_LINK_MODE := copy

RUN := uv run

# Raw downloads MUST go to the untracked data/raw/ directory.
RAW_DIR := data/raw

WATCHER_CLIENT := $(RAW_DIR)/fairystack/external-agent-client.py
WATCHER_PRIVATE_DIR := $(HOME)/.config/fairystack-watcher
WATCHER_CONFIG := $(WATCHER_PRIVATE_DIR)/ca8ffac066a4.json
WATCHER_AFTER ?= 0

# Optional: TABLES="events chat_messages" and REVISION=<commit>.
DOWNLOAD_ARGS := --dest $(RAW_DIR) $(if $(TABLES),--tables $(TABLES)) $(if $(REVISION),--revision $(REVISION))

help: ## Show this help
	@awk -F':.*## ' '/^[a-z-]+:.*## /{printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Create .venv and install dependencies with uv
	uv sync

data-info: setup ## List dataset files and sizes (no download; needs HF_TOKEN)
	$(RUN) python -m swarm_forensics.ingest.download info $(DOWNLOAD_ARGS)

data-download: setup ## Download all non-image files to data/raw/ (about 5.8 GB; needs HF_TOKEN)
	$(RUN) python -m swarm_forensics.ingest.download download $(DOWNLOAD_ARGS)

data-sample: setup ## Write synthetic sample tables to data/raw/sample/ (offline)
	$(RUN) python -m swarm_forensics.ingest.sample --dest $(RAW_DIR)/sample

test: setup ## Run the offline unit tests
	$(RUN) python -m unittest discover -s src -t src -p "test_*.py"

lint: setup ## Check code style with ruff
	$(RUN) ruff check src

watcher-client: $(WATCHER_CLIENT) ## Download the official FairyStack external-agent client

$(WATCHER_CLIENT):
	@mkdir -p "$(dir $(WATCHER_CLIENT))"
	curl --fail --silent --show-error --location --proto '=https' --max-time 30 --output "$@" https://multi.fairystack.com/external-agent-client.py

watcher-init: watcher-client ## Create a private watcher credential and print public enrollment metadata
	@install -d -m 700 "$(WATCHER_PRIVATE_DIR)"
	$(RUN) python "$(WATCHER_CLIENT)" --config "$(WATCHER_CONFIG)" init --origin https://multi.fairystack.com --id hermes-maria-ca8ffac066a4 --name "Hermes Silent Watcher"

watcher-read: watcher-client ## Read the enrolled conversation with WATCHER_AFTER as its cursor
	$(RUN) python "$(WATCHER_CLIENT)" --config "$(WATCHER_CONFIG)" read --after "$(WATCHER_AFTER)"
