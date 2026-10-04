.PHONY: test lint

test:
	node --test test.js config.test.js http.test.js mcp.test.js mcp-setup.test.js wizard-route.test.js kanban.test.js discord.test.js deploy/fairystack/coordination/adapter.test.js
	@if [ "$$RUN_DB_TESTS" = "1" ]; then node --test database.test.js relay-records.test.js kanban.database.test.js; fi

lint:
	@for f in frontend/wizard-route.js wizard-route.test.js deploy/fairystack/coordination/adapter.js deploy/fairystack/coordination/cli.js deploy/fairystack/coordination/adapter.test.js kanban.js kanban.test.js kanban.database.test.js kanban.browser.test.mjs frontend/board.js relay-records.js relay-records.test.js mcp.js mcp.test.js mcp-setup.test.js frontend/mcp-setup.js frontend/image-loader.js image-loader.browser.test.mjs wizard.browser.test.mjs config.js authentication.js deploy/fairystack/adapter.js frontend/auth.js scripts/auth-oidc.js scripts/build.js platform.test.js config.test.js core.js research.js providers.js vault.js store.js experiment.js discord.js discord.test.js server.js frontend/app.js frontend/http.js http.test.js test.js database.test.js; do node --check $$f || exit 1; done

	git diff --check
