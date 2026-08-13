import asyncio
import logging
from typing import Dict, Any
from google import genai
from google.genai import types

from src.ai.client import create_gemini_client
from src.ai.prompts import SYSTEM_INSTRUCTION
from src.tools.registry import get_tool, get_all_tool_declarations
from src.config.settings import settings
from src.services.logging import log_tool_request, log_tool_result, log_ai_response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_ai_request(context: Dict[str, Any], user_message: str) -> str:
	client = create_gemini_client()

	tool_declarations = get_all_tool_declarations()

	context_str = format_context(context)

	full_message = f"""Context: {context_str}

User request: {user_message}"""

	round = 0

	while round < settings.MAX_TOOL_ROUNDS:
		try:
			models_to_try = [settings.GEMINI_MODEL] + getattr(settings, "GEMINI_FALLBACK_MODELS", [])
			response = None
			last_exc = None
			for model in models_to_try:
				try:
					response = client.models.generate_content(
						model=model,
						contents=full_message,
						config=types.GenerateContentConfig(
							system_instruction=SYSTEM_INSTRUCTION,
							tools=[types.Tool(function_declarations=tool_declarations)] if tool_declarations else None
						)
					)
					break
				except Exception as e:
					logger.warning(f"Model {model} failed: {e}")
					last_exc = e
			if response is None:
				if last_exc:
					raise last_exc
				else:
					return "I apologize, but I couldn't generate a response."

			if not response.candidates or not response.candidates[0].content:
				return "I apologize, but I couldn't generate a response."

			candidate = response.candidates[0]
			content = candidate.content

			if not content.parts:
				return "I apologize, but I couldn't generate a response."

			function_calls = []
			text_parts = []

			for part in content.parts:
				if hasattr(part, 'function_call') and part.function_call:
					function_calls.append(part.function_call)
				elif hasattr(part, 'text') and part.text:
					text_parts.append(part.text)

			if not function_calls:
				return "".join(text_parts) if text_parts else "I apologize, but I couldn't generate a response."

			logger.info(f"Round {round + 1}: Gemini requested {len(function_calls)} tool(s)")

			results = await execute_tool_calls(function_calls, context)

			full_message = build_message_with_results(full_message, results)

			round += 1

		except Exception as e:
			logger.error(f"Error in AI request round {round + 1}: {e}")
			return f"An error occurred while processing your request: {str(e)}"

	return "I apologize, but I couldn't complete your request after multiple attempts."


async def execute_tool_calls(function_calls, context: Dict[str, Any]) -> list:
	tasks = []

	for call in function_calls:
		task = execute_single_tool(call, context)
		tasks.append(task)

	results = await asyncio.gather(*tasks, return_exceptions=True)

	processed_results = []
	for i, result in enumerate(results):
		if isinstance(result, Exception):
			logger.error(f"Tool execution error: {result}")
			processed_results.append({
				"name": function_calls[i].name,
				"response": {
					"success": False,
					"error": str(result)
				}
			})
		else:
			processed_results.append(result)

	return processed_results


async def execute_single_tool(function_call, context: Dict[str, Any]) -> Dict[str, Any]:
	tool_name = function_call.name
	arguments = function_call.args

	user_id = context.get("user_id", "unknown")
	username = context.get("username", "unknown")

	log_tool_request(user_id, username, "AI tool request", tool_name, arguments)

	tool_func = get_tool(tool_name)

	if tool_func is None:
		logger.warning(f"Unknown tool requested: {tool_name}")
		result = {
			"success": False,
			"error": f"Unknown tool: {tool_name}"
		}
		log_tool_result(tool_name, result)
		return {
			"name": tool_name,
			"response": result
		}

	try:
		result = await asyncio.wait_for(
			tool_func(context, **arguments),
			timeout=settings.TOOL_TIMEOUT_SECONDS
		)
		log_tool_result(tool_name, result)
		return {
			"name": tool_name,
			"response": result
		}
	except asyncio.TimeoutError:
		logger.error(f"Tool {tool_name} timed out")
		result = {
			"success": False,
			"error": "Tool execution timed out"
		}
		log_tool_result(tool_name, result)
		return {
			"name": tool_name,
			"response": result
		}
	except Exception as e:
		logger.error(f"Tool {tool_name} failed: {e}")
		result = {
			"success": False,
			"error": str(e)
		}
		log_tool_result(tool_name, result)
		return {
			"name": tool_name,
			"response": result
		}


def format_context(context: Dict[str, Any]) -> str:
	lines = []
	lines.append(f"User: {context.get('display_name', context.get('username', 'Unknown'))} (ID: {context.get('user_id', 'Unknown')})")

	if context.get('guild_name'):
		lines.append(f"Server: {context.get('guild_name')} (ID: {context.get('guild_id')})")
		lines.append(f"Channel: {context.get('channel_name')} (ID: {context.get('channel_id')})")

	if context.get('referenced_users'):
		lines.append(f"Mentioned users: {', '.join([u['display_name'] for u in context['referenced_users']])}")

	if context.get('referenced_channels'):
		lines.append(f"Mentioned channels: {', '.join([c['name'] for c in context['referenced_channels']])}")

	if context.get('referenced_roles'):
		lines.append(f"Mentioned roles: {', '.join([r['name'] for r in context['referenced_roles']])}")


	return "\n".join(lines)


def build_message_with_results(original_message: str, results: list) -> str:
	result_text = "\n\nTool results:\n"
	for result in results:
		result_text += f"- {result['name']}: {result['response']}\n"

	return original_message + result_text
