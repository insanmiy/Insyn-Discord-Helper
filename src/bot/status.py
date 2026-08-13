import discord
from src.config.settings import settings


def get_bot_activity() -> discord.Activity:
	status_type = settings.BOT_STATUS_TYPE.lower()
	message = settings.BOT_STATUS_MESSAGE

	activity_types = {
		"playing": discord.ActivityType.playing,
		"watching": discord.ActivityType.watching,
		"listening": discord.ActivityType.listening,
		"competing": discord.ActivityType.competing,
	}

	activity_type = activity_types.get(status_type, discord.ActivityType.watching)
	return discord.Activity(type=activity_type, name=message)
