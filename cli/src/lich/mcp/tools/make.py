from lich.commands.make import (
    make_entity, make_service, make_api, make_dto,
    make_factory, make_middleware, make_event,
    make_listener, make_job, make_policy
)
from lich.commands._validate import ValidationError, validate_identifier

def register_make_tools(mcp):
    """Register Code Generation tools."""

    @mcp.tool()
    def lich_make_service(name: str):
        """Create a new Backend Service (Use Case)."""
        try:
            name = validate_identifier(name)
        except ValidationError as e:
            return f"ERROR: {e}"
        make_service(name)
        return f"Service '{name}' created."

    @mcp.tool()
    def lich_make_entity(name: str):
        """Create a new Domain Entity."""
        try:
            name = validate_identifier(name)
        except ValidationError as e:
            return f"ERROR: {e}"
        make_entity(name)
        return f"Entity '{name}' created."

    @mcp.tool()
    def lich_make_api(name: str):
        """Create a new API Resource (Controller)."""
        try:
            name = validate_identifier(name)
        except ValidationError as e:
            return f"ERROR: {e}"
        make_api(name)
        return f"API '{name}' created."

    @mcp.tool()
    def lich_make_dto(name: str):
        """Create a new Data Transfer Object."""
        try:
            name = validate_identifier(name)
        except ValidationError as e:
            return f"ERROR: {e}"
        make_dto(name)
        return f"DTO '{name}' created."

    @mcp.tool()
    def lich_make_factory(name: str):
        """Create a Test Factory."""
        try:
            name = validate_identifier(name)
        except ValidationError as e:
            return f"ERROR: {e}"
        make_factory(name)
        return f"Factory '{name}' created."

    @mcp.tool()
    def lich_make_middleware(name: str):
        """Create a Middleware."""
        try:
            name = validate_identifier(name)
        except ValidationError as e:
            return f"ERROR: {e}"
        make_middleware(name)
        return f"Middleware '{name}' created."

    @mcp.tool()
    def lich_make_event(name: str):
        """Create a Domain Event."""
        try:
            name = validate_identifier(name)
        except ValidationError as e:
            return f"ERROR: {e}"
        make_event(name)
        return f"Event '{name}' created."

    @mcp.tool()
    def lich_make_listener(name: str, event: str = "SomeEvent"):
        """Create an Event Listener."""
        try:
            name = validate_identifier(name)
        except ValidationError as e:
            return f"ERROR: {e}"
        try:
            event = validate_identifier(event)
        except ValidationError as e:
            return f"ERROR: {e}"
        make_listener(name, event=event)
        return f"Listener '{name}' created for event '{event}'."

    @mcp.tool()
    def lich_make_job(name: str, queue: str = "celery"):
        """Create a Background Job (queue: 'celery' or 'temporal')."""
        try:
            name = validate_identifier(name)
        except ValidationError as e:
            return f"ERROR: {e}"
        make_job(name, queue_type=queue)
        return f"Job '{name}' created."

    @mcp.tool()
    def lich_make_policy(name: str):
        """Create an Authorization Policy."""
        try:
            name = validate_identifier(name)
        except ValidationError as e:
            return f"ERROR: {e}"
        make_policy(name)
        return f"Policy '{name}' created."
