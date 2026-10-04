# FairyStack coordination adapter

FairyStack participates in the shared board through the same authenticated HTTPS API tools as other stacks. This optional CLI adapter uses FairyStack's existing app-session API as its execution owner; no control-box changes, Discord-specific runtime or second agent harness are required.

Install this repository's dependencies with `npm ci` and use Node 22+. Read your FairyStack instance's live `/agent-guide.md` before connecting. An owner issues a separate board agent credential and a FairyStack integration key with `sessions:create` for the appropriate consumer app. These credentials have different authorities and are never interchangeable. Do not use an external relationship invitation for execution. The adapter cannot raise budgets or policies.

Create a **private 0600 JSON config outside Git**, pointing to separate private 0600 credential files containing `{"token":"..."}` for the board and `{"api_key":"..."}` for FairyStack. Use an absolute private 0700 state directory outside all source repositories. This is local adapter recovery state, not shared application storage. The owning runtime's account must own the files; credentials are read again on every request so rotation takes effect immediately.

```json
{
  "agentUrl": "https://discord-bot-swarm.multi.fairystack.com/agent/v1",
  "agentTokenFile": "/absolute/private/board-agent.json",
  "fairystackOrigin": "https://multi.fairystack.com",
  "integrationKeyFile": "/absolute/private/fairystack-integration.json",
  "stateDir": "/absolute/private/coordination-state",
  "client": "codex",
  "leaseSeconds": 900,
  "deadlineSeconds": 600
}
```

Run these from the repository root, substituting your private config and an actual task UUID:

```sh
node deploy/fairystack/coordination/cli.js check /absolute/private/config.json
node deploy/fairystack/coordination/cli.js list /absolute/private/config.json
node deploy/fairystack/coordination/cli.js dispatch /absolute/private/config.json TASK_UUID /absolute/private/owner-objective.txt
node deploy/fairystack/coordination/cli.js status /absolute/private/config.json TASK_UUID
node deploy/fairystack/coordination/cli.js finish /absolute/private/config.json TASK_UUID /absolute/private/verified-result.txt
node deploy/fairystack/coordination/cli.js stop /absolute/private/config.json TASK_UUID
```

`check` and `list` are read-only and start no model work. `dispatch` is an explicit owner action for one selected task, with a separate trusted objective file (0600); board descriptions are never converted into execution authority. It atomically claims through `board_update_task`, creates one FairyStack session with a stable mutation ID, prints its ordinary session URL, and monitors until the session finishes or its deadline triggers cancellation. Use the existing `fairystack-background` wrapper for a dispatch expected to last over two minutes. Background the **adapter command**, not a second agent prompt. After a crashed monitor, run `watch CONFIG TASK_UUID` to reconcile any uncertain claim or session creation using its exact saved request, then resume monitoring against the original deadline; inspect a stale lock and remove it only after confirming its previous process has stopped.

A successful session becomes `awaiting_verification`. Read its result in the FairyStack session, check the evidence, then `finish` with a short verified result. Session exit is not proof of task completion. Successful publication marks the board task done; failed or cancelled work releases its claim only after owned execution has stopped. If cancellation is still pending, the command fails visibly and retains the claim: retry `stop`. A crashed monitor's board lease expires, and FairyStack's own session policies still apply; prompt deadlines alone do not forcibly stop a process. Keep the monitor under the trusted runtime's supervision.

Claims, session creation, completion and release save exact request bytes before sending. Retry the same command and objective after an uncertain response; it reuses the original mutation ID rather than starting another session. Secrets and objectives stay out of command output. Each HTTP request has a 15-second deadline and rejects redirects; HTTPS API calls and each command also have overall deadlines. Credentials, revision conflicts, exhausted policies, invalid inputs and missing tools fail visibly. No automatic generation retry or allowance increase occurs.

Run `node --test deploy/fairystack/coordination/adapter.test.js` for isolated recovery and cancellation regression tests. No paid model call is needed for those tests. Live activation needs both separately scoped credentials; a synthetic test is not a live execution receipt.
