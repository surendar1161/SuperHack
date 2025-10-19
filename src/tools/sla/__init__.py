"""
SLA Management Tools for SuperOps Integration

This package provides comprehensive SLA (Service Level Agreement) management
capabilities including monitoring, alerting, and reporting.
"""

from .models import (
    SLAPolicy,
    TicketSLAStatus,
    TechnicianSLAMetrics,
    SLABreach,
    SLAReport,
    EscalationRule,
    AlertRule
)

from .exceptions import (
    SLAError,
    SLAPolicyNotFoundError,
    SLACalculationError,
    SLABreachError,
    SLAConfigurationError
)

from .data_access import SLADataAccess

from .tools import (
    SLACalculatorTool,
    BreachDetectorTool,
    EscalationManagerTool,
    calculate_sla_status,
    calculate_time_remaining,
    check_sla_breach,
    detect_sla_breaches,
    predict_sla_breaches,
    analyze_ticket_sla_risk,
    execute_sla_escalation,
    notify_sla_breach,
    escalate_ticket_priority
)

__version__ = "1.0.0"
__all__ = [
    # Models
    "SLAPolicy",
    "TicketSLAStatus", 
    "TechnicianSLAMetrics",
    "SLABreach",
    "SLAReport",
    "EscalationRule",
    "AlertRule",
    
    # Exceptions
    "SLAError",
    "SLAPolicyNotFoundError",
    "SLACalculationError", 
    "SLABreachError",
    "SLAConfigurationError",
    
    # Data Access
    "SLADataAccess",
    
    # Tools
    "SLACalculatorTool",
    "BreachDetectorTool",
    "EscalationManagerTool",
    
    # Strands tool functions
    "calculate_sla_status",
    "calculate_time_remaining", 
    "check_sla_breach",
    "detect_sla_breaches",
    "predict_sla_breaches",
    "analyze_ticket_sla_risk",
    "execute_sla_escalation",
    "notify_sla_breach",
    "escalate_ticket_priority"
]