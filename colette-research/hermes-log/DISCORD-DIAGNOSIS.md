# Caduceus Discord setup: diagnostic record

Status: advisory investigation, not an accepted implementation plan.
Evidence window: October 3, 2026, through approximately 18:40 UTC.
Target: Telepathic Pugs's server `1430962816315031654`, `#general` channel `1430962817045106792`.
The named assistant GLM performed setup steps. Caduceus is the separate Discord bot.

## Finding

Caduceus connected to Discord and received Colette's messages in the target channel.
The gateway then rejected those messages at its authorization stage.
Changing the default profile and restarting did not resolve the rejection.
The exact effective authorization value that caused rejection remains unproven.
Do not attribute the failure to Pug's permissions or a default-profile override without further evidence.

No Discord source collector or ledger extractor is installed for this channel.
The earlier FairyStack collector cannot read Discord.
The FairyStack cron job is paused after its session enrollment expired.

## Direct evidence

- `~/.hermes/profiles/caduceus/logs/gateway.log`, lines 15292–15306:
  text batches from `agent:caduceus:discord:group:1430962817045106792:816894571693735946` reached the gateway.
  Each batch was followed by `Unauthorized user: 816894571693735946 (colette) on discord`.
- The same log, lines 15308–15321:
  Caduceus connected again at 11:18:25 local time.
  Additional Colette messages were rejected at 11:29, 11:30, 11:39, and 11:40.
  These later failures disprove the claim that the default-profile change fixed the problem.
- `~/.hermes/profiles/caduceus/config.yaml`, lines 9–22 and 35–37:
  this profile owns the connected Discord adapter.
  Its saved configuration has `allow_from` containing Colette's ID and `allow_all_users: true`.
  It also lists `#general` under both `allowed_channels` and `free_response_channels`.
- `~/.hermes/config.yaml`, `platforms.discord.enabled: false`:
  the default profile is not the connected Discord bot.
  The connection log names the `caduceus` profile.
- `gateway/authz_mixin.py`, lines 614–695:
  the gateway performs a separate authorization check after adapter admission.
  It reads scoped authorization settings and can reject a delivered text batch.
  The corresponding rejection is logged in `gateway/run_inbound.py`, lines 283–295.
- `plugins/platforms/discord/adapter.py`, lines 1495–1525 and 5982–6055:
  the adapter has separate bot, user, channel, and mention admission checks.
  It drops unmentioned channel messages before normal conversation dispatch unless an exception applies.

Code paths above are relative to `~/.hermes/hermes-agent/`.
The profile log is the correct first place to inspect Caduceus.
The default profile's log omitted these recent inbound batches.

## Why the setup loop failed

1. GLM treated `Discord connected` as proof of end-to-end message handling.
   That proves transport login only.
   The recorded Colette batches failed at the later gateway authorization gate.
2. GLM inferred that the default profile overrode Caduceus because one process multiplexes profiles.
   The adapter's connected identity and session keys both identify `caduceus`.
   The continued rejection after changing default settings falsifies that proposed fix.
   The remaining effective-policy failure needs a scoped diagnostic, not another guessed restart.
3. GLM read the wrong log first.
   The Caduceus profile log contains the channel batches and unauthorized verdicts.
   The absence of entries in the default log did not mean the bot missed the messages.
4. GLM repeatedly restarted the gateway before establishing a narrow reproduction.
   The first rejected batch predates the relevant restart.
   At least one restart sent a shutdown notification to the existing home channel.
5. GLM conflated a responsive bot with a silent watcher.
   A Discord conversational session contains messages admitted for bot interaction.
   It is not a continuous, complete archive of every channel message.
   A scheduled job reading those sessions would miss messages rejected before dispatch.

The precise cause inside the second authorization check is still unknown.
The saved YAML flags do not establish what the scoped runtime check saw.
Do not inspect or publish bot tokens to investigate this.

## Corrections to previous guidance

- `permissions=1024` grants View Channel, not Read Message History.
  `68672` combines View Channel, Send Messages, and Read Message History.
  These permission bits do not change an application's private/public install status.
- Discord's Public Bot setting governs who can add an app to other servers.[2]
  GLM's suggestion to change the permission integer for a “private integration” error was incorrect.
  Pug's successful installation does not independently reveal which app setting changed.
- `discord.free_response_channels` means the bot can answer without an `@mention`.[1]
  `require_mention: true` does not override a free-response exception.
  Joined threads may also admit replies without a fresh mention under current thread defaults.[1]
  Thus the current `#general` setting does not meet Colette's mention-only request.
- `discord.allowed_channels` controls where the bot may respond.
  It is not a channel subscription or durable transcript source.
