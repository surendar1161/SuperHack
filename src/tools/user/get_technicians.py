"""Get technicians tool for IT Technician Agent - Strands Compatible"""

from typing import Any, Dict, List, Optional
from strands import tool

from ...clients.superops_client import SuperOpsClient
from ...utils.logger import get_logger

logger = get_logger("get_technicians")


@tool
async def get_technicians(
    page: int = 1,
    page_size: int = 100,
    search_name: Optional[str] = None,
    department: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get list of technicians from SuperOps
    
    Args:
        page: Page number for pagination (default: 1)
        page_size: Number of technicians per page (default: 100, max: 100)
        search_name: Optional name filter to search for specific technicians
        department: Optional department filter
        
    Returns:
        Dictionary containing technician list with names, roles, emails, and departments
    """
    try:
        logger.info(f"Fetching technicians list (page {page}, size {page_size})")
        
        # Initialize SuperOps client with proper cleanup
        from ...agents.config import AgentConfig
        config = AgentConfig()
        client = SuperOpsClient(config)
        
        # Use async context manager for proper cleanup
        async with client:
            # Build search conditions
            conditions = [
                {
                    "attribute": "roles.roleId",
                    "operator": "is",
                    "value": 3  # Role ID 3 = Technician role
                }
            ]
            
            # Add name filter if provided
            if search_name:
                conditions.append({
                    "attribute": "name",
                    "operator": "contains",
                    "value": search_name
                })
            
            # Add department filter if provided
            if department:
                conditions.append({
                    "attribute": "department",
                    "operator": "is",
                    "value": department
                })
            
            # Get technicians via SuperOps client
            result = await client.get_technicians(
                page=page,
                page_size=page_size,
                conditions=conditions
            )
            
            technicians = result.get("userList", [])
            list_info = result.get("listInfo", {})
            
            logger.info(f"Retrieved {len(technicians)} technicians")
            
            # Format technician data
            formatted_technicians = []
            for tech in technicians:
                formatted_tech = {
                    "name": tech.get("name"),
                    "email": tech.get("email"),
                    "roles": tech.get("roles", [])
                }
                formatted_technicians.append(formatted_tech)
            
            return {
                "success": True,
                "technicians": formatted_technicians,
                "total_count": len(formatted_technicians),
                "page_info": {
                    "current_page": list_info.get("page", page),
                    "page_size": list_info.get("pageSize", page_size),
                    "has_more": len(technicians) == page_size
                },
                "filters_applied": {
                    "search_name": search_name,
                    "department": department
                },
                "message": f"Retrieved {len(formatted_technicians)} technicians",
                "data": result
            }
        
    except Exception as e:
        logger.error(f"Failed to get technicians: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve technicians list"
        }


@tool
async def find_technician_by_name(
    name: str
) -> Dict[str, Any]:
    """
    Find a specific technician by name
    
    Args:
        name: Name of the technician to search for
        
    Returns:
        Dictionary containing matching technician details
    """
    try:
        logger.info(f"Searching for technician: {name}")
        
        # Use the get_technicians function with name filter
        result = await get_technicians(search_name=name, page_size=10)
        
        if result["success"]:
            technicians = result["technicians"]
            
            # Look for exact match first
            exact_match = None
            partial_matches = []
            
            for tech in technicians:
                tech_name = tech.get("name", "").lower()
                search_name = name.lower()
                
                if tech_name == search_name:
                    exact_match = tech
                    break
                elif search_name in tech_name:
                    partial_matches.append(tech)
            
            if exact_match:
                return {
                    "success": True,
                    "technician": exact_match,
                    "match_type": "exact",
                    "message": f"Found exact match for technician: {name}"
                }
            elif partial_matches:
                return {
                    "success": True,
                    "technician": partial_matches[0],  # Return first partial match
                    "all_matches": partial_matches,
                    "match_type": "partial",
                    "message": f"Found {len(partial_matches)} partial match(es) for: {name}"
                }
            else:
                return {
                    "success": False,
                    "error": "Technician not found",
                    "message": f"No technician found with name: {name}"
                }
        else:
            return result
            
    except Exception as e:
        logger.error(f"Failed to find technician: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to search for technician: {name}"
        }


@tool
async def get_technicians_by_department(
    department: str,
    page_size: int = 50
) -> Dict[str, Any]:
    """
    Get all technicians in a specific department
    
    Args:
        department: Department name to filter by
        page_size: Maximum number of technicians to return
        
    Returns:
        Dictionary containing technicians in the specified department
    """
    try:
        logger.info(f"Getting technicians for department: {department}")
        
        # Use the get_technicians function with department filter
        result = await get_technicians(
            department=department,
            page_size=page_size
        )
        
        if result["success"]:
            result["message"] = f"Found {result['total_count']} technicians in {department} department"
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get technicians by department: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to get technicians for department: {department}"
        }