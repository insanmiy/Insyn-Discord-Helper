import json
from pathlib import Path
from typing import Dict, Any, Optional


STORAGE_DIR = Path("data")
REACTION_ROLES_FILE = STORAGE_DIR / "reaction_roles.json"


def ensure_storage_dir():
	STORAGE_DIR.mkdir(exist_ok=True)


def load_reaction_roles() -> Dict[str, Any]:
	ensure_storage_dir()

	if not REACTION_ROLES_FILE.exists():
		return {}

	with open(REACTION_ROLES_FILE, "r") as f:
		return json.load(f)


def save_reaction_roles(data: Dict[str, Any]):
	ensure_storage_dir()

	with open(REACTION_ROLES_FILE, "w") as f:
		json.dump(data, f, indent=2)


def get_message_config(guild_id: str, message_id: str) -> Optional[Dict[str, Any]]:
	return load_reaction_roles().get(guild_id, {}).get(message_id)


def set_message_config(guild_id: str, message_id: str, config: Dict[str, Any]):
	data = load_reaction_roles()
	data.setdefault(guild_id, {})[message_id] = config
	save_reaction_roles(data)


def remove_message_config(guild_id: str, message_id: str):
	data = load_reaction_roles()
	guild_data = data.get(guild_id, {})
	if message_id in guild_data:
		del guild_data[message_id]
		if guild_data:
			data[guild_id] = guild_data
		elif guild_id in data:
			del data[guild_id]
		save_reaction_roles(data)


def list_guild_reaction_roles(guild_id: str) -> Dict[str, Any]:
	return load_reaction_roles().get(guild_id, {})


def emoji_key(emoji) -> str:
	if getattr(emoji, "id", None):
		return f"{emoji.name}:{emoji.id}"
	return str(emoji)
