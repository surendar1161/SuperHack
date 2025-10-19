"""Data formatters for the IT Technician Agent"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import re

def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime object to string"""
    return dt.strftime(format_str)

def format_duration(minutes: float) -> str:
    """Format duration in minutes to human readable format"""
    if minutes < 60:
        return f"{int(minutes)} minutes"
    elif minutes < 1440:  # Less than 24 hours
        hours = minutes / 60
        return f"{hours:.1f} hours"
    else:
        days = minutes / 1440
        return f"{days:.1f} days"

def format_ticket_summary(ticket: Dict[str, Any]) -> str:
    """Format ticket data into a readable summary"""
    summary = f"Ticket #{ticket.get('number', 'N/A')}: {ticket.get('title', 'No Title')}\n"
    summary += f"Status: {ticket.get('status', 'Unknown')}\n"
    summary += f"Priority: {ticket.get('priority', 'Unknown')}\n"
    summary += f"Assigned to: {ticket.get('assigned_to', 'Unassigned')}\n"

    if ticket.get('created_at'):
        created = datetime.fromisoformat(ticket['created_at'])
        summary += f"Created: {format_datetime(created)}\n"

    if ticket.get('description'):
        desc = ticket['description'][:100] + "..." if len(ticket['description']) > 100 else ticket['description']
        summary += f"Description: {desc}"

    return summary

def format_time_entry(entry: Dict[str, Any]) -> str:
    """Format time entry for display"""
    time_str = format_duration(entry.get('time_spent', 0))
    desc = entry.get('description', 'No description')
    date = entry.get('date', 'Unknown date')

    return f"{time_str} on {date}: {desc}"

def format_analytics_report(report_data: Dict[str, Any]) -> str:
    """Format analytics report for display"""
    report_type = report_data.get('report_type', 'Analytics Report')
    date_range = report_data.get('date_range', 'Unknown period')

    formatted = f"=== {report_type.title()} Report ({date_range}) ===\n\n"

    analytics = report_data.get('analytics_data', {})

    if 'total_tickets' in analytics:
        formatted += f"Total Tickets: {analytics['total_tickets']}\n"
        formatted += f"Resolved Tickets: {analytics.get('resolved_tickets', 0)}\n"
        formatted += f"Resolution Rate: {analytics.get('resolution_rate', 0):.1f}%\n"
        formatted += f"Avg Resolution Time: {format_duration(analytics.get('avg_resolution_time_hours', 0) * 60)}\n\n"

    if 'priority_breakdown' in analytics:
        formatted += "Priority Breakdown:\n"
        for priority, count in analytics['priority_breakdown'].items():
            formatted += f"  {priority.title()}: {count}\n"

    return formatted

def format_error_message(error: Exception, context: Optional[str] = None) -> str:
    """Format error message for user display"""
    error_msg = f"Error: {str(error)}"
    if context:
        error_msg = f"{context} - {error_msg}"
    return error_msg

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove multiple underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    # Trim and limit length
    return sanitized.strip('_')[:100]

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix
