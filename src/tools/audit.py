import discord
from typing import Dict, Any, Optional
from src.tools.registry import register_tool
from google import genai


async def get_audit_log(context: Dict[str, Any], action: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
	guild = context.get("_guild")

	if not guild:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	try:
		entries = []

		async for entry in guild.audit_logs(limit=limit, action=discord.AuditLogAction.__dict__.get(action) if action else None):
			entries.append({
				"action": entry.action.name,
				"user": str(entry.user),
				"user_id": str(entry.user.id) if entry.user else None,
				"target": str(entry.target) if entry.target else None,
				"target_id": str(entry.target.id) if entry.target and hasattr(entry.target, 'id') else None,
				"reason": entry.reason,
				"created_at": entry.created_at.isoformat()
			})

		return {
			"success": True,
			"data": {
				"entries": entries,
				"total_count": len(entries)
			}
		}
	except discord.Forbidden:
		return {
			"success": False,
			"error": "Bot lacks permission to view audit logs."
		}
	except Exception as e:
		return {
			"success": False,
			"error": str(e)
		}


async def get_recent_role_changes(context: Dict[str, Any], limit: int = 20) -> Dict[str, Any]:
	return await get_audit_log(context, action="role_update", limit=limit)


async def get_recent_channel_changes(context: Dict[str, Any], limit: int = 20) -> Dict[str, Any]:
	return await get_audit_log(context, action="channel_update", limit=limit)


async def get_recent_permission_changes(context: Dict[str, Any], limit: int = 20) -> Dict[str, Any]:
	return await get_audit_log(context, action="overwrite_update", limit=limit)


async def get_recent_bans(context: Dict[str, Any], limit: int = 20) -> Dict[str, Any]:
	return await get_audit_log(context, action="ban", limit=limit)


async def get_recent_kicks(context: Dict[str, Any], limit: int = 20) -> Dict[str, Any]:
	return await get_audit_log(context, action="kick", limit=limit)


def register_audit_tools():
	register_tool(
		"get_audit_log",
		get_audit_log,
		genai.types.FunctionDeclaration(
			name="get_audit_log",
			description="Get entries from the server audit log. Can filter by action type.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"action": genai.types.Schema(
						type="string",
						description="Optional action type to filter by (e.g., 'ban', 'kick', 'role_update', 'channel_update')."
					),
					"limit": genai.types.Schema(
						type="integer",
						description="Maximum number of entries to return. Default is 20."
					)
				},
				required=[]
			)
		),
		"audit"
	)

	register_tool(
		"get_recent_role_changes",
		get_recent_role_changes,
		genai.types.FunctionDeclaration(
			name="get_recent_role_changes",
			description="Get recent role changes from the audit log.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"limit": genai.types.Schema(
						type="integer",
						description="Maximum number of entries to return. Default is 20."
					)
				},
				required=[]
			)
		),
		"audit"
	)

	register_tool(
		"get_recent_channel_changes",
		get_recent_channel_changes,
		genai.types.FunctionDeclaration(
			name="get_recent_channel_changes",
			description="Get recent channel changes from the audit log.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"limit": genai.types.Schema(
						type="integer",
						description="Maximum number of entries to return. Default is 20."
					)
				},
				required=[]
			)
		),
		"audit"
	)

	register_tool(
		"get_recent_permission_changes",
		get_recent_permission_changes,
		genai.types.FunctionDeclaration(
			name="get_recent_permission_changes",
			description="Get recent permission changes from the audit log.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"limit": genai.types.Schema(
						type="integer",
						description="Maximum number of entries to return. Default is 20."
					)
				},
				required=[]
			)
		),
		"audit"
	)

	register_tool(
		"get_recent_bans",
		get_recent_bans,
		genai.types.FunctionDeclaration(
			name="get_recent_bans",
			description="Get recent bans from the audit log.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"limit": genai.types.Schema(
						type="integer",
						description="Maximum number of entries to return. Default is 20."
					)
				},
				required=[]
			)
		),
		"audit"
	)

	register_tool(
		"get_recent_kicks",
		get_recent_kicks,
		genai.types.FunctionDeclaration(
			name="get_recent_kicks",
			description="Get recent kicks from the audit log.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"limit": genai.types.Schema(
						type="integer",
						description="Maximum number of entries to return. Default is 20."
					)
				},
				required=[]
			)
		),
		"audit"
	)
