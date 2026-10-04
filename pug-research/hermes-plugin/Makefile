.DEFAULT_GOAL := help
.PHONY: help check

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
