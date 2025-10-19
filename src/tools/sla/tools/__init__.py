"""
SLA Management Tools Package

Strands-compatible Python tools for comprehensive SLA management operations.
Following industry standards and best practices for agent-based systems.
"""

from .sla_calculator import (
    SLACalculatorTool,
    calculate_sla_status,
    calculate_time_remaining,
    check_sla_breach
)
from .breach_detector import (
    BreachDetectorTool,
    detect_sla_breaches,
    predict_sla_breaches,
    analyze_ticket_sla_risk
)
from .escalation_manager import (
    EscalationManagerTool,
    execute_sla_escalation,
    notify_sla_breach,
    escalate_ticket_priority
)

__all__ = [
    # Tool classes
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