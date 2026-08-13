# Insyn Helper - AI Discord Assistant

Insyn Helper is an AI-powered Discord server assistant that allows authorized users to interact with Discord naturally through an AI interface.

## Features

- Natural language Discord server management
- AI-powered command interpretation
- Multiple tool execution in a single request
- Comprehensive moderation, channel, role, and permission management
- Audit log queries
- Weather information
- Secure authorization system

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
- DISCORD_TOKEN: Your Discord bot token
- GEMINI_API_KEY: Your Google Gemini API key
- DISCORD_APPLICATION_ID: Your Discord application ID
- ALLOWED_USER_ID: Discord user ID authorized to control the bot
- GEMINI_MODEL: Gemini model to use (default: gemini-2.5-flash)

3. Run the bot:
```bash
python src/main.py
```

## Usage

Mention the bot in Discord to interact:

```
@HelperBot ban @user for being mean
@HelperBot what's the weather in Miami?
@HelperBot check the audit log for role changes
@HelperBot create a channel called helperbothelpsthepoor
@HelperBot remove @user's access to #media
@HelperBot ban @user and tell me the weather
```

## Architecture

The bot uses a secure tool-based architecture:
- User → Discord → Insyn Helper → Gemini → Explicit Tool → Validation → Discord API
- Gemini selects tools, Insyn Helper validates and executes
- No arbitrary Discord API access through AI
- Application-level security layer

## Security

- Only authorized users can invoke AI functionality
- Tool execution requires application-level validation
- Discord permission and role hierarchy checks
- Credentials stored in environment variables
- Comprehensive logging of all tool requests
