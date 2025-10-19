"""
Create Alert Tool - Create alerts for asset threshold breaches in SuperOps
"""
import asyncio
from typing import Dict, Any, Optional
from src.tools.base_tool import BaseTool
from src.clients.superops_client import SuperOpsClient
from src.utils.logger import get_logger

logger = get_logger(__name__)

class CreateAlertTool(BaseTool):
    """Tool for creating alerts when asset thresholds are breached"""
    
    def __init__(self, client: SuperOpsClient):
        super().__init__(
            name="create_alert",
            description="Create alerts for asset threshold breaches and monitoring events"
        )
        self.client = client
    
    async def execute(self, asset_id: str, message: str, description: str, severity: str = "High") -> Dict[str, Any]:
        """
        Create an alert for asset threshold breach
        
        Args:
            asset_id: ID of the asset that triggered the alert
            message: Alert message (e.g., "High CPU Usage")
            description: Detailed description of the alert
            severity: Alert severity level (High, Medium, Low)
            
        Returns:
            Dict containing alert creation result
        """
        try:
            logger.info(f"Creating alert for asset {asset_id}: {message}")
            
            # Connect to SuperOps API
            await self.client.connect()
            
            result = await self.client.create_alert(
                asset_id=asset_id,
                message=message,
                description=description,
                severity=severity
            )
            
            # Close the connection
            await self.client.close()
            
            if result and result.get('success'):
                alert_data = result.get('alert', {})
                
                logger.info(f"Successfully created alert: {alert_data.get('id')} for asset {asset_id}")
                
                return {
                    "success": True,
                    "alert_id": alert_data.get('id'),
                    "message": alert_data.get('message'),
                    "severity": alert_data.get('severity'),
                    "status": alert_data.get('status'),
                    "created_time": alert_data.get('createdTime'),
                    "asset_id": asset_id,
                    "description": description
                }
            else:
                logger.error("Failed to create alert")
                return {
                    "success": False,
                    "error": result.get('error', 'Failed to create alert in SuperOps API')
                }
                
        except Exception as e:
            logger.error(f"Error creating alert: {str(e)}")
            return {
                "success": False,
                "error": f"Exception occurred: {str(e)}"
            }

# Convenience functions
async def create_alert(asset_id: str, message: str, description: str, severity: str = "High") -> Dict[str, Any]:
    """Create an alert for asset threshold breach"""
    from src.clients.superops_client import SuperOpsClient
    from src.agents.config import AgentConfig
    
    config = AgentConfig()
    client = SuperOpsClient(config)
    tool = CreateAlertTool(client)
    return await tool.execute(asset_id=asset_id, message=message, description=description, severity=severity)

async def create_cpu_alert(asset_id: str, cpu_percentage: float) -> Dict[str, Any]:
    """Create a high CPU usage alert"""
    return await create_alert(
        asset_id=asset_id,
        message="High CPU Usage",
        description=f"CPU Usage is {cpu_percentage}% which is higher than the configured threshold",
        severity="High"
    )

async def create_memory_alert(asset_id: str, memory_percentage: float) -> Dict[str, Any]:
    """Create a high memory usage alert"""
    return await create_alert(
        asset_id=asset_id,
        message="High Memory Usage",
        description=f"Memory Usage is {memory_percentage}% which exceeds the configured threshold",
        severity="High"
    )

async def create_disk_alert(asset_id: str, disk_percentage: float, drive_name: str = "C:") -> Dict[str, Any]:
    """Create a low disk space alert"""
    return await create_alert(
        asset_id=asset_id,
        message="Low Disk Space",
        description=f"Disk space on {drive_name} is {disk_percentage}% full, approaching capacity limit",
        severity="Medium"
    )

async def create_network_alert(asset_id: str, issue_type: str = "connectivity") -> Dict[str, Any]:
    """Create a network connectivity alert"""
    return await create_alert(
        asset_id=asset_id,
        message="Network Connectivity Issue",
        description=f"Network {issue_type} issue detected on asset, may impact system performance",
        severity="High"
    )

async def create_service_alert(asset_id: str, service_name: str) -> Dict[str, Any]:
    """Create a service down alert"""
    return await create_alert(
        asset_id=asset_id,
        message="Service Down",
        description=f"Critical service '{service_name}' is not responding or has stopped unexpectedly",
        severity="High"
    )

if __name__ == "__main__":
    async def test_create_alert():
        print("Testing Create Alert Tool...")
        
        # Test basic alert creation
        result = await create_alert(
            asset_id="4293925678745489408",
            message="High CPU Usage",
            description="CPU Usage is very higher than usual",
            severity="High"
        )
        print(f"Alert Creation Result: {result}")
        
        # Test CPU alert
        cpu_result = await create_cpu_alert("4293925678745489408", 95.5)
        print(f"CPU Alert Result: {cpu_result}")
    
    asyncio.run(test_create_alert())