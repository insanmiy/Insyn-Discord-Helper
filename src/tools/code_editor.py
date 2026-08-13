import os
from pathlib import Path
from typing import Dict, Any
from src.tools.registry import register_tool
from src.permissions.access import is_server_owner
from google import genai


PROJECT_ROOT = Path(__file__).parent.parent.parent


async def read_file(context: Dict[str, Any], file_path: str) -> Dict[str, Any]:
	user_id = context.get("user_id")
	guild = context.get("_guild")

	if not guild:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	if not is_server_owner(user_id, str(guild.owner_id)):
		return {
			"success": False,
			"error": "Only the server owner can use code editing tools."
		}

	try:
		full_path = PROJECT_ROOT / file_path

		if not full_path.exists():
			return {
				"success": False,
				"error": f"File not found: {file_path}"
			}

		if not full_path.is_file():
			return {
				"success": False,
				"error": f"Path is not a file: {file_path}"
			}

		with open(full_path, 'r', encoding='utf-8') as f:
			content = f.read()

		return {
			"success": True,
			"data": {
				"file_path": file_path,
				"content": content,
				"size": len(content)
			}
		}
	except Exception as e:
		return {
			"success": False,
			"error": str(e)
		}


async def write_file(context: Dict[str, Any], file_path: str, content: str) -> Dict[str, Any]:
	user_id = context.get("user_id")
	guild = context.get("_guild")

	if not guild:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	if not is_server_owner(user_id, str(guild.owner_id)):
		return {
			"success": False,
			"error": "Only the server owner can use code editing tools."
		}

	try:
		full_path = PROJECT_ROOT / file_path

		if full_path.exists() and not full_path.is_file():
			return {
				"success": False,
				"error": f"Path exists but is not a file: {file_path}"
			}

		full_path.parent.mkdir(parents=True, exist_ok=True)

		with open(full_path, 'w', encoding='utf-8') as f:
			f.write(content)

		return {
			"success": True,
			"data": {
				"file_path": file_path,
				"size": len(content)
			}
		}
	except Exception as e:
		return {
			"success": False,
			"error": str(e)
		}


async def edit_file(context: Dict[str, Any], file_path: str, old_string: str, new_string: str) -> Dict[str, Any]:
	user_id = context.get("user_id")
	guild = context.get("_guild")

	if not guild:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	if not is_server_owner(user_id, str(guild.owner_id)):
		return {
			"success": False,
			"error": "Only the server owner can use code editing tools."
		}

	try:
		full_path = PROJECT_ROOT / file_path

		if not full_path.exists():
			return {
				"success": False,
				"error": f"File not found: {file_path}"
			}

		if not full_path.is_file():
			return {
				"success": False,
				"error": f"Path is not a file: {file_path}"
			}

		with open(full_path, 'r', encoding='utf-8') as f:
			content = f.read()

		if old_string not in content:
			return {
				"success": False,
				"error": f"Old string not found in file. The exact string must match."
			}

		new_content = content.replace(old_string, new_string, 1)

		with open(full_path, 'w', encoding='utf-8') as f:
			f.write(new_content)

		return {
			"success": True,
			"data": {
				"file_path": file_path,
				"replacements": 1,
				"old_size": len(content),
				"new_size": len(new_content)
			}
		}
	except Exception as e:
		return {
			"success": False,
			"error": str(e)
		}


async def list_files(context: Dict[str, Any], directory: str = "") -> Dict[str, Any]:
	user_id = context.get("user_id")
	guild = context.get("_guild")

	if not guild:
		return {
			"success": False,
			"error": "This command can only be used in a server."
		}

	if not is_server_owner(user_id, str(guild.owner_id)):
		return {
			"success": False,
			"error": "Only the server owner can use code editing tools."
		}

	try:
		full_path = PROJECT_ROOT / directory if directory else PROJECT_ROOT

		if not full_path.exists():
			return {
				"success": False,
				"error": f"Directory not found: {directory}"
			}

		if not full_path.is_dir():
			return {
				"success": False,
				"error": f"Path is not a directory: {directory}"
			}

		files = []
		directories = []
		for item in full_path.iterdir():
			if item.is_file():
				files.append({
					"name": item.name,
					"path": str(item.relative_to(PROJECT_ROOT)),
					"size": item.stat().st_size,
					"type": "file"
				})
			elif item.is_dir():
				directories.append({
					"name": item.name,
					"path": str(item.relative_to(PROJECT_ROOT)),
					"type": "directory"
				})

		return {
			"success": True,
			"data": {
				"directory": directory or ".",
				"files": files,
				"directories": directories,
				"file_count": len(files),
				"directory_count": len(directories)
			}
		}
	except Exception as e:
		return {
			"success": False,
			"error": str(e)
		}


def register_code_editor_tools():
	register_tool(
		"read_file",
		read_file,
		genai.types.FunctionDeclaration(
			name="read_file",
			description="Read the contents of a file in the bot's codebase. Only the server owner can use this.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"file_path": genai.types.Schema(
						type="string",
						description="Relative path to the file to read (e.g., 'src/main.py')"
					)
				},
				required=["file_path"]
			)
		),
		"owner"
	)

	register_tool(
		"write_file",
		write_file,
		genai.types.FunctionDeclaration(
			name="write_file",
			description="Write or edit a file in the bot's codebase by providing the full new content. This can be used to create new files or overwrite existing ones. Only the server owner can use this.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"file_path": genai.types.Schema(
						type="string",
						description="Relative path to the file to write (e.g., 'bot_config.xml', 'src/main.py')"
					),
					"content": genai.types.Schema(
						type="string",
						description="The complete content to write to the file. To edit a file, read it first, modify the content, then write the modified content."
					)
				},
				required=["file_path", "content"]
			)
		),
		"owner"
	)

	register_tool(
		"edit_file",
		edit_file,
		genai.types.FunctionDeclaration(
			name="edit_file",
			description="Edit a file by replacing a specific string with another string. This is safer than write_file for small changes. Only the server owner can use this.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"file_path": genai.types.Schema(
						type="string",
						description="Relative path to the file to edit (e.g., 'bot_config.xml', 'src/main.py')"
					),
					"old_string": genai.types.Schema(
						type="string",
						description="The exact string to find and replace. Must match exactly including whitespace."
					),
					"new_string": genai.types.Schema(
						type="string",
						description="The new string to replace the old string with."
					)
				},
				required=["file_path", "old_string", "new_string"]
			)
		),
		"owner"
	)

	register_tool(
		"list_files",
		list_files,
		genai.types.FunctionDeclaration(
			name="list_files",
			description="List files in a directory in the bot's codebase. Only the server owner can use this.",
			parameters=genai.types.Schema(
				type="object",
				properties={
					"directory": genai.types.Schema(
						type="string",
						description="Relative path to the directory to list (optional, defaults to project root)"
					)
				},
				required=[]
			)
		),
		"owner"
	)
