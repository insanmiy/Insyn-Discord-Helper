from typing import Dict, Callable, Any

TOOLS: Dict[str, Callable] = {}

TOOL_DECLARATIONS: Dict[str, Any] = {}

TOOL_PERMISSIONS: Dict[str, str] = {
	"get_audit_log": "audit",
	"ban_user": "moderation",
	"delete_channel": "server_management",
	"set_channel_permission": "permissions"
}


def register_tool(name: str, func: Callable, declaration: Dict[str, Any], permission: str = "read"):
	TOOLS[name] = func
	TOOL_DECLARATIONS[name] = declaration
	TOOL_PERMISSIONS[name] = permission


def get_tool(name: str) -> Callable:
	return TOOLS.get(name)


def get_tool_declaration(name: str) -> Dict[str, Any]:
	return TOOL_DECLARATIONS.get(name)


def get_all_tool_declarations() -> list:
	return list(TOOL_DECLARATIONS.values())


def get_tool_permission(name: str) -> str:
	return TOOL_PERMISSIONS.get(name, "read")
