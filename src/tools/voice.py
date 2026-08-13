import discord
from typing import Dict, Any
from src.tools.registry import register_tool
from google import genai


async def disconnect_member_from_voice(context: Dict[str, Any], user_id: str) -> Dict[str, Any]:
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

		await member.move_to(None, reason="Disconnected by Insyn Helper")

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

		await member.move_to(target_channel, reason="Moved by Insyn Helper")

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


async def mute_member(context: Dict[str, Any], user_id: str) -> Dict[str, Any]:
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

		await member.edit(mute=True, reason="Muted by Insyn Helper")

		return {
			"success": True,
			"user_id": str(user_id)
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Bot lacks permission to mute this member."
		}
	except discord.HTTPException as error:
		return {
			"success": False,
			"error": str(error)
		}


async def unmute_member(context: Dict[str, Any], user_id: str) -> Dict[str, Any]:
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

		await member.edit(mute=False, reason="Unmuted by Insyn Helper")

		return {
			"success": True,
			"user_id": str(user_id)
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Bot lacks permission to unmute this member."
		}
	except discord.HTTPException as error:
		return {
			"success": False,
			"error": str(error)
		}


async def deafen_member(context: Dict[str, Any], user_id: str) -> Dict[str, Any]:
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

		await member.edit(deafen=True, reason="Deafened by Insyn Helper")

		return {
			"success": True,
			"user_id": str(user_id)
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Bot lacks permission to deafen this member."
		}
	except discord.HTTPException as error:
		return {
			"success": False,
			"error": str(error)
		}


async def undeafen_member(context: Dict[str, Any], user_id: str) -> Dict[str, Any]:
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

		await member.edit(deafen=False, reason="Undeafened by Insyn Helper")

		return {
			"success": True,
			"user_id": str(user_id)
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Bot lacks permission to undeafen this member."
		}
	except discord.HTTPException as error:
		return {
			"success": False,
			"error": str(error)
		}


def register_voice_tools():
	register_tool(
		"disconnect_member_from_voice",
		disconnect_member_from_voice,
		genai.types.FunctionDeclaration(
			name="disconnect_member_from_voice",
			description="Disconnect a member from their current voice channel.",
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

	register_tool(
		"mute_member",
		mute_member,
		genai.types.FunctionDeclaration(
			name="mute_member",
			description="Mute a member in voice chat.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"user_id": genai.types.Schema(
						type="string",
						description="Discord ID of the member to mute."
					)
				},
				required=["user_id"]
			)
		),
		"moderation"
	)

	register_tool(
		"unmute_member",
		unmute_member,
		genai.types.FunctionDeclaration(
			name="unmute_member",
			description="Unmute a member in voice chat.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"user_id": genai.types.Schema(
						type="string",
						description="Discord ID of the member to unmute."
					)
				},
				required=["user_id"]
			)
		),
		"moderation"
	)

	register_tool(
		"deafen_member",
		deafen_member,
		genai.types.FunctionDeclaration(
			name="deafen_member",
			description="Deafen a member in voice chat.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"user_id": genai.types.Schema(
						type="string",
						description="Discord ID of the member to deafen."
					)
				},
				required=["user_id"]
			)
		),
		"moderation"
	)

	register_tool(
		"undeafen_member",
		undeafen_member,
		genai.types.FunctionDeclaration(
			name="undeafen_member",
			description="Undeafen a member in voice chat.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"user_id": genai.types.Schema(
						type="string",
						description="Discord ID of the member to undeafen."
					)
				},
				required=["user_id"]
			)
		),
		"moderation"
	)
