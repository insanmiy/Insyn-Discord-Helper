import discord
from typing import Dict, Any, List, Optional
from google import genai

from src.tools.registry import register_tool
from src.reaction_roles.storage import (
	set_message_config,
	remove_message_config,
	list_guild_reaction_roles,
	get_message_config,
	emoji_key
)


def parse_emoji(emoji_str: str):
	emoji_str = emoji_str.strip()

	if emoji_str.startswith("<") and emoji_str.endswith(">"):
		parts = emoji_str.strip("<>").split(":")
		if len(parts) >= 3:
			return discord.PartialEmoji(name=parts[1], id=int(parts[2]))
		if len(parts) == 2 and parts[1].isdigit():
			return discord.PartialEmoji(name=parts[0], id=int(parts[1]))

	if ":" in emoji_str:
		name, emoji_id = emoji_str.rsplit(":", 1)
		if emoji_id.isdigit():
			return discord.PartialEmoji(name=name, id=int(emoji_id))

	return emoji_str


async def create_reaction_role_panel(
	context: Dict[str, Any],
	content: str,
	role_mappings: List[Dict[str, str]],
	channel_id: Optional[str] = None,
	exclusive: bool = False
) -> Dict[str, Any]:
	guild = context.get("_guild")
	channel = context.get("_channel")

	if not guild or not channel:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	if not role_mappings:
		return {
			"success": False,
			"error": "At least one emoji-to-role mapping is required."
		}

	target_channel = channel
	if channel_id:
		target_channel = guild.get_channel(int(channel_id))
		if target_channel is None:
			return {
				"success": False,
				"error": "Channel not found."
			}

	if not isinstance(target_channel, discord.abc.Messageable):
		return {
			"success": False,
			"error": "This operation can only be performed on messageable channels."
		}

	try:
		message = await target_channel.send(content)
		mappings = {}

		for mapping in role_mappings:
			emoji_input = mapping.get("emoji")
			role_id = mapping.get("role_id")

			if not emoji_input or not role_id:
				continue

			role = guild.get_role(int(role_id))
			if role is None:
				return {
					"success": False,
					"error": f"Role {role_id} not found."
				}

			parsed_emoji = parse_emoji(emoji_input)
			await message.add_reaction(parsed_emoji)
			mappings[emoji_key(parsed_emoji)] = str(role_id)

		if not mappings:
			await message.delete()
			return {
				"success": False,
				"error": "No valid emoji-to-role mappings were provided."
			}

		set_message_config(
			str(guild.id),
			str(message.id),
			{
				"channel_id": str(target_channel.id),
				"exclusive": exclusive,
				"mappings": mappings
			}
		)

		return {
			"success": True,
			"message_id": str(message.id),
			"channel_id": str(target_channel.id),
			"mappings": mappings,
			"exclusive": exclusive
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Bot lacks permission to send messages, add reactions, or manage roles."
		}
	except discord.HTTPException as error:
		return {
			"success": False,
			"error": str(error)
		}


async def add_reaction_role(
	context: Dict[str, Any],
	message_id: str,
	emoji: str,
	role_id: str,
	channel_id: Optional[str] = None
) -> Dict[str, Any]:
	guild = context.get("_guild")
	channel = context.get("_channel")

	if not guild:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	config = get_message_config(str(guild.id), message_id)
	if config is None:
		return {
			"success": False,
			"error": "Reaction role message not found."
		}

	target_channel_id = channel_id or config.get("channel_id") or context.get("channel_id")
	target_channel = guild.get_channel(int(target_channel_id))

	if target_channel is None or not isinstance(target_channel, discord.abc.Messageable):
		return {
			"success": False,
			"error": "Channel not found."
		}

	role = guild.get_role(int(role_id))
	if role is None:
		return {
			"success": False,
			"error": "Role not found."
		}

	try:
		message = await target_channel.fetch_message(int(message_id))
		parsed_emoji = parse_emoji(emoji)
		await message.add_reaction(parsed_emoji)

		config.setdefault("mappings", {})[emoji_key(parsed_emoji)] = str(role_id)
		set_message_config(str(guild.id), message_id, config)

		return {
			"success": True,
			"message_id": message_id,
			"emoji": emoji_key(parsed_emoji),
			"role_id": str(role_id)
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Bot lacks permission to add reactions or manage roles."
		}
	except discord.HTTPException as error:
		return {
			"success": False,
			"error": str(error)
		}


