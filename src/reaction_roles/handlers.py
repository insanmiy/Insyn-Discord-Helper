import discord
from src.reaction_roles.storage import get_message_config, emoji_key, list_guild_reaction_roles


async def handle_reaction_add(bot, payload: discord.RawReactionActionEvent):
	if payload.user_id == bot.user.id:
		return

	config = get_message_config(str(payload.guild_id), str(payload.message_id))
	if not config:
		return

	role_id = config.get("mappings", {}).get(emoji_key(payload.emoji))
	if not role_id:
		return

	guild = bot.get_guild(payload.guild_id)
	if not guild:
		return

	member = guild.get_member(payload.user_id)
	if member is None:
		try:
			member = await guild.fetch_member(payload.user_id)
		except discord.HTTPException:
			return

	role = guild.get_role(int(role_id))
	if role is None:
		return

	try:
		if config.get("exclusive"):
			for other_role_id in config.get("mappings", {}).values():
				if other_role_id == role_id:
					continue
				other_role = guild.get_role(int(other_role_id))
				if other_role and other_role in member.roles:
					await member.remove_roles(other_role, reason="Reaction role (exclusive)")

		await member.add_roles(role, reason="Reaction role")
	except discord.Forbidden:
		pass
	except discord.HTTPException:
		pass


async def handle_reaction_remove(bot, payload: discord.RawReactionActionEvent):
	if payload.user_id == bot.user.id:
		return

	config = get_message_config(str(payload.guild_id), str(payload.message_id))
	if not config:
		return

	role_id = config.get("mappings", {}).get(emoji_key(payload.emoji))
	if not role_id:
		return

	guild = bot.get_guild(payload.guild_id)
	if not guild:
		return

	member = guild.get_member(payload.user_id)
	if member is None:
		try:
			member = await guild.fetch_member(payload.user_id)
		except discord.HTTPException:
			return

	role = guild.get_role(int(role_id))
	if role is None or role not in member.roles:
		return

	try:
		await member.remove_roles(role, reason="Reaction role removed")
	except discord.Forbidden:
		pass
	except discord.HTTPException:
		pass
