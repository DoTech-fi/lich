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
_SSH_DEST_RE = re.compile(r"^(?:[a-zA-Z0-9._-]+@)?[a-zA-Z0-9._-]+$")


class ValidationError(ValueError):
    """Raised when user input fails validation."""


def validate_identifier(name: str) -> str:
    """Validate a Python identifier used in generated code (entity, service, ... names)."""
    name = (name or "").strip()
    if not _IDENTIFIER_RE.fullmatch(name):
        raise ValidationError(
            f"Invalid name {name!r}: use letters, digits and underscores, "
            "starting with a letter or underscore (e.g. Product, order_item)."
        )
    return name


def validate_deploy_path(path: str) -> str:
    """Validate an absolute server-side deploy path (used inside SSH commands)."""
    path = (path or "").strip()
    if not _DEPLOY_PATH_RE.fullmatch(path) or ".." in path or "//" in path or path.count("/") < 2 or path.endswith("/"):
        raise ValidationError(
            f"Invalid deploy path {path!r}: must be an absolute path using only "
            "letters, digits, '.', '_', '-' and '/', e.g. /opt/app (at least two segments)."
        )
    return path


def validate_git_url(url: str) -> str:
    """Validate a git remote URL (ssh 'git@host:owner/repo.git' or https)."""
    url = (url or "").strip()
    if not (_GIT_SSH_RE.fullmatch(url) or _GIT_HTTPS_RE.fullmatch(url)):
        raise ValidationError(
            f"Invalid git URL {url!r}: expected git@host:owner/repo.git "
            "or https://host/owner/repo.git."
        )
    return url


def validate_git_ref(ref: str) -> str:
    """Validate a git ref (tag, branch, sha) used in 'git checkout <ref>'."""
    ref = (ref or "").strip()
    if not _GIT_REF_RE.fullmatch(ref) or ".." in ref:
        raise ValidationError(
            f"Invalid git ref {ref!r}: use letters, digits, '.', '_', '-' and '/', "
            "not starting with '-' (e.g. v1.2.3, feature/login)."
        )
    return ref


def validate_ssh_destination(dest: str) -> str:
    """Validate an SSH destination ('host', 'user@host', or an ssh-config alias)."""
    dest = (dest or "").strip()
    # The regex cannot match a leading '-', but keep the explicit check as
    # belt-and-braces defense: this guards against ssh option smuggling.
    if not _SSH_DEST_RE.fullmatch(dest) or dest.startswith("-"):
        raise ValidationError(
            f"Invalid SSH destination {dest!r}: use host, user@host or an ssh-config "
            "alias (letters, digits, '.', '_', '-')."
        )
    return dest


def validate_domain(domain: str) -> str:
    """Validate a DNS domain name."""
    domain = (domain or "").strip()
    if (
        not _DOMAIN_RE.fullmatch(domain)
        or len(domain) > 253
        or any(len(label) > 63 for label in domain.split("."))
    ):
        raise ValidationError(
            f"Invalid domain {domain!r}: use letters, digits, '-' and '.' only "
            "(e.g. example.com)."
        )
    return domain
