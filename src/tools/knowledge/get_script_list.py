"""
Get Script List Tool - Retrieve scripts by type from SuperOps
"""
import asyncio
from typing import Dict, Any, List, Optional
from src.tools.base_tool import BaseTool
from src.clients.superops_client import SuperOpsClient
from src.utils.logger import get_logger

logger = get_logger(__name__)

class GetScriptListTool(BaseTool):
    """Tool for retrieving script lists by type from SuperOps"""
    
    def __init__(self, client: SuperOpsClient):
        super().__init__(
            name="get_script_list_by_type",
            description="Retrieve automation scripts by platform type from SuperOps"
        )
        self.client = client
    
    async def execute(self, script_type: str = "WINDOWS", page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        Get script list by type
        
        Args:
            script_type: Type of scripts to retrieve (WINDOWS, LINUX, etc.)
            page: Page number for pagination
            page_size: Number of scripts per page
            
        Returns:
            Dict containing script list and metadata
        """
        try:
            logger.info(f"Getting script list for type: {script_type}")
            
            # Connect to SuperOps API
            await self.client.connect()
            
            result = await self.client.get_script_list_by_type(
                script_type=script_type,
                page=page,
                page_size=page_size
            )
            
            # Close the connection
            await self.client.close()
            
            if result and result.get('success'):
                scripts = result.get('scripts', [])
                list_info = result.get('listInfo', {})
                
                logger.info(f"Successfully retrieved {len(scripts)} scripts of type {script_type}")
                
                return {
                    "success": True,
                    "scripts": scripts,
                    "list_info": list_info,
                    "script_type": script_type,
                    "total_scripts": len(scripts)
                }
            else:
                logger.error("Failed to retrieve script list")
                return {
                    "success": False,
                    "error": result.get('error', 'Failed to retrieve script list from SuperOps API')
                }
                
        except Exception as e:
            logger.error(f"Error getting script list: {str(e)}")
            return {
                "success": False,
                "error": f"Exception occurred: {str(e)}"
            }

# Convenience functions
async def get_script_list_by_type(script_type: str = "WINDOWS", page: int = 1, page_size: int = 10) -> Dict[str, Any]:
    """Get scripts by type with pagination"""
    from src.clients.superops_client import SuperOpsClient
    from src.agents.config import AgentConfig
    
    config = AgentConfig()
    client = SuperOpsClient(config)
    tool = GetScriptListTool(client)
    return await tool.execute(script_type=script_type, page=page, page_size=page_size)

async def get_windows_scripts(page: int = 1, page_size: int = 10) -> Dict[str, Any]:
    """Get Windows scripts"""
    return await get_script_list_by_type("WINDOWS", page, page_size)

async def get_linux_scripts(page: int = 1, page_size: int = 10) -> Dict[str, Any]:
    """Get Linux scripts"""
    return await get_script_list_by_type("LINUX", page, page_size)

async def search_scripts_by_name(script_name: str, script_type: str = "WINDOWS") -> Dict[str, Any]:
    """Search for scripts by name within a specific type"""
    result = await get_script_list_by_type(script_type, page=1, page_size=100)
    
    if result.get('success'):
        scripts = result.get('scripts', [])
        matching_scripts = [
            script for script in scripts 
            if script_name.lower() in script.get('name', '').lower()
        ]
        
        return {
            "success": True,
            "scripts": matching_scripts,
            "search_term": script_name,
            "script_type": script_type,
            "total_matches": len(matching_scripts)
        }
    else:
        return result

async def get_script_summary() -> Dict[str, Any]:
    """Get summary of available scripts across all types"""
    try:
        windows_result = await get_windows_scripts(page_size=100)
        linux_result = await get_linux_scripts(page_size=100)
        
        summary = {
            "success": True,
            "script_types": {},
            "total_scripts": 0
        }
        
        if windows_result.get('success'):
            windows_scripts = windows_result.get('scripts', [])
            summary["script_types"]["WINDOWS"] = {
                "count": len(windows_scripts),
                "scripts": [{"name": s.get('name'), "scriptId": s.get('scriptId')} for s in windows_scripts[:5]]
            }
            summary["total_scripts"] += len(windows_scripts)
        
        if linux_result.get('success'):
            linux_scripts = linux_result.get('scripts', [])
            summary["script_types"]["LINUX"] = {
                "count": len(linux_scripts),
                "scripts": [{"name": s.get('name'), "scriptId": s.get('scriptId')} for s in linux_scripts[:5]]
            }
            summary["total_scripts"] += len(linux_scripts)
        
        return summary
        
    except Exception as e:
        logger.error(f"Error getting script summary: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to get script summary: {str(e)}"
        }

if __name__ == "__main__":
    async def test_script_list():
        print("Testing Script List Tool...")
        
        # Test Windows scripts
        result = await get_windows_scripts()
        print(f"Windows Scripts Result: {result}")
        
        # Test script summary
        summary = await get_script_summary()
        print(f"Script Summary: {summary}")
    
    asyncio.run(test_script_list())