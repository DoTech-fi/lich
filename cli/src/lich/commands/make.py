"""
lich make - Code generation commands (like Laravel Artisan).
"""
from pathlib import Path
from datetime import datetime

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
    console.print(f"   1. Register router in backend/main.py")
    console.print(f"   2. Add request/response DTOs")


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
