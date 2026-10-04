.DEFAULT_GOAL := help
.PHONY: help check selftest desktop-check

# Hermes tracehound plugin lane. Scaffolds the Hermes-agent skill that runs
# the hunt methodology on a loop. Run `make help` for targets.

help: ## Show this help
	@awk -F':.*## ' '/^[a-z0-9-]+:.*## /{printf "  %-12s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

check: ## Validate scaffold: python syntax + required files present
	python3 -m py_compile skills/tracehound/scripts/tracehound.py skills/tracehound/scripts/lib/*.py
	@test -f skills/tracehound/SKILL.md || { echo "missing SKILL.md"; exit 1; }
	@test -f skills/tracehound/config.example.ini || { echo "missing config.example.ini"; exit 1; }
	@test -f MODULE.md || { echo "missing MODULE.md"; exit 1; }
	@test -f DESIGN.md || { echo "missing DESIGN.md"; exit 1; }
	@echo "tracehound scaffold OK"

selftest: ## Run firewall golden selftest: parser + taint screen, no model calls
	python3 skills/tracehound/scripts/lib/firewall.py --selftest

desktop-check: ## Syntax-check desktop plugin.js (node --check) and plugin_api.py (py_compile)
	if command -v node >/dev/null 2>&1; then \
		cp skills/tracehound/desktop/plugin.js /tmp/tracehound-plugin-check.mjs && \
		node --check /tmp/tracehound-plugin-check.mjs && \
		rm -f /tmp/tracehound-plugin-check.mjs && \
		echo "plugin.js: node --check OK"; \
	else \
		echo "node not found; run the manual load test:"; \
		echo "  1. Open the Hermes desktop app"; \
		echo "  2. Go to Capabilities -> Plugins"; \
		echo "  3. Enable tracehound"; \
		echo "  4. Check the console for load errors"; \
	fi
	python3 -m py_compile skills/tracehound/dashboard/plugin_api.py && echo "plugin_api.py: py_compile OK"
