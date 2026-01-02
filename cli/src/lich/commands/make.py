"""
lich make - Code generation commands (like Laravel Artisan).
"""
from pathlib import Path

import typer
from rich.console import Console

console = Console()

make_app = typer.Typer(
    name="make",
    help="Generate code scaffolding (entities, services, APIs)",
    no_args_is_help=True,
)


def _check_lich_project() -> bool:
    """Check if we're in a Lich project."""
    if not Path(".lich").exists():
        console.print("[red]❌ Not a Lich project![/red]")
        return False
    return True


def _write_file(path: Path, content: str, force: bool = False) -> bool:
    """Write content to file, creating directories if needed."""
    if path.exists() and not force:
        console.print(f"[yellow]⚠️ File exists: {path}[/yellow]")
        console.print("   Use --force to overwrite")
        return False
    
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    console.print(f"[green]✅ Created: {path}[/green]")
    return True


@make_app.command("entity")
def make_entity(
    name: str = typer.Argument(..., help="Entity name (e.g., Product)"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files"),
):
    """
    Generate a new entity with port and adapter.
    
    Creates:
    - backend/internal/entities/{name}.py
    - backend/internal/ports/{name}_port.py  
    - backend/internal/adapters/db/{name}_repo.py
    """
    if not _check_lich_project():
        raise typer.Exit(1)
    
    name_lower = name.lower()
    name_pascal = name[0].upper() + name[1:] if name else name
    
    console.print(f"\n🔨 [bold blue]Creating entity: {name_pascal}[/bold blue]\n")
    
    # Entity file
    entity_content = f'''"""
{name_pascal} entity - Domain model.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class {name_pascal}:
    """
    {name_pascal} domain entity.
    """
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @classmethod
    def create(cls, **kwargs) -> "{name_pascal}":
        """Factory method to create a new {name_pascal}."""
        return cls(
            id=uuid4(),
            created_at=datetime.utcnow(),
            **kwargs
        )
'''
    _write_file(Path(f"backend/internal/entities/{name_lower}.py"), entity_content, force)
    
    # Port file
    port_content = f'''"""
{name_pascal} port - Repository interface.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from internal.entities.{name_lower} import {name_pascal}


class {name_pascal}Port(ABC):
    """
    {name_pascal} repository interface.
    """
    
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[{name_pascal}]:
        """Get {name_pascal} by ID."""
        pass
    
    @abstractmethod
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[{name_pascal}]:
        """List all {name_pascal}s."""
        pass
    
    @abstractmethod
    async def save(self, entity: {name_pascal}) -> {name_pascal}:
        """Save {name_pascal}."""
        pass
    
    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        """Delete {name_pascal}."""
        pass
'''
    _write_file(Path(f"backend/internal/ports/{name_lower}_port.py"), port_content, force)
    
    # Adapter file
    adapter_content = f'''"""
{name_pascal} repository - Database adapter.
"""
from typing import List, Optional
from uuid import UUID

from internal.entities.{name_lower} import {name_pascal}
from internal.ports.{name_lower}_port import {name_pascal}Port


class {name_pascal}Repository({name_pascal}Port):
    """
    {name_pascal} database repository implementation.
    """
    
    def __init__(self, db_session):
        self.db = db_session
    
    async def get_by_id(self, id: UUID) -> Optional[{name_pascal}]:
        # TODO: Implement database query
        pass
    
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[{name_pascal}]:
        # TODO: Implement database query
        pass
    
    async def save(self, entity: {name_pascal}) -> {name_pascal}:
        # TODO: Implement database save
        pass
    
    async def delete(self, id: UUID) -> bool:
        # TODO: Implement database delete
        pass
'''
    _write_file(Path(f"backend/internal/adapters/db/{name_lower}_repo.py"), adapter_content, force)
    
    console.print(f"\n[green]✅ Entity {name_pascal} created successfully![/green]")
    console.print("\nNext steps:")
    console.print(f"   1. Edit backend/internal/entities/{name_lower}.py - add fields")
    console.print(f"   2. Implement backend/internal/adapters/db/{name_lower}_repo.py")
    console.print(f"   3. Run: lich make service {name_pascal}Service")


@make_app.command("service")
def make_service(
    name: str = typer.Argument(..., help="Service name (e.g., ProductService)"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing"),
):
    """
    Generate a new service (use case).
    
    Creates: backend/internal/services/{name}.py
    """
    if not _check_lich_project():
        raise typer.Exit(1)
    
    name_lower = name.lower().replace("service", "")
    name_pascal = name[0].upper() + name[1:] if name else name
    if not name_pascal.endswith("Service"):
        name_pascal += "Service"
    
    console.print(f"\n🔨 [bold blue]Creating service: {name_pascal}[/bold blue]\n")
    
    content = f'''"""
{name_pascal} - Application service (use case).
"""
from typing import List, Optional
from uuid import UUID


class {name_pascal}:
    """
    {name_pascal} handles business logic.
    """
    
    def __init__(self, repository):
        self.repo = repository
    
    async def get_by_id(self, id: UUID):
        """Get entity by ID."""
        return await self.repo.get_by_id(id)
    
    async def list_all(self, limit: int = 100, offset: int = 0):
        """List all entities."""
        return await self.repo.list_all(limit=limit, offset=offset)
    
    async def create(self, **data):
        """Create new entity."""
        # TODO: Add validation and business logic
        pass
    
    async def update(self, id: UUID, **data):
        """Update entity."""
        # TODO: Add validation and business logic
        pass
    
    async def delete(self, id: UUID) -> bool:
        """Delete entity."""
        return await self.repo.delete(id)
'''
    
    filename = name_lower + "_service" if not name_lower.endswith("_service") else name_lower
    _write_file(Path(f"backend/internal/services/{filename}.py"), content, force)
    
    console.print(f"\n[green]✅ Service {name_pascal} created![/green]")


@make_app.command("api")
def make_api(
    name: str = typer.Argument(..., help="API resource name (e.g., products)"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing"),
):
    """
    Generate API endpoints (FastAPI router).
    
    Creates: backend/api/http/{name}.py
    """
    if not _check_lich_project():
        raise typer.Exit(1)
    
    name_lower = name.lower()
    name_pascal = name[0].upper() + name[1:] if name else name
    
    console.print(f"\n🔨 [bold blue]Creating API: {name_lower}[/bold blue]\n")
    
    content = f'''"""
{name_pascal} API endpoints.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/{name_lower}", tags=["{name_pascal}"])


@router.get("/", response_model=List[dict])
async def list_{name_lower}(
    limit: int = 100,
    offset: int = 0,
):
    """List all {name_lower}."""
    # TODO: Inject service and return data
    return []


@router.get("/{{id}}")
async def get_{name_lower.rstrip('s')}(id: UUID):
    """Get {name_lower.rstrip('s')} by ID."""
    # TODO: Inject service and return data
    raise HTTPException(status_code=404, detail="Not found")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_{name_lower.rstrip('s')}(data: dict):
    """Create new {name_lower.rstrip('s')}."""
    # TODO: Inject service and create
    return {{"id": "...", **data}}


@router.put("/{{id}}")
async def update_{name_lower.rstrip('s')}(id: UUID, data: dict):
    """Update {name_lower.rstrip('s')}."""
    # TODO: Inject service and update
    return {{"id": str(id), **data}}


@router.delete("/{{id}}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_{name_lower.rstrip('s')}(id: UUID):
    """Delete {name_lower.rstrip('s')}."""
    # TODO: Inject service and delete
    return None
'''
    
    _write_file(Path(f"backend/api/http/{name_lower}.py"), content, force)
    
    console.print(f"\n[green]✅ API {name_lower} created![/green]")
    console.print("\nNext steps:")
    console.print("   1. Register router in backend/main.py")
    console.print("   2. Add request/response DTOs")


@make_app.command("dto")
def make_dto(
    name: str = typer.Argument(..., help="DTO name (e.g., ProductDTO)"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing"),
):
    """
    Generate DTO (Data Transfer Object) with Pydantic.
    
    Creates: backend/internal/dto/{name}.py
    """
    if not _check_lich_project():
        raise typer.Exit(1)
    
    name_lower = name.lower().replace("dto", "")
    name_pascal = name[0].upper() + name[1:] if name else name
    
    console.print(f"\n🔨 [bold blue]Creating DTO: {name_pascal}[/bold blue]\n")
    
    content = f'''"""
{name_pascal} DTOs - Request/Response schemas.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class {name_pascal}Create(BaseModel):
    """Request schema for creating {name_pascal}."""
    # TODO: Add fields
    name: str = Field(..., min_length=1, max_length=255)
    
    class Config:
        json_schema_extra = {{
            "example": {{
                "name": "Example"
            }}
        }}


class {name_pascal}Update(BaseModel):
    """Request schema for updating {name_pascal}."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)


class {name_pascal}Response(BaseModel):
    """Response schema for {name_pascal}."""
    id: UUID
    name: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
'''
    
    filename = name_lower + "_dto" if not name_lower.endswith("_dto") else name_lower
    _write_file(Path(f"backend/internal/dto/{filename}.py"), content, force)
    
    console.print(f"\n[green]✅ DTO {name_pascal} created![/green]")


@make_app.command("factory")
def make_factory(
    name: str = typer.Argument(..., help="Factory name (e.g., User)"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing"),
):
    """
    Generate a model factory for testing.
    
    Creates: backend/tests/factories/{name}_factory.py
    """
    if not _check_lich_project():
        raise typer.Exit(1)
    
    name_lower = name.lower().replace("factory", "")
    name_pascal = name[0].upper() + name[1:] if name else name
    if name_pascal.endswith("Factory"):
        name_pascal = name_pascal[:-7]
    
    console.print(f"\n🏭 [bold blue]Creating factory: {name_pascal}Factory[/bold blue]\n")
    
    content = f'''"""
{name_pascal}Factory - Generate fake {name_pascal} instances for testing.
"""
from faker import Faker
from typing import List, Optional
from uuid import uuid4
from datetime import datetime

# from internal.entities.{name_lower} import {name_pascal}

fake = Faker()


class {name_pascal}Factory:
    """
    Factory for creating {name_pascal} test instances.
    
    Usage:
        factory = {name_pascal}Factory()
        user = factory.make()
        users = factory.make_many(10)
    """
    
    @staticmethod
    def make(**overrides):
        """Create a single {name_pascal} instance."""
        data = {{
            "id": uuid4(),
            "created_at": datetime.utcnow(),
            # TODO: Add more fields with fake data
            # "name": fake.name(),
            # "email": fake.email(),
        }}
        data.update(overrides)
        # return {name_pascal}(**data)
        return data
    
    @classmethod
    def make_many(cls, count: int = 10, **overrides) -> List:
        """Create multiple {name_pascal} instances."""
        return [cls.make(**overrides) for _ in range(count)]
'''
    
    _write_file(Path(f"backend/tests/factories/{name_lower}_factory.py"), content, force)
    
    console.print(f"\n[green]✅ Factory {name_pascal}Factory created![/green]")
    console.print("\nUsage in tests:")
    console.print(f"   from tests.factories.{name_lower}_factory import {name_pascal}Factory")
    console.print(f"   user = {name_pascal}Factory.make()")


@make_app.command("middleware")
def make_middleware(
    name: str = typer.Argument(..., help="Middleware name (e.g., RateLimit)"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing"),
):
    """
    Generate a FastAPI middleware.
    
    Creates: backend/api/middleware/{name}.py
    """
    if not _check_lich_project():
        raise typer.Exit(1)
    
    name_lower = name.lower().replace("middleware", "")
    name_pascal = name[0].upper() + name[1:] if name else name
    
    console.print(f"\n🛡️ [bold blue]Creating middleware: {name_pascal}[/bold blue]\n")
    
    content = f'''"""
{name_pascal} Middleware - Request/Response interceptor.
"""
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class {name_pascal}Middleware(BaseHTTPMiddleware):
    """
    {name_pascal} middleware for FastAPI.
    
    Usage in main.py:
        app.add_middleware({name_pascal}Middleware)
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Before request
        # Example: Check auth, rate limit, add headers
        
        response = await call_next(request)
        
        # After response
        # Example: Add custom headers, logging
        
        return response


# Alternative: Function-based middleware
async def {name_lower}_middleware(request: Request, call_next: Callable) -> Response:
    """Function-based middleware."""
    # Before request
    response = await call_next(request)
    # After response
    return response
'''
    
    _write_file(Path(f"backend/api/middleware/{name_lower}_middleware.py"), content, force)
    
    console.print(f"\n[green]✅ Middleware {name_pascal} created![/green]")
    console.print("\nRegister in main.py:")
    console.print(f"   from api.middleware.{name_lower}_middleware import {name_pascal}Middleware")
    console.print(f"   app.add_middleware({name_pascal}Middleware)")


@make_app.command("event")
def make_event(
    name: str = typer.Argument(..., help="Event name (e.g., UserRegistered)"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing"),
):
    """
    Generate a domain event class.
    
    Creates: backend/internal/events/{name}.py
    """
    if not _check_lich_project():
        raise typer.Exit(1)
    
    name_lower = name.lower()
    name_pascal = name[0].upper() + name[1:] if name else name
    
    console.print(f"\n📢 [bold blue]Creating event: {name_pascal}[/bold blue]\n")
    
    content = f'''"""
{name_pascal} Event - Domain event.
"""
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class {name_pascal}:
    """
    {name_pascal} domain event.
    
    Fired when: [describe when this event is triggered]
    
    Usage:
        event = {name_pascal}(user_id=user.id)
        await event_bus.publish(event)
    """
    # Event payload
    # TODO: Add event-specific fields
    
    # Event metadata
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def event_name(self) -> str:
        return "{name_pascal}"
'''
    
    _write_file(Path(f"backend/internal/events/{name_lower}.py"), content, force)
    
    console.print(f"\n[green]✅ Event {name_pascal} created![/green]")
    console.print("\nNext: Create a listener with:")
    console.print(f"   lich make listener Handle{name_pascal}")


@make_app.command("listener")
def make_listener(
    name: str = typer.Argument(..., help="Listener name (e.g., SendWelcomeEmail)"),
    event: str = typer.Option(None, "--event", "-e", help="Event to listen for"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing"),
):
    """
    Generate an event listener.
    
    Creates: backend/internal/listeners/{name}.py
    """
    if not _check_lich_project():
        raise typer.Exit(1)
    
    name_lower = name.lower()
    name_pascal = name[0].upper() + name[1:] if name else name
    event_name = event or "SomeEvent"
    
    console.print(f"\n👂 [bold blue]Creating listener: {name_pascal}[/bold blue]\n")
    
    content = f'''"""
{name_pascal} Listener - Handles events.
"""
from typing import Any


class {name_pascal}:
    """
    {name_pascal} event listener.
    
    Listens for: {event_name}
    """
    
    def __init__(self):
        # Inject dependencies here
        pass
    
    async def handle(self, event: Any) -> None:
        """
        Handle the event.
        
        Args:
            event: The event instance
        """
        # TODO: Implement event handling logic
        # Example:
        # await self.email_service.send_welcome(event.email)
        pass
'''
    
    _write_file(Path(f"backend/internal/listeners/{name_lower}.py"), content, force)
    
    console.print(f"\n[green]✅ Listener {name_pascal} created![/green]")


@make_app.command("job")
def make_job(
    name: str = typer.Argument(..., help="Job name (e.g., SendInvoice)"),
    queue_type: str = typer.Option(
        None, "--queue", "-q",
        help="Queue type: celery or temporal"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing"),
):
    """
    Generate a background job.
    
    Creates: backend/internal/jobs/{name}.py
    """
    if not _check_lich_project():
        raise typer.Exit(1)
    
    name_lower = name.lower().replace("job", "")
    name_pascal = name[0].upper() + name[1:] if name else name
    if name_pascal.endswith("Job"):
        name_pascal = name_pascal[:-3]
    
    # Ask for queue type if not provided
    if not queue_type:
        console.print("\n[bold]Select queue type:[/bold]")
        console.print("   1. Celery (simple, Redis-based)")
        console.print("   2. Temporal (durable, workflow-based)")
        choice = typer.prompt("Choice", default="1")
        queue_type = "temporal" if choice == "2" else "celery"
    
    console.print(f"\n⚙️ [bold blue]Creating job: {name_pascal}Job ({queue_type})[/bold blue]\n")
    
    if queue_type == "temporal":
        content = f'''"""
{name_pascal}Job - Temporal workflow/activity.
"""
from datetime import timedelta
from temporalio import activity, workflow


@activity.defn
async def {name_lower}_activity(data: dict) -> dict:
    """
    {name_pascal} activity - the actual work.
    
    Args:
        data: Job input data
    
    Returns:
        Job result
    """
    # TODO: Implement job logic
    return {{"status": "completed"}}


@workflow.defn
class {name_pascal}Workflow:
    """
    {name_pascal} workflow - orchestrates activities.
    """
    
    @workflow.run
    async def run(self, data: dict) -> dict:
        """Execute the workflow."""
        result = await workflow.execute_activity(
            {name_lower}_activity,
            data,
            start_to_close_timeout=timedelta(minutes=5),
        )
        return result
'''
    else:
        content = f'''"""
{name_pascal}Job - Celery background task.
"""
from celery import shared_task


@shared_task(bind=True, max_retries=3)
def {name_lower}_job(self, data: dict) -> dict:
    """
    {name_pascal} background job.
    
    Args:
        self: Celery task instance
        data: Job input data
    
    Returns:
        Job result
    
    Usage:
        {name_lower}_job.delay({{"key": "value"}})
    """
    try:
        # TODO: Implement job logic
        
        return {{"status": "completed"}}
    
    except Exception as exc:
        # Retry with exponential backoff
        self.retry(exc=exc, countdown=2 ** self.request.retries)
'''
    
    _write_file(Path(f"backend/internal/jobs/{name_lower}_job.py"), content, force)
    
    console.print(f"\n[green]✅ Job {name_pascal}Job created ({queue_type})![/green]")
    console.print("\nUsage:")
    if queue_type == "temporal":
        console.print("   # Start workflow")
        console.print(f"   await client.start_workflow({name_pascal}Workflow.run, data, id='...')")
    else:
        console.print(f"   {name_lower}_job.delay({{'key': 'value'}})")


@make_app.command("policy")
def make_policy(
    name: str = typer.Argument(..., help="Policy name (e.g., Post)"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing"),
):
    """
    Generate an authorization policy.
    
    Creates: backend/internal/policies/{name}_policy.py
    """
    if not _check_lich_project():
        raise typer.Exit(1)
    
    name_lower = name.lower().replace("policy", "")
    name_pascal = name[0].upper() + name[1:] if name else name
    if name_pascal.endswith("Policy"):
        name_pascal = name_pascal[:-6]
    
    console.print(f"\n🔐 [bold blue]Creating policy: {name_pascal}Policy[/bold blue]\n")
    
    content = f'''"""
{name_pascal}Policy - Authorization rules for {name_pascal}.
"""
from typing import Any


class {name_pascal}Policy:
    """
    Authorization policy for {name_pascal} resource.
    
    Defines who can perform which actions on {name_pascal}.
    
    Usage:
        policy = {name_pascal}Policy()
        if policy.can_edit(user, post):
            # allow edit
    """
    
    def can_view(self, user: Any, resource: Any) -> bool:
        """Check if user can view the resource."""
        # Public resources can be viewed by anyone
        return True
    
    def can_create(self, user: Any) -> bool:
        """Check if user can create new resources."""
        # Any authenticated user can create
        return user is not None
    
    def can_edit(self, user: Any, resource: Any) -> bool:
        """Check if user can edit the resource."""
        if user is None:
            return False
        # Owner or admin can edit
        return (
            getattr(resource, 'owner_id', None) == getattr(user, 'id', None)
            or getattr(user, 'is_admin', False)
        )
    
    def can_delete(self, user: Any, resource: Any) -> bool:
        """Check if user can delete the resource."""
        # Same as edit
        return self.can_edit(user, resource)
'''
    
    _write_file(Path(f"backend/internal/policies/{name_lower}_policy.py"), content, force)
    
    console.print(f"\n[green]✅ Policy {name_pascal}Policy created![/green]")
    console.print("\nUsage:")
    console.print(f"   from internal.policies.{name_lower}_policy import {name_pascal}Policy")
    console.print(f"   if {name_pascal}Policy().can_edit(user, {name_lower}):")
    console.print("       # allow action")

