from langchain_core.tools import tool, InjectedToolCallId
from langgraph.types import Command
from langchain_core.messages import ToolMessage
from typing import Annotated, List, Union
from langgraph.prebuilt import InjectedState
from .prompts import WRITE_TODOS_DESCRIPTION, EDIT_DESCRIPTION, TOOL_DESCRIPTION
from .state import Todo, DeepAgentState

@tool(description=WRITE_TODOS_DESCRIPTION)
def write_todos(
    todos: List[Todo], tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """Create and manage a structured task list."""
    return Command(
        update={
            "todos": todos,
            "messages": [
                ToolMessage(content=f"Updated todo list: {len(todos)} items.", tool_call_id=tool_call_id)
            ],
        }
    )

@tool
def ls(state: Annotated[DeepAgentState, InjectedState]) -> str:
    """List all files in the current state."""
    files = list(state.get("files", {}).keys())
    if not files:
        return "No files found."
    return "\n".join(files)

@tool(description=TOOL_DESCRIPTION)
def read_file(
    file_path: str,
    state: Annotated[DeepAgentState, InjectedState],
    offset: int = 0,
    limit: int = 2000,
) -> str:
    """Read file with optional line offset and limit."""
    mock_filesystem = state.get("files", {})
    if file_path not in mock_filesystem:
        return f"Error: File '{file_path}' not found."

    content = mock_filesystem.get(file_path, "")
    if not content.strip():
        return "System reminder: File exists but is empty."

    lines = content.splitlines()
    if offset >= len(lines):
        return f"Error: Line offset {offset} exceeds file length ({len(lines)} lines)."

    end_idx = min(offset + limit, len(lines))
    
    result_lines = [
        f"{i + 1:6d}\t{lines[i][:2000]}" for i in range(offset, end_idx)
    ]
    
    return "\n".join(result_lines)

@tool
def write_file(
    file_path: str,
    content: str,
    state: Annotated[DeepAgentState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Write content to a file, overwriting if it exists."""
    files = state.get("files", {}).copy()
    files[file_path] = content
    return Command(
        update={
            "files": files,
            "messages": [
                ToolMessage(content=f"Successfully wrote to file {file_path}", tool_call_id=tool_call_id)
            ],
        }
    )

@tool(description=EDIT_DESCRIPTION)
def edit_file(
    file_path: str,
    old_string: str,
    new_string: str,
    state: Annotated[DeepAgentState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
    replace_all: bool = False,
) -> Union[Command, ToolMessage]:
    """Perform exact string replacements in a file."""
    mock_filesystem = state.get("files", {}).copy()
    if file_path not in mock_filesystem:
        return ToolMessage(content=f"Error: File '{file_path}' not found", tool_call_id=tool_call_id)

    content = mock_filesystem[file_path]
    if old_string not in content:
        return ToolMessage(content=f"Error: String not found in file: '{old_string}'", tool_call_id=tool_call_id)

    if not replace_all:
        occurrences = content.count(old_string)
        if occurrences > 1:
            return ToolMessage(content=f"Error: String '{old_string}' appears {occurrences} times. Use replace_all=True or a more specific string.", tool_call_id=tool_call_id)

    if replace_all:
        new_content = content.replace(old_string, new_string)
        msg = f"Replaced all instances of the string in '{file_path}'"
    else:
        new_content = content.replace(old_string, new_string, 1)
        msg = f"Replaced the string in '{file_path}'"
        
    mock_filesystem[file_path] = new_content
    return Command(
        update={
            "files": mock_filesystem,
            "messages": [ToolMessage(content=msg, tool_call_id=tool_call_id)],
        }
    )