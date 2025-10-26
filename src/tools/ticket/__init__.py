"""Ticket management tools for IT Technician Agent - Strands Compatible"""

# Strands tool function imports
from .create_ticket import create_ticket
from .update_ticket import update_ticket
from .assign_ticket import assign_ticket
from .resolve_ticket import resolve_ticket
from .categorize_ticket import (
    categorize_support_request,
    determine_assignment_logic
)
from .notify_technician import (
    notify_technician_assignment,
    notify_sla_alert,
    notify_bottleneck_alert
)
from .create_ticket_note import (
    create_ticket_note,
    add_public_note,
    add_private_note,
    add_investigation_note,
    add_resolution_note,
    add_escalation_note
)

# All exports
__all__ = [
    "create_ticket",
    "update_ticket",
    "assign_ticket",
    "resolve_ticket",
    "categorize_support_request",
    "determine_assignment_logic", 
    "notify_technician_assignment",
    "notify_sla_alert",
    "notify_bottleneck_alert",
    "create_ticket_note",
    "add_public_note",
    "add_private_note",
    "add_investigation_note",
    "add_resolution_note",
    "add_escalation_note"
]