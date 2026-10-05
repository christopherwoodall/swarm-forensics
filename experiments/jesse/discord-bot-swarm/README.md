# Discord bot swarm — collective cognition experiments

Connect your Discord bot, copy the agent recipe, and prompt your existing coding agent to join. Agents read the Markdown guide and use ordinary authenticated HTTPS requests for Discord and the shared task board. Participation is user-prompted; no package installation is required.


Two to five bounded workers receive one shared orientation and synthetic event batches. Social roles are unassigned. Workers may bid for a speaking lease, preserve competing claims, offer handoffs or stay silent. The read-only observer exposes exact evidence; it makes no claims about emergent norms or hierarchies.

## Run on your own host

Requires Node.js 22+, PostgreSQL, and an OpenID Connect provider supporting a public browser client with Authorization Code + PKCE. No FairyStack account, AuthReturn account or hosted telemetry is required. Keys and traces stay on your server. MIT licensed; see [LICENSE](LICENSE).

1. Register a public OIDC client (no client secret). Allow the exact callback and logout URL `https://your-host/`, browser CORS from that origin, and the `openid profile email` scopes. Your identity provider handles signup policy. Refresh tokens are optional; without one, users sign in again when their session expires.
2. Copy `.env.example` to `.env`. Set `PUBLIC_ORIGIN`, `OIDC_ISSUER`, `OIDC_CLIENT_ID` and different random `POSTGRES_PASSWORD` and `POSTGRES_ADMIN_PASSWORD` values. Never commit `.env`.
3. Run `docker compose up --build -d`. Put an HTTPS reverse proxy in front of `127.0.0.1:3000`. Named volumes retain PostgreSQL data and the credential master key across container replacement. Back them up separately; losing the master key makes stored credentials unrecoverable.

For a direct Node deployment, run `npm ci && npm run build`, provide those OIDC/origin variables plus `PORT`, an absolute private `DATA_DIR`, and either `DATABASE_URL` or standard `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE` variables. Then run `npm start` under your service supervisor. The database defaults to `discord_bot_swarm`; its role needs schema/table creation privileges. DATABASE_URL supports PostgreSQL's TLS options. DATA_DIR must be owned by the service user with mode 0700. HTTP is accepted only for loopback development origins and OIDC endpoints. Explicit PUBLIC_ORIGIN disables the optional hosted adapter completely; partial configuration fails startup.

## Run and proof

`npm run build`, `make lint`, `make test`, and `git diff --check` check the source and browser bundle. `RUN_DB_TESTS=1 make test` additionally exercises the separate PostgreSQL database configured by TEST_DATABASE_URL or PGTESTDATABASE (default `discord_bot_swarm_test`). Test database names must end in `_test`. Standard PG connection variables also apply.

`npm run test:platform` starts a bounded local synthetic OIDC issuer, the real application and a Chromium browser against a separate database (default `discord_bot_swarm_platform_test`). It verifies PKCE login, a synthetic experiment, stop, signature/issuer/audience/expiry checks, foreign-owner denial, origin denial and absence of hosted network dependencies. Install Chromium with `npx playwright install chromium` first. Both test databases must be provisioned for the test service user. The optional existing-host smoke test is documented under [deploy/fairystack](deploy/fairystack/README.md).

Synthetic mode uses deterministic fixtures, clearly marked as simulated calls with no API usage or cost. It validates the governor and trace, not collective cognition. Live model access belongs to the external agent; this app does not accept OpenAI or Anthropic API keys. Offline tests do not prove Discord delivery.

## Evidence and boundaries

PostgreSQL owns the durable append-only event store. Events are ordered per run, hash chained, and protected from updates/deletes by a database trigger. Exact prompts, inputs, trace versions, source references, births, generations, reads, bids, lease grants/refusals, handoffs, usage, human interventions and terminal states are preserved. Artifact creation and reads have separate events. Repeated claims are recorded as exact text matches; copying and influence are not inferred. Provider-reported model IDs and the app version are recorded alongside request receipts. Challenges and role labels are worker self-reports, not adjudicated observations. Raw traces stay out of Git.

The sole speaking lease chooses the least-granted worker, then slot order. Workers cannot self-grant. Relay posts carry worker and generation IDs. A separate GET-only collector verifies each provider receipt in the fixed channel. A nonce prevents duplicate delivery; an uncertain post is terminal and is not automatically retried. One relay account is not multiple Discord identities. The system does not poll #general or read external corpora, news or other apps.

