import discord
from typing import Dict, Any, Optional
from src.tools.registry import register_tool
from google import genai


async def create_text_channel(context: Dict[str, Any], name: str, category_id: Optional[str] = None, topic: Optional[str] = None) -> Dict[str, Any]:
	guild = context.get("_guild")

	if not guild:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	try:
		category = guild.get_channel(int(category_id)) if category_id else None

		channel = await guild.create_text_channel(
			name,
			category=category,
			topic=topic,
			reason="Created by Insyn Helper"
		)

		return {
			"success": True,
			"channel_id": str(channel.id),
			"channel_name": channel.name,
			"category_id": str(channel.category_id) if channel.category else None
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Bot lacks permission to create channels."
		}
	except discord.HTTPException as error:
		return {
			"success": False,
			"error": str(error)
		}


async def create_voice_channel(context: Dict[str, Any], name: str, category_id: Optional[str] = None) -> Dict[str, Any]:
	guild = context.get("_guild")

	if not guild:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	try:
		category = guild.get_channel(int(category_id)) if category_id else None

		channel = await guild.create_voice_channel(
			name,
			category=category,
			reason="Created by Insyn Helper"
		)

		return {
			"success": True,
			"channel_id": str(channel.id),
			"channel_name": channel.name,
			"category_id": str(channel.category_id) if channel.category else None
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Bot lacks permission to create channels."
		}
	except discord.HTTPException as error:
		return {
			"success": False,
			"error": str(error)
		}


async def create_category(context: Dict[str, Any], name: str) -> Dict[str, Any]:
	guild = context.get("_guild")

	if not guild:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	try:
		category = await guild.create_category(name, reason="Created by Insyn Helper")

		return {
			"success": True,
			"category_id": str(category.id),
			"category_name": category.name
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Bot lacks permission to create categories."
		}
	except discord.HTTPException as error:
		return {
			"success": False,
			"error": str(error)
		}


async def delete_channel(context: Dict[str, Any], channel_id: str) -> Dict[str, Any]:
	guild = context.get("_guild")

	if not guild:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	try:
		channel = guild.get_channel(int(channel_id))

		if channel is None:
			return {
				"success": False,
				"error": "Channel not found."
			}

		await channel.delete(reason="Deleted by Insyn Helper")

		return {
			"success": True,
			"channel_id": str(channel_id),
			"channel_name": channel.name
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Bot lacks permission to delete this channel."
		}
	except discord.HTTPException as error:
		return {
			"success": False,
			"error": str(error)
		}


async def rename_channel(context: Dict[str, Any], channel_id: str, new_name: str) -> Dict[str, Any]:
	guild = context.get("_guild")

	if not guild:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	try:
		channel = guild.get_channel(int(channel_id))

		if channel is None:
			return {
				"success": False,
				"error": "Channel not found."
			}

		old_name = channel.name
		await channel.edit(name=new_name, reason="Renamed by Insyn Helper")

		return {
			"success": True,
			"channel_id": str(channel_id),
			"old_name": old_name,
			"new_name": new_name
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Bot lacks permission to rename this channel."
		}
	except discord.HTTPException as error:
		return {
			"success": False,
			"error": str(error)
		}


async def edit_channel_topic(context: Dict[str, Any], channel_id: str, topic: str) -> Dict[str, Any]:
	guild = context.get("_guild")

	if not guild:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	try:
		channel = guild.get_channel(int(channel_id))

		if channel is None:
			return {
				"success": False,
				"error": "Channel not found."
			}

		if not isinstance(channel, discord.TextChannel):
			return {
				"success": False,
				"error": "This operation can only be performed on text channels."
			}

		await channel.edit(topic=topic, reason="Topic edited by Insyn Helper")

		return {
			"success": True,
			"channel_id": str(channel_id),
			"channel_name": channel.name,
			"new_topic": topic
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Bot lacks permission to edit this channel."
		}
	except discord.HTTPException as error:
		return {
			"success": False,
			"error": str(error)
		}


async def move_channel(context: Dict[str, Any], channel_id: str, new_category_id: Optional[str] = None, position: Optional[int] = None) -> Dict[str, Any]:
	guild = context.get("_guild")

	if not guild:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	try:
		channel = guild.get_channel(int(channel_id))

		if channel is None:
			return {
				"success": False,
				"error": "Channel not found."
			}

		category = guild.get_channel(int(new_category_id)) if new_category_id else None

		kwargs = {"reason": "Channel moved by Insyn Helper"}
		if category:
			kwargs["category"] = category
		if position is not None:
			kwargs["position"] = position

		await channel.edit(**kwargs)

		return {
			"success": True,
			"channel_id": str(channel_id),
			"channel_name": channel.name,
			"new_category_id": str(new_category_id) if new_category_id else None,
			"new_position": position
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Bot lacks permission to move this channel."
		}
	except discord.HTTPException as error:
		return {
			"success": False,
			"error": str(error)
		}


