"""
SLA Data Models v2 - Pydantic Implementation

Modern data models using Pydantic 2.0+ for validation, serialization,
and better integration with the tech stack.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field, validator, root_validator
from pydantic.types import PositiveInt, PositiveFloat


class SLAPriority(str, Enum):
    """SLA priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BreachType(str, Enum):
    """Types of SLA breaches"""
    RESPONSE = "response"
    RESOLUTION = "resolution"


class RiskLevel(str, Enum):
    """SLA breach risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class PerformanceTrend(str, Enum):
    """Performance trend indicators"""
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"


class BaseTimestampModel(BaseModel):
    """Base model with timestamp fields"""
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            timedelta: lambda v: v.total_seconds()
        }


class EscalationRule(BaseModel):
    """Defines escalation rules for SLA breaches"""
    id: str
    name: str
    trigger_after_minutes: PositiveInt
    escalate_to_role: str
    escalate_to_users: List[str] = Field(default_factory=list)
    notification_template: str = ""
    is_active: bool = True


class AlertRule(BaseModel):
    """Defines alert rules for SLA monitoring"""
    id: str
    name: str
    condition: str = Field(..., description="e.g., 'time_remaining < 30'")
    severity: AlertSeverity
    notification_channels: List[str] = Field(default_factory=list)
    is_active: bool = True
    cooldown_minutes: PositiveInt = 15


class SLAPolicy(BaseTimestampModel):
    """SLA policy configuration with validation"""
    id: str
    name: str
    description: str = ""
    priority_level: SLAPriority
    response_time_minutes: PositiveInt
    resolution_time_hours: PositiveFloat
    business_hours_only: bool = True
    escalation_rules: List[EscalationRule] = Field(default_factory=list)
    alert_rules: List[AlertRule] = Field(default_factory=list)
    is_active: bool = True
    
    @validator('resolution_time_hours')
    def validate_resolution_time(cls, v, values):
        """Ensure resolution time is greater than response time"""
        response_minutes = values.get('response_time_minutes', 0)
        if v * 60 <= response_minutes:
            raise ValueError('Resolution time must be greater than response time')
        return v
    
    @property
    def resolution_time_minutes(self) -> int:
        """Get resolution time in minutes"""
        return int(self.resolution_time_hours * 60)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Strands tools"""
        return {
            "id": self.id,
            "name": self.name,
            "priority_level": self.priority_level.value,
            "response_time_minutes": self.response_time_minutes,
            "resolution_time_hours": self.resolution_time_hours,
            "business_hours_only": self.business_hours_only,
            "escalation_rules": [rule.dict() for rule in self.escalation_rules]
        }


class TicketSLAStatus(BaseModel):
    """Current SLA status for a specific ticket"""
    ticket_id: str
    ticket_number: str
    sla_policy_id: str
    created_at: datetime
    first_response_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    response_time_remaining_minutes: Optional[int] = None
    resolution_time_remaining_minutes: Optional[int] = None
    is_response_breached: bool = False
    is_resolution_breached: bool = False
    breach_risk_level: RiskLevel = RiskLevel.LOW
    escalation_level: int = Field(0, ge=0)
    last_updated: datetime = Field(default_factory=datetime.now)
    
    @property
    def is_breached(self) -> bool:
        """Check if any SLA is breached"""
        return self.is_response_breached or self.is_resolution_breached
    
    @property
    def response_time_remaining(self) -> Optional[timedelta]:
        """Get response time remaining as timedelta"""
        if self.response_time_remaining_minutes is not None:
            return timedelta(minutes=self.response_time_remaining_minutes)
        return None
    
    @property
    def resolution_time_remaining(self) -> Optional[timedelta]:
        """Get resolution time remaining as timedelta"""
        if self.resolution_time_remaining_minutes is not None:
            return timedelta(minutes=self.resolution_time_remaining_minutes)
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Strands tools"""
        return {
            "ticket_id": self.ticket_id,
            "is_response_breached": self.is_response_breached,
            "is_resolution_breached": self.is_resolution_breached,
            "response_time_remaining_minutes": self.response_time_remaining_minutes,
            "resolution_time_remaining_minutes": self.resolution_time_remaining_minutes,
            "breach_risk_level": self.breach_risk_level.value,
            "escalation_level": self.escalation_level,
            "last_updated": self.last_updated.isoformat()
        }


class SLABreach(BaseTimestampModel):
    """Represents an SLA breach incident"""
    id: str
    ticket_id: str
    ticket_number: str
    breach_type: BreachType
    breach_time: datetime
    sla_policy_id: str
    technician_id: Optional[str] = None
    technician_name: Optional[str] = None
    severity: AlertSeverity = AlertSeverity.WARNING
    customer_impact: str = Field("medium", regex="^(low|medium|high)$")
    escalation_required: bool = False
    escalation_level: int = Field(0, ge=0)
    resolution_time: Optional[datetime] = None
    root_cause: Optional[str] = None
    corrective_actions: List[str] = Field(default_factory=list)
    
    @property
    def is_resolved(self) -> bool:
        """Check if breach is resolved"""
        return self.resolution_time is not None
    
    @property
    def breach_duration_minutes(self) -> int:
        """Calculate breach duration in minutes"""
        end_time = self.resolution_time or datetime.now()
        return int((end_time - self.breach_time).total_seconds() / 60)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Strands tools"""
        return {
            "id": self.id,
            "ticket_id": self.ticket_id,
            "ticket_number": self.ticket_number,
            "breach_type": self.breach_type.value,
            "breach_time": self.breach_time.isoformat(),
            "severity": self.severity.value,
            "customer_impact": self.customer_impact,
            "escalation_required": self.escalation_required,
            "escalation_level": self.escalation_level,
            "technician_id": self.technician_id,
            "technician_name": self.technician_name
        }


