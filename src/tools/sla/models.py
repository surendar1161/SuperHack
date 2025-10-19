"""
SLA Data Models

Defines all data structures used in the SLA management system.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from enum import Enum


class SLAPriority(Enum):
    """SLA priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BreachType(Enum):
    """Types of SLA breaches"""
    RESPONSE = "response"
    RESOLUTION = "resolution"


class RiskLevel(Enum):
    """SLA breach risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PerformanceTrend(Enum):
    """Performance trend indicators"""
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class EscalationRule:
    """Defines escalation rules for SLA breaches"""
    id: str
    name: str
    trigger_after_minutes: int
    escalate_to_role: str
    escalate_to_users: List[str] = field(default_factory=list)
    notification_template: str = ""
    is_active: bool = True


@dataclass
class AlertRule:
    """Defines alert rules for SLA monitoring"""
    id: str
    name: str
    condition: str  # e.g., "time_remaining < 30"
    severity: AlertSeverity
    notification_channels: List[str] = field(default_factory=list)
    is_active: bool = True
    cooldown_minutes: int = 15


@dataclass
class SLAPolicy:
    """SLA policy configuration"""
    id: str
    name: str
    description: str
    priority_level: SLAPriority
    response_time_minutes: int
    resolution_time_hours: int
    business_hours_only: bool = True
    escalation_rules: List[EscalationRule] = field(default_factory=list)
    alert_rules: List[AlertRule] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate SLA policy data"""
        if self.response_time_minutes <= 0:
            raise ValueError("Response time must be positive")
        if self.resolution_time_hours <= 0:
            raise ValueError("Resolution time must be positive")
        if self.response_time_minutes >= (self.resolution_time_hours * 60):
            raise ValueError("Response time must be less than resolution time")


@dataclass
class TicketSLAStatus:
    """Current SLA status for a specific ticket"""
    ticket_id: str
    ticket_number: str
    sla_policy: SLAPolicy
    created_at: datetime
    first_response_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    response_time_remaining: Optional[timedelta] = None
    resolution_time_remaining: Optional[timedelta] = None
    is_response_breached: bool = False
    is_resolution_breached: bool = False
    breach_risk_level: RiskLevel = RiskLevel.LOW
    escalation_level: int = 0
    last_updated: datetime = field(default_factory=datetime.now)
    
    @property
    def is_breached(self) -> bool:
        """Check if any SLA is breached"""
        return self.is_response_breached or self.is_resolution_breached
    
    @property
    def response_time_elapsed(self) -> timedelta:
        """Calculate elapsed response time"""
        if self.first_response_at:
            return self.first_response_at - self.created_at
        return datetime.now() - self.created_at
    
    @property
    def resolution_time_elapsed(self) -> Optional[timedelta]:
        """Calculate elapsed resolution time"""
        if self.resolved_at:
            return self.resolved_at - self.created_at
        return datetime.now() - self.created_at


@dataclass
class TechnicianSLAMetrics:
    """SLA performance metrics for a technician"""
    technician_id: str
    technician_name: str
    technician_email: str
    period_start: datetime
    period_end: datetime
    total_tickets: int = 0
    sla_compliant_tickets: int = 0
    response_breaches: int = 0
    resolution_breaches: int = 0
    average_response_time: Optional[timedelta] = None
    average_resolution_time: Optional[timedelta] = None
    performance_trend: PerformanceTrend = PerformanceTrend.STABLE
    last_updated: datetime = field(default_factory=datetime.now)
    
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


@dataclass
class SLABreach:
    """Represents an SLA breach incident"""
    id: str
    ticket_id: str
    ticket_number: str
    breach_type: BreachType
    breach_time: datetime
    sla_policy: SLAPolicy
    technician_id: Optional[str] = None
    technician_name: Optional[str] = None
    severity: AlertSeverity = AlertSeverity.WARNING
    customer_impact: str = "medium"
    escalation_required: bool = False
    escalation_level: int = 0
    resolution_time: Optional[datetime] = None
    root_cause: Optional[str] = None
    corrective_actions: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def is_resolved(self) -> bool:
        """Check if breach is resolved"""
        return self.resolution_time is not None
    
    @property
    def breach_duration(self) -> timedelta:
        """Calculate breach duration"""
        end_time = self.resolution_time or datetime.now()
        return end_time - self.breach_time


@dataclass
class SLAReportData:
    """Data structure for SLA report sections"""
    total_tickets: int = 0
    sla_compliant_tickets: int = 0
    response_breaches: int = 0
    resolution_breaches: int = 0
    average_response_time: Optional[timedelta] = None
    average_resolution_time: Optional[timedelta] = None
    compliance_rate: float = 0.0
    breach_rate: float = 0.0


@dataclass
class SLAReport:
    """Comprehensive SLA performance report"""
    id: str
    report_name: str
    period_start: datetime
    period_end: datetime
    generated_at: datetime = field(default_factory=datetime.now)
    
    # Overall metrics
    overall_metrics: SLAReportData = field(default_factory=SLAReportData)
    
    # Breakdown by priority
    metrics_by_priority: Dict[str, SLAReportData] = field(default_factory=dict)
    
    # Breakdown by technician
    metrics_by_technician: Dict[str, TechnicianSLAMetrics] = field(default_factory=dict)
    
    # Breach incidents
    breach_incidents: List[SLABreach] = field(default_factory=list)
    
    # Top performers
    top_performers: List[str] = field(default_factory=list)
    
    # Areas for improvement
    improvement_areas: List[str] = field(default_factory=list)
    
    # Trends and insights
    trends: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def total_breaches(self) -> int:
        """Calculate total number of breaches"""
        return len(self.breach_incidents)
    
    @property
    def critical_breaches(self) -> int:
        """Calculate number of critical breaches"""
        return len([b for b in self.breach_incidents if b.severity == AlertSeverity.CRITICAL])


@dataclass
class DateRange:
    """Date range for queries and reports"""
    start_date: datetime
    end_date: datetime
    
    def __post_init__(self):
        """Validate date range"""
        if self.start_date >= self.end_date:
            raise ValueError("Start date must be before end date")
    
    @property
    def duration(self) -> timedelta:
        """Calculate duration of the date range"""
        return self.end_date - self.start_date
    
    def contains(self, date: datetime) -> bool:
        """Check if date falls within the range"""
        return self.start_date <= date <= self.end_date