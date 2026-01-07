from lich.commands.git import git_commit, git_tag, git_push

def register_git_tools(mcp):
    """Register Git-related tools."""

    @mcp.tool()
    def lich_git_commit(message: str):
        """Create a Semantic Commit with the given message."""
        git_commit(message=message)
        return f"Committed with message: {message}"

    @mcp.tool()
    def lich_git_tag(version: str, push: bool = False):
        """Create a git tag."""
        git_tag(version=version, push=push)
        return f"Tagged version {version} (Push: {push})"

    @mcp.tool()
    def lich_git_push(tags: bool = False):
        """Push changes to remote."""
        git_push(tags=tags)
        return "Pushed to remote."
