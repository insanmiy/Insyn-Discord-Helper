import logging
from typing import Dict, Any
from datetime import datetime


def setup_logging():
	logging.basicConfig(
		level=logging.INFO,
		format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
		datefmt='%Y-%m-%d %H:%M:%S'
	)


def log_tool_request(user_id: str, username: str, request: str, tool_name: str, arguments: Dict[str, Any]):
	logger = logging.getLogger(__name__)
	
	sanitized_args = sanitize_arguments(arguments)
	
	logger.info(f"User: {username} (ID: {user_id})")
	logger.info(f"Request: {request}")
	logger.info(f"Tool: {tool_name}")
	logger.info(f"Arguments: {sanitized_args}")


def log_tool_result(tool_name: str, result: Dict[str, Any]):
	logger = logging.getLogger(__name__)
	
	success = result.get("success", False)
	logger.info(f"Tool {tool_name} result: success={success}")
	
	if not success:
		error = result.get("error", "Unknown error")
		logger.info(f"Tool {tool_name} error: {error}")


def log_ai_response(user_id: str, username: str, response: str):
	logger = logging.getLogger(__name__)
	
	logger.info(f"AI response to {username} (ID: {user_id}): {response[:200]}...")


def sanitize_arguments(arguments: Dict[str, Any]) -> Dict[str, Any]:
	sanitized = {}
	
	for key, value in arguments.items():
		if "token" in key.lower() or "password" in key.lower() or "secret" in key.lower():
			sanitized[key] = "[REDACTED]"
		elif isinstance(value, str) and len(value) > 100:
			sanitized[key] = value[:100] + "..."
		else:
			sanitized[key] = value
	
	return sanitized
