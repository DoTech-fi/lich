"""
Tests for lich make commands.
"""
import pytest
from pathlib import Path
from typer.testing import CliRunner

from lich.cli import app


class TestMakeEntity:
    """Tests for lich make entity command."""
    
    def test_make_entity_creates_files(self, runner: CliRunner, in_lich_project: Path):
        """Test that make entity creates entity, port, and adapter files."""
        result = runner.invoke(app, ["make", "entity", "Product"])
        
        assert result.exit_code == 0
        assert "Created" in result.output
        
        # Check files exist
        assert (in_lich_project / "backend/internal/entities/product.py").exists()
        assert (in_lich_project / "backend/internal/ports/product_port.py").exists()
        assert (in_lich_project / "backend/internal/adapters/db/product_repo.py").exists()
    
    def test_make_entity_content(self, runner: CliRunner, in_lich_project: Path):
        """Test that generated entity has correct content."""
        runner.invoke(app, ["make", "entity", "User"])
        
        entity_file = in_lich_project / "backend/internal/entities/user.py"
        content = entity_file.read_text()
        
        assert "class User:" in content
        assert "@dataclass" in content
        assert "id: UUID" in content
    
    def test_make_entity_not_in_project(self, runner: CliRunner, temp_dir: Path, monkeypatch):
        """Test that make entity fails outside Lich project."""
        monkeypatch.chdir(temp_dir)
        result = runner.invoke(app, ["make", "entity", "Product"])
        
        assert result.exit_code == 1
        assert "Not a Lich project" in result.output


class TestMakeService:
    """Tests for lich make service command."""
    
    def test_make_service_creates_file(self, runner: CliRunner, in_lich_project: Path):
        """Test that make service creates service file."""
        result = runner.invoke(app, ["make", "service", "UserService"])
        
        assert result.exit_code == 0
        assert "Created" in result.output
        assert (in_lich_project / "backend/internal/services/user_service.py").exists()
    
    def test_make_service_content(self, runner: CliRunner, in_lich_project: Path):
        """Test that generated service has correct content."""
        runner.invoke(app, ["make", "service", "OrderService"])
        
        content = (in_lich_project / "backend/internal/services/order_service.py").read_text()
        
        assert "class OrderService:" in content
        assert "async def get_by_id" in content
        assert "async def create" in content


class TestMakeApi:
    """Tests for lich make api command."""
    
    def test_make_api_creates_file(self, runner: CliRunner, in_lich_project: Path):
        """Test that make api creates router file."""
        result = runner.invoke(app, ["make", "api", "products"])
        
        assert result.exit_code == 0
        assert "Created" in result.output
        assert (in_lich_project / "backend/api/http/products.py").exists()
    
    def test_make_api_content(self, runner: CliRunner, in_lich_project: Path):
        """Test that generated API has correct routes."""
        runner.invoke(app, ["make", "api", "users"])
        
        content = (in_lich_project / "backend/api/http/users.py").read_text()
        
        assert "router = APIRouter" in content
        assert "@router.get" in content
        assert "@router.post" in content
        assert "@router.delete" in content


class TestMakeDto:
    """Tests for lich make dto command."""
    
    def test_make_dto_creates_file(self, runner: CliRunner, in_lich_project: Path):
        """Test that make dto creates DTO file."""
        result = runner.invoke(app, ["make", "dto", "Product"])
        
        assert result.exit_code == 0
        assert (in_lich_project / "backend/internal/dto/product_dto.py").exists()
    
    def test_make_dto_content(self, runner: CliRunner, in_lich_project: Path):
        """Test that generated DTO has Pydantic models."""
        runner.invoke(app, ["make", "dto", "Order"])
        
        content = (in_lich_project / "backend/internal/dto/order_dto.py").read_text()
        
        assert "from pydantic import BaseModel" in content
        assert "class OrderCreate(BaseModel)" in content
        assert "class OrderUpdate(BaseModel)" in content
        assert "class OrderResponse(BaseModel)" in content


class TestMakeFactory:
    """Tests for lich make factory command."""
    
    def test_make_factory_creates_file(self, runner: CliRunner, in_lich_project: Path):
        """Test that make factory creates factory file."""
        result = runner.invoke(app, ["make", "factory", "User"])
        
        assert result.exit_code == 0
        assert (in_lich_project / "backend/tests/factories/user_factory.py").exists()
    
    def test_make_factory_content(self, runner: CliRunner, in_lich_project: Path):
        """Test that generated factory has Faker."""
        runner.invoke(app, ["make", "factory", "Product"])
        
        content = (in_lich_project / "backend/tests/factories/product_factory.py").read_text()
        
        assert "from faker import Faker" in content
        assert "class ProductFactory:" in content
        assert "def make(" in content
        assert "def make_many(" in content


