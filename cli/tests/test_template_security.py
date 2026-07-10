"""Static security assertions on the cookiecutter template sources.

These read the RAW template files (Jinja not rendered) and assert
security-relevant content, so template regressions fail this repo's CI.
"""
import json
from pathlib import Path

TEMPLATE_ROOT = Path(__file__).resolve().parent.parent.parent / "template"
PROJECT_TEMPLATE = TEMPLATE_ROOT / "{{cookiecutter.project_slug}}"


class TestSettingsGuard:
    def test_settings_has_production_secret_guard(self):
        settings = (PROJECT_TEMPLATE / "backend/pkg/config/settings.py").read_text()
        assert "model_validator" in settings
        assert "_reject_default_secrets_in_production" in settings

    def test_generated_projects_get_the_guard_test(self):
        assert (PROJECT_TEMPLATE / "backend/tests/test_settings_guard.py").exists()


class TestAdminPassword:
    def test_cookiecutter_has_no_default_admin_password(self):
        config = json.loads((TEMPLATE_ROOT / "cookiecutter.json").read_text())
        assert config["admin_password"] == "", "admin_password must have no usable default"

    def test_post_gen_hook_generates_password(self):
        hook = (TEMPLATE_ROOT / "hooks/post_gen_project.py").read_text()
        assert "token_urlsafe" in hook
        assert "harden_admin_password" in hook

    def test_seed_script_refuses_weak_password(self):
        seed = (PROJECT_TEMPLATE / "backend/scripts/seed_db.py").read_text()
        assert 'in ("", "admin")' in seed