- `Channel directory built: 0 target(s)` does not establish whether Discord delivered an inbound message.
  The Caduceus profile's batch log supplies direct evidence of delivery to the gateway.
- A screenshot showing reactions or typing does not prove a completed model response.
  For the sampled Colette messages, the gateway instead recorded authorization failures.

## Pug's message: unknown

The reviewed Caduceus profile log shows Colette batches in `#general`.
It contains no accepted Pug turn in the reviewed interval.
An unmentioned human message may be dropped before normal conversation logging.
A bot-authored message may meet an additional `allow_bots: none` filter.
Neither possibility is established for Pug's specific message.
The message ID, author type, mention state, and adapter verdict were not captured.
Do not say Pug lacked access or the bot could not see his message without that evidence.

## Current operational risks

- The saved Caduceus policy still has `free_response_channels: '1430962817045106792'`.
- The saved Caduceus policy also has `allow_all_users: true`.
  This is broader than a proven channel-specific grant.
  Actual effective authorization remains unverified because the runner continued to reject Colette.
- The default profile also received broad allow-user and channel changes during troubleshooting.
  Its Discord platform remains disabled; do not assume its settings govern Caduceus.
- The existing watcher ledger's `EVENTS.jsonl` contains only FairyStack session `ca8ffac066a4`.
  It contains no Discord-derived events as of this evidence snapshot.
- The FairyStack cron job `698c454d0a09` is paused, not a Discord monitor.
- No message was posted into the target Discord channel by this diagnosis.

## Next authorized diagnostic transition

1. Preserve the current configuration before further changes.
2. Trace one explicitly mentioned message from Pug with its Discord message ID.
3. Correlate adapter admission, scoped gateway authorization, agent dispatch, and delivery.
4. Test mention-only policy separately from sender authorization and channel observation.
5. Do not enable a Discord ledger job until it captures all authorized channel messages read-only.
6. Keep source message IDs, authors, timestamps, and raw text separate from inferred ledger events.
7. Verify a real new Discord message reaches the ledger before claiming continuous monitoring.

This document does not authorize opening Caduceus to all DMs or writing in the channel.
It does not change the chat, the bot configuration, or the existing ledger.

## Bot-admission fix and verification — October 3, 2026

Colette authorized work on the fix after this diagnosis.
The authorization mismatch was reproduced using actual adapter and runner methods with synthetic inputs.
The tracer failed with the previous Caduceus configuration and passed after the scoped change.
The tracer is outside the repository under `~/.hermes/cache/scratch/caduceus-auth-tracer.py`.
It reads saved configuration but does not access bot credentials or contact Discord.

- Preserve Colette's existing `allow_from` entry for her DMs.
- Set `platforms.discord.extra.allowed_roles` to `1430962816315031654`.
  Discord assigns the `@everyone` role the same ID as the server.[3]
  The adapter checks this role against the sender's originating guild.
  It sets a verified role flag for the gateway's second authorization gate.
- Set `platforms.discord.extra.allow_all_users` to `false`.
  Do not grant the entire bot global DM access to fix one team channel.
- Limit `discord.allowed_channels` to `1430962817045106792,1551370707487826010`.
  The second entry preserves the previously configured Caduceus study channel.
- Restore `discord.free_response_channels` to the study channel alone.
  Set `discord.thread_require_mention: true`.
  Set `discord.no_thread_channels` to the team channel.
  Mentioned team replies can now stay inline without thread-creation permissions.
- Revert the troubleshooting changes on the disabled default Discord profile.

The gateway restarted after the complete configuration change.
The Caduceus adapter reconnected without a privileged-intent error.
At 12:01 local time, the Caduceus profile log recorded a team message from
`Suspect Jesse` in `1430962817045106792`.
It then recorded a completed response and an outbound send to the same channel.
Colette supplied source message ID `1556018234652893368` and confirmed Caduceus replied.
The supplied ID's Discord timestamp matches the logged event window.
The gateway log does not print the inbound message ID; identity matching is time-and-user corroboration.
See `~/.hermes/profiles/caduceus/logs/gateway.log`, lines 15347–15350.

This verifies a real member-to-bot response after the authorization change.
A live unmentioned-message suppression check and a live Colette-DM regression check remain outstanding.
Do not describe these as tested merely because the synthetic tracer passes.
The fix does not implement a Discord watcher or extend the ledger.

## Sources

[1] https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord — Hermes Discord Setup
[2] https://support-dev.discord.com/hc/en-us/articles/21204493235991-How-Can-Users-Discover-and-Play-My-Activity — Discord Public/Private Bot Setting
[3] https://docs.discord.com/developers/topics/permissions — Discord Permissions
