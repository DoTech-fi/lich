from lich.commands.git import git_commit, git_tag, git_push
from lich.commands._validate import ValidationError, validate_git_ref


def lich_git_commit(message: str):
    """Create a Semantic Commit with the given message."""
    # I2: reject empty or dash-prefixed messages to prevent option smuggling
    if not message or message.startswith("-"):
        return "ERROR: Commit message must not be empty or start with '-'."
    git_commit(message=message)
    return f"Committed with message: {message}"


def lich_git_tag(version: str, push: bool = False):
    """Create a git tag."""
    # I1: validate version as a safe git ref before forwarding to CLI
    try:
        version = validate_git_ref(version)
    except ValidationError as e:
        return f"ERROR: {e}"
    git_tag(version=version, push=push)
    return f"Tagged version {version} (Push: {push})"


def lich_git_push(tags: bool = False):
    """Push changes to remote."""
    git_push(tags=tags)
    return "Pushed to remote."


_TOOLS = [lich_git_commit, lich_git_tag, lich_git_push]


def register_git_tools(mcp):
    """Register Git-related tools."""
    for tool in _TOOLS:
        mcp.tool()(tool)
