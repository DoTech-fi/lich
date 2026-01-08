import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm
import subprocess
from pathlib import Path
from typing import Optional

console = Console()

def _run_command(cmd: list, cwd: Path = None) -> tuple[int, str, str]:
    """Run a shell command."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd or Path.cwd(),
        )
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        return -1, "", f"Command not found: {cmd[0]}"


def git_commit(
    message: Optional[str] = typer.Option(None, "--message", "-m", help="Direct commit message (bypass wizard)"),
    add_all: bool = typer.Option(False, "--all", "-a", help="Stage all changes before committing"),
):
    """
    📝 Create a Conventional Commit.
    
    Helps you build a standardized commit message using the Conventional Commits format:
    <type>(<scope>): <description>
    """
    if add_all:
        _run_command(["git", "add", "-A"])
        console.print("[green]✓ Staged all changes[/green]")

    if message:
        final_message = message
    else:
        # Interactive Wizard
        console.print("[bold blue]Semantic Commit Wizard[/bold blue]")
        
        commit_types = [
            ("feat", "A new feature"),
            ("fix", "A bug fix"),
            ("docs", "Documentation only changes"),
            ("style", "Changes that do not affect the meaning of the code"),
            ("refactor", "A code change that neither fixes a bug nor adds a feature"),
            ("perf", "A code change that improves performance"),
            ("test", "Adding missing tests or correcting existing tests"),
            ("chore", "Changes to the build process or auxiliary tools"),
        ]
        
        console.print("\nChoose a type:")
        for idx, (ctype, desc) in enumerate(commit_types, 1):
            console.print(f"  [cyan]{idx}. {ctype}[/cyan]: {desc}")
            
        type_idx = 0
        while type_idx < 1 or type_idx > len(commit_types):
            try:
                type_idx = int(Prompt.ask("Select type (number)"))
            except ValueError:
                pass
        
        selected_type = commit_types[type_idx-1][0]
        
        scope = Prompt.ask("Scope (optional)", default="")
        description = Prompt.ask("Description (short imperative summary)")
        
        if scope:
            final_message = f"{selected_type}({scope}): {description}"
        else:
            final_message = f"{selected_type}: {description}"
            
        console.print(f"\n[bold]Commit Message:[/bold] {final_message}")
        if not Confirm.ask("Proceed with this message?"):
            raise typer.Abort()

    # Run git commit
    code, stdout, stderr = _run_command(["git", "commit", "-m", final_message])
    
    if code == 0:
        console.print("[green]✓ Commit successful![/green]")
        console.print(stdout)
    else:
        console.print("[red]✗ Commit failed:[/red]")
        console.print(stderr)
        raise typer.Exit(1)




def git_tag(
    version: str = typer.Argument(..., help="Version to tag (e.g. v1.0.0)"),
    push: bool = typer.Option(False, "--push", "-p", help="Push tag immediately after creating"),
):
    """
    🏷️ Create a new version tag.
    """
    if not version.startswith("v"):
        if Confirm.ask(f"Did you mean 'v{version}'?"):
            version = f"v{version}"
            
    code, stdout, stderr = _run_command(["git", "tag", version])
    
    if code == 0:
        console.print(f"[green]✓ Tag {version} created successfully![/green]")
        if push or Confirm.ask("Push this tag to remote?"):
            p_code, p_out, p_err = _run_command(["git", "push", "origin", version])
            if p_code == 0:
                console.print(f"[green]✓ Tag {version} pushed to origin![/green]")
            else:
                console.print(f"[red]✗ Failed to push tag:[/red] {p_err}")
    else:
        console.print(f"[red]✗ Failed to create tag:[/red] {stderr}")
        if "already exists" in stderr:
             console.print("[yellow]Tip: Use a new version number.[/yellow]")



def git_push(
    tags: bool = typer.Option(False, "--tags", "-t", help="Push tags as well"),
):
    """
    🚀 Push changes to remote (origin main/master).
    """
    cmd = ["git", "push", "origin", "main"]
    # Fallback to current branch detection if needed, but keeping it simple for now
    
    if tags:
        cmd.append("--tags")
        
    console.print("[blue]Pushing to origin...[/blue]")
    code, stdout, stderr = _run_command(cmd)
    
    if code == 0:
        console.print("[green]✓ Pushed successfully![/green]")
        console.print(stdout)
        console.print(stderr)
    else:
        console.print("[red]✗ Push failed:[/red]")
        console.print(stderr)
        raise typer.Exit(1)