class TechnicianSLAMetrics(BaseModel):
    """SLA performance metrics for a technician"""
    technician_id: str
    technician_name: str
    technician_email: str
    period_start: datetime
    period_end: datetime
    total_tickets: int = Field(0, ge=0)
    sla_compliant_tickets: int = Field(0, ge=0)
    response_breaches: int = Field(0, ge=0)
    resolution_breaches: int = Field(0, ge=0)
    average_response_time_minutes: Optional[PositiveFloat] = None
    average_resolution_time_hours: Optional[PositiveFloat] = None
    performance_trend: PerformanceTrend = PerformanceTrend.STABLE
    last_updated: datetime = Field(default_factory=datetime.now)
    
    @validator('sla_compliant_tickets')
    def validate_compliant_tickets(cls, v, values):
        """Ensure compliant tickets don't exceed total"""
        total = values.get('total_tickets', 0)
        if v > total:
            raise ValueError('Compliant tickets cannot exceed total tickets')
        return v
    
    @property
    def compliance_rate(self) -> float:
        """Calculate SLA compliance rate"""
        if self.total_tickets == 0:
            return 0.0
        return (self.sla_compliant_tickets / self.total_tickets) * 100
    
    @property
    def breach_rate(self) -> float:
        """Calculate SLA breach rate"""
        if self.total_tickets == 0:
            return 0.0
        total_breaches = self.response_breaches + self.resolution_breaches
        return (total_breaches / self.total_tickets) * 100


class SuperOpsTicket(BaseModel):
    """SuperOps ticket data model for API integration"""
    id: str
    number: str
    subject: str
    description: Optional[str] = None
    priority: str = "medium"
    status: str = "open"
    category: Optional[str] = None
    created_at: datetime = Field(alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")
    first_response_at: Optional[datetime] = Field(None, alias="firstResponseAt")
    resolved_at: Optional[datetime] = Field(None, alias="resolvedAt")
    assignee: Optional[Dict[str, Any]] = None
    customer: Optional[Dict[str, Any]] = None
    
    class Config:
        allow_population_by_field_name = True
    
    def to_sla_dict(self) -> Dict[str, Any]:
        """Convert to format expected by SLA tools"""
        return {
            "id": self.id,
            "number": self.number,
            "subject": self.subject,
            "priority": self.priority,
            "status": self.status,
            "category": self.category,
            "createdAt": self.created_at.isoformat(),
            "firstResponseAt": self.first_response_at.isoformat() if self.first_response_at else None,
            "resolvedAt": self.resolved_at.isoformat() if self.resolved_at else None,
            "assignee": self.assignee,
            "customer": self.customer
        }


class DateRange(BaseModel):
    """Date range for queries and reports"""
    start_date: datetime
    end_date: datetime
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        """Ensure end date is after start date"""
        start = values.get('start_date')
        if start and v <= start:
            raise ValueError('End date must be after start date')
        return v
    
    @property
    def duration_days(self) -> int:
        """Calculate duration in days"""
        return (self.end_date - self.start_date).days
    
    def contains(self, date: datetime) -> bool:
        """Check if date falls within the range"""
        return self.start_date <= date <= self.end_date


# Factory functions for creating models from SuperOps data
def create_sla_policy_from_superops(data: Dict[str, Any]) -> SLAPolicy:
    """Create SLA policy from SuperOps data"""
    return SLAPolicy(
        id=data.get('id', ''),
        name=data.get('name', ''),
        description=data.get('description', ''),
        priority_level=SLAPriority(data.get('priority_level', 'medium')),
        response_time_minutes=data.get('response_time_minutes', 60),
        resolution_time_hours=data.get('resolution_time_hours', 24),
        business_hours_only=data.get('business_hours_only', True)
    )


def create_ticket_from_superops(data: Dict[str, Any]) -> SuperOpsTicket:
    """Create ticket model from SuperOps API data"""
    return SuperOpsTicket(**data)


def create_sla_status_from_calculation(
    ticket: SuperOpsTicket, 
    policy: SLAPolicy, 
    calculation_result: Dict[str, Any]
) -> TicketSLAStatus:
    """Create SLA status from calculation result"""
    return TicketSLAStatus(
        ticket_id=ticket.id,
        ticket_number=ticket.number,
        sla_policy_id=policy.id,
        created_at=ticket.created_at,
        first_response_at=ticket.first_response_at,
        resolved_at=ticket.resolved_at,
        response_time_remaining_minutes=calculation_result.get('response_time_remaining_minutes'),
        resolution_time_remaining_minutes=calculation_result.get('resolution_time_remaining_minutes'),
        is_response_breached=calculation_result.get('is_response_breached', False),
        is_resolution_breached=calculation_result.get('is_resolution_breached', False),
        breach_risk_level=RiskLevel(calculation_result.get('breach_risk_level', 'low')),
        escalation_level=calculation_result.get('escalation_level', 0)
    )