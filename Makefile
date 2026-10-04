.DEFAULT_GOAL := help
PLUGIN_DIR := showcase/hermes-plugin
JESSE_DIR := experiments/jesse
.PHONY: help setup test lint check hermes-test hermes-lint hermes-check hermes-install hermes-hunter hermes-hunter-test hermes-hunter-ui-test jesse-setup jesse-test jesse-lint

help: ## List showcase commands
	@awk -F':.*## ' '/^[a-z-]+:.*## /{printf "  %-22s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Install development dependencies for both maintained modules
	$(MAKE) -C $(PLUGIN_DIR) setup
	$(MAKE) -C $(JESSE_DIR) setup

test: hermes-test jesse-test ## Run Python and JavaScript regression tests

lint: hermes-lint jesse-lint ## Check both maintained modules

check: hermes-check ## Check the Hermes plugin package

hermes-test: ## Test the Hermes plugin offline
	$(MAKE) -C $(PLUGIN_DIR) test

hermes-lint: ## Lint the Hermes plugin
	$(MAKE) -C $(PLUGIN_DIR) lint

hermes-check: ## Validate the Hermes plugin package
	$(MAKE) -C $(PLUGIN_DIR) check

hermes-install: ## Install the Hermes plugin into the selected Hermes home
	$(MAKE) -C $(PLUGIN_DIR) install

hermes-hunter: ## Survey or discover raw-data patterns with ARGS
	$(MAKE) -C $(PLUGIN_DIR) hunter ARGS="$(ARGS)"

hermes-hunter-test: ## Test morphology discovery and migration compatibility
	$(MAKE) -C $(PLUGIN_DIR) hunter-test

hermes-hunter-ui-test: ## Test morphology rendering and request handlers
	$(MAKE) -C $(PLUGIN_DIR) hunter-ui-test

jesse-setup: ## Install locked Discord Swarm dependencies
	$(MAKE) -C $(JESSE_DIR) setup

jesse-test: ## Test Discord Swarm and synchronization tooling
	$(MAKE) -C $(JESSE_DIR) test

jesse-lint: ## Check Discord Swarm and synchronization tooling
	$(MAKE) -C $(JESSE_DIR) lint
