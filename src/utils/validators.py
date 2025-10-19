"""Input validators for the IT Technician Agent"""

import re
from typing import Any, Dict, List, Optional
from email_validator import validate_email as _validate_email, EmailNotValidError

def validate_ticket_data(ticket_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """Validate ticket creation/update data"""
    errors = {}

    # Required fields validation
    if not ticket_data.get("title"):
        errors.setdefault("title", []).append("Title is required")
    elif len(ticket_data["title"]) < 5:
        errors.setdefault("title", []).append("Title must be at least 5 characters")

    if not ticket_data.get("description"):
        errors.setdefault("description", []).append("Description is required")
    elif len(ticket_data["description"]) < 10:
        errors.setdefault("description", []).append("Description must be at least 10 characters")

    # Priority validation
    if ticket_data.get("priority") and not validate_priority(ticket_data["priority"]):
        errors.setdefault("priority", []).append("Invalid priority level")

    # Email validation
    if ticket_data.get("requester_email") and not validate_email(ticket_data["requester_email"]):
        errors.setdefault("requester_email", []).append("Invalid email format")

    return errors

def validate_email(email: str) -> bool:
    """Validate email address format"""
    try:
        _validate_email(email)
        return True
    except EmailNotValidError:
        return False

def validate_priority(priority: str) -> bool:
    """Validate priority level"""
    from .constants import PRIORITY_LEVELS
    return priority.lower() in PRIORITY_LEVELS

def validate_ticket_status(status: str) -> bool:
    """Validate ticket status"""
    from .constants import TICKET_STATUSES
    return status.lower() in TICKET_STATUSES

def validate_time_entry(time_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """Validate time entry data"""
    errors = {}

    if not time_data.get("ticket_id"):
        errors.setdefault("ticket_id", []).append("Ticket ID is required")

    time_spent = time_data.get("time_spent", 0)
    if not isinstance(time_spent, (int, float)) or time_spent <= 0:
        errors.setdefault("time_spent", []).append("Time spent must be a positive number")
    elif time_spent > 24 * 60:  # More than 24 hours
        errors.setdefault("time_spent", []).append("Time spent cannot exceed 24 hours")

    return errors

def validate_worklog_data(worklog_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """Validate worklog entry data"""
    errors = {}

    if not worklog_data.get("ticket_id"):
        errors.setdefault("ticket_id", []).append("Ticket ID is required")

    if not worklog_data.get("activity_type"):
        errors.setdefault("activity_type", []).append("Activity type is required")

    if not worklog_data.get("description"):
        errors.setdefault("description", []).append("Description is required")
    elif len(worklog_data["description"]) < 5:
        errors.setdefault("description", []).append("Description must be at least 5 characters")

    return errors
