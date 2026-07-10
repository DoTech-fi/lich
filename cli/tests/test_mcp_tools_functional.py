"""
Functional tests for MCP tools: command construction and error paths.
Tools are module-level (post-refactor), so we patch the runner in each
tool's module namespace and assert the exact CLI command built.
"""
import pytest

from lich.mcp.tools import ops, migration, seed, secret, ci


@pytest.fixture
def recorded_async(monkeypatch):
    """Patch run_lich_command_async in async tool modules; record cmds."""
    calls = []

    async def fake(cmd, force_no_color=True):
        calls.append(cmd)
        return "OK"

    monkeypatch.setattr(ops, "run_lich_command_async", fake)
    monkeypatch.setattr(migration, "run_lich_command_async", fake)
    return calls


@pytest.fixture
def recorded_sync(monkeypatch):
    """Patch run_lich_command in sync tool modules; record cmds."""
    calls = []

    def fake(cmd, force_no_color=True):
        calls.append(cmd)
        return "OK"

    monkeypatch.setattr(seed, "run_lich_command", fake)
    monkeypatch.setattr(secret, "run_lich_command", fake)
    return calls


class TestOpsTools:
    @pytest.mark.asyncio
    async def test_deploy_stage_full_flags(self, recorded_async):
        out = await ops.lich_deploy_stage("backend", version="1.2.3", dry_run=True)
        assert out == "OK"
        assert recorded_async == [
            ["lich", "deploy", "stage", "backend", "--version", "1.2.3", "--dry-run"]
        ]

    @pytest.mark.asyncio
    async def test_deploy_prod_forces_noninteractive(self, recorded_async):
        await ops.lich_deploy_prod("web")
        assert recorded_async == [["lich", "deploy", "prod", "web", "--force"]]

    @pytest.mark.asyncio
    async def test_backup_list(self, recorded_async):
        await ops.lich_backup(list_backups=True)
        assert recorded_async == [["lich", "backup", "--list"]]

    def test_deploy_setup_is_instructional(self):
        out = ops.lich_deploy_setup()
        assert "lich deploy setup" in out


class TestMigrationTools:
    @pytest.mark.asyncio
    async def test_migration_up_default_head(self, recorded_async):
        await migration.lich_migration_up()
        assert recorded_async == [["lich", "migration", "up", "head"]]

    @pytest.mark.asyncio
    async def test_migration_create_manual(self, recorded_async):
        await migration.lich_migration_create("add_users", autogenerate=False)
        assert recorded_async == [["lich", "migration", "create", "add_users", "--manual"]]

    @pytest.mark.asyncio
    async def test_migration_down_default_one_step(self, recorded_async):
        await migration.lich_migration_down()
        assert recorded_async == [["lich", "migration", "down", "-1"]]


class TestSyncTools:
    def test_seed_named_fresh(self, recorded_sync):
        seed.lich_seed(name="users", fresh=True)
        assert recorded_sync == [["lich", "seed", "users", "--fresh"]]

    def test_secret_generate_flags(self, recorded_sync):
        secret.lich_secret_generate(length=64, count=2, format="urlsafe")
        assert recorded_sync == [
            ["lich", "secret", "generate", "-l", "64", "-c", "2", "-f", "urlsafe"]
        ]


class TestErrorPropagation:
    @pytest.mark.asyncio
    async def test_async_tool_propagates_error_prefix(self, monkeypatch):
        async def failing(cmd, force_no_color=True):
            return "ERROR (exit 1):\nboom"

        monkeypatch.setattr(migration, "run_lich_command_async", failing)
        out = await migration.lich_migration_up()
        assert out.startswith("ERROR")
