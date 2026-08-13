import discord
from discord.ext import commands
from src.config.settings import settings


class InsynBot(commands.Bot):
	def __init__(self):
		intents = discord.Intents.default()
		intents.message_content = True
		intents.guilds = True
		intents.members = True
		intents.moderation = True
		intents.reactions = True

		super().__init__(
			command_prefix="!",
			intents=intents,
			application_id=settings.DISCORD_APPLICATION_ID
		)


def create_bot() -> InsynBot:
	return InsynBot()
