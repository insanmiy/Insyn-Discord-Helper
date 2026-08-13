import discord
from typing import Dict, Any, Optional
from src.tools.registry import register_tool
from google import genai


async def get_channel_permissions(context: Dict[str, Any], channel_id: str) -> Dict[str, Any]:
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

		permissions_list = []

		for role in guild.roles:
			overwrite = channel.overwrites_for(role)
			if overwrite.is_empty():
				continue

			permissions_list.append({
				"type": "role",
				"id": str(role.id),
				"name": role.name,
				"allow": str(overwrite.allow),
				"deny": str(overwrite.deny)
			})

		for member in guild.members:
			overwrite = channel.overwrites_for(member)
			if overwrite.is_empty():
				continue

			permissions_list.append({
				"type": "member",
				"id": str(member.id),
				"name": member.display_name,
				"allow": str(overwrite.allow),
				"deny": str(overwrite.deny)
			})

		return {
			"success": True,
			"channel_id": str(channel_id),
			"channel_name": channel.name,
			"permissions": permissions_list
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Bot lacks permission to view channel permissions."
		}
	except discord.HTTPException as error:
		return {
			"success": False,
			"error": str(error)
		}


async def set_channel_permission(context: Dict[str, Any], channel_id: str, target_type: str, target_id: str, permission: str, value: bool) -> Dict[str, Any]:
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

		if target_type == "role":
			target = guild.get_role(int(target_id))
			if target is None:
				return {
					"success": False,
					"error": "Role not found."
				}
		elif target_type == "member":
			target = guild.get_member(int(target_id))
			if target is None:
				return {
					"success": False,
					"error": "Member not found."
				}
		else:
			return {
				"success": False,
				"error": "Invalid target type. Must be 'role' or 'member'."
			}

		overwrite = channel.overwrites_for(target)

		if hasattr(discord.Permissions, permission):
			setattr(overwrite, permission, value)
		else:
			return {
				"success": False,
				"error": f"Invalid permission: {permission}"
			}

		await channel.set_permissions(target, overwrite=overwrite, reason="Permission changed by Insyn Helper")

		return {
			"success": True,
			"channel_id": str(channel_id),
			"channel_name": channel.name,
			"target_type": target_type,
			"target_id": str(target_id),
			"permission": permission,
			"value": value
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Bot lacks permission to edit channel permissions."
		}
	except discord.HTTPException as error:
		return {
			"success": False,
			"error": str(error)
		}


async def remove_channel_permission(context: Dict[str, Any], channel_id: str, target_type: str, target_id: str) -> Dict[str, Any]:
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

		if target_type == "role":
			target = guild.get_role(int(target_id))
			if target is None:
				return {
					"success": False,
					"error": "Role not found."
				}
		elif target_type == "member":
			target = guild.get_member(int(target_id))
			if target is None:
				return {
					"success": False,
					"error": "Member not found."
				}
		else:
			return {
				"success": False,
				"error": "Invalid target type. Must be 'role' or 'member'."
			}

		await channel.set_permissions(target, overwrite=None, reason="Permission removed by Insyn Helper")

		return {
			"success": True,
			"channel_id": str(channel_id),
			"channel_name": channel.name,
			"target_type": target_type,
			"target_id": str(target_id)
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Bot lacks permission to edit channel permissions."
		}
	except discord.HTTPException as error:
		return {
			"success": False,
			"error": str(error)
		}


async def reset_channel_permissions(context: Dict[str, Any], channel_id: str) -> Dict[str, Any]:
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

		for overwrite in channel.overwrites:
			await channel.set_permissions(overwrite.target, overwrite=None, reason="Permissions reset by Insyn Helper")

		return {
			"success": True,
			"channel_id": str(channel_id),
			"channel_name": channel.name
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Bot lacks permission to edit channel permissions."
		}
	except discord.HTTPException as error:
		return {
			"success": False,
			"error": str(error)
		}


def register_permission_tools():
	register_tool(
		"get_channel_permissions",
		get_channel_permissions,
		genai.types.FunctionDeclaration(
			name="get_channel_permissions",
			description="Get permission overwrites for a specific channel.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"channel_id": genai.types.Schema(
						type="string",
						description="Discord ID of the channel."
					)
				},
				required=["channel_id"]
			)
		),
		"permissions"
	)

	register_tool(
		"set_channel_permission",
		set_channel_permission,
		genai.types.FunctionDeclaration(
			name="set_channel_permission",
			description="Set a specific permission for a role or member on a channel.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"channel_id": genai.types.Schema(
						type="string",
						description="Discord ID of the channel."
					),
					"target_type": genai.types.Schema(
						type="string",
						description="Type of target ('role' or 'member')."
					),
					"target_id": genai.types.Schema(
						type="string",
						description="Discord ID of the role or member."
					),
					"permission": genai.types.Schema(
						type="string",
						description="Permission name (e.g., 'view_channel', 'send_messages', 'connect')."
					),
					"value": genai.types.Schema(
						type="boolean",
						description="True to allow, False to deny."
					)
				},
				required=["channel_id", "target_type", "target_id", "permission", "value"]
			)
		),
		"permissions"
	)

	register_tool(
		"remove_channel_permission",
		remove_channel_permission,
		genai.types.FunctionDeclaration(
			name="remove_channel_permission",
			description="Remove permission overwrites for a role or member on a channel.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"channel_id": genai.types.Schema(
						type="string",
						description="Discord ID of the channel."
					),
					"target_type": genai.types.Schema(
						type="string",
						description="Type of target ('role' or 'member')."
					),
					"target_id": genai.types.Schema(
						type="string",
						description="Discord ID of the role or member."
					)
				},
				required=["channel_id", "target_type", "target_id"]
			)
		),
		"permissions"
	)

	register_tool(
		"reset_channel_permissions",
		reset_channel_permissions,
		genai.types.FunctionDeclaration(
			name="reset_channel_permissions",
			description="Reset all permission overwrites for a channel to default.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"channel_id": genai.types.Schema(
						type="string",
						description="Discord ID of the channel."
					)
				},
				required=["channel_id"]
			)
		),
		"permissions"
	)
