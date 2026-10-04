.DEFAULT_GOAL := help
.PHONY: help match invert ablate all

# Goal-inference experiment lane. All scripts are standard-library only.
# match: fragment -> goal on the labeled eval set, then the OpenAI holdout.
# invert: mine village prompt-like content, map prompt -> behavior, invert
# to the holdout. Holdout labels stay hypotheses. Run `make help` for targets.

help: ## Show this help
	@awk -F':.*## ' '/^[a-z0-9-]+:.*## /{printf "  %-12s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

match: ## Fragment-to-goal matcher (MODE=loo|anchored|infer|all, FRAG=stride2|drop_top5)
	python3 match.py --mode $(if $(MODE),$(MODE),all) --frag-mode $(if $(FRAG),$(FRAG),stride2)

invert: ## Prompt inversion: mine village prompts, map prompt->behavior, invert to holdout (MODE=mine|map|invert|all)
	python3 invert.py --mode $(if $(MODE),$(MODE),all)

ablate: ## Ablations & diagnostics: feature families, village confusion, prompt elements, evidence types
	python3 ablate.py

all: ## Run the full goal-inference lane: match, invert, ablate
	$(MAKE) match
	$(MAKE) invert
	$(MAKE) ablate
	$(MAKE) match
	$(MAKE) invert
