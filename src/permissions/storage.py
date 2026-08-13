import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional


STORAGE_DIR = Path("data")
AUTH_FILE = STORAGE_DIR / "authorizations.json"


def ensure_storage_dir():
	STORAGE_DIR.mkdir(exist_ok=True)


def load_authorizations() -> Dict[str, Any]:
	ensure_storage_dir()

	if not AUTH_FILE.exists():
		return {}

	with open(AUTH_FILE, 'r') as f:
		return json.load(f)


def save_authorizations(auth_data: Dict[str, Any]):
	ensure_storage_dir()

	with open(AUTH_FILE, 'w') as f:
		json.dump(auth_data, f, indent=2)


def get_server_config(guild_id: str) -> Dict[str, Any]:
	auth_data = load_authorizations()
	return auth_data.get(guild_id, {
		"authorized_roles": [],
		"authorized_users": [],
		"allowed_channels": []
	})


def set_server_config(guild_id: str, config: Dict[str, Any]):
	auth_data = load_authorizations()
	auth_data[guild_id] = config
	save_authorizations(auth_data)


def add_authorized_role(guild_id: str, role_id: str):
	config = get_server_config(guild_id)
	if role_id not in config["authorized_roles"]:
		config["authorized_roles"].append(role_id)
		set_server_config(guild_id, config)


def remove_authorized_role(guild_id: str, role_id: str):
	config = get_server_config(guild_id)
	if role_id in config["authorized_roles"]:
		config["authorized_roles"].remove(role_id)
		set_server_config(guild_id, config)


def add_authorized_user(guild_id: str, user_id: str):
	config = get_server_config(guild_id)
	if user_id not in config["authorized_users"]:
		config["authorized_users"].append(user_id)
		set_server_config(guild_id, config)


def remove_authorized_user(guild_id: str, user_id: str):
	config = get_server_config(guild_id)
	if user_id in config["authorized_users"]:
		config["authorized_users"].remove(user_id)
		set_server_config(guild_id, config)


def add_allowed_channel(guild_id: str, channel_id: str):
	config = get_server_config(guild_id)
	if channel_id not in config["allowed_channels"]:
		config["allowed_channels"].append(channel_id)
		set_server_config(guild_id, config)


def remove_allowed_channel(guild_id: str, channel_id: str):
	config = get_server_config(guild_id)
	if channel_id in config["allowed_channels"]:
		config["allowed_channels"].remove(channel_id)
		set_server_config(guild_id, config)


def is_authorized(guild_id: str, user_id: str, role_ids: List[str], channel_id: str) -> bool:
	config = get_server_config(guild_id)

	if not config["allowed_channels"]:
		channel_allowed = True
	else:
		channel_allowed = channel_id in config["allowed_channels"]

	if not channel_allowed:
		return False

	if user_id in config["authorized_users"]:
		return True

	for role_id in role_ids:
		if role_id in config["authorized_roles"]:
			return True

	return False
