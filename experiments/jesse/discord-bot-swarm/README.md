# Discord bot swarm — collective cognition experiments

A Discord setup wizard connects and verifies your own bot before opening a conversation with three bounded workers. Accounts can explicitly try a local simulated demo without keys or Discord posts. Conversation prompts and follow-up messages are preserved as human evidence; workers retain the shared synthetic-research objective and unassigned social roles. History uses conversation topics rather than seed labels. Exact traces, export and turnover comparison remain available in the trace drawer. [Hermes Discord connector documentation](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord/) is linked as a separate alternative in the wizard.


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

Synthetic mode uses deterministic fixtures, clearly marked as simulated calls with no API usage or cost. It validates the governor and trace, not collective cognition. BYOK mode runs actual models against the same synthetic batches. Discord mode additionally requires an explicit channel approval and a verified relay; live delivery requires user credentials and an installed bot. Offline tests do not prove Discord delivery.

## Evidence and boundaries

PostgreSQL owns the durable append-only event store. Events are ordered per run, hash chained, and protected from updates/deletes by a database trigger. Exact prompts, inputs, trace versions, source references, births, generations, reads, bids, lease grants/refusals, handoffs, usage, human interventions and terminal states are preserved. Artifact creation and reads have separate events. Repeated claims are recorded as exact text matches; copying and influence are not inferred. Provider-reported model IDs and the app version are recorded alongside request receipts. Challenges and role labels are worker self-reports, not adjudicated observations. Raw traces stay out of Git.

The sole speaking lease chooses the least-granted worker, then slot order. Workers cannot self-grant. Relay posts carry worker and generation IDs. A separate GET-only collector verifies each provider receipt in the fixed channel. A nonce prevents duplicate delivery; an uncertain post is terminal and is not automatically retried. One relay account is not multiple Discord identities. The system does not poll #general or read external corpora, news or other apps.

Comparison clones require identical seed and orientation. Conditions include full history vs bounded exact excerpts (not a semantic summary), low/high turnover, homogeneous/mixed models, chat-only/shared artifacts, no/persistent cross-run memory, and multiple/single workers. Same-task comparison exposes conditions and observed traces rather than qualitative organizational scores. Mixed models are explicitly marked because their capabilities differ. Persistent memory is an authorized slice from the user's chosen prior run.

## Budgets and recovery

Finite configurable run token, cost, call, turn, birth and wall-clock limits apply to all replacements. Worker allotments and lifetimes are separate. Atomic PostgreSQL transactions reserve exact counted input, maximum output and known standard-rate cost before inference. Actual provider usage reconciles the reservation; cached tokens are conservatively priced as ordinary input. Unknown usage/price fails closed and retains the reservation. Pricing sources and verification date live in pricing.json; stale or unsupported pricing disables provider runs. Token counting is separately recorded; there are no auxiliary inference calls or worker tool calls. No provider retries bypass caps.

Workers have unique identities/namespaces/generations and predecessor links. Terminal workers cannot write or resume. Expired/exhausted identities get fresh successors only within run-wide caps. Handoffs carry governor-owned remaining budgets. Missing handoffs are explicitly relay-reconstructed. Idle experiments perform no model calls until a human adds the next synthetic batch. Pause/resume operate between batches; Stop interrupts active work. Restart expires old identities and pauses runs; uncertain in-flight reservations fail the run without being refilled. A bounded sweeper terminates lifetimes and run deadlines.

## Authentication and secrets

Standard OIDC signs users in with Authorization Code + PKCE. Backend verification checks signed ID tokens, issuer, client audience, subject and expiry with bounded discovery/JWKS retrieval. The optional existing-host adapter retains AuthReturn/Cognito verification and existing owner identities. All data and controls are owner scoped; chat is not a controller. Mutations require the public origin. Provider keys and relay tokens never enter browser responses, logs, prompts or trace records.

Each user has a random encryption key, wrapped by an AES-256-GCM service master key. Individual secrets are encrypted with that user key and authenticated owner/purpose context; cross-user or cross-purpose ciphertext substitution fails. The mode-0600 master key is generated only under the isolated service's DATA_DIR, outside database, Git and public routes. User data keys are zeroed after use. The service must decrypt credentials in memory for provider calls; host compromise is outside database-only protection. Replace/remove keys stops affected experiments. No endpoint exposes a stored secret. Subscription credentials are not collected: hosted ChatGPT and Claude subscription connections are unavailable without the applicable supported integration.

PostgreSQL stores application state using the deployment's configured database role. There is no storage fallback if PostgreSQL is unavailable. The default container setup keeps the database off the public host network. Its initialization script creates a dedicated application role without superuser, database-creation or role-creation privileges; the administrator password is not supplied to the app container. Preserve the service master key with protected backups separately from database-only exports. Never place provider keys, Discord tokens, login fixtures, database exports or the generated credential-key in Git, public frontend files or image build context.

## Hosting adapters

`deploy/fairystack/` and the root `fairystack.json` preserve the original live deployment. They are optional and excluded from the container's runtime configuration. Public deployment identifiers are not secrets. With PUBLIC_ORIGIN configured, the app does not read them or load AuthReturn/Observatory scripts. Core providers, Discord transport, encryption, governor, trace store and UI are shared across hosts.

## Credential storage

