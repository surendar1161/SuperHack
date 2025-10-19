"""Resolve ticket tool for IT Technician Agent - Strands Compatible"""

from typing import Any, Dict, Optional
from strands import tool

from ...clients.superops_client import SuperOpsClient
from ...utils.logger import get_logger

logger = get_logger("resolve_ticket")

@tool
async def resolve_ticket(
    ticket_id: str,
    resolution: str,
    time_spent: float = 0,
    resolution_category: str = "Fixed",
    customer_satisfaction: Optional[str] = None,
    follow_up_required: bool = False,
    knowledge_base_update: bool = False
) -> Dict[str, Any]:
    """
    Resolve and close a support ticket with a solution description
    
    Args:
        ticket_id: The ID or number of the ticket to resolve
        resolution: Detailed description of how the issue was resolved or what actions were taken
        time_spent: Time spent resolving the ticket in hours (e.g., 1.5 for 1 hour 30 minutes)
        resolution_category: Category of resolution - Fixed, Workaround, User Error, Duplicate, Cannot Reproduce, By Design
        customer_satisfaction: Expected customer satisfaction level - Very Satisfied, Satisfied, Neutral, Dissatisfied
        follow_up_required: Whether follow-up is required to ensure the solution is working
        knowledge_base_update: Whether this resolution should be added to the knowledge base
        
    Returns:
        Dictionary containing resolution results with success status and details
    """
    try:
        logger.info(f"Resolving ticket {ticket_id}")
        
        # Initialize SuperOps client (in real implementation, this would be injected)
        from ...agents.config import AgentConfig
        config = AgentConfig()
        client = SuperOpsClient(config)

        # Resolve the ticket
        result = await client.resolve_ticket(
            ticket_id=ticket_id,
            resolution=resolution,
            time_spent=time_spent
        )

        # Log time entry if time was spent
        if time_spent > 0:
            try:
                await client.log_time_entry({
                    "ticket_id": ticket_id,
                    "duration": time_spent,
                    "description": f"Resolution: {resolution[:100]}...",
                    "billable": True
                })
            except Exception as e:
                logger.warning(f"Failed to log time entry: {e}")

        # Add resolution details as work log
        try:
            await client.add_work_log({
                "ticket_id": ticket_id,
                "description": f"RESOLVED: {resolution}",
                "time_spent": time_spent,
                "visibility": "internal"
            })
        except Exception as e:
            logger.warning(f"Failed to add work log: {e}")

        logger.info(f"Successfully resolved ticket: {ticket_id}")

        return {
            "success": True,
            "ticket_id": ticket_id,
            "resolution": resolution,
            "time_spent": time_spent,
            "resolution_category": resolution_category,
            "follow_up_required": follow_up_required,
            "knowledge_base_update": knowledge_base_update,
            "message": f"Ticket {ticket_id} resolved successfully",
            "data": result
        }

    except Exception as e:
        logger.error(f"Failed to resolve ticket: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to resolve ticket {ticket_id}"
        }