async def remove_reaction_role(
	context: Dict[str, Any],
	message_id: str,
	emoji: str,
	channel_id: Optional[str] = None
) -> Dict[str, Any]:
	guild = context.get("_guild")

	if not guild:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	config = get_message_config(str(guild.id), message_id)
	if config is None:
		return {
			"success": False,
			"error": "Reaction role message not found."
		}

	key = emoji_key(parse_emoji(emoji))
	mappings = config.get("mappings", {})

	if key not in mappings:
		return {
			"success": False,
			"error": "That emoji is not configured for this message."
		}

	del mappings[key]

	if mappings:
		config["mappings"] = mappings
		set_message_config(str(guild.id), message_id, config)
	else:
		remove_message_config(str(guild.id), message_id)

	return {
		"success": True,
		"message_id": message_id,
		"emoji": key
	}


async def list_reaction_role_panels(context: Dict[str, Any]) -> Dict[str, Any]:
	guild = context.get("_guild")

	if not guild:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	panels = list_guild_reaction_roles(str(guild.id))
	formatted = []

	for message_id, panel in panels.items():
		formatted.append({
			"message_id": message_id,
			"channel_id": panel.get("channel_id"),
			"exclusive": panel.get("exclusive", False),
			"mappings": panel.get("mappings", {})
		})

	return {
		"success": True,
		"panels": formatted,
		"count": len(formatted)
	}


def register_reaction_role_tools():
	register_tool(
		"create_reaction_role_panel",
		create_reaction_role_panel,
		genai.types.FunctionDeclaration(
			name="create_reaction_role_panel",
			description="Create a reaction role panel by sending a message and attaching emoji reactions that grant roles.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"content": genai.types.Schema(
						type="string",
						description="The message content shown on the reaction role panel."
					),
					"role_mappings": genai.types.Schema(
						type="array",
						description="List of emoji-to-role mappings.",
						items=genai.types.Schema(
							type="object",
							properties={
								"emoji": genai.types.Schema(
									type="string",
									description="Unicode emoji or custom emoji in name:id format."
								),
								"role_id": genai.types.Schema(
									type="string",
									description="Discord role ID to grant when the emoji is clicked."
								)
							},
							required=["emoji", "role_id"]
						)
					),
					"channel_id": genai.types.Schema(
						type="string",
						description="Optional channel ID. Defaults to the current channel."
					),
					"exclusive": genai.types.Schema(
						type="boolean",
						description="If true, users can only have one role from this panel at a time."
					)
				},
				required=["content", "role_mappings"]
			)
		),
		"server_management"
	)

	register_tool(
		"add_reaction_role",
		add_reaction_role,
		genai.types.FunctionDeclaration(
			name="add_reaction_role",
			description="Add an emoji-to-role mapping to an existing reaction role panel.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"message_id": genai.types.Schema(
						type="string",
						description="Discord message ID of the reaction role panel."
					),
					"emoji": genai.types.Schema(
						type="string",
						description="Unicode emoji or custom emoji in name:id format."
					),
					"role_id": genai.types.Schema(
						type="string",
						description="Discord role ID to grant."
					),
					"channel_id": genai.types.Schema(
						type="string",
						description="Optional channel ID if not stored in the panel config."
					)
				},
				required=["message_id", "emoji", "role_id"]
			)
		),
		"server_management"
	)

	register_tool(
		"remove_reaction_role",
		remove_reaction_role,
		genai.types.FunctionDeclaration(
			name="remove_reaction_role",
			description="Remove an emoji-to-role mapping from a reaction role panel.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"message_id": genai.types.Schema(
						type="string",
						description="Discord message ID of the reaction role panel."
					),
					"emoji": genai.types.Schema(
						type="string",
						description="Unicode emoji or custom emoji in name:id format."
					),
					"channel_id": genai.types.Schema(
						type="string",
						description="Optional channel ID if not stored in the panel config."
					)
				},
				required=["message_id", "emoji"]
			)
		),
		"server_management"
	)

	register_tool(
		"list_reaction_role_panels",
		list_reaction_role_panels,
		genai.types.FunctionDeclaration(
			name="list_reaction_role_panels",
			description="List all reaction role panels configured in the current server.",
			parameters=genai.types.Schema(
				type="object",
				properties={},
				required=[]
			)
		),
		"read"
	)
