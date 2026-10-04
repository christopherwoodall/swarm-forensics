# Discord bot setup instructions

## Creating a bot and adding it to the channel

1. In the [Developer Portal](https://discord.com/developers/applications), click "New Application" and create an application. Copy `APPLICATION_ID` and `PUBLIC_KEY` into `.env`.
2. Open the `Bot` page from the left menu of the Developer Portal and create a bot user if you don't already have one. If you selected the bot application type, a bot user may already exist. Reset its token if necessary, then copy the token to `.env` as `DISCORD_TOKEN`.
3. From the `Bot` page, make sure `Public Bot`, `Server Members Intent`, and `Message Content Intent` are all enabled.
4. Open `Installation` from the left menu. Enable `Guild Install`. Under `Default Install Settings > Guild Install`, add the `bot` scope and the following permissions: `Read Message History`, `Send Messages`, `View Channels`.
5. On the same page, copy the `Install Link` and open it in the browser. It should redirect you to Discord, with a GUI for adding the bot to the channel. As long as you are a channel admin, you should see a success message when done.

## Using the bot

Under `chris-research/tools/discord_bot.py`, there is a Python utility that Cursor (or your agent harness of choice) can use for driving Discord.

To use the bot from Cursor Cloud, you will need to set the credentials as secrets in a dedicated project environment created from the https://cursor.com/agents interface. Similar persistent secret setup can be done for other cloud agent platforms like Codex Cloud and Claude Code on the Web.