# Existing FairyStack deployment

This directory preserves the public authentication identifiers and compatibility adapter for the original hosted app. The root fairystack.json is the allocated deployment manifest and must remain at the root for the platform deployer. These files are not needed by independent installations; explicit PUBLIC_ORIGIN makes the adapter inactive. The portable Docker image excludes the manifest and authentication identifiers.

The adapter provides the original HTTPS origin, Unix-socket PostgreSQL connection, Cognito identity namespace, AuthReturn login component. Existing users, encrypted credentials and traces stay in their original service data directory/database. Do not migrate or replace the credential master key.

Use `fairystack-app-deploy discord-bot-swarm` for this deployment. `TEST_AUTH_JSON=/path/to/private-test-login.json APP_ORIGIN=https://your-host npm run test:browser` runs its AuthReturn smoke test; keep the private fixture outside Git. Deployment-specific agent requirements are in AGENTS.md here.

Browser checks must use a separate ordinary account with an email beginning `swarm-ui-check-`. The test runner rejects the operator account so synthetic verification conversations do not fill the operator's history. Store its email/password in the private fixture outside Git.