class TestMakeMiddleware:
    """Tests for lich make middleware command."""
    
    def test_make_middleware_creates_file(self, runner: CliRunner, in_lich_project: Path):
        """Test that make middleware creates middleware file."""
        result = runner.invoke(app, ["make", "middleware", "RateLimit"])
        
        assert result.exit_code == 0
        assert (in_lich_project / "backend/api/middleware/ratelimit_middleware.py").exists()
    
    def test_make_middleware_content(self, runner: CliRunner, in_lich_project: Path):
        """Test that generated middleware extends BaseHTTPMiddleware."""
        runner.invoke(app, ["make", "middleware", "Auth"])
        
        content = (in_lich_project / "backend/api/middleware/auth_middleware.py").read_text()
        
        assert "BaseHTTPMiddleware" in content
        assert "async def dispatch" in content
        assert "call_next" in content


class TestMakeEvent:
    """Tests for lich make event command."""
    
    def test_make_event_creates_file(self, runner: CliRunner, in_lich_project: Path):
        """Test that make event creates event file."""
        result = runner.invoke(app, ["make", "event", "UserRegistered"])
        
        assert result.exit_code == 0
        assert (in_lich_project / "backend/internal/events/userregistered.py").exists()
    
    def test_make_event_content(self, runner: CliRunner, in_lich_project: Path):
        """Test that generated event is a dataclass."""
        runner.invoke(app, ["make", "event", "OrderPlaced"])
        
        content = (in_lich_project / "backend/internal/events/orderplaced.py").read_text()
        
        assert "@dataclass" in content
        assert "class OrderPlaced:" in content
        assert "event_id: UUID" in content


class TestMakeListener:
    """Tests for lich make listener command."""
    
    def test_make_listener_creates_file(self, runner: CliRunner, in_lich_project: Path):
        """Test that make listener creates listener file."""
        result = runner.invoke(app, ["make", "listener", "SendWelcomeEmail"])
        
        assert result.exit_code == 0
        assert (in_lich_project / "backend/internal/listeners/sendwelcomeemail.py").exists()
    
    def test_make_listener_content(self, runner: CliRunner, in_lich_project: Path):
        """Test that generated listener has handle method."""
        runner.invoke(app, ["make", "listener", "NotifyAdmin"])
        
        content = (in_lich_project / "backend/internal/listeners/notifyadmin.py").read_text()
        
        assert "class NotifyAdmin:" in content
        assert "async def handle(" in content


class TestMakeJob:
    """Tests for lich make job command."""
    
    def test_make_job_celery(self, runner: CliRunner, in_lich_project: Path):
        """Test that make job creates Celery job."""
        result = runner.invoke(app, ["make", "job", "SendEmail", "--queue", "celery"])
        
        assert result.exit_code == 0
        assert (in_lich_project / "backend/internal/jobs/sendemail_job.py").exists()
        
        content = (in_lich_project / "backend/internal/jobs/sendemail_job.py").read_text()
        assert "@shared_task" in content
        assert "from celery import" in content
    
    def test_make_job_temporal(self, runner: CliRunner, in_lich_project: Path):
        """Test that make job creates Temporal workflow."""
        result = runner.invoke(app, ["make", "job", "ProcessOrder", "--queue", "temporal"])
        
        assert result.exit_code == 0
        assert (in_lich_project / "backend/internal/jobs/processorder_job.py").exists()
        
        content = (in_lich_project / "backend/internal/jobs/processorder_job.py").read_text()
        assert "@activity.defn" in content
        assert "@workflow.defn" in content
        assert "from temporalio import" in content


class TestMakePolicy:
    """Tests for lich make policy command."""
    
    def test_make_policy_creates_file(self, runner: CliRunner, in_lich_project: Path):
        """Test that make policy creates policy file."""
        result = runner.invoke(app, ["make", "policy", "Post"])
        
        assert result.exit_code == 0
        assert (in_lich_project / "backend/internal/policies/post_policy.py").exists()
    
    def test_make_policy_content(self, runner: CliRunner, in_lich_project: Path):
        """Test that generated policy has authorization methods."""
        runner.invoke(app, ["make", "policy", "Comment"])
        
        content = (in_lich_project / "backend/internal/policies/comment_policy.py").read_text()
        
        assert "class CommentPolicy:" in content
        assert "def can_view(" in content
        assert "def can_create(" in content
        assert "def can_edit(" in content
        assert "def can_delete(" in content
