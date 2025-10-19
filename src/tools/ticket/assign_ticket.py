"""Assign ticket tool for IT Technician Agent - Strands Compatible"""

from typing import Any, Dict, Optional
from strands import tool

from ...clients.superops_client import SuperOpsClient
from ...utils.logger import get_logger

logger = get_logger("assign_ticket")


@tool
async def assign_ticket(
    ticket_id: str,
    assignee: str,
    notes: Optional[str] = None,
    priority_adjustment: Optional[str] = None,
    notify_assignee: bool = True
) -> Dict[str, Any]:
    """
    Assign a support ticket to a specific technician or team member
    
    Args:
        ticket_id: The ID or number of the ticket to assign
        assignee: ID, email, or name of the technician to assign the ticket to
        notes: Optional notes about why this assignment was made or any special instructions
        priority_adjustment: Optionally adjust priority when assigning - LOW, MEDIUM, HIGH, URGENT, CRITICAL
        notify_assignee: Whether to send notification to the assignee (default: true)
        
    Returns:
        Dictionary containing assignment results with success status and details
    """
    try:
        logger.info(f"Assigning ticket {ticket_id} to {assignee}")
        
        # Initialize SuperOps client (in real implementation, this would be injected)
        from ...agents.config import AgentConfig
        config = AgentConfig()
        client = SuperOpsClient(config)
        
        # First, assign the ticket
        result = await client.assign_ticket(
            ticket_id=ticket_id,
            assignee=assignee,
            notes=notes or ""
        )
        
        # If priority adjustment is requested, update the ticket
        if priority_adjustment:
            priority_str = priority_adjustment.upper()
            if priority_str in ["LOW", "MEDIUM", "HIGH", "URGENT", "CRITICAL"]:
                await client.update_ticket(ticket_id, {
                    "priority": priority_str.lower()
                })
        
        logger.info(f"Successfully assigned ticket {ticket_id} to {assignee}")
        
        return {
            "success": True,
            "ticket_id": ticket_id,
            "assignee": assignee,
            "message": f"Ticket {ticket_id} assigned to {assignee}",
            "notes": notes or "",
            "priority_adjusted": priority_adjustment is not None,
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Failed to assign ticket: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to assign ticket {ticket_id}"
        }


