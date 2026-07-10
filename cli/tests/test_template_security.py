"""Static security assertions on the cookiecutter template sources.

These read the RAW template files (Jinja not rendered) and assert
security-relevant content, so template regressions fail this repo's CI.
"""
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
