"""
Tool for retrieving alerts list from SuperOps
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from ..base_tool import BaseTool
from ...clients.superops_client import SuperOpsClient


class GetAlertsListInput(BaseModel):
    """Input parameters for getting alerts list"""
    page: int = Field(default=1, description="Page number for pagination")
    page_size: int = Field(default=10, description="Number of alerts per page")


class GetAlertsListTool(BaseTool):
    """Tool for retrieving alerts list from SuperOps"""
    
    name = "get_alerts_list"
    description = "Retrieve a list of alerts from SuperOps with pagination support"
    
    def __init__(self, superops_client: SuperOpsClient):
        super().__init__()
        self.superops_client = superops_client
    
    async def execute(self, input_data: GetAlertsListInput) -> Dict[str, Any]:
        """
        Execute the get alerts list operation
        
        Args:
            input_data: Input parameters containing page and page_size
            
        Returns:
            Dict containing alerts list and pagination info
        """
        try:
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
                    "page": input_data.page,
                    "pageSize": input_data.page_size
                }
            }
            
            # Execute the GraphQL query
            response = await self.superops_client.execute_graphql_query(
                query=query,
                variables=variables
            )
            
            if not response or 'data' not in response:
                return {
                    "success": False,
                    "error": "No data received from SuperOps API",
                    "alerts": [],
                    "pagination": None
                }
            
            alert_data = response['data'].get('getAlertList', {})
            alerts = alert_data.get('alerts', [])
            list_info = alert_data.get('listInfo', {})
            
            return {
                "success": True,
                "alerts": alerts,
                "pagination": {
                    "current_page": list_info.get('page', input_data.page),
                    "page_size": list_info.get('pageSize', input_data.page_size),
                    "total_count": list_info.get('totalCount', 0),
                    "total_pages": list_info.get('totalPages', 0)
                },
                "total_alerts": len(alerts)
            }
            
        except Exception as e:
            self.logger.error(f"Error retrieving alerts list: {e}")
            return {
                "success": False,
                "error": str(e),
                "alerts": [],
                "pagination": None
            }
    
    def get_input_schema(self) -> Dict[str, Any]:
        """Get the input schema for this tool"""
        return GetAlertsListInput.model_json_schema()