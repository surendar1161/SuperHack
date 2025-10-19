"""Memory data models"""

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class InteractionContext(BaseModel):
    """Context information for agent interactions"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ticket_id: Optional[str] = None
    interaction_type: str = "general"
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MemoryEntry(BaseModel):
    """Individual memory entry"""
    id: str
    content: str
    context: InteractionContext
    timestamp: datetime
    ttl: datetime
    
class TicketContext(BaseModel):
    """Ticket-specific context data"""
    ticket_id: str
    summary: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    related_tickets: list = Field(default_factory=list)
    knowledge_base_articles: list = Field(default_factory=list)
    interaction_history: list = Field(default_factory=list)

class WorklogEntry(BaseModel):
    """Worklog entry model"""
    id: str
    ticket_id: str
    activity_type: str
    description: str
    time_spent: float  # in hours
    timestamp: datetime
    user_id: Optional[str] = None
