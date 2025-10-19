"""Track time tool for IT Technician Agent - Strands Compatible"""

from typing import Any, Dict, Optional
from datetime import datetime, timedelta
from strands import tool

from ...clients.superops_client import SuperOpsClient
from ...utils.logger import get_logger

logger = get_logger("track_time")
def _calculate_start_time(duration: float, end_time: Optional[str] = None) -> str:
    """Calculate start time based on duration and end time"""
    if end_time:
        try:
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        except ValueError:
            end_dt = datetime.now()
    else:
        end_dt = datetime.now()
    
    start_dt = end_dt - timedelta(hours=duration)
    return start_dt.isoformat()

def _validate_duration(duration: float) -> bool:
    """Validate that duration is reasonable"""
    if duration <= 0:
        raise ValueError("Duration must be greater than 0")
    if duration > 24:
        raise ValueError("Duration cannot exceed 24 hours")
    return True

def _format_time_entry(**kwargs) -> Dict[str, Any]:
    """Format time entry data for SuperOps API"""
    duration = kwargs["duration"]
    description = kwargs["description"]
    activity_type = kwargs.get("activity_type", "Troubleshooting")
    billable = kwargs.get("billable", True)
    internal_notes = kwargs.get("internal_notes", "")

    # Format description with activity type and internal notes
    formatted_description = f"[{activity_type}] {description}"
    if internal_notes:
        formatted_description += f" | Notes: {internal_notes}"

    time_entry = {
        "ticket_id": kwargs["ticket_id"],
        "duration": duration,
        "description": formatted_description,
        "billable": billable,
        "activity_type": activity_type
    }

    return time_entry

@tool
async def track_time(
    ticket_id: str,
    duration: float = None,
    time_spent: float = None,  # Backward compatibility
    description: str = "Time tracking entry",
    activity_type: str = "Troubleshooting",
    billable: bool = True,
    start_time: Optional[str] = None,
    technician_id: Optional[str] = None,
    internal_notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Track time spent working on tickets or IT tasks
    
    Args:
        ticket_id: The ID or number of the ticket to track time for
        duration: Time spent in hours (e.g., 1.5 for 1 hour 30 minutes, 0.25 for 15 minutes)
        description: Description of the work performed during this time
        activity_type: Type of activity - Research, Troubleshooting, Implementation, Testing, Documentation, Communication
        billable: Whether this time should be billed to the customer
        start_time: Start time in ISO format (YYYY-MM-DDTHH:MM:SS) - if not provided, uses current time minus duration
        technician_id: ID of the technician who performed the work (defaults to current user)
        internal_notes: Internal notes about the work (not visible to customer)
        
    Returns:
        Dictionary containing time tracking results with success status and details
    """
    try:
        # Handle backward compatibility
        if time_spent and not duration:
            duration = time_spent / 60.0  # Convert minutes to hours
        elif not duration:
            duration = 1.0  # Default to 1 hour
        
        logger.info(f"Tracking {duration} hours for ticket {ticket_id}")
        
        # Validate duration
        _validate_duration(duration)

        # Initialize SuperOps client (in real implementation, this would be injected)
        from ...agents.config import AgentConfig
        config = AgentConfig()
        client = SuperOpsClient(config)

        # Format time entry
        time_entry = _format_time_entry(
            ticket_id=ticket_id,
            duration=duration,
            description=description,
            activity_type=activity_type,
            billable=billable,
            start_time=start_time,
            technician_id=technician_id,
            internal_notes=internal_notes
        )

        # Log time entry via SuperOps client
        result = await client.log_time_entry(time_entry)

        # Calculate some metrics
        hours = int(duration)
        minutes = int((duration - hours) * 60)
        time_formatted = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

        logger.info(f"Tracked {time_formatted} for ticket {ticket_id}")

        return {
            "success": True,
            "ticket_id": ticket_id,
            "duration": duration,
            "duration_hours": duration,
            "duration_minutes": int(duration * 60),
            "duration_formatted": time_formatted,
            "description": description,
            "activity_type": activity_type,
            "billable": billable,
            "timer_id": result.get("timer_id"),
            "time_entry_id": result.get("id"),
            "running": result.get("running", False),
            "segments": result.get("segments", []),
            "message": f"Tracked {time_formatted} for ticket {ticket_id}",
            "data": result
        }

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to track time - validation error"
        }
    except Exception as e:
        logger.error(f"Failed to track time: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to track time for ticket {ticket_id}"
        }