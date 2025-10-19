"""Ticket data models"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import Field
from .common import BaseModel, TimestampMixin

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

class TicketStatus(str, Enum):
    NEW = "new"
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"
    RESOLVED = "resolved"
    CLOSED = "closed"
    CANCELLED = "cancelled"

# Alias for backward compatibility
Status = TicketStatus

class TicketCreate(BaseModel):
    """Model for creating new tickets"""
    title: str
    description: str
    priority: Priority = Priority.MEDIUM
    status: TicketStatus = TicketStatus.OPEN
    category: Optional[str] = None
    requester_email: Optional[str] = None
    assigned_to: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)

class TicketUpdate(BaseModel):
    """Model for updating existing tickets"""
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[Priority] = None
    status: Optional[TicketStatus] = None
    category: Optional[str] = None
    assigned_to: Optional[str] = None
    resolution: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    time_spent: Optional[float] = None

class Ticket(TimestampMixin):
    """Ticket model"""
    id: str
    number: str
    title: str
    description: str
    priority: Priority = Priority.MEDIUM
    status: TicketStatus = TicketStatus.NEW
    category: Optional[str] = None
    requester_email: Optional[str] = None
    assigned_to: Optional[str] = None
    resolution: Optional[str] = None
    resolution_time: Optional[float] = None  # in hours
    first_response_time: Optional[float] = None  # in hours
    reopened_count: int = 0
    escalated: bool = False
    tags: List[str] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    resolved_at: Optional[datetime] = None

    def is_overdue(self, sla_hours: int = 24) -> bool:
        """Check if ticket is overdue based on SLA"""
        if self.status in [TicketStatus.RESOLVED, TicketStatus.CLOSED]:
            return False

        hours_since_creation = (datetime.now() - self.created_at).total_seconds() / 3600
        return hours_since_creation > sla_hours

    def calculate_resolution_time(self) -> Optional[float]:
        """Calculate resolution time in hours"""
        if self.resolved_at and self.created_at:
            return (self.resolved_at - self.created_at).total_seconds() / 3600
        return None
