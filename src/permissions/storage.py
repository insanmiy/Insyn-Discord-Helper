import json
import sqlite3
from pathlib import Path
from typing import Dict, Any, List

from src.config.settings import settings


DB_PATH = Path(settings.DATABASE_PATH)
LEGACY_AUTH_FILE = Path("data/authorizations.json")


def _connect() -> sqlite3.Connection:
	DB_PATH.parent.mkdir(parents=True, exist_ok=True)
	connection = sqlite3.connect(DB_PATH, timeout=10)
	connection.row_factory = sqlite3.Row
	connection.execute("PRAGMA journal_mode=WAL")
	return connection


def ensure_database() -> None:
	with _connect() as connection:
		connection.executescript("""
			CREATE TABLE IF NOT EXISTS authorized_users (
				guild_id TEXT NOT NULL,
				user_id TEXT NOT NULL,
				PRIMARY KEY (guild_id, user_id)
			);
			CREATE TABLE IF NOT EXISTS authorized_roles (
				guild_id TEXT NOT NULL,
				role_id TEXT NOT NULL,
				PRIMARY KEY (guild_id, role_id)
			);
			CREATE TABLE IF NOT EXISTS allowed_channels (
				guild_id TEXT NOT NULL,
				channel_id TEXT NOT NULL,
				PRIMARY KEY (guild_id, channel_id)
			);
			CREATE TABLE IF NOT EXISTS public_channels (
				guild_id TEXT NOT NULL,
				channel_id TEXT NOT NULL,
				PRIMARY KEY (guild_id, channel_id)
			);
		""")
	_migrate_legacy_auth()


def _migrate_legacy_auth() -> None:
	if not LEGACY_AUTH_FILE.exists():
		return
	with _connect() as connection:
		try:
			legacy = json.loads(LEGACY_AUTH_FILE.read_text(encoding="utf-8"))
		except (OSError, json.JSONDecodeError):
			return
		for guild_id, config in legacy.items():
			for user_id in config.get("authorized_users", []):
				connection.execute("INSERT OR IGNORE INTO authorized_users VALUES (?, ?)", (guild_id, str(user_id)))
			for role_id in config.get("authorized_roles", []):
				connection.execute("INSERT OR IGNORE INTO authorized_roles VALUES (?, ?)", (guild_id, str(role_id)))
			for channel_id in config.get("allowed_channels", []):
				connection.execute("INSERT OR IGNORE INTO allowed_channels VALUES (?, ?)", (guild_id, str(channel_id)))
		# Rename only after a successful import. The SQLite rows remain the source of truth.
		backup = LEGACY_AUTH_FILE.with_suffix(".json.migrated")
		try:
			LEGACY_AUTH_FILE.replace(backup)
		except OSError:
			pass


def _ensure() -> None:
	ensure_database()


def get_server_config(guild_id: str) -> Dict[str, Any]:
	_ensure()
	with _connect() as connection:
		users = [row[0] for row in connection.execute("SELECT user_id FROM authorized_users WHERE guild_id = ?", (guild_id,))]
		roles = [row[0] for row in connection.execute("SELECT role_id FROM authorized_roles WHERE guild_id = ?", (guild_id,))]
		channels = [row[0] for row in connection.execute("SELECT channel_id FROM allowed_channels WHERE guild_id = ?", (guild_id,))]
		public = [row[0] for row in connection.execute("SELECT channel_id FROM public_channels WHERE guild_id = ?", (guild_id,))]
	return {"authorized_roles": roles, "authorized_users": users, "allowed_channels": channels, "public_channels": public}


def add_authorized_role(guild_id: str, role_id: str):
	_ensure()
	with _connect() as connection:
		connection.execute("INSERT OR IGNORE INTO authorized_roles VALUES (?, ?)", (guild_id, role_id))


def remove_authorized_role(guild_id: str, role_id: str):
	_ensure()
	with _connect() as connection:
		connection.execute("DELETE FROM authorized_roles WHERE guild_id = ? AND role_id = ?", (guild_id, role_id))


def add_authorized_user(guild_id: str, user_id: str):
	_ensure()
	with _connect() as connection:
		connection.execute("INSERT OR IGNORE INTO authorized_users VALUES (?, ?)", (guild_id, user_id))


def remove_authorized_user(guild_id: str, user_id: str):
	_ensure()
	with _connect() as connection:
		connection.execute("DELETE FROM authorized_users WHERE guild_id = ? AND user_id = ?", (guild_id, user_id))


def add_allowed_channel(guild_id: str, channel_id: str):
	_ensure()
	with _connect() as connection:
		connection.execute("INSERT OR IGNORE INTO allowed_channels VALUES (?, ?)", (guild_id, channel_id))


def remove_allowed_channel(guild_id: str, channel_id: str):
	_ensure()
	with _connect() as connection:
		connection.execute("DELETE FROM allowed_channels WHERE guild_id = ? AND channel_id = ?", (guild_id, channel_id))


def add_public_channel(guild_id: str, channel_id: str):
	_ensure()
	with _connect() as connection:
		connection.execute("INSERT OR IGNORE INTO public_channels VALUES (?, ?)", (guild_id, channel_id))


def remove_public_channel(guild_id: str, channel_id: str):
	_ensure()
	with _connect() as connection:
		connection.execute("DELETE FROM public_channels WHERE guild_id = ? AND channel_id = ?", (guild_id, channel_id))


def is_authorized(guild_id: str, user_id: str, role_ids: List[str], channel_id: str) -> bool:
	config = get_server_config(guild_id)
	if config["allowed_channels"] and channel_id not in config["allowed_channels"]:
		return False
	if channel_id in config["public_channels"]:
		return True
	return user_id in config["authorized_users"] or bool(set(role_ids) & set(config["authorized_roles"]))