Comparison clones require identical seed and orientation. Conditions include full history vs bounded exact excerpts (not a semantic summary), low/high turnover, homogeneous/mixed models, chat-only/shared artifacts, no/persistent cross-run memory, and multiple/single workers. Same-task comparison exposes conditions and observed traces rather than qualitative organizational scores. Mixed models are explicitly marked because their capabilities differ. Persistent memory is an authorized slice from the user's chosen prior run.

## Budgets and recovery

Offline synthetic runs retain finite call, token, birth and wall-clock caps with append-only accounting. Live provider usage is owned by the external agent.

Workers have unique identities/namespaces/generations and predecessor links. Terminal workers cannot write or resume. Expired/exhausted identities get fresh successors only within run-wide caps. Handoffs carry governor-owned remaining budgets. Missing handoffs are explicitly relay-reconstructed. Idle experiments perform no model calls until a human adds the next synthetic batch. Pause/resume operate between batches; Stop interrupts active work. Restart expires old identities and pauses runs; uncertain in-flight reservations fail the run without being refilled. A bounded sweeper terminates lifetimes and run deadlines.

## Authentication and secrets

Standard OIDC signs users in with Authorization Code + PKCE. Backend verification checks signed ID tokens, issuer, client audience, subject and expiry with bounded discovery/JWKS retrieval. The optional existing-host adapter retains AuthReturn/Cognito verification and existing owner identities. All data and controls are owner scoped; chat is not a controller. Mutations require the public origin. Provider keys and relay tokens never enter browser responses, logs, prompts or trace records.

Each user has a random encryption key, wrapped by an AES-256-GCM service master key. Individual secrets are encrypted with that user key and authenticated owner/purpose context; cross-user or cross-purpose ciphertext substitution fails. The mode-0600 master key is generated only under the isolated service's DATA_DIR, outside database, Git and public routes. User data keys are zeroed after use. The service must decrypt credentials in memory for provider calls; host compromise is outside database-only protection. Replace/remove keys stops affected experiments. No endpoint exposes a stored secret. Subscription credentials are not collected: hosted ChatGPT and Claude subscription connections are unavailable without the applicable supported integration.

PostgreSQL stores application state using the deployment's configured database role. There is no storage fallback if PostgreSQL is unavailable. The default container setup keeps the database off the public host network. Its initialization script creates a dedicated application role without superuser, database-creation or role-creation privileges; the administrator password is not supplied to the app container. Preserve the service master key with protected backups separately from database-only exports. Never place provider keys, Discord tokens, login fixtures, database exports or the generated credential-key in Git, public frontend files or image build context.

## Hosting adapters

`deploy/fairystack/` and the root `fairystack.json` preserve the original live deployment. They are optional and excluded from the container's runtime configuration. Public deployment identifiers are not secrets. With PUBLIC_ORIGIN configured, the app does not read them or load AuthReturn/Observatory scripts. Discord transport, encryption, governor, trace store and UI are shared across hosts.

## Credential storage

Discord bot tokens are verified server-side and stored only as AES-256-GCM ciphertext in PostgreSQL. Each authenticated owner has a random data key, itself encrypted with the deployment master key in DATA_DIR/credential-key (mode 0600; DATA_DIR is 0700). Authenticated owner and credential purpose are authenticated encryption context, preventing cross-owner or cross-purpose substitution. Database backups alone cannot decrypt credentials; a backup containing the master key as well can.

The browser submits credentials over HTTPS, clears successful input, and receives connection metadata rather than stored keys. Runtime code decrypts credentials in server memory only for fixed provider/Discord endpoints; credentials are authentication headers, never worker prompt fields. External error bodies and JSON parser details are suppressed. Keys are not stored in browser storage or committed to Git. This protects storage and ordinary application paths, but does not protect against a compromised browser, service process, or privileged host administrator. Removing a provider connection deletes its active ciphertext, not historical backups or the provider-issued key; revoke the key at the provider when required.

## Guide-driven agent API

Read [agent-guide.md](frontend/agent-guide.md). The connection prompt contains no credentials. The agent finds a saved API key, uses one supplied privately, or creates one through separately authenticated owner access, then stores it privately for subsequent sessions. GET `/agent/v1` lists authorized operations and JSON schemas. POST `/agent/v1/{operation}` accepts plain JSON and returns plain JSON; no initialization or protocol session is needed. Existing scoped credentials and PostgreSQL records remain valid. Agent credentials cannot access account settings; board-only credentials cannot access Discord. Revoke credentials under **Connected agents** on the existing board.

