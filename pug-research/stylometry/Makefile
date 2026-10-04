.DEFAULT_GOAL := help
.PHONY: help download lexdb lexdb-v2 compare compare-v2 actions baselines style-exps all

# Stylometry experiment lane. All scripts are standard-library only.
# Raw downloads go to data/raw/ (untracked). Run `make help` for targets.

help: ## Show this help
	@awk -F':.*## ' '/^[a-z0-9-]+:.*## /{printf "  %-12s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

download: ## Download AI Village tables (HF_TOKEN required; skips existing files)
	bash fetch_aivillage.sh

lexdb: ## Build the partitioned lexical DB (PARTS, TOK)
	python3 build_lexdb.py --db lexdb.sqlite $(if $(PARTS),--partitions $(PARTS)) $(if $(TOK),--tokenizers $(TOK))

lexdb-v2: ## Build the functionally-matched lexdb v2 (PARTS, TOK; skips missing village tables)
	python3 build_lexdb_v2.py --db lexdb_v2.sqlite --skip-missing $(if $(PARTS),--partitions $(PARTS)) $(if $(TOK),--tokenizers $(TOK))

compare: ## Pairwise stylometric runs on lexdb v1 (PAIR="a b", MATRIX=1 for full matrix)
	python3 compare.py --db lexdb.sqlite $(if $(PAIR),--pair "$(PAIR)") $(if $(MATRIX),--matrix)

compare-v2: ## Pairwise stylometric runs on lexdb v2 (PAIR="a b", MATRIX=1 for full matrix)
	python3 compare.py --db lexdb_v2.sqlite $(if $(PAIR),--pair "$(PAIR)") $(if $(MATRIX),--matrix)

actions: ## Action-type distributions and transitions: computer-use turns vs traces
	python3 analyze_actions.py --out action_analysis.json

baselines: ## Split-half within-partition baselines for every method (adversarial #10)
	python3 baselines.py --db lexdb.sqlite --out baselines.json

style-exps: ## Seven non-lexical style experiments on v2 diagonal pairs (PAIRS="a:b,...")
	python3 experiments2.py --db lexdb_v2.sqlite $(if $(PAIRS),--pairs "$(PAIRS)")

all: ## Run the full stylometry lane: download, lexdb v1+v2, compare, actions
	$(MAKE) download
	$(MAKE) lexdb
	$(MAKE) lexdb-v2
	$(MAKE) compare MATRIX=1
	$(MAKE) compare-v2 MATRIX=1
	$(MAKE) actions