async def lock_channel(context: Dict[str, Any], channel_id: str) -> Dict[str, Any]:
	guild = context.get("_guild")

	if not guild:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	try:
		channel = guild.get_channel(int(channel_id))

		if channel is None:
			return {
				"success": False,
				"error": "Channel not found."
			}

		if not isinstance(channel, discord.abc.Messageable):
			return {
				"success": False,
				"error": "This operation can only be performed on messageable channels."
			}

		overwrite = channel.overwrites_for(guild.default_role)
		overwrite.send_messages = False

		await channel.set_permissions(guild.default_role, overwrite=overwrite, reason="Channel locked by Insyn Helper")

		return {
			"success": True,
			"channel_id": str(channel_id),
			"channel_name": channel.name
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Bot lacks permission to lock this channel."
		}
	except discord.HTTPException as error:
		return {
			"success": False,
			"error": str(error)
		}


async def unlock_channel(context: Dict[str, Any], channel_id: str) -> Dict[str, Any]:
	guild = context.get("_guild")

	if not guild:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	try:
		channel = guild.get_channel(int(channel_id))

		if channel is None:
			return {
				"success": False,
				"error": "Channel not found."
			}

		if not isinstance(channel, discord.abc.Messageable):
			return {
				"success": False,
				"error": "This operation can only be performed on messageable channels."
			}

		overwrite = channel.overwrites_for(guild.default_role)
		overwrite.send_messages = None

		await channel.set_permissions(guild.default_role, overwrite=overwrite, reason="Channel unlocked by Insyn Helper")

		return {
			"success": True,
			"channel_id": str(channel_id),
			"channel_name": channel.name
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Bot lacks permission to unlock this channel."
		}
	except discord.HTTPException as error:
		return {
			"success": False,
			"error": str(error)
		}


def register_channel_tools():
	register_tool(
		"create_text_channel",
		create_text_channel,
		genai.types.FunctionDeclaration(
			name="create_text_channel",
			description="Create a new text channel in the server.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"name": genai.types.Schema(
						type="string",
						description="Name for the new text channel."
					),
					"category_id": genai.types.Schema(
						type="string",
						description="Optional category ID to place the channel in."
					),
					"topic": genai.types.Schema(
						type="string",
						description="Optional topic for the channel."
					)
				},
				required=["name"]
			)
		),
		"server_management"
	)

	register_tool(
		"create_voice_channel",
		create_voice_channel,
		genai.types.FunctionDeclaration(
			name="create_voice_channel",
			description="Create a new voice channel in the server.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"name": genai.types.Schema(
						type="string",
						description="Name for the new voice channel."
					),
					"category_id": genai.types.Schema(
						type="string",
						description="Optional category ID to place the channel in."
					)
				},
				required=["name"]
			)
		),
		"server_management"
	)

	register_tool(
		"create_category",
		create_category,
		genai.types.FunctionDeclaration(
			name="create_category",
			description="Create a new category in the server.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"name": genai.types.Schema(
						type="string",
						description="Name for the new category."
					)
				},
				required=["name"]
			)
		),
		"server_management"
	)

	register_tool(
		"delete_channel",
		delete_channel,
		genai.types.FunctionDeclaration(
			name="delete_channel",
			description="Delete a channel from the server.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"channel_id": genai.types.Schema(
						type="string",
						description="Discord ID of the channel to delete."
					)
				},
				required=["channel_id"]
			)
		),
		"server_management"
	)

	register_tool(
		"rename_channel",
		rename_channel,
		genai.types.FunctionDeclaration(
			name="rename_channel",
			description="Rename a channel in the server.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"channel_id": genai.types.Schema(
						type="string",
						description="Discord ID of the channel to rename."
					),
					"new_name": genai.types.Schema(
						type="string",
						description="New name for the channel."
					)
				},
				required=["channel_id", "new_name"]
			)
		),
		"server_management"
	)

	register_tool(
		"edit_channel_topic",
		edit_channel_topic,
		genai.types.FunctionDeclaration(
			name="edit_channel_topic",
			description="Edit the topic of a text channel.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"channel_id": genai.types.Schema(
						type="string",
						description="Discord ID of the text channel."
					),
					"topic": genai.types.Schema(
						type="string",
						description="New topic for the channel."
					)
				},
				required=["channel_id", "topic"]
			)
		),
		"server_management"
	)

	register_tool(
		"move_channel",
		move_channel,
		genai.types.FunctionDeclaration(
			name="move_channel",
			description="Move a channel to a different category or position.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"channel_id": genai.types.Schema(
						type="string",
						description="Discord ID of the channel to move."
					),
					"new_category_id": genai.types.Schema(
						type="string",
						description="Optional category ID to move the channel to."
					),
					"position": genai.types.Schema(
						type="integer",
						description="Optional new position for the channel."
					)
				},
				required=["channel_id"]
			)
		),
		"server_management"
	)

	register_tool(
		"lock_channel",
		lock_channel,
		genai.types.FunctionDeclaration(
			name="lock_channel",
			description="Lock a channel so members cannot send messages.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"channel_id": genai.types.Schema(
						type="string",
						description="Discord ID of the channel to lock."
					)
				},
				required=["channel_id"]
			)
		),
		"server_management"
	)

	register_tool(
		"unlock_channel",
		unlock_channel,
		genai.types.FunctionDeclaration(
			name="unlock_channel",
			description="Unlock a channel so members can send messages again.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"channel_id": genai.types.Schema(
						type="string",
						description="Discord ID of the channel to unlock."
					)
				},
				required=["channel_id"]
			)
		),
		"server_management"
	)
