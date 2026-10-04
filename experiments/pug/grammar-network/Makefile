.DEFAULT_GOAL := help
.PHONY: help extract vcode-extract a b patterns behavior all

# Grammar-network experiment lane. All scripts are standard-library only.
# Build A tests structural convergence; Build B is the request-grammar
# toolkit fingerprint; patterns/behavior mine plain counts. Run `make help`.

help: ## Show this help
	@awk -F':.*## ' '/^[a-z0-9-]+:.*## /{printf "  %-12s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

extract: ## Extract natural language from inside source code (strings, comments, docs)
	python3 extract_code_text.py

vcode-extract: ## Extract natural language from village code-adjacent messages (claude/turns)
	python3 extract_village_code_nl.py

a: ## Build A: syntactic co-occurrence networks per partition (graph metrics, not words)
	python3 build_a.py

b: ## Build B: request-construction grammar graph (nonce templates, relay chains, param grammars)
	python3 build_b.py

patterns: ## Pattern DB (SQLite, stdlib): url/relay/param/nonce/action patterns + PATTERNS.md
	python3 patterns.py

behavior: ## Behavioral experiments: Markov, retry loops, burstiness, failure vocab -> BEHAVIOR.md
	python3 behavior.py

all: ## Run the full grammar lane: extract, build A, build B, patterns, behavior
	$(MAKE) extract
	$(MAKE) vcode-extract
	$(MAKE) a
	$(MAKE) b
	$(MAKE) patterns
	$(MAKE) behavior
