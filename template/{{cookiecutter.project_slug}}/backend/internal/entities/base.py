"""
Base Entity - Pure domain model.
NO external dependencies (no SQLAlchemy, no Pydantic).
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class BaseEntity:
    """
    Base class for all domain entities.
    
    IMPORTANT: This is a PURE domain model.
    - No ORM decorators
    - No Pydantic validators
    - No HTTP-related code
    
    All business rules and invariants should be enforced here.
    """
    
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate invariants after initialization."""
        self._validate()
    
    def _validate(self):
        """
        Override in subclasses to enforce domain invariants.
        Raise ValueError for validation failures.
        """
        pass
    
    def touch(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
