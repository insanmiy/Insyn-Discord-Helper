import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
	DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
	GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
	DISCORD_APPLICATION_ID = os.getenv("DISCORD_APPLICATION_ID")
	
	allowed_user_id = os.getenv("ALLOWED_USER_ID", "0")
	ALLOWED_USER_ID = int(allowed_user_id) if allowed_user_id else 0
	
	GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

	MAX_TOOL_ROUNDS = 10
	TOOL_TIMEOUT_SECONDS = 15


settings = Settings()
