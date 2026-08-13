import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.bot.client import create_bot
from src.bot.events import setup_events
from src.config.settings import settings
from src.tools.information import register_information_tools
from src.tools.audit import register_audit_tools
from src.tools.moderation import register_moderation_tools
from src.tools.channels import register_channel_tools
from src.tools.roles import register_role_tools
from src.tools.permissions import register_permission_tools
from src.tools.messages import register_message_tools
from src.tools.voice import register_voice_tools
from src.tools.code_editor import register_code_editor_tools
from src.services.logging import setup_logging


async def main():
	setup_logging()
	register_information_tools()
	register_audit_tools()
	register_moderation_tools()
	register_channel_tools()
	register_role_tools()
	register_permission_tools()
	register_message_tools()
	register_voice_tools()
	register_code_editor_tools()
	bot = create_bot()
	await setup_events(bot)

	try:
		await bot.start(settings.DISCORD_TOKEN)
	except KeyboardInterrupt:
		await bot.close()
	except Exception as e:
		print(f"Error starting bot: {e}")
		await bot.close()


if __name__ == "__main__":
	asyncio.run(main())
