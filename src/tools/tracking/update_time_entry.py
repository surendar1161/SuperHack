"""Update time entry tool for IT Technician Agent - Strands Compatible"""

from typing import Any, Dict, Optional
from strands import tool

from ...clients.superops_client import SuperOpsClient
from ...utils.logger import get_logger

logger = get_logger("update_time_entry")


@tool
async def update_time_entry(
    timer_id: str,
    notes: Optional[str] = None,
    billable: Optional[bool] = None,
    running: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Update an existing worklog timer entry in SuperOps
    
    Args:
        timer_id: The ID of the timer entry to update
        notes: Updated description/notes for the time entry
        billable: Whether this time should be billed to the customer (True/False)
        running: Whether the timer should be running (True) or stopped (False)
        
    Returns:
        Dictionary containing update results with success status and timer details
    """
    try:
        logger.info(f"Updating timer entry: {timer_id}")
        
        # Initialize SuperOps client (in real implementation, this would be injected)
        from ...agents.config import AgentConfig
        config = AgentConfig()
        client = SuperOpsClient(config)
        
        # Build update data from provided parameters
        update_data = {}
        
        if notes is not None:
            update_data["notes"] = notes
        if billable is not None:
            update_data["billable"] = billable
        if running is not None:
            update_data["running"] = running
        
        if not update_data:
            raise ValueError("At least one field must be provided for update (notes, billable, or running)")
        
        # Update timer entry via SuperOps client
        result = await client.update_time_entry(timer_id, update_data)
        
        logger.info(f"Successfully updated timer entry: {timer_id}")
        
        return {
            "success": True,
            "timer_id": timer_id,
            "updated_fields": list(update_data.keys()),
            "notes": result.get("notes"),
            "billable": result.get("billable"),
            "running": result.get("running"),
            "time_spent": result.get("time_spent"),
            "segments": result.get("segments", []),
            "message": f"Timer entry {timer_id} updated successfully",
            "data": result
        }
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to update timer entry - validation error"
        }
    except Exception as e:
        logger.error(f"Failed to update timer entry: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to update timer entry {timer_id}"
        }


@tool
async def stop_timer(
    timer_id: str,
    final_notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Stop a running timer entry
    
    Args:
        timer_id: The ID of the timer entry to stop
        final_notes: Optional final notes to add when stopping the timer
        
    Returns:
        Dictionary containing stop results with success status and timer details
    """
    try:
        logger.info(f"Stopping timer: {timer_id}")
        
        # Build update data to stop the timer
        update_data = {"running": False}
        
        if final_notes:
            update_data["notes"] = final_notes
        
        # Use the update_time_entry function to stop the timer
        result = await update_time_entry(
            timer_id=timer_id,
            running=False,
            notes=final_notes
        )
        
        if result["success"]:
            result["message"] = f"Timer {timer_id} stopped successfully"
            logger.info(f"Successfully stopped timer: {timer_id}")
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to stop timer: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to stop timer {timer_id}"
        }


@tool
async def update_timer_notes(
    timer_id: str,
    notes: str
) -> Dict[str, Any]:
    """
    Update only the notes/description of a timer entry
    
    Args:
        timer_id: The ID of the timer entry to update
        notes: New notes/description for the timer entry
        
    Returns:
        Dictionary containing update results with success status and timer details
    """
    try:
        logger.info(f"Updating notes for timer: {timer_id}")
        
        # Use the update_time_entry function to update notes only
        result = await update_time_entry(
            timer_id=timer_id,
            notes=notes
        )
        
        if result["success"]:
            result["message"] = f"Timer notes updated successfully"
            logger.info(f"Successfully updated notes for timer: {timer_id}")
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to update timer notes: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to update notes for timer {timer_id}"
        }


@tool
async def toggle_timer_billable(
    timer_id: str,
    billable: bool,
    reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update the billable status of a timer entry
    
    Args:
        timer_id: The ID of the timer entry to update
        billable: Whether the time should be billable (True) or non-billable (False)
        reason: Optional reason for changing the billable status
        
    Returns:
        Dictionary containing update results with success status and timer details
    """
    try:
        logger.info(f"Updating billable status for timer: {timer_id} to {billable}")
        
        # Build update data
        update_data = {"billable": billable}
        notes = None
        
        if reason:
            notes = f"Billable status changed to {billable}: {reason}"
        
        # Use the update_time_entry function to update billable status
        result = await update_time_entry(
            timer_id=timer_id,
            billable=billable,
            notes=notes
        )
        
        if result["success"]:
            status = "billable" if billable else "non-billable"
            result["message"] = f"Timer marked as {status} successfully"
            logger.info(f"Successfully updated billable status for timer: {timer_id}")
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to update timer billable status: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to update billable status for timer {timer_id}"
        }