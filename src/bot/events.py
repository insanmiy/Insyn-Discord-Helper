import discord
from src.permissions.access import is_allowed_user, is_server_owner
from src.permissions.storage import (
	add_authorized_role,
	remove_authorized_role,
	add_authorized_user,
	remove_authorized_user,
	add_allowed_channel,
	remove_allowed_channel,
	get_server_config
)
from src.ai.runner import run_ai_request
from src.bot.status import get_bot_activity
from src.reaction_roles.handlers import handle_reaction_add, handle_reaction_remove


async def handle_owner_command(message, bot):
	cleaned_message = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip().lower()

	guild_id = str(message.guild.id)

	if "make this role have full access to the bot" in cleaned_message:
		if not message.role_mentions:
			await message.reply("Please mention a role to grant access.")
			return True

		role = message.role_mentions[0]
		add_authorized_role(guild_id, str(role.id))
		await message.reply(f"Role '{role.name}' now has full access to the bot.")
		return True

	elif "make this person have full access to the bot" in cleaned_message or "make this user have full access to the bot" in cleaned_message:
		if not message.mentions:
			await message.reply("Please mention a user to grant access.")
			return True

		user = message.mentions[0]
		add_authorized_user(guild_id, str(user.id))
		await message.reply(f"User '{user.display_name}' now has full access to the bot.")
		return True

	elif "remove access from this role" in cleaned_message:
		if not message.role_mentions:
			await message.reply("Please mention a role to remove access.")
			return True

		role = message.role_mentions[0]
		remove_authorized_role(guild_id, str(role.id))
		await message.reply(f"Role '{role.name}' no longer has access to the bot.")
		return True

	elif "remove access from this user" in cleaned_message or "remove access from this person" in cleaned_message:
		if not message.mentions:
			await message.reply("Please mention a user to remove access.")
			return True

		user = message.mentions[0]
		remove_authorized_user(guild_id, str(user.id))
		await message.reply(f"User '{user.display_name}' no longer has access to the bot.")
		return True

	elif "make the bot work in this channel" in cleaned_message:
		add_allowed_channel(guild_id, str(message.channel.id))
		await message.reply(f"Bot now works in this channel.")
		return True

	elif "make the bot not work in this channel" in cleaned_message:
		remove_allowed_channel(guild_id, str(message.channel.id))
		await message.reply(f"Bot no longer works in this channel.")
		return True

	elif "show bot config" in cleaned_message or "show authorization config" in cleaned_message:
		config = get_server_config(guild_id)
		config_text = f"Authorized roles: {len(config['authorized_roles'])}\n"
		config_text += f"Authorized users: {len(config['authorized_users'])}\n"
		config_text += f"Allowed channels: {len(config['allowed_channels'])} (empty = all channels)"
		await send_long_message(message.channel, config_text)
		return True

	return False


async def send_long_message(channel, content):
	MAX_LENGTH = 2000

	if len(content) <= MAX_LENGTH:
		await channel.send(content)
		return

	chunks = []
	current_chunk = ""

	for line in content.split('\n'):
		if len(current_chunk) + len(line) + 1 <= MAX_LENGTH:
			current_chunk += line + '\n'
		else:
			if current_chunk:
				chunks.append(current_chunk.rstrip())
			current_chunk = line + '\n'

	if current_chunk:
		chunks.append(current_chunk.rstrip())

	for chunk in chunks:
		await channel.send(chunk)


async def setup_events(bot):
	@bot.event
	async def on_ready():
		await bot.change_presence(activity=get_bot_activity())
		print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")

	@bot.event
	async def on_raw_reaction_add(payload):
		await handle_reaction_add(bot, payload)

	@bot.event
	async def on_raw_reaction_remove(payload):
		await handle_reaction_remove(bot, payload)

	@bot.event
	async def on_message(message):
		if message.author.bot:
			return

		if bot.user not in message.mentions:
			return

		if not message.guild:
			await message.reply("This bot can only be used in servers.")
			return

		guild_id = str(message.guild.id)
		user_id = str(message.author.id)
		role_ids = [str(role.id) for role in message.author.roles]
		channel_id = str(message.channel.id)

		if is_server_owner(user_id, str(message.guild.owner_id)):
			if await handle_owner_command(message, bot):
				return

		if not is_allowed_user(guild_id, user_id, role_ids, channel_id) and not is_server_owner(user_id, str(message.guild.owner_id)):
			await message.reply("You are not authorized to use Insyn Helper.")
			return

		cleaned_message = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()

		if not cleaned_message:
			return

		context = build_discord_context(message, bot)

		try:
			response = await run_ai_request(context, cleaned_message)
			await send_long_message(message.channel, response)
		except Exception as e:
			await send_long_message(message.channel, f"An error occurred: {str(e)}")


def build_discord_context(message, bot):
	guild = message.guild
	channel = message.channel

	referenced_users = []
	for mention in message.mentions:
		if mention.id != bot.user.id:
			referenced_users.append({
				"id": str(mention.id),
				"username": mention.name,
				"discriminator": mention.discriminator,
				"display_name": mention.display_name
			})

	referenced_channels = []
	for mention in message.channel_mentions:
		referenced_channels.append({
			"id": str(mention.id),
			"name": mention.name
		})

	referenced_roles = []
	for mention in message.role_mentions:
		referenced_roles.append({
			"id": str(mention.id),
			"name": mention.name
		})

	return {
		"user_id": str(message.author.id),
		"username": message.author.name,
		"display_name": message.author.display_name,
		"guild_id": str(guild.id) if guild else None,
		"guild_name": guild.name if guild else None,
		"channel_id": str(channel.id),
		"channel_name": channel.name,
		"message_id": str(message.id),
		"is_guild": guild is not None,
		"referenced_users": referenced_users,
		"referenced_channels": referenced_channels,
		"referenced_roles": referenced_roles,
		"bot_id": str(bot.user.id),
		"bot_name": bot.user.name,
		"_guild": guild,
		"_channel": channel
	}
