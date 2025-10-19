"""User data models"""

from typing import Optional, List
from enum import Enum
from pydantic import Field
from .common import BaseModel, TimestampMixin

class UserRole(str, Enum):
    ADMIN = "admin"
    TECHNICIAN = "technician"
    MANAGER = "manager"
    USER = "user"

class User(TimestampMixin):
    """User model"""
    id: str
    email: str
    first_name: str
    last_name: str
    role: UserRole = UserRole.USER
    department: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool = True
    skills: List[str] = Field(default_factory=list)
    max_concurrent_tickets: int = 10

    @property
    def full_name(self) -> str:
        """Get full name"""
        return f"{self.first_name} {self.last_name}"

    def can_handle_priority(self, priority: str) -> bool:
        """Check if user can handle tickets of given priority"""
        if self.role == UserRole.ADMIN:
            return True
        elif self.role == UserRole.TECHNICIAN:
            return priority.lower() in ["low", "medium", "high"]
        return False
