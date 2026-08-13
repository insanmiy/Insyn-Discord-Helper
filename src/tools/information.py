import discord
from typing import Dict, Any
from src.tools.registry import register_tool
from src.services.weather import get_weather
from google import genai


async def get_server_info(context: Dict[str, Any]) -> Dict[str, Any]:
	guild_id = context.get("guild_id")

	if not guild_id:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	try:
		guild = context.get("_guild")
		if not guild:
			return {
				"success": False,
				"error": "Guild context not available."
			}

		return {
			"success": True,
			"data": {
				"id": str(guild.id),
				"name": guild.name,
				"owner_id": str(guild.owner_id),
				"member_count": guild.member_count,
				"role_count": len(guild.roles),
				"channel_count": len(guild.channels),
				"created_at": guild.created_at.isoformat(),
				"description": guild.description,
				"region": str(guild.region) if hasattr(guild, 'region') else None,
				"verification_level": str(guild.verification_level),
				"premium_tier": guild.premium_tier
			}
		}
	except Exception as e:
		return {
			"success": False,
			"error": str(e)
		}


async def get_member(context: Dict[str, Any], user_id: str = None) -> Dict[str, Any]:
	guild = context.get("_guild")

	if not guild:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	try:
		if user_id:
			member = guild.get_member(int(user_id))
			if not member:
				return {
					"success": False,
					"error": f"Member with ID {user_id} not found."
				}
		else:
			user_id = context.get("user_id")
			member = guild.get_member(int(user_id))
			if not member:
				return {
					"success": False,
					"error": "Member not found."
				}

		roles = [str(role.id) for role in member.roles]

		return {
			"success": True,
			"data": {
				"id": str(member.id),
				"username": member.name,
				"discriminator": member.discriminator,
				"display_name": member.display_name,
				"bot": member.bot,
				"joined_at": member.joined_at.isoformat() if member.joined_at else None,
				"roles": roles,
				"top_role": str(member.top_role.id),
				"top_role_name": member.top_role.name,
				"nick": member.nick,
				"avatar_url": member.avatar.url if member.avatar else None
			}
		}
	except Exception as e:
		return {
			"success": False,
			"error": str(e)
		}


async def get_members(context: Dict[str, Any], limit: int = 20) -> Dict[str, Any]:
	guild = context.get("_guild")

	if not guild:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	try:
		members_list = []
		count = 0

		for member in guild.members:
			if count >= limit:
				break

			members_list.append({
				"id": str(member.id),
				"username": member.name,
				"display_name": member.display_name,
				"bot": member.bot
			})
			count += 1

		return {
			"success": True,
			"data": {
				"members": members_list,
				"total_count": guild.member_count,
				"returned_count": len(members_list)
			}
		}
	except Exception as e:
		return {
			"success": False,
			"error": str(e)
		}


async def get_roles(context: Dict[str, Any]) -> Dict[str, Any]:
	guild = context.get("_guild")

	if not guild:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	try:
		roles_list = []
		for role in guild.roles:
			roles_list.append({
				"id": str(role.id),
				"name": role.name,
				"color": str(role.color),
				"hoist": role.hoist,
				"position": role.position,
				"mentionable": role.mentionable,
				"managed": role.managed,
				"member_count": len(role.members)
			})

		return {
			"success": True,
			"data": {
				"roles": roles_list,
				"total_count": len(roles_list)
			}
		}
	except Exception as e:
		return {
			"success": False,
			"error": str(e)
		}


async def get_channels(context: Dict[str, Any]) -> Dict[str, Any]:
	guild = context.get("_guild")

	if not guild:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	try:
		channels_list = []
		for channel in guild.channels:
			channel_type = "unknown"
			if isinstance(channel, discord.TextChannel):
				channel_type = "text"
			elif isinstance(channel, discord.VoiceChannel):
				channel_type = "voice"
			elif isinstance(channel, discord.CategoryChannel):
				channel_type = "category"

			channels_list.append({
				"id": str(channel.id),
				"name": channel.name,
				"type": channel_type,
				"position": channel.position,
				"category_id": str(channel.category_id) if channel.category else None
			})

		return {
			"success": True,
			"data": {
				"channels": channels_list,
				"total_count": len(channels_list)
			}
		}
	except Exception as e:
		return {
			"success": False,
			"error": str(e)
		}


async def get_current_user(context: Dict[str, Any]) -> Dict[str, Any]:
	try:
		return {
			"success": True,
			"data": {
				"id": context.get("user_id"),
				"username": context.get("username"),
				"display_name": context.get("display_name"),
				"guild_id": context.get("guild_id"),
				"guild_name": context.get("guild_name"),
				"channel_id": context.get("channel_id"),
				"channel_name": context.get("channel_name")
			}
		}
	except Exception as e:
		return {
			"success": False,
			"error": str(e)
		}


async def get_weather_tool(context: Dict[str, Any], location: str) -> Dict[str, Any]:
	return await get_weather(location)


def register_information_tools():
	register_tool(
		"get_server_info",
		get_server_info,
		genai.types.FunctionDeclaration(
			name="get_server_info",
			description="Get information about the current Discord server.",
			parameters=genai.types.Schema(
				type="object",
				properties={},
				required=[]
			)
		),
		"read"
	)

	register_tool(
		"get_member",
		get_member,
		genai.types.FunctionDeclaration(
			name="get_member",
			description="Get information about a specific Discord member. If no user_id is provided, returns information about the current user.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"user_id": genai.types.Schema(
						type="string",
						description="Discord ID of the member to look up. Optional - if not provided, returns current user."
					)
				},
				required=[]
			)
		),
		"read"
	)

	register_tool(
		"get_members",
		get_members,
		genai.types.FunctionDeclaration(
			name="get_members",
			description="Get a list of members in the server.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"limit": genai.types.Schema(
						type="integer",
						description="Maximum number of members to return. Default is 20."
					)
				},
				required=[]
			)
		),
		"read"
	)

	register_tool(
		"get_roles",
		get_roles,
		genai.types.FunctionDeclaration(
			name="get_roles",
			description="Get a list of all roles in the server.",
			parameters=genai.types.Schema(
				type="object",
				properties={},
				required=[]
			)
		),
		"read"
	)

	register_tool(
		"get_channels",
		get_channels,
		genai.types.FunctionDeclaration(
			name="get_channels",
			description="Get a list of all channels in the server.",
			parameters=genai.types.Schema(
				type="object",
				properties={},
				required=[]
			)
		),
		"read"
	)

	register_tool(
		"get_current_user",
		get_current_user,
		genai.types.FunctionDeclaration(
			name="get_current_user",
			description="Get information about the current user who sent the message.",
			parameters=genai.types.Schema(
				type="object",
				properties={},
				required=[]
			)
		),
		"read"
	)

	register_tool(
		"get_weather",
		get_weather_tool,
		genai.types.FunctionDeclaration(
			name="get_weather",
			description="Get current weather information for a location.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"location": genai.types.Schema(
						type="string",
						description="City name or location to get weather for."
					)
				},
				required=["location"]
			)
		),
		"read"
	)
