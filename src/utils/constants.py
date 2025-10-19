"""Constants and enums for the IT Technician Agent"""

# Priority levels
PRIORITY_LEVELS = [
    "low",
    "medium",
    "high",
    "urgent",
    "critical"
]

# Ticket statuses
TICKET_STATUSES = [
    "new",
    "open",
    "in_progress",
    "pending",
    "resolved",
    "closed",
    "cancelled"
]

# Activity types for worklog entries
ACTIVITY_TYPES = [
    "investigation",
    "diagnosis",
    "solution_implementation",
    "testing",
    "communication",
    "documentation",
    "escalation",
    "follow_up"
]

# Time periods for analytics
DATE_RANGES = {
    "last_7_days": 7,
    "last_30_days": 30,
    "last_90_days": 90,
    "last_6_months": 180,
    "last_year": 365
}

# SLA thresholds (in hours)
SLA_THRESHOLDS = {
    "critical": 1,
    "urgent": 4,
    "high": 8,
    "medium": 24,
    "low": 72
}

# Default agent configuration
DEFAULT_AGENT_CONFIG = {
    "max_tokens": 1024,
    "temperature": 0.7,
    "model": "claude-3-sonnet-20240229"
}

# API rate limits
API_RATE_LIMITS = {
    "requests_per_minute": 60,
    "requests_per_hour": 1000
}

# File size limits
FILE_SIZE_LIMITS = {
    "max_log_file_size": 100 * 1024 * 1024,  # 100MB
    "max_attachment_size": 25 * 1024 * 1024   # 25MB
}

# Regex patterns
PATTERNS = {
    "ticket_number": r"^[A-Z]{2,3}-\d{4,6}$",
    "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    "phone": r"^\+?1?-?\s?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$"
}
