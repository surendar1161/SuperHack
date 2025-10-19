"""Get offered items tool for IT Technician Agent - Strands Compatible"""

from typing import Any, Dict, List, Optional
from strands import tool

from ...clients.superops_client import SuperOpsClient
from ...utils.logger import get_logger

logger = get_logger("get_offered_items")


@tool
async def get_offered_items(
    page: int = 1,
    page_size: int = 10
) -> Dict[str, Any]:
    """
    Get list of offered items/services from SuperOps
    
    Args:
        page: Page number for pagination (default: 1)
        page_size: Number of items per page (default: 10)
    
    Returns:
        Dictionary containing offered items list with pagination info
    """
    try:
        logger.info(f"Fetching offered items list (page {page}, size {page_size})")
        
        # Use session manager for proper cleanup
        from ...utils.session_manager import get_superops_client
        
        async with get_superops_client() as client:
            # Use the exact GraphQL query from your working curl
            query = """
            query getOfferedItems($input: ListInfoInput) {
              getOfferedItems(input: $input) {
                items {
                  itemId 
                  serviceItem 
                  notes 
                }
                listInfo {
                  pageSize 
                }
              }
            }
            """
            
            variables = {
                "input": {
                    "page": page,
                    "pageSize": page_size
                }
            }

            # Execute the GraphQL query directly
            result = await client.execute_graphql_query(query, variables)
            
            if result and result.get("data") and result["data"].get("getOfferedItems"):
                offered_items_data = result["data"]["getOfferedItems"]
                items = offered_items_data.get("items", [])
                list_info = offered_items_data.get("listInfo", {})
                
                logger.info(f"Successfully retrieved {len(items)} offered items")
                return {
                    "success": True,
                    "offered_items": items,
                    "total_items": len(items),
                    "page": page,
                    "page_size": list_info.get("pageSize", page_size),
                    "list_info": list_info,
                    "message": f"Retrieved {len(items)} offered items"
                }
            
            logger.error(f"Failed to get offered items: {result}")
            return {
                "success": False,
                "error": f"Failed to retrieve offered items: {result}",
                "offered_items": []
            }
                
    except Exception as e:
        logger.error(f"Error getting offered items: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "offered_items": []
        }


@tool
async def get_offered_item_by_id(
    item_id: str
) -> Dict[str, Any]:
    """
    Get specific offered item by ID
    
    Args:
        item_id: The ID of the offered item to retrieve
        
    Returns:
        Dictionary containing offered item details
    """
    try:
        logger.info(f"Fetching offered item details for ID: {item_id}")
        
        # Get all offered items and filter by ID
        result = await get_offered_items(page_size=100)  # Get more items to search
        
        if result["success"]:
            offered_items = result["offered_items"]
            
            # Find the specific offered item
            for item in offered_items:
                if item.get("itemId") == item_id:
                    logger.info(f"Found offered item: {item.get('serviceItem')}")
                    return {
                        "success": True,
                        "offered_item": item,
                        "item_id": item.get("itemId"),
                        "service_item": item.get("serviceItem"),
                        "notes": item.get("notes"),
                        "message": f"Retrieved offered item: {item.get('serviceItem')}"
                    }
            
            logger.warning(f"Offered item not found: {item_id}")
            return {
                "success": False,
                "error": f"Offered item not found: {item_id}",
                "offered_item": None
            }
        else:
            return result
                
    except Exception as e:
        logger.error(f"Error getting offered item {item_id}: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "offered_item": None
        }


@tool
async def search_offered_items(
    search_term: str,
    search_type: str = "service_item",
    page_size: int = 50
) -> Dict[str, Any]:
    """
    Search for offered items by service name or notes
    
    Args:
        search_term: The term to search for
        search_type: Type of search - service_item, notes, or all (default: service_item)
        page_size: Maximum number of results to return (default: 50)
        
    Returns:
        Dictionary containing matching offered items
    """
    try:
        logger.info(f"Searching offered items for '{search_term}' by {search_type}")
        
        # Get offered items to search through
        result = await get_offered_items(page_size=page_size)
        
        if result["success"]:
            offered_items = result["offered_items"]
            
            # Search for offered items based on search_type
            search_term_lower = search_term.lower()
            matching_items = []
            
            for item in offered_items:
                match_found = False
                
                if search_type == "service_item" or search_type == "all":
                    service_item = item.get("serviceItem", "").lower()
                    if search_term_lower in service_item:
                        match_found = True
                
                if search_type == "notes" or search_type == "all":
                    notes = item.get("notes", "").lower()
                    if search_term_lower in notes:
                        match_found = True
                
                if match_found:
                    matching_items.append(item)
            
            logger.info(f"Found {len(matching_items)} matching offered items")
            return {
                "success": True,
                "offered_items": matching_items,
                "search_term": search_term,
                "search_type": search_type,
                "total_matches": len(matching_items),
                "message": f"Found {len(matching_items)} offered items matching '{search_term}'"
            }
        else:
            return result
                
    except Exception as e:
        logger.error(f"Error searching offered items: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "offered_items": []
        }


@tool
async def get_offered_items_summary() -> Dict[str, Any]:
    """
    Get a summary of all available offered items with key statistics
    
    Returns:
        Dictionary containing offered items summary and statistics
    """
    try:
        logger.info("Generating offered items summary")
        
        # Get all offered items
        result = await get_offered_items(page_size=100)
        
        if result["success"]:
            offered_items = result["offered_items"]
            
            # Generate summary statistics
            total_items = len(offered_items)
            service_names = [item.get("serviceItem", "") for item in offered_items if item.get("serviceItem")]
            items_with_notes = [item for item in offered_items if item.get("notes")]
            
            # Categorize items (basic categorization based on service names)
            categories = {}
            for item in offered_items:
                service_item = item.get("serviceItem", "").lower()
                if "support" in service_item or "maintenance" in service_item:
                    category = "Support & Maintenance"
                elif "installation" in service_item or "setup" in service_item:
                    category = "Installation & Setup"
                elif "consultation" in service_item or "consulting" in service_item:
                    category = "Consultation"
                elif "training" in service_item:
                    category = "Training"
                else:
                    category = "Other Services"
                
                categories[category] = categories.get(category, 0) + 1
            
            summary = {
                "total_offered_items": total_items,
                "items_with_notes": len(items_with_notes),
                "items_without_notes": total_items - len(items_with_notes),
                "service_categories": categories,
                "sample_services": service_names[:5]  # First 5 service names as samples
            }
            
            logger.info(f"Generated summary for {total_items} offered items")
            return {
                "success": True,
                "summary": summary,
                "offered_items": offered_items,
                "message": f"Generated summary for {total_items} offered items"
            }
        else:
            return result
                
    except Exception as e:
        logger.error(f"Error generating offered items summary: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "summary": None
        }