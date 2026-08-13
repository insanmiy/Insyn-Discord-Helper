import discord
from typing import Dict, Any, Optional
from src.tools.registry import register_tool
from google import genai


async def create_role(context: Dict[str, Any], name: str, color: Optional[str] = None, hoist: bool = False, mentionable: bool = False) -> Dict[str, Any]:
	guild = context.get("_guild")

	if not guild:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	try:
		role_color = discord.Color.from_str(color) if color else discord.Color.default()

		role = await guild.create_role(
			name=name,
			color=role_color,
			hoist=hoist,
			mentionable=mentionable,
			reason="Created by Insyn Helper"
		)

		return {
			"success": True,
			"role_id": str(role.id),
			"role_name": role.name,
			"color": str(role.color),
			"hoist": role.hoist,
			"mentionable": role.mentionable
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Bot lacks permission to create roles."
		}
	except discord.HTTPException as error:
		return {
			"success": False,
			"error": str(error)
		}


async def delete_role(context: Dict[str, Any], role_id: str) -> Dict[str, Any]:
	guild = context.get("_guild")

	if not guild:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	try:
		role = guild.get_role(int(role_id))

		if role is None:
			return {
				"success": False,
				"error": "Role not found."
			}

		await role.delete(reason="Deleted by Insyn Helper")

		return {
			"success": True,
			"role_id": str(role_id),
			"role_name": role.name
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Bot lacks permission to delete this role."
		}
	except discord.HTTPException as error:
		return {
			"success": False,
			"error": str(error)
		}


async def rename_role(context: Dict[str, Any], role_id: str, new_name: str) -> Dict[str, Any]:
	guild = context.get("_guild")

	if not guild:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	try:
		role = guild.get_role(int(role_id))

		if role is None:
			return {
				"success": False,
				"error": "Role not found."
			}

		old_name = role.name
		await role.edit(name=new_name, reason="Renamed by Insyn Helper")

		return {
			"success": True,
			"role_id": str(role_id),
			"old_name": old_name,
			"new_name": new_name
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Bot lacks permission to rename this role."
		}
	except discord.HTTPException as error:
		return {
			"success": False,
			"error": str(error)
		}


async def edit_role(context: Dict[str, Any], role_id: str, color: Optional[str] = None, hoist: Optional[bool] = None, mentionable: Optional[bool] = None) -> Dict[str, Any]:
	guild = context.get("_guild")

	if not guild:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	try:
		role = guild.get_role(int(role_id))

		if role is None:
			return {
				"success": False,
				"error": "Role not found."
			}

		kwargs = {"reason": "Edited by Insyn Helper"}
		if color:
			kwargs["color"] = discord.Color.from_str(color)
		if hoist is not None:
			kwargs["hoist"] = hoist
		if mentionable is not None:
			kwargs["mentionable"] = mentionable

		await role.edit(**kwargs)

		return {
			"success": True,
			"role_id": str(role_id),
			"role_name": role.name
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Bot lacks permission to edit this role."
		}
	except discord.HTTPException as error:
		return {
			"success": False,
			"error": str(error)
		}


async def add_role_to_member(context: Dict[str, Any], user_id: str, role_id: str) -> Dict[str, Any]:
	guild = context.get("_guild")

	if not guild:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	try:
		member = guild.get_member(int(user_id))
		role = guild.get_role(int(role_id))

		if member is None:
			return {
				"success": False,
				"error": "Member not found."
			}

		if role is None:
			return {
				"success": False,
				"error": "Role not found."
			}

		await member.add_roles(role, reason="Role added by Insyn Helper")

		return {
			"success": True,
			"user_id": str(user_id),
			"role_id": str(role_id),
			"role_name": role.name
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Bot lacks permission to add this role due to permissions or role hierarchy."
		}
	except discord.HTTPException as error:
		return {
			"success": False,
			"error": str(error)
		}


async def remove_role_from_member(context: Dict[str, Any], user_id: str, role_id: str) -> Dict[str, Any]:
	guild = context.get("_guild")

	if not guild:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	try:
		member = guild.get_member(int(user_id))
		role = guild.get_role(int(role_id))

		if member is None:
			return {
				"success": False,
				"error": "Member not found."
			}

		if role is None:
			return {
				"success": False,
				"error": "Role not found."
			}

		await member.remove_roles(role, reason="Role removed by Insyn Helper")

		return {
			"success": True,
			"user_id": str(user_id),
			"role_id": str(role_id),
			"role_name": role.name
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Bot lacks permission to remove this role due to permissions or role hierarchy."
		}
	except discord.HTTPException as error:
		return {
			"success": False,
			"error": str(error)
		}


