"""
Input validation for user-supplied values that reach code generation,
file paths, or shell commands. Every validator returns the (stripped)
value on success and raises ValidationError on failure.

These are the security boundary for the CLI and the MCP server:
validate at the entry point, so everything downstream can trust its inputs.
"""
import re

_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_DEPLOY_PATH_RE = re.compile(r"^/[a-zA-Z0-9._/-]*$")
_GIT_SSH_RE = re.compile(r"^git@[a-zA-Z0-9.-]+:[a-zA-Z0-9._-]+(/[a-zA-Z0-9._-]+)+(\.git)?$")
_GIT_HTTPS_RE = re.compile(r"^https://[a-zA-Z0-9.-]+(/[a-zA-Z0-9._-]+)+(\.git)?$")
_GIT_REF_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")
_DOMAIN_RE = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)*$")


class ValidationError(ValueError):
    """Raised when user input fails validation."""


def validate_identifier(name: str) -> str:
    """Validate a Python identifier used in generated code (entity, service, ... names)."""
    name = (name or "").strip()
    if not _IDENTIFIER_RE.match(name):
        raise ValidationError(
            f"Invalid name '{name}': use letters, digits and underscores, "
            "starting with a letter or underscore (e.g. Product, order_item)."
        )
    return name


def validate_deploy_path(path: str) -> str:
    """Validate an absolute server-side deploy path (used inside SSH commands)."""
    path = (path or "").strip()
    if not _DEPLOY_PATH_RE.match(path) or ".." in path:
        raise ValidationError(
            f"Invalid deploy path '{path}': must be an absolute path using only "
            "letters, digits, '.', '_', '-' and '/' (e.g. /opt/app)."
        )
    return path


def validate_git_url(url: str) -> str:
    """Validate a git remote URL (ssh 'git@host:owner/repo.git' or https)."""
    url = (url or "").strip()
    if not (_GIT_SSH_RE.match(url) or _GIT_HTTPS_RE.match(url)):
        raise ValidationError(
            f"Invalid git URL '{url}': expected git@host:owner/repo.git "
            "or https://host/owner/repo.git."
        )
    return url


def validate_git_ref(ref: str) -> str:
    """Validate a git ref (tag, branch, sha) used in 'git checkout <ref>'."""
    ref = (ref or "").strip()
    if not _GIT_REF_RE.match(ref):
        raise ValidationError(
            f"Invalid git ref '{ref}': use letters, digits, '.', '_', '-' and '/', "
            "not starting with '-' (e.g. v1.2.3, feature/login)."
        )
    return ref


def validate_domain(domain: str) -> str:
    """Validate a DNS domain name."""
    domain = (domain or "").strip()
    if not _DOMAIN_RE.match(domain):
        raise ValidationError(
            f"Invalid domain '{domain}': use letters, digits, '-' and '.' only "
            "(e.g. example.com)."
        )
    return domain
