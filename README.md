# Insyn Discord Helper

Insyn Helper is a Discord bot that lets you manage your server by talking to it instead of using commands.

## Features

* Manage your server with normal messages
* Run multiple actions at once
* Manage users, channels, roles, and permissions
* Control who can use the bot
* Limit the bot to specific channels

## Setup

1. Install the dependencies.

`pip install -r requirements.txt`

2. Copy `.env.example` to `.env`.

3. Add your keys to `.env`.

* `DISCORD_TOKEN` - Your Discord bot token
* `GEMINI_API_KEY` - Your Gemini API key
* `DISCORD_APPLICATION_ID` - Your Discord application ID
* `GEMINI_MODEL` - Gemini model to use

4. Start the bot.

`python src/main.py`

## Config

You can edit `bot_config.xml` to change things like the bot name, status, limits, and timeouts.

## Permissions

The server owner always has full access.

The owner can also give access to other users or roles and limit which channels the bot can be used in.

Examples:

* `@bot give this role access`
* `@bot give this user access`
* `@bot remove access from this user`
* `@bot only work in #general`
* `@bot show bot config`

## Examples

Mention the bot and tell it what you want.

* `@bot ban @user for spamming`
* `@bot create a channel called announcements`
* `@bot check the audit log`
* `@bot what's the weather in Miami?`
* `@bot ban @user and check the weather in Chicago`

## How It Works

The bot receives your message, figures out what needs to be done, checks permissions, and then performs the action through Discord.

All actions are checked before they are run.

## Security

* Access is controlled by the server owner
* Permissions are checked before every action
* Discord's role hierarchy is respected
* API keys are stored in `.env`
