.DEFAULT_GOAL := help
.PHONY: help test lint check install uninstall js-deps

# Hermes swarm-forensics plugin lane. Run `make help` for targets.
# The root Makefile delegates here (hermes-test, hermes-lint, hermes-install).

UV_PROJECT := ../..
export UV_LINK_MODE := copy

PLUGIN_ID  := swarm-forensics
PLUGIN_SRC := plugins/$(PLUGIN_ID)

# Test-only JS dependencies (react) live outside the repository, on a Linux
# path. They are never copied into the installed plugin.
JS_DEPS := $(HOME)/.cache/swarm-forensics-plugin/js

# Pick the Hermes to install into. Order: an explicit HERMES_HOME, then the
# Windows desktop app (when this runs under WSL), then ~/.hermes.
WIN_HERMES := /mnt/c/Users/$(WIN_USER)/AppData/Local/hermes
ifdef HERMES_HOME
  HERMES_BIN ?= hermes
else ifneq ($(wildcard $(WIN_HERMES)/config.yaml),)
  HERMES_HOME := $(WIN_HERMES)
  HERMES_BIN ?= $(WIN_HERMES)/bin/hermes.exe
else
  HERMES_HOME := $(HOME)/.hermes
  HERMES_BIN ?= hermes
endif
PLUGIN_DST := $(HERMES_HOME)/plugins/$(PLUGIN_ID)

help: ## Show this help
	@awk -F':.*## ' '/^[a-z0-9-]+:.*## /{printf "  %-12s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

$(JS_DEPS)/node_modules/react-dom/package.json: tests/package.json
	mkdir -p $(JS_DEPS)
	cp tests/package.json $(JS_DEPS)/package.json
	npm install --prefix $(JS_DEPS) --no-audit --no-fund

js-deps: $(JS_DEPS)/node_modules/react-dom/package.json ## Install the test-only JS dependencies (react) under ~/.cache

test: js-deps ## Run the offline tests: Python engine and API, JS render of the desktop page
	uv run --project $(UV_PROJECT) python -m unittest discover -s tests -p "test_*.py"
	SF_JS_DEPS=$(JS_DEPS) node --test tests/render.test.mjs

lint: ## Run ruff on the plugin and its tests
	uv run --project $(UV_PROJECT) ruff check --line-length 100 --select E,F,W,I $(PLUGIN_SRC) tests

check: ## Validate the package: required files, manifests, python and JS syntax
	@for f in plugin.yaml __init__.py dashboard/manifest.json dashboard/plugin_api.py desktop/plugin.js skills/$(PLUGIN_ID)/SKILL.md; do \
		test -f $(PLUGIN_SRC)/$$f || { echo "missing $(PLUGIN_SRC)/$$f"; exit 1; }; \
	done
	python3 -c "import json; m = json.load(open('$(PLUGIN_SRC)/dashboard/manifest.json')); assert m['name'] == '$(PLUGIN_ID)' and m['api'] == 'plugin_api.py'"
	python3 -m compileall -q $(PLUGIN_SRC)
	@find $(PLUGIN_SRC) -name __pycache__ -prune -exec rm -rf {} +
	node --input-type=module --check < $(PLUGIN_SRC)/desktop/plugin.js
	@echo "$(PLUGIN_ID) package OK"

install: check ## Install into the local Hermes ($$HERMES_HOME/plugins) and enable it
	@case "$(PLUGIN_DST)" in */plugins/$(PLUGIN_ID)) ;; *) echo "refusing odd target: $(PLUGIN_DST)"; exit 1;; esac
	@echo "Target: $(PLUGIN_DST)"
	mkdir -p $(PLUGIN_DST)
	@# Replace the code. Keep state/ so a first-generation install can still be imported.
	find $(PLUGIN_DST) -mindepth 1 -maxdepth 1 ! -name state -exec rm -rf {} +
	cp -R $(PLUGIN_SRC)/. $(PLUGIN_DST)/
	@find $(PLUGIN_DST) -name __pycache__ -prune -exec rm -rf {} +
	@if command -v "$(HERMES_BIN)" >/dev/null 2>&1 || test -x "$(HERMES_BIN)"; then \
		"$(HERMES_BIN)" plugins enable $(PLUGIN_ID) || echo "Enable failed. Run: hermes plugins enable $(PLUGIN_ID)"; \
	else \
		echo "hermes CLI not found. Add '$(PLUGIN_ID)' to plugins.enabled in $(HERMES_HOME)/config.yaml"; \
	fi
	@echo "Installed. Restart the Hermes desktop app (or gateway) so the backend routes mount."

uninstall: ## Remove the plugin from the local Hermes (the hunt database is kept)
	@case "$(PLUGIN_DST)" in */plugins/$(PLUGIN_ID)) ;; *) echo "refusing odd target: $(PLUGIN_DST)"; exit 1;; esac
	-@if command -v "$(HERMES_BIN)" >/dev/null 2>&1 || test -x "$(HERMES_BIN)"; then "$(HERMES_BIN)" plugins disable $(PLUGIN_ID); fi
	rm -rf $(PLUGIN_DST)
	@echo "Removed $(PLUGIN_DST). Data stays in $(HERMES_HOME)/$(PLUGIN_ID)/."
