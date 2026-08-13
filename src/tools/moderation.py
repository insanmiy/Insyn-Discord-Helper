import discord
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from src.tools.registry import register_tool
from google import genai


async def ban_user(context: Dict[str, Any], user_id: str, reason: str) -> Dict[str, Any]:
	guild = context.get("_guild")

	if not guild:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	try:
		member = guild.get_member(int(user_id))

		if member is None:
			return {
				"success": False,
				"error": "Member not found."
			}

		await member.ban(reason=reason)

		return {
			"success": True,
			"user_id": str(user_id),
			"reason": reason
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Discord rejected the ban because of permissions or role hierarchy."
		}
	except discord.HTTPException as error:
		return {
			"success": False,
			"error": str(error)
		}


async def unban_user(context: Dict[str, Any], user_id: str, reason: str = None) -> Dict[str, Any]:
	guild = context.get("_guild")

	if not guild:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	try:
		await guild.unban(discord.Object(id=int(user_id)), reason=reason)

		return {
			"success": True,
			"user_id": str(user_id),
			"reason": reason
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Bot lacks permission to unban this user."
		}
	except discord.NotFound:
		return {
			"success": False,
			"error": "User is not banned."
		}
	except discord.HTTPException as error:
		return {
			"success": False,
			"error": str(error)
		}


async def kick_user(context: Dict[str, Any], user_id: str, reason: str) -> Dict[str, Any]:
	guild = context.get("_guild")

	if not guild:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	try:
		member = guild.get_member(int(user_id))

		if member is None:
			return {
				"success": False,
				"error": "Member not found."
			}

		await member.kick(reason=reason)

		return {
			"success": True,
			"user_id": str(user_id),
			"reason": reason
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Discord rejected the kick because of permissions or role hierarchy."
		}
	except discord.HTTPException as error:
		return {
			"success": False,
			"error": str(error)
		}


async def timeout_user(context: Dict[str, Any], user_id: str, duration_minutes: int, reason: str) -> Dict[str, Any]:
	guild = context.get("_guild")

	if not guild:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	try:
		member = guild.get_member(int(user_id))

		if member is None:
			return {
				"success": False,
				"error": "Member not found."
			}

		duration = timedelta(minutes=duration_minutes)
		await member.timeout(duration, reason=reason)

		return {
			"success": True,
			"user_id": str(user_id),
			"duration_minutes": duration_minutes,
			"reason": reason
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Discord rejected the timeout because of permissions or role hierarchy."
		}
	except discord.HTTPException as error:
		return {
			"success": False,
			"error": str(error)
		}


async def remove_timeout(context: Dict[str, Any], user_id: str, reason: str = None) -> Dict[str, Any]:
	guild = context.get("_guild")

	if not guild:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	try:
		member = guild.get_member(int(user_id))

		if member is None:
			return {
				"success": False,
				"error": "Member not found."
			}

		await member.timeout(None, reason=reason)

		return {
			"success": True,
			"user_id": str(user_id),
			"reason": reason
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Discord rejected the timeout removal because of permissions or role hierarchy."
		}
	except discord.HTTPException as error:
		return {
			"success": False,
			"error": str(error)
		}


async def warn_user(context: Dict[str, Any], user_id: str, reason: str) -> Dict[str, Any]:
	guild = context.get("_guild")

	if not guild:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	try:
		member = guild.get_member(int(user_id))

		if member is None:
			return {
				"success": False,
				"error": "Member not found."
			}

		try:
			await member.send(f"You have been warned in {guild.name}: {reason}")
		except discord.Forbidden:
			pass

		return {
			"success": True,
			"user_id": str(user_id),
			"reason": reason
		}
	except Exception as e:
		return {
			"success": False,
			"error": str(e)
		}


async def delete_message(context: Dict[str, Any], message_id: str) -> Dict[str, Any]:
	guild = context.get("_guild")
	channel = context.get("_channel")

	if not guild or not channel:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	try:
		message = await channel.fetch_message(int(message_id))

		await message.delete()

		return {
			"success": True,
			"message_id": str(message_id)
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Bot lacks permission to delete this message."
		}
	except discord.NotFound:
		return {
			"success": False,
			"error": "Message not found."
		}
	except discord.HTTPException as error:
		return {
			"success": False,
			"error": str(error)
		}


async def purge_messages(context: Dict[str, Any], limit: int = 100) -> Dict[str, Any]:
	channel = context.get("_channel")

	if not channel:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	try:
		deleted = await channel.purge(limit=limit)

		return {
			"success": True,
			"deleted_count": len(deleted)
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Bot lacks permission to purge messages."
		}
	except discord.HTTPException as error:
		return {
			"success": False,
			"error": str(error)
		}


async def disconnect_from_voice(context: Dict[str, Any], user_id: str) -> Dict[str, Any]:
	guild = context.get("_guild")

	if not guild:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	try:
		member = guild.get_member(int(user_id))

		if member is None:
			return {
				"success": False,
				"error": "Member not found."
			}

		if not member.voice:
			return {
				"success": False,
				"error": "Member is not in a voice channel."
			}

		await member.move_to(None)

		return {
			"success": True,
			"user_id": str(user_id)
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Bot lacks permission to move this member."
		}
	except discord.HTTPException as error:
		return {
			"success": False,
			"error": str(error)
		}


