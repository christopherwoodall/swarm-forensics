.DEFAULT_GOAL := help
.PHONY: help setup index index-sample index-memories report serve start stop status restart llm test lint clean

# The repository can sit on a different filesystem than the uv cache.
export UV_LINK_MODE := copy

RUN := uv run
PORT ?= 8002
DATA_DIR ?= ../../data/raw
DB_PATH ?= ../../data/raw/trajectories/index-v2.db
LIMIT ?= 200000
PID_FILE := .serve.pid

help: ## Show this help
	@awk -F':.*## ' '/^[a-z-]+:.*## /{printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Create the local .venv with uv (pyyaml, ruff)
	uv sync

index: setup ## Stream data/raw/ into the v2 index (resumable; scans each archive once)
	$(RUN) python importer.py --dir $(DATA_DIR) --db $(DB_PATH)

index-sample: setup ## Build a bounded sample index (LIMIT rows per table) at DB_PATH
	$(RUN) python importer.py --dir $(DATA_DIR) --db $(DB_PATH) --limit $(LIMIT)

index-memories: setup ## Also scan agent_memories (about 2.3 GB, optional; counts rows only)
	$(RUN) python importer.py --dir $(DATA_DIR) --db $(DB_PATH) --memories

report: setup ## Print the coverage report for the index at DB_PATH
	$(RUN) python importer.py --report --dir $(DATA_DIR) --db $(DB_PATH)

serve: setup ## Run the 3D viewer on 127.0.0.1 in the foreground (PORT=8002)
	$(RUN) python serve.py --port $(PORT) --db $(DB_PATH)

start: setup ## Start the 3D viewer in the background
	@if [ -f $(PID_FILE) ] && kill -0 $$(cat $(PID_FILE)) 2>/dev/null; then \
		echo "Server already running (PID $$(cat $(PID_FILE)))."; \
	else \
		nohup $(RUN) python serve.py --port $(PORT) --db $(DB_PATH) > serve.log 2>&1 & echo $$! > $(PID_FILE); \
		sleep 2; \
		if kill -0 $$(cat $(PID_FILE)) 2>/dev/null; then \
			echo "Viewer at http://127.0.0.1:$(PORT)/ (PID $$(cat $(PID_FILE)))."; \
		else echo "Server failed to start. See serve.log."; rm -f $(PID_FILE); exit 1; fi; \
	fi

stop: ## Stop the background 3D viewer
	@if [ -f $(PID_FILE) ]; then \
		pkill -P $$(cat $(PID_FILE)) 2>/dev/null || true; \
		kill $$(cat $(PID_FILE)) 2>/dev/null || true; \
		rm -f $(PID_FILE); echo "Server stopped."; \
	else echo "Server is not running."; fi

status: ## Show whether the background viewer runs
	@if [ -f $(PID_FILE) ] && kill -0 $$(cat $(PID_FILE)) 2>/dev/null; then \
		echo "Running on http://127.0.0.1:$(PORT)/ (PID $$(cat $(PID_FILE)))."; \
	else echo "Stopped."; fi

restart: stop start ## Restart the background viewer

llm: setup ## Opt-in LLM link hypotheses (TRACES="session:<id> ..." MODEL=<name> MAX_USD=<n>; see llm.example.yaml)
	@test -n "$(TRACES)" || { echo "Set TRACES=\"session:<id> episode:<id>\"."; exit 1; }
	$(RUN) python llm.py --enable-llm --db $(DB_PATH) --model "$(MODEL)" --max-usd "$(MAX_USD)" $(foreach t,$(TRACES),--trace $(t))

test: setup ## Run the offline unit tests (synthetic data, no network)
	$(RUN) python -m unittest discover -s . -p "test_*.py"

lint: setup ## Check Python code style with ruff
	$(RUN) ruff check .

clean: stop ## Stop the viewer and remove logs and caches
	rm -f serve.log
	rm -rf __pycache__ .ruff_cache
