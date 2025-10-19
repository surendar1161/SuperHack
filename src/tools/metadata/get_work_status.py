"""Get work status list tool for IT Technician Agent - Strands Compatible"""

from typing import Any, Dict, List
from strands import tool

from ...clients.superops_client import SuperOpsClient
from ...utils.logger import get_logger

logger = get_logger("get_work_status")


@tool
async def get_work_status_list() -> Dict[str, Any]:
    """
    Get the list of available work statuses from SuperOps metadata
    
    This tool retrieves all available work status options that can be used
    when creating or updating tickets, tasks, and work items in SuperOps.
    
    Returns:
        Dictionary containing:
        - success: Boolean indicating if the operation was successful
        - statuses: List of work status objects with statusId, name, and state
        - count: Number of statuses retrieved
        - message: Success or error message
    """
    try:
        logger.info("Retrieving work status list from SuperOps")
        
        # Initialize SuperOps client (in real implementation, this would be injected)
        from ...agents.config import AgentConfig
        config = AgentConfig()
        client = SuperOpsClient(config)
        
        # Get work status list from SuperOps
        result = await client.get_work_status_list()
        
        if result and result.get("statusList"):
            status_list = result["statusList"]
            count = result.get("count", len(status_list))
            
            logger.info(f"Successfully retrieved {count} work statuses")
            
            # Format the statuses for better readability
            formatted_statuses = []
            for status in status_list:
                formatted_status = {
                    "id": status.get("statusId"),
                    "name": status.get("name"),
                    "state": status.get("state"),
                    "display_name": f"{status.get('name')} ({status.get('state')})"
                }
                formatted_statuses.append(formatted_status)
            
            return {
                "success": True,
                "statuses": formatted_statuses,
                "count": count,
                "message": f"Successfully retrieved {count} work statuses",
                "raw_data": status_list
            }
        else:
            logger.warning("No work statuses found or empty response")
            return {
                "success": False,
                "statuses": [],
                "count": 0,
                "message": "No work statuses found",
                "error": "Empty or invalid response from SuperOps API"
            }
        
    except Exception as e:
        logger.error(f"Failed to get work status list: {str(e)}")
        return {
            "success": False,
            "statuses": [],
            "count": 0,
            "message": "Failed to retrieve work status list",
            "error": str(e)
        }


@tool
async def get_work_status_by_name(status_name: str) -> Dict[str, Any]:
    """
    Get a specific work status by name
    
    Args:
        status_name: Name of the work status to find (case-insensitive)
        
    Returns:
        Dictionary containing the matching work status or error if not found
    """
    try:
        logger.info(f"Looking for work status: {status_name}")
        
        # Get all work statuses
        all_statuses_result = await get_work_status_list()
        
        if not all_statuses_result.get("success"):
            return all_statuses_result
        
        statuses = all_statuses_result.get("statuses", [])
        
        # Search for matching status (case-insensitive)
        matching_status = None
        for status in statuses:
            if status.get("name", "").lower() == status_name.lower():
                matching_status = status
                break
        
        if matching_status:
            logger.info(f"Found work status: {matching_status['name']}")
            return {
                "success": True,
                "status": matching_status,
                "message": f"Found work status: {matching_status['name']}"
            }
        else:
            logger.warning(f"Work status not found: {status_name}")
            available_names = [s.get("name") for s in statuses if s.get("name")]
            return {
                "success": False,
                "status": None,
                "message": f"Work status '{status_name}' not found",
                "available_statuses": available_names,
                "error": f"No work status found with name '{status_name}'"
            }
        
    except Exception as e:
        logger.error(f"Failed to find work status: {str(e)}")
        return {
            "success": False,
            "status": None,
            "message": f"Failed to find work status '{status_name}'",
            "error": str(e)
        }


@tool
async def get_work_status_by_state(state: str) -> Dict[str, Any]:
    """
    Get all work statuses that match a specific state
    
    Args:
        state: State to filter by (e.g., 'OPEN', 'CLOSED', 'IN_PROGRESS')
        
    Returns:
        Dictionary containing matching work statuses
    """
    try:
        logger.info(f"Looking for work statuses with state: {state}")
        
        # Get all work statuses
        all_statuses_result = await get_work_status_list()
        
        if not all_statuses_result.get("success"):
            return all_statuses_result
        
        statuses = all_statuses_result.get("statuses", [])
        
        # Filter by state (case-insensitive)
        matching_statuses = []
        for status in statuses:
            if status.get("state", "").lower() == state.lower():
                matching_statuses.append(status)
        
        if matching_statuses:
            logger.info(f"Found {len(matching_statuses)} work statuses with state '{state}'")
            return {
                "success": True,
                "statuses": matching_statuses,
                "count": len(matching_statuses),
                "message": f"Found {len(matching_statuses)} work statuses with state '{state}'"
            }
        else:
            logger.warning(f"No work statuses found with state: {state}")
            available_states = list(set(s.get("state") for s in statuses if s.get("state")))
            return {
                "success": False,
                "statuses": [],
                "count": 0,
                "message": f"No work statuses found with state '{state}'",
                "available_states": available_states,
                "error": f"No work statuses found with state '{state}'"
            }
        
    except Exception as e:
        logger.error(f"Failed to filter work statuses by state: {str(e)}")
        return {
            "success": False,
            "statuses": [],
            "count": 0,
            "message": f"Failed to filter work statuses by state '{state}'",
            "error": str(e)
        }