async def move_member_to_voice(context: Dict[str, Any], user_id: str, channel_id: str) -> Dict[str, Any]:
	guild = context.get("_guild")

	if not guild:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	try:
		member = guild.get_member(int(user_id))
		target_channel = guild.get_channel(int(channel_id))

		if member is None:
			return {
				"success": False,
				"error": "Member not found."
			}

		if target_channel is None or not isinstance(target_channel, discord.VoiceChannel):
			return {
				"success": False,
				"error": "Target voice channel not found."
			}

		await member.move_to(target_channel)

		return {
			"success": True,
			"user_id": str(user_id),
			"channel_id": str(channel_id),
			"channel_name": target_channel.name
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Bot lacks permission to move this member."
		}
	except discord.HTTPException as error:
		return {
			"success": False,
			"error": str(error)
		}


def register_moderation_tools():
	register_tool(
		"ban_user",
		ban_user,
		genai.types.FunctionDeclaration(
			name="ban_user",
			description="Ban a Discord member from the current server.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"user_id": genai.types.Schema(
						type="string",
						description="Discord ID of the member to ban."
					),
					"reason": genai.types.Schema(
						type="string",
						description="Reason for the ban."
					)
				},
				required=["user_id", "reason"]
			)
		),
		"moderation"
	)

	register_tool(
		"unban_user",
		unban_user,
		genai.types.FunctionDeclaration(
			name="unban_user",
			description="Unban a Discord user from the current server.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"user_id": genai.types.Schema(
						type="string",
						description="Discord ID of the user to unban."
					),
					"reason": genai.types.Schema(
						type="string",
						description="Reason for the unban. Optional."
					)
				},
				required=["user_id"]
			)
		),
		"moderation"
	)

	register_tool(
		"kick_user",
		kick_user,
		genai.types.FunctionDeclaration(
			name="kick_user",
			description="Kick a Discord member from the current server.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"user_id": genai.types.Schema(
						type="string",
						description="Discord ID of the member to kick."
					),
					"reason": genai.types.Schema(
						type="string",
						description="Reason for the kick."
					)
				},
				required=["user_id", "reason"]
			)
		),
		"moderation"
	)

	register_tool(
		"timeout_user",
		timeout_user,
		genai.types.FunctionDeclaration(
			name="timeout_user",
			description="Timeout a Discord member for a specified duration.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"user_id": genai.types.Schema(
						type="string",
						description="Discord ID of the member to timeout."
					),
					"duration_minutes": genai.types.Schema(
						type="integer",
						description="Duration of timeout in minutes."
					),
					"reason": genai.types.Schema(
						type="string",
						description="Reason for the timeout."
					)
				},
				required=["user_id", "duration_minutes", "reason"]
			)
		),
		"moderation"
	)

	register_tool(
		"remove_timeout",
		remove_timeout,
		genai.types.FunctionDeclaration(
			name="remove_timeout",
			description="Remove timeout from a Discord member.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"user_id": genai.types.Schema(
						type="string",
						description="Discord ID of the member to untimeout."
					),
					"reason": genai.types.Schema(
						type="string",
						description="Reason for removing timeout. Optional."
					)
				},
				required=["user_id"]
			)
		),
		"moderation"
	)

	register_tool(
		"warn_user",
		warn_user,
		genai.types.FunctionDeclaration(
			name="warn_user",
			description="Send a warning message to a Discord member.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"user_id": genai.types.Schema(
						type="string",
						description="Discord ID of the member to warn."
					),
					"reason": genai.types.Schema(
						type="string",
						description="Warning message/reason."
					)
				},
				required=["user_id", "reason"]
			)
		),
		"moderation"
	)

	register_tool(
		"delete_message",
		delete_message,
		genai.types.FunctionDeclaration(
			name="delete_message",
			description="Delete a specific message by ID.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"message_id": genai.types.Schema(
						type="string",
						description="Discord ID of the message to delete."
					)
				},
				required=["message_id"]
			)
		),
		"moderation"
	)

	register_tool(
		"purge_messages",
		purge_messages,
		genai.types.FunctionDeclaration(
			name="purge_messages",
			description="Delete multiple messages from the current channel.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"limit": genai.types.Schema(
						type="integer",
						description="Maximum number of messages to delete. Default is 100."
					)
				},
				required=[]
			)
		),
		"moderation"
	)

	register_tool(
		"disconnect_from_voice",
		disconnect_from_voice,
		genai.types.FunctionDeclaration(
			name="disconnect_from_voice",
			description="Disconnect a member from their voice channel.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"user_id": genai.types.Schema(
						type="string",
						description="Discord ID of the member to disconnect."
					)
				},
				required=["user_id"]
			)
		),
		"moderation"
	)

	register_tool(
		"move_member_to_voice",
		move_member_to_voice,
		genai.types.FunctionDeclaration(
			name="move_member_to_voice",
			description="Move a member to a different voice channel.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"user_id": genai.types.Schema(
						type="string",
						description="Discord ID of the member to move."
					),
					"channel_id": genai.types.Schema(
						type="string",
						description="Discord ID of the target voice channel."
					)
				},
				required=["user_id", "channel_id"]
			)
		),
		"moderation"
	)
