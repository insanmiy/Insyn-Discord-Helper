import discord
from typing import Dict, Any, Optional
from src.tools.registry import register_tool
from google import genai


async def get_message(context: Dict[str, Any], channel_id: str, message_id: str) -> Dict[str, Any]:
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

		message = await channel.fetch_message(int(message_id))

		return {
			"success": True,
			"data": {
				"id": str(message.id),
				"content": message.content,
				"author_id": str(message.author.id),
				"author_name": message.author.name,
				"channel_id": str(channel.id),
				"channel_name": channel.name,
				"created_at": message.created_at.isoformat(),
				"edited_at": message.edited_at.isoformat() if message.edited_at else None
			}
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Bot lacks permission to read messages in this channel."
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


async def search_messages(context: Dict[str, Any], channel_id: str, query: str, limit: int = 20) -> Dict[str, Any]:
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

		messages = []
		count = 0

		async for message in channel.history(limit=100):
			if count >= limit:
				break

			if query.lower() in message.content.lower():
				messages.append({
					"id": str(message.id),
					"content": message.content[:200],
					"author_id": str(message.author.id),
					"author_name": message.author.name,
					"created_at": message.created_at.isoformat()
				})
				count += 1

		return {
			"success": True,
			"channel_id": str(channel_id),
			"channel_name": channel.name,
			"query": query,
			"messages": messages,
			"total_found": len(messages)
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Bot lacks permission to read messages in this channel."
		}
	except discord.HTTPException as error:
		return {
			"success": False,
			"error": str(error)
		}


async def send_message(context: Dict[str, Any], channel_id: str, content: str) -> Dict[str, Any]:
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

		message = await channel.send(content)

		return {
			"success": True,
			"message_id": str(message.id),
			"channel_id": str(channel_id),
			"channel_name": channel.name,
			"content": content
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Bot lacks permission to send messages in this channel."
		}
	except discord.HTTPException as error:
		return {
			"success": False,
			"error": str(error)
		}


async def edit_message(context: Dict[str, Any], channel_id: str, message_id: str, new_content: str) -> Dict[str, Any]:
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

		message = await channel.fetch_message(int(message_id))

		if message.author != guild.me:
			return {
				"success": False,
				"error": "Can only edit messages sent by the bot."
			}

		await message.edit(content=new_content)

		return {
			"success": True,
			"message_id": str(message_id),
			"channel_id": str(channel_id),
			"new_content": new_content
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Bot lacks permission to edit messages in this channel."
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


async def bulk_delete_messages(context: Dict[str, Any], channel_id: str, message_ids: list) -> Dict[str, Any]:
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

		messages_to_delete = []
		for msg_id in message_ids:
			try:
				message = await channel.fetch_message(int(msg_id))
				messages_to_delete.append(message)
			except discord.NotFound:
				continue

		await channel.delete_messages(messages_to_delete)

		return {
			"success": True,
			"deleted_count": len(messages_to_delete),
			"channel_id": str(channel_id),
			"channel_name": channel.name
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Bot lacks permission to bulk delete messages in this channel."
		}
	except discord.HTTPException as error:
		return {
			"success": False,
			"error": str(error)
		}


def register_message_tools():
	register_tool(
		"get_message",
		get_message,
		genai.types.FunctionDeclaration(
			name="get_message",
			description="Get a specific message by ID from a channel.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"channel_id": genai.types.Schema(
						type="string",
						description="Discord ID of the channel."
					),
					"message_id": genai.types.Schema(
						type="string",
						description="Discord ID of the message."
					)
				},
				required=["channel_id", "message_id"]
			)
		),
		"read"
	)

	register_tool(
		"search_messages",
		search_messages,
		genai.types.FunctionDeclaration(
			name="search_messages",
			description="Search for messages in a channel containing a specific query.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"channel_id": genai.types.Schema(
						type="string",
						description="Discord ID of the channel to search."
					),
					"query": genai.types.Schema(
						type="string",
						description="Search query to look for in message content."
					),
					"limit": genai.types.Schema(
						type="integer",
						description="Maximum number of results to return. Default is 20."
					)
				},
				required=["channel_id", "query"]
			)
		),
		"read"
	)

	register_tool(
		"send_message",
		send_message,
		genai.types.FunctionDeclaration(
			name="send_message",
			description="Send a message to a specific channel.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"channel_id": genai.types.Schema(
						type="string",
						description="Discord ID of the channel to send the message to."
					),
					"content": genai.types.Schema(
						type="string",
						description="Content of the message to send."
					)
				},
				required=["channel_id", "content"]
			)
		),
		"moderation"
	)

	register_tool(
		"edit_message",
		edit_message,
		genai.types.FunctionDeclaration(
			name="edit_message",
			description="Edit a message sent by the bot.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"channel_id": genai.types.Schema(
						type="string",
						description="Discord ID of the channel containing the message."
					),
					"message_id": genai.types.Schema(
						type="string",
						description="Discord ID of the message to edit."
					),
					"new_content": genai.types.Schema(
						type="string",
						description="New content for the message."
					)
				},
				required=["channel_id", "message_id", "new_content"]
			)
		),
		"moderation"
	)

	register_tool(
		"bulk_delete_messages",
		bulk_delete_messages,
		genai.types.FunctionDeclaration(
			name="bulk_delete_messages",
			description="Delete multiple messages by their IDs.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"channel_id": genai.types.Schema(
						type="string",
						description="Discord ID of the channel containing the messages."
					),
					"message_ids": genai.types.Schema(
						type="array",
						items=genai.types.Schema(type="string"),
						description="List of Discord message IDs to delete."
					)
				},
				required=["channel_id", "message_ids"]
			)
		),
		"moderation"
	)
