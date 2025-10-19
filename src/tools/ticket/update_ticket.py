"""Update ticket tool for IT Technician Agent - Strands Compatible"""

from typing import Any, Dict, Optional
from strands import tool

from ...clients.superops_client import SuperOpsClient
from ...models.ticket import TicketUpdate, Priority, TicketStatus
from ...utils.logger import get_logger

logger = get_logger("update_ticket")


@tool
async def update_ticket(
    ticket_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    notes: Optional[str] = None,
    assigned_to: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update an existing support ticket in SuperOps
    
    Args:
        ticket_id: The ID or number of the ticket to update
        title: Updated title/subject of the ticket (optional)
        description: Updated description or additional information (optional)
        priority: Updated priority level - LOW, MEDIUM, HIGH, URGENT, CRITICAL (optional)
        status: Updated status - NEW, OPEN, IN_PROGRESS, PENDING, RESOLVED, CLOSED (optional)
        category: Updated category - Hardware, Software, Network, Email, Security, Account (optional)
        notes: Additional notes or comments about the update (optional)
        assigned_to: ID or email of technician to assign the ticket to (optional)
        
    Returns:
        Dictionary containing update results with success status and updated fields
    """
    try:
        logger.info(f"Updating ticket: {ticket_id}")
        
        # Use session manager for proper cleanup
        from ...utils.session_manager import get_superops_client
        
        async with get_superops_client() as client:
            # Build update data
            update_data = {}
            
            if title:
                update_data["subject"] = title
            if description:
                update_data["description"] = description
            if priority:
                priority_str = priority.upper()
                if priority_str in Priority.__members__:
                    update_data["priority"] = priority_str.lower()
            if status:
                status_str = status.upper()
                if status_str in TicketStatus.__members__:
                    update_data["status"] = status_str.lower()
            if category:
                update_data["category"] = category
            if assigned_to:
                update_data["technician"] = {
                    "userId": assigned_to
                }
            if notes:
                update_data["notes"] = notes
            
            # Update ticket via SuperOps client
            result = await client.update_ticket(ticket_id, update_data)
        
            logger.info(f"Successfully updated ticket: {ticket_id}")
            
            return {
                "success": True,
                "ticket_id": ticket_id,
                "message": f"Ticket {ticket_id} updated successfully",
                "updated_fields": list(update_data.keys()),
                "data": result
            }
        
    except Exception as e:
        logger.error(f"Failed to update ticket: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to update ticket {ticket_id}"
        }

