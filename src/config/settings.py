import os
import xml.etree.ElementTree as ET
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

CONFIG_FILE = Path("bot_config.xml")


def load_bot_config():
	if CONFIG_FILE.exists():
		tree = ET.parse(CONFIG_FILE)
		root = tree.getroot()

		def get_text(element, tag, default=""):
			el = element.find(tag)
			return el.text if el is not None and el.text else default

		def get_bool(element, tag, default=False):
			el = element.find(tag)
			if el is not None and el.text:
				return el.text.lower() in ("true", "1", "yes")
			return default

		def get_int(element, tag, default=0):
			el = element.find(tag)
			return int(el.text) if el is not None and el.text else default

		def get_float(element, tag, default=0.0):
			el = element.find(tag)
			return float(el.text) if el is not None and el.text else default

		bot_status = root.find("bot_status")
		ai_settings = root.find("ai_settings")
		response_settings = root.find("response_settings")
		logging_settings = root.find("logging")
		permissions_settings = root.find("permissions")

		return {
			"bot_name": get_text(root, "bot_name", "Insyn Helper"),
			"bot_description": get_text(root, "bot_description", "AI powered Discord server assistant"),
			"bot_status": {
				"type": get_text(bot_status, "type", "watching") if bot_status else "watching",
				"message": get_text(bot_status, "message", "for mentions") if bot_status else "for mentions"
			} if bot_status else {"type": "watching", "message": "for mentions"},
			"ai_settings": {
				"temperature": get_float(ai_settings, "temperature", 0.7) if ai_settings else 0.7,
				"max_output_tokens": get_int(ai_settings, "max_output_tokens", 2048) if ai_settings else 2048,
				"max_tool_rounds": get_int(ai_settings, "max_tool_rounds", 5) if ai_settings else 5,
				"tool_timeout_seconds": get_int(ai_settings, "tool_timeout_seconds", 30) if ai_settings else 30
			} if ai_settings else {"temperature": 0.7, "max_output_tokens": 2048, "max_tool_rounds": 5, "tool_timeout_seconds": 30},
			"response_settings": {
				"use_embeds": get_bool(response_settings, "use_embeds", True) if response_settings else True,
				"embed_color": get_text(response_settings, "embed_color", "#5865F2") if response_settings else "#5865F2",
				"show_tool_execution": get_bool(response_settings, "show_tool_execution", False) if response_settings else False,
				"split_long_messages": get_bool(response_settings, "split_long_messages", True) if response_settings else True
			} if response_settings else {"use_embeds": True, "embed_color": "#5865F2", "show_tool_execution": False, "split_long_messages": True},
			"logging": {
				"enabled": get_bool(logging_settings, "enabled", True) if logging_settings else True,
				"log_file": get_text(logging_settings, "log_file", "logs/bot.log") if logging_settings else "logs/bot.log",
				"log_level": get_text(logging_settings, "log_level", "INFO") if logging_settings else "INFO",
				"log_tool_requests": get_bool(logging_settings, "log_tool_requests", True) if logging_settings else True,
				"log_tool_results": get_bool(logging_settings, "log_tool_results", True) if logging_settings else True
			} if logging_settings else {"enabled": True, "log_file": "logs/bot.log", "log_level": "INFO", "log_tool_requests": True, "log_tool_results": True},
			"permissions": {
				"default_allow_all_channels": get_bool(permissions_settings, "default_allow_all_channels", True) if permissions_settings else True,
				"require_owner_for_config": get_bool(permissions_settings, "require_owner_for_config", True) if permissions_settings else True
			} if permissions_settings else {"default_allow_all_channels": True, "require_owner_for_config": True}
		}

	return {
		"bot_name": "Insyn Helper",
		"bot_description": "AI powered Discord server assistant",
		"bot_status": {
			"type": "watching",
			"message": "for mentions"
		},
		"ai_settings": {
			"temperature": 0.7,
			"max_output_tokens": 2048,
			"max_tool_rounds": 5,
			"tool_timeout_seconds": 30
		},
		"response_settings": {
			"use_embeds": True,
			"embed_color": "#5865F2",
			"show_tool_execution": False,
			"split_long_messages": True
		},
		"logging": {
			"enabled": True,
			"log_file": "logs/bot.log",
			"log_level": "INFO",
			"log_tool_requests": True,
			"log_tool_results": True
		},
		"permissions": {
			"default_allow_all_channels": True,
			"require_owner_for_config": True
		}
	}


bot_config = load_bot_config()


class Settings:
	DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
	GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
	DISCORD_APPLICATION_ID = os.getenv("DISCORD_APPLICATION_ID")

	BOT_NAME = bot_config.get("bot_name", "Insyn Helper")
	BOT_DESCRIPTION = bot_config.get("bot_description", "AI powered Discord server assistant")

	BOT_STATUS_TYPE = bot_config.get("bot_status", {}).get("type", "watching")
	BOT_STATUS_MESSAGE = bot_config.get("bot_status", {}).get("message", "for mentions")

	GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

	# Comma-separated fallback models. Defaults chosen to try common Gemini variants.
	GEMINI_FALLBACK_MODELS = [m.strip() for m in os.getenv("GEMINI_FALLBACK_MODELS", "gemini-3.5-flash,gemini-3.1-flash-lite,gemini-3.6-flash").split(",") if m.strip()]

	ai_settings = bot_config.get("ai_settings", {})
	AI_TEMPERATURE = ai_settings.get("temperature", 0.7)
	AI_MAX_OUTPUT_TOKENS = ai_settings.get("max_output_tokens", 2048)
	MAX_TOOL_ROUNDS = ai_settings.get("max_tool_rounds", 5)
	TOOL_TIMEOUT_SECONDS = ai_settings.get("tool_timeout_seconds", 30)

	response_settings = bot_config.get("response_settings", {})
	USE_EMBEDS = response_settings.get("use_embeds", True)
	EMBED_COLOR = response_settings.get("embed_color", "#5865F2")
	SHOW_TOOL_EXECUTION = response_settings.get("show_tool_execution", False)
	SPLIT_LONG_MESSAGES = response_settings.get("split_long_messages", True)

	logging_settings = bot_config.get("logging", {})
	LOGGING_ENABLED = logging_settings.get("enabled", True)
	LOG_FILE = logging_settings.get("log_file", "logs/bot.log")
	LOG_LEVEL = logging_settings.get("log_level", "INFO")
	LOG_TOOL_REQUESTS = logging_settings.get("log_tool_requests", True)
	LOG_TOOL_RESULTS = logging_settings.get("log_tool_results", True)

	permissions = bot_config.get("permissions", {})
	DEFAULT_ALLOW_ALL_CHANNELS = permissions.get("default_allow_all_channels", True)
	REQUIRE_OWNER_FOR_CONFIG = permissions.get("require_owner_for_config", True)


settings = Settings()



