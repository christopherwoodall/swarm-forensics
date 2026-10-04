.DEFAULT_GOAL := help
SOURCE_DIR := discord-bot-swarm
.PHONY: help setup sync auto-sync check build test lint browser-test

help: ## List Jesse experiment commands
	@awk -F':.*## ' '/^[a-z-]+:.*## /{printf "  %-14s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

$(SOURCE_DIR)/node_modules/.package-lock.json: $(SOURCE_DIR)/package-lock.json $(SOURCE_DIR)/package.json
	cd $(SOURCE_DIR) && npm ci --no-audit --no-fund

setup: $(SOURCE_DIR)/node_modules/.package-lock.json ## Install locked source dependencies

sync: ## Import committed source (SOURCE_REPO and SOURCE_REV are required)
	node sync-source.mjs "$(SOURCE_REPO)" "$(SOURCE_REV)"

auto-sync: ## Publish and merge verified source (SYNC_CONFIG is a private credential file)
	node auto-sync.mjs "$(SYNC_CONFIG)"

check: ## Verify all committed source hashes
	node check-source.mjs

build: setup ## Build browser assets
	cd $(SOURCE_DIR) && npm run build

test: setup check ## Run source and synchronization regression tests
	$(MAKE) -C $(SOURCE_DIR) test
	node --test sync-source.test.mjs auto-sync.test.mjs

lint: setup check ## Check JavaScript syntax and whitespace
	$(MAKE) -C $(SOURCE_DIR) lint
	node --check check-source.mjs
	node --check sync-source.mjs
	node --check sync-source.test.mjs
	node --check auto-sync.mjs
	node --check auto-sync.test.mjs
	sh -n $(SOURCE_DIR)/deploy/postgres/init.sh

browser-test: setup ## Test onboarding with synthetic fixtures
	cd $(SOURCE_DIR) && npm run test:wizard
