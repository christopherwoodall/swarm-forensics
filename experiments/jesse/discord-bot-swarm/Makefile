.PHONY: test lint

test:
	node --test test.js config.test.js http.test.js mcp.test.js mcp-setup.test.js
	@if [ "$$RUN_DB_TESTS" = "1" ]; then node --test database.test.js relay-records.test.js; fi

lint:
	@for f in relay-records.js relay-records.test.js mcp.js mcp.test.js mcp-setup.test.js frontend/mcp-setup.js frontend/image-loader.js image-loader.browser.test.mjs wizard.browser.test.mjs config.js authentication.js deploy/fairystack/adapter.js frontend/auth.js scripts/auth-oidc.js scripts/build.js platform.test.js config.test.js core.js research.js providers.js vault.js store.js experiment.js discord.js server.js frontend/app.js frontend/http.js http.test.js test.js database.test.js browser.test.mjs; do node --check $$f || exit 1; done
	git diff --check