async def set_role_permissions(context: Dict[str, Any], role_id: str, permissions: Dict[str, bool]) -> Dict[str, Any]:
	guild = context.get("_guild")

	if not guild:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	try:
		role = guild.get_role(int(role_id))

		if role is None:
			return {
				"success": False,
				"error": "Role not found."
			}

		permission_update = discord.Permissions()
		for perm_name, perm_value in permissions.items():
			if hasattr(permission_update, perm_name):
				setattr(permission_update, perm_name, perm_value)

		await role.edit(permissions=permission_update, reason="Permissions edited by Insyn Helper")

		return {
			"success": True,
			"role_id": str(role_id),
			"role_name": role.name
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Bot lacks permission to edit this role's permissions."
		}
	except discord.HTTPException as error:
		return {
			"success": False,
			"error": str(error)
		}


def register_role_tools():
	register_tool(
		"create_role",
		create_role,
		genai.types.FunctionDeclaration(
			name="create_role",
			description="Create a new role in the server.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"name": genai.types.Schema(
						type="string",
						description="Name for the new role."
					),
					"color": genai.types.Schema(
						type="string",
						description="Optional color for the role in hex format (e.g., '#ff0000')."
					),
					"hoist": genai.types.Schema(
						type="boolean",
						description="Whether the role should be displayed separately in the member list. Default is false."
					),
					"mentionable": genai.types.Schema(
						type="boolean",
						description="Whether the role should be mentionable. Default is false."
					)
				},
				required=["name"]
			)
		),
		"server_management"
	)

	register_tool(
		"delete_role",
		delete_role,
		genai.types.FunctionDeclaration(
			name="delete_role",
			description="Delete a role from the server.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"role_id": genai.types.Schema(
						type="string",
						description="Discord ID of the role to delete."
					)
				},
				required=["role_id"]
			)
		),
		"server_management"
	)

	register_tool(
		"rename_role",
		rename_role,
		genai.types.FunctionDeclaration(
			name="rename_role",
			description="Rename a role in the server.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"role_id": genai.types.Schema(
						type="string",
						description="Discord ID of the role to rename."
					),
					"new_name": genai.types.Schema(
						type="string",
						description="New name for the role."
					)
				},
				required=["role_id", "new_name"]
			)
		),
		"server_management"
	)

	register_tool(
		"edit_role",
		edit_role,
		genai.types.FunctionDeclaration(
			name="edit_role",
			description="Edit properties of a role.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"role_id": genai.types.Schema(
						type="string",
						description="Discord ID of the role to edit."
					),
					"color": genai.types.Schema(
						type="string",
						description="Optional new color for the role in hex format."
					),
					"hoist": genai.types.Schema(
						type="boolean",
						description="Optional new hoist status."
					),
					"mentionable": genai.types.Schema(
						type="boolean",
						description="Optional new mentionable status."
					)
				},
				required=["role_id"]
			)
		),
		"server_management"
	)

	register_tool(
		"add_role_to_member",
		add_role_to_member,
		genai.types.FunctionDeclaration(
			name="add_role_to_member",
			description="Add a role to a member.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"user_id": genai.types.Schema(
						type="string",
						description="Discord ID of the member."
					),
					"role_id": genai.types.Schema(
						type="string",
						description="Discord ID of the role to add."
					)
				},
				required=["user_id", "role_id"]
			)
		),
		"permissions"
	)

	register_tool(
		"remove_role_from_member",
		remove_role_from_member,
		genai.types.FunctionDeclaration(
			name="remove_role_from_member",
			description="Remove a role from a member.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"user_id": genai.types.Schema(
						type="string",
						description="Discord ID of the member."
					),
					"role_id": genai.types.Schema(
						type="string",
						description="Discord ID of the role to remove."
					)
				},
				required=["user_id", "role_id"]
			)
		),
		"permissions"
	)

	register_tool(
		"set_role_permissions",
		set_role_permissions,
		genai.types.FunctionDeclaration(
			name="set_role_permissions",
			description="Set permissions for a role. Permissions should be a dictionary of permission names to boolean values.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"role_id": genai.types.Schema(
						type="string",
						description="Discord ID of the role."
					),
					"permissions": genai.types.Schema(
						type="object",
						description="Dictionary of permission names to boolean values (e.g., {'administrator': false, 'send_messages': true})."
					)
				},
				required=["role_id", "permissions"]
			)
		),
		"permissions"
	)
