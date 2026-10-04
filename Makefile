.DEFAULT_GOAL := help
.PHONY: help setup data-info data-schema data-download data-sample data-validate replay-mock replay-export replay-serve pivot-check pivot-serve stylo-lexdb stylo-lexdb-v2 stylo-compare stylo-compare-v2 stylo-actions grammar-net goal-match goal-invert goal-ablate village-download pug-all test lint hermes-test hermes-lint hermes-check hermes-install hermes-uninstall watcher-client watcher-init watcher-read watcher-poll watcher-pending watcher-ack watcher-status watcher-monitor

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
PIVOT_FILE ?= pug-research/experiments/viz_mock/v3_transluce/data/graph.json
PIVOT_PORT ?= 8001

DOWNLOAD_ARGS := --dest $(RAW_DIR) $(if $(TABLES),--tables $(TABLES)) $(if $(REVISION),--revision $(REVISION))

help: ## Show this help
	@awk -F':.*## ' '/^[a-z0-9-]+:.*## /{printf "  %-18s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

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
	$(RUN) python pug-research/experiments/viz_mock/v2/serve.py --case $(CASE) --port $(PORT)

pivot-check: setup ## Check the pivot graph file shape (PIVOT_FILE=<json>)
	$(RUN) python -m swarm_forensics.pivot --file $(PIVOT_FILE)

# pug-research experiment lanes. Each lane owns its Makefile; the root delegates.
# Run `make -C <lane> help` for lane-local targets.
STYLO_DIR := pug-research/stylometry
GOAL_DIR := pug-research/goal-inference
GRAM_DIR := pug-research/grammar-network
HERMES_DIR := pug-research/hermes-plugin

pivot-serve: setup ## Serve the pivot graph viewer on 127.0.0.1 (PIVOT_PORT=8001)
	$(RUN) python pug-research/experiments/viz_mock/v3_transluce/serve.py --port $(PIVOT_PORT)

village-download: ## Download AI Village tables (HF_TOKEN required; skips existing files)
	$(MAKE) -C $(STYLO_DIR) download

stylo-lexdb: ## Build the partitioned lexical DB (STYLO_PARTS, STYLO_TOK)
	$(MAKE) -C $(STYLO_DIR) lexdb $(if $(STYLO_PARTS),PARTS="$(STYLO_PARTS)") $(if $(STYLO_TOK),TOK="$(STYLO_TOK)")

stylo-lexdb-v2: ## Build the functionally-matched lexdb v2 (STYLO_PARTS, STYLO_TOK)
	$(MAKE) -C $(STYLO_DIR) lexdb-v2 $(if $(STYLO_PARTS),PARTS="$(STYLO_PARTS)") $(if $(STYLO_TOK),TOK="$(STYLO_TOK)")

stylo-compare: ## Pairwise stylometric runs (PAIR="a b", MATRIX=1 for full matrix)
	$(MAKE) -C $(STYLO_DIR) compare $(if $(PAIR),PAIR="$(PAIR)") $(if $(MATRIX),MATRIX=1)

stylo-compare-v2: ## Pairwise stylometric runs on lexdb v2 (PAIR="a b", MATRIX=1)
	$(MAKE) -C $(STYLO_DIR) compare-v2 $(if $(PAIR),PAIR="$(PAIR)") $(if $(MATRIX),MATRIX=1)

stylo-actions: ## Action-type distributions and transitions: computer-use turns vs traces
	$(MAKE) -C $(STYLO_DIR) actions

grammar-net: ## Grammar networks: extract (MODE=extract), co-occurrence graphs (MODE=a), request-grammar graph (MODE=b), or all (MODE=all)
	$(MAKE) -C $(GRAM_DIR) $(if $(MODE),$(MODE),all)

goal-match: ## Fragment-to-goal matcher (MODE=loo|anchored|infer|all, FRAG=stride2|drop_top5)
	$(MAKE) -C $(GOAL_DIR) match $(if $(MODE),MODE=$(MODE)) $(if $(FRAG),FRAG=$(FRAG))

goal-invert: ## Prompt inversion: mine village prompts, map prompt->behavior, invert to holdout (MODE=mine|map|invert|all)
	$(MAKE) -C $(GOAL_DIR) invert $(if $(MODE),MODE=$(MODE))

goal-ablate: ## Goal-inference ablations: feature families, village confusion, prompt elements, evidence types
	$(MAKE) -C $(GOAL_DIR) ablate

# Full pug-research pipeline, end to end. Recreates every lane from raw data.
# Needs HF_TOKEN for the download step; all other steps are offline and idempotent.
pug-all: ## Run the full pug-research pipeline: download, stylometry, grammar nets, goal inference
	$(MAKE) -C $(STYLO_DIR) all
	$(MAKE) -C $(GRAM_DIR) all
	$(MAKE) -C $(GOAL_DIR) all

hermes-test: setup ## Run the Hermes plugin tests (offline)
	$(MAKE) -C $(HERMES_DIR) test

hermes-lint: setup ## Lint the Hermes plugin
	$(MAKE) -C $(HERMES_DIR) lint

hermes-check: setup ## Validate the Hermes plugin package (files, manifests, syntax)
	$(MAKE) -C $(HERMES_DIR) check

hermes-install: setup ## Install the Hermes plugin into the local Hermes and enable it (HERMES_HOME optional)
	$(MAKE) -C $(HERMES_DIR) install

hermes-uninstall: ## Remove the Hermes plugin from the local Hermes (keeps the database)
	$(MAKE) -C $(HERMES_DIR) uninstall

test: setup hermes-test jesse-test ## Run the offline unit tests (includes the Hermes plugin)
	$(RUN) python -m unittest discover -s src -t src -p "test_*.py"

lint: setup hermes-lint jesse-lint ## Check code style with ruff (includes the Hermes plugin)
	$(RUN) ruff check src pug-research/experiments/viz_mock/v2/serve.py pug-research/experiments/viz_mock/v3_transluce/serve.py

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

JESSE_DIR := experiments/jesse/discord-bot-swarm
.PHONY: jesse-setup jesse-check jesse-build jesse-test jesse-lint jesse-browser-test

$(JESSE_DIR)/node_modules/.package-lock.json: $(JESSE_DIR)/package-lock.json $(JESSE_DIR)/package.json
	cd $(JESSE_DIR) && npm ci --no-audit --no-fund

jesse-setup: $(JESSE_DIR)/node_modules/.package-lock.json ## Install locked Discord Swarm dependencies

jesse-check: ## Verify the imported Discord Swarm source hashes
	node experiments/jesse/check-source.mjs

jesse-build: jesse-setup ## Build Discord Swarm browser assets
	cd $(JESSE_DIR) && npm run build

jesse-test: jesse-setup jesse-check ## Run offline Discord Swarm unit tests
	$(MAKE) -C $(JESSE_DIR) test

jesse-lint: jesse-setup jesse-check ## Check Discord Swarm JavaScript syntax
	$(MAKE) -C $(JESSE_DIR) lint
	node --check experiments/jesse/check-source.mjs
	sh -n $(JESSE_DIR)/deploy/postgres/init.sh

jesse-browser-test: jesse-setup ## Test Discord Swarm onboarding with synthetic fixtures
	cd $(JESSE_DIR) && npm run test:wizard
