from src.permissions.storage import is_authorized


def is_allowed_user(guild_id: str, user_id: str, role_ids: list, channel_id: str) -> bool:
	return is_authorized(guild_id, user_id, role_ids, channel_id)


def is_server_owner(user_id: str, owner_id: str) -> bool:
	return user_id == owner_id