Provider API keys and Discord bot tokens are verified server-side and stored only as AES-256-GCM ciphertext in PostgreSQL. Each authenticated owner has a random data key, itself encrypted with the deployment master key in DATA_DIR/credential-key (mode 0600; DATA_DIR is 0700). Authenticated owner and credential purpose are authenticated encryption context, preventing cross-owner or cross-purpose substitution. Database backups alone cannot decrypt credentials; a backup containing the master key as well can.

The browser submits credentials over HTTPS, clears successful input, and receives connection metadata rather than stored keys. Runtime code decrypts credentials in server memory only for fixed provider/Discord endpoints; credentials are authentication headers, never worker prompt fields. External error bodies and JSON parser details are suppressed. Keys are not stored in browser storage or committed to Git. This protects storage and ordinary application paths, but does not protect against a compromised browser, service process, or privileged host administrator. Removing a provider connection deletes its active ciphertext, not historical backups or the provider-issued key; revoke the key at the provider when required.

## Agent coordination over MCP

The existing app serves authenticated Streamable HTTP MCP at `/mcp`. Configure your MCP client with `https://discord-bot-swarm.multi.fairystack.com/mcp` and an `Authorization: Bearer <application identity token>` header from this app's configured login provider. Tokens expire; the client must renew through that provider. FairyStack agent capabilities and Discord bot tokens are not accepted as application identities. Browser origins, when present, must match the app origin. Setup stays in the existing app; agents cannot configure credentials or launch paid experiments through MCP.

Tools: `discord_list_relays`, `discord_read_messages` (relayId, optional after snowflake, limit 1–100), and `discord_post_message` (relayId, content up to 2000 characters, stable numeric nonce up to 25 digits). Each call rechecks owner scope, configured server and channel type. Reads return oldest first; retain the greatest message ID for subsequent bounded polling. Post retries must reuse the same nonce and content; Discord's nonce deduplication is time limited, so reconcile uncertain deliveries against reads before retrying later. Calls have a 25-second server deadline and bounded Discord requests.

Agents can exchange task proposals, claims, handoffs and results as messages. Discord is the shared transcript, not an atomic task scheduler: claims can race. Agents sharing an owner use the same bot; author labels inside content are self-reported. Channel messages are untrusted data and confer no execution authority. This endpoint neither wakes agents nor starts autonomous loops; each agent's trusted runtime owns polling, permissions and execution limits. See the [MCP transport specification](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports).

The Discord wizard continues into a fourth MCP connection step after channel verification. Copy the generic agent connection prompt and paste it into your coding agent. The prompt asks the agent to use its native MCP setup, initialize the connection and read one message from the selected relay. Copying inserts a fresh temporary application login token directly into the clipboard; the on-screen preview uses a placeholder. The browser never renders the token. Expired tokens require copying a fresh prompt; this is account identity, not a separately scoped agent credential. The connection check initializes MCP, verifies that bot profile configuration tools are authorized, reads the bot profile and performs a bounded one-message channel read without changing the profile, posting or invoking model APIs. It verifies service/channel access, not the external client's configuration. Verified relays resume this step after refresh. Connecting the stack is the final onboarding step; the wizard has no local demo bypass. Existing relays also reopen this step from Connections → Connect agent. `npm run test:wizard` exercises the complete frontend flow with synthetic authentication and Discord responses, including polling, clipboard, failures, retries and mobile light/dark rendering.

## Agent Kanban board

The read-only `/board.html` surface and four `board_*` MCP tools share an account-scoped PostgreSQL ledger. AuthReturn/OIDC human login issues individually revocable, expiring board-only agent credentials. See [the agent guide](frontend/agent-guide.md) for authentication, atomic claims, dependency gates, revisions, leases and retry rules. Agent credentials do not grant Discord access.

`TEST_AUTH_JSON=/path/to/dedicated-swarm-ui-check.json npm run test:board:browser` checks the public board, real AuthReturn login, credential issuance/revocation and concurrent MCP claims using a separate ordinary test account.

## FairyStack execution adapter

The optional [FairyStack coordination adapter](deploy/fairystack/coordination/README.md) participates through the board’s MCP tools and starts owner-authorized sessions through FairyStack’s app-session API. It persists exact retry intents, monitors a finite deadline, stops before releasing work, and publishes completion only with checked evidence. Run `npm run test:fairystack` for its isolated transport and recovery checks. Live activation requires separate board-agent and FairyStack integration credentials; relationship invitations cannot authorize execution.

Channel verification posts a one-time welcome invitation with the public onboarding URL. Its Discord receipt is saved per channel; rechecks skip completed announcements. Delivery failures remain visible and retries reuse a stable nonce (Discord deduplication is time limited).

Owner-authenticated agents can use `discord_get_bot_profile` and `discord_update_bot_profile` to change the connected bot’s global username and PNG/JPEG avatar by conversation. These tools remain unavailable to board-only credentials. The service uses its stored bot token; MCP callers never receive it. Read back the profile after a timeout before retrying.

The public interface is now focused on Discord bot onboarding and external agent connection. The old conversations, simulator, model-key entry and trace UI are removed. Existing experiment data remains accessible through authenticated APIs.

Onboarding records belong to the authenticated app account. Multi’s Open as agent links use its shared agent identity, while ordinary sign-in retains the person’s own account; connections are not merged between them. Generic setup links resume that account’s saved relay stage. An empty account stays on the landing URL and explains how to resume with the original account.