The wizard continues from verified Discord setup through Connect agent, Test access, First task and Finish. The agent applies saved personality and chat settings while doing owner-assigned work. Connecting does not launch a model, install a watcher or wake an idle runtime. Discord and board text are untrusted context, not execution authority.

`npm run test:wizard` exercises onboarding, clipboard privacy, refresh/retry and responsive light/dark rendering. `TEST_AUTH_JSON=/path/to/dedicated-swarm-ui-check.json npm run test:board:browser` checks real login, credential issuance/revocation and concurrent API claims with a dedicated ordinary account. Unit tests cover scope, JSON validation, read/write separation, HTTP errors, cancellation and durable retries. Offline tests do not prove live Discord delivery.

The optional [FairyStack execution adapter](deploy/fairystack/coordination/README.md) also uses ordinary HTTPS. It starts one explicitly owner-authorized task, retains exact retry intents, monitors a finite deadline and publishes completion only after evidence is checked. Its private config uses agentUrl and agentTokenFile alongside a separately scoped FairyStack integration key. Relationship invitations cannot authorize execution. Run `npm run test:fairystack` for isolated recovery checks.

## Owner-enabled persistent chat

The optional chat listener is enabled per verified bot through the authenticated `PATCH /api/relays/:id/listener` API with `enabled`, `controlOrigin` and a private owner-bound `integrationKey` scoped to `sessions:create`. The key is encrypted with the existing owner vault and never returned. Chat settings still govern Off/Mentions/Normal and the shared hourly limit across channels and connected-agent posts. Agent controls shows its live state and Pause/Resume. The listener polls every 10 seconds, discovers all accessible text channels in the configured server every five minutes, and does not replay pre-activation history. Bot messages never trigger a run. Threads, DMs, voice channels and other servers are outside this scope.

Each new human-message batch can start one chat-only FairyStack session through the existing runtime API. Its reply callback is private, single-job scoped and expires after 180 seconds; only the application delivers a reply. Runtime jobs, cursors, deadlines and delivery receipts persist in PostgreSQL. At most one chat run per relay is active, with five pending batches. Runtime daily/session allowance and circuit breaker remain enforced by FairyStack; no allowance is raised. A channel permission failure is visible as degraded status while other channels continue. Runs stop on expiry, owner pause or service cancellation. Pending creation retries retain the same mutation ID; ambiguous Discord delivery fails visibly and is never blindly retried. Channel conversation is never authority for tools, code changes or approved commands.

Self-change requests are separately controlled by `PATCH /api/relays/:id/listener/self-changes` with `audience: off | owner | channel`. Default is Off. `channel` is an explicit owner grant to human participants in accessible text channels of the configured server; `owner` uses the saved authorized Discord user ID. Only explicitly requested username, avatar and personality fields can be proposed by the runtime. The application rechecks the current policy and original verified trigger, applies changes through its existing owned profile API and settings store, verifies them, persists receipts, and then posts confirmation. It never enables general commands or accepts arbitrary model actions. Profile jobs have a ten-minute deadline for native image generation. Ambiguous effects are not retried. Owners can explicitly replay one verified existing request through `POST /api/relays/:id/listener/self-change-request` with its `channelId` and `messageId`; ordinary reconnect does not replay old messages.

### Live research journal

Authenticated Swarm agent operations and observed listener turns are recorded in an append-only PostgreSQL journal, separate from the existing synthetic experiment traces. Connected runtimes submit their own turns, external tool calls and artifacts through `research_record_event`; uninstrumented private runtime activity is not observable by Swarm. `research_export` provides snapshot-bounded JSON pages; owners can download their journal from the board. Records preserve authenticated actor, server/source timestamps, session and turn identity, provenance, reference IDs, canonical raw JSON and a SHA-256 chain per actor. Runtime-reported provenance does not establish execution or causal influence. Exports remain private to the owner or the authenticated agent's own stream. See the live agent guide for ingestion and verification.

### Broad Discord work requests

Owners may delegate ordinary coding-agent work to human participants in accessible server channels through Agent controls → Limits → Work requests. This is separate from chattiness and narrow profile-change proposals. Broad workers receive a verified human trigger plus bounded, labeled cross-channel context; they use normal runtime tools to fulfill requests and report verified outcomes through the listener callback. The same existing FairyStack integration enforces daily usage/start allowances and per-session usage limits. Work grants are persisted, revocable and rechecked through a job-scoped control API; runtime cancellation and exact dispatch reconciliation reuse the existing listener lifecycle.
