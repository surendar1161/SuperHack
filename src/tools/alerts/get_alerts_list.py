"""Get alerts list tool for IT Technician Agent - Strands Compatible"""

from typing import Any, Dict, List, Optional
from strands import tool

from ...clients.superops_client import SuperOpsClient
from ...utils.logger import get_logger

logger = get_logger("get_alerts_list")


@tool
async def get_alerts_list(
    page: int = 1,
    page_size: int = 10
) -> Dict[str, Any]:
    """
    Get list of alerts from SuperOps
    
    Args:
        page: Page number for pagination (default: 1)
        page_size: Number of alerts per page (default: 10)
        
    Returns:
        Dictionary containing alerts list with asset info, severity, status, and pagination details
    """
    try:
        logger.info(f"Fetching alerts list (page {page}, size {page_size})")
        
        # Use session manager for proper cleanup
        from ...utils.session_manager import get_superops_client
        
        async with get_superops_client() as client:
            
            # GraphQL query for getting alerts list
            query = """
            query getAlertList($input: ListInfoInput!) {
              getAlertList(input: $input) {
                alerts {
                  id
                  asset
                  severity
                  status
                  message
                }
                listInfo {
                  page
                  pageSize
                  totalCount
                }
              }
            }
            """
            
            # Variables for the query
            variables = {
                "input": {
                    "page": page,
                    "pageSize": page_size
                }
            }
            
            # Execute the GraphQL query
            response = await client.execute_graphql_query(
                query=query,
                variables=variables
            )
            
            if not response or 'data' not in response:
                logger.error("No data received from SuperOps API")
                return {
                    "success": False,
                    "error": "No data received from SuperOps API",
                    "alerts": [],
                    "pagination": None
                }
            
            alert_data = response['data'].get('getAlertList', {})
            alerts = alert_data.get('alerts', [])
            list_info = alert_data.get('listInfo', {})
            
            logger.info(f"Successfully retrieved {len(alerts)} alerts")
            
            return {
                "success": True,
                "alerts": alerts,
                "pagination": {
                    "current_page": list_info.get('page', page),
                    "page_size": list_info.get('pageSize', page_size),
                    "total_count": list_info.get('totalCount', 0),
                    "total_pages": list_info.get('totalPages', 0)
                },
                "total_alerts": len(alerts)
            }
        
    except Exception as e:
        logger.error(f"Error retrieving alerts list: {e}")
        return {
            "success": False,
            "error": str(e),
            "alerts": [],
            "pagination": None
        }


@tool
async def get_alert_by_id(alert_id: str) -> Dict[str, Any]:
    """
    Get specific alert details by ID
    
    Args:
        alert_id: The ID of the alert to retrieve
        
    Returns:
        Dictionary containing detailed alert information
    """
    try:
        logger.info(f"Fetching alert details for ID: {alert_id}")
        
        # Initialize SuperOps client
        from ...agents.config import AgentConfig
        config = AgentConfig()
        client = SuperOpsClient(config)
        
        # GraphQL query for getting specific alert
        query = """
        query getAlert($alertId: String!) {
          getAlert(alertId: $alertId) {
            id
            asset
            severity
            status
            message
          }
        }
        """
        
        variables = {"alertId": alert_id}
        
        response = await client.execute_graphql_query(
            query=query,
            variables=variables
        )
        
        if not response or 'data' not in response:
            return {
                "success": False,
                "error": "No data received from SuperOps API",
                "alert": None
            }
        
        alert = response['data'].get('getAlert')
        
        if not alert:
            return {
                "success": False,
                "error": f"Alert with ID {alert_id} not found",
                "alert": None
            }
        
        logger.info(f"Successfully retrieved alert {alert_id}")
        
        return {
            "success": True,
            "alert": alert
        }
        
    except Exception as e:
        logger.error(f"Error retrieving alert {alert_id}: {e}")
        return {
            "success": False,
            "error": str(e),
            "alert": None
        }