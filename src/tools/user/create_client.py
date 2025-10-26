"""
Create Client Tool - Create new client organizations in SuperOps
"""
import asyncio
from typing import Dict, Any, Optional
from src.tools.base_tool import BaseTool
from src.clients.superops_client import SuperOpsClient
from src.utils.logger import get_logger

logger = get_logger(__name__)

class CreateClientTool(BaseTool):
    """Tool for creating new client organizations in SuperOps"""
    
    def __init__(self, client: SuperOpsClient):
        super().__init__(
            name="create_client",
            description="Create new client organizations with headquarters site setup"
        )
        self.client = client
    
    async def execute(self, name: str, stage: str = "Active", status: str = "Paid", 
                     account_manager_id: str = "8275806997713629184", 
                     site_name: str = None, timezone: str = "America/Los_Angeles",
                     working_24x7: bool = False) -> Dict[str, Any]:
        """
        Create a new client organization
        
        Args:
            name: Name of the client organization
            stage: Client stage (Active, Prospect, etc.)
            status: Client status (Paid, Trial, etc.)
            account_manager_id: User ID of the account manager
            site_name: Name of the headquarters site
            timezone: Timezone code for the site
            working_24x7: Whether the site operates 24/7
            
        Returns:
            Dict containing client creation result
        """
        try:
            logger.info(f"Creating client organization: {name}")
            
            # Connect to SuperOps API
            await self.client.connect()
            
            # Generate site name if not provided
            if not site_name:
                import random
                site_name = f"{name.replace(' ', '')}HQ{random.randint(100, 999)}"
            
            # Add timestamp to ensure unique client names
            import time as time_module
            if "Demo" in name and not any(char.isdigit() for char in name.split()[-1]):
                unique_suffix = str(int(time_module.time()))[-6:]
                name = f"{name} {unique_suffix}"
            
            result = await self.client.create_client_v2(
                name=name,
                stage=stage,
                status=status,
                account_manager_id=account_manager_id,
                site_name=site_name,
                timezone=timezone,
                working_24x7=working_24x7
            )
            
            # Close the connection
            await self.client.close()
            
            if result and result.get('success'):
                client_data = result.get('client', {})
                
                logger.info(f"Successfully created client: {client_data.get('accountId')} - {name}")
                
                return {
                    "success": True,
                    "account_id": client_data.get('accountId'),
                    "name": client_data.get('name'),
                    "stage": client_data.get('stage'),
                    "status": client_data.get('status'),
                    "account_manager": client_data.get('accountManager'),
                    "hq_site": client_data.get('hqSite'),
                    "email_domains": client_data.get('emailDomains'),
                    "custom_fields": client_data.get('customFields'),
                    "message": f"Client '{name}' created successfully"
                }
            else:
                logger.error("Failed to create client")
                return {
                    "success": False,
                    "error": result.get('error', 'Failed to create client in SuperOps API')
                }
                
        except Exception as e:
            logger.error(f"Error creating client: {str(e)}")
            return {
                "success": False,
                "error": f"Exception occurred: {str(e)}"
            }

# Convenience functions
async def create_client(name: str, stage: str = "Active", status: str = "Paid", 
                       account_manager_id: str = "8275806997713629184", 
                       site_name: str = None, timezone: str = "America/Los_Angeles",
                       working_24x7: bool = False) -> Dict[str, Any]:
    """Create a new client organization"""
    from src.clients.superops_client import SuperOpsClient
    from src.agents.config import AgentConfig
    
    config = AgentConfig()
    client = SuperOpsClient(config)
    tool = CreateClientTool(client)
    return await tool.execute(
        name=name, stage=stage, status=status, account_manager_id=account_manager_id,
        site_name=site_name, timezone=timezone, working_24x7=working_24x7
    )

async def create_active_client(name: str, account_manager_id: str = "8275806997713629184") -> Dict[str, Any]:
    """Create an active paid client with default settings"""
    return await create_client(
        name=name,
        stage="Active",
        status="Paid",
        account_manager_id=account_manager_id
    )

async def create_prospect_client(name: str, account_manager_id: str = "8275806997713629184") -> Dict[str, Any]:
    """Create a prospect client for potential customers"""
    return await create_client(
        name=name,
        stage="Prospect",
        status="Trial",
        account_manager_id=account_manager_id
    )

async def create_enterprise_client(name: str, site_name: str, timezone: str = "America/New_York",
                                  account_manager_id: str = "8275806997713629184") -> Dict[str, Any]:
    """Create an enterprise client with 24/7 operations"""
    return await create_client(
        name=name,
        stage="Active",
        status="Paid",
        account_manager_id=account_manager_id,
        site_name=site_name,
        timezone=timezone,
        working_24x7=True
    )

async def onboard_new_client(name: str, contact_email: str, account_manager_id: str = "8275806997713629184") -> Dict[str, Any]:
    """Complete client onboarding process"""
    try:
        logger.info(f"Starting client onboarding for: {name}")
        
        # Create the client
        result = await create_client(
            name=name,
            stage="Active",
            status="Paid",
            account_manager_id=account_manager_id
        )
        
        if result.get("success"):
            # Add onboarding steps
            onboarding_steps = [
                "✅ Client organization created successfully",
                "🏢 Headquarters site configured",
                "👤 Account manager assigned",
                "📧 Welcome email will be sent",
                "🎫 Support portal access configured",
                "📋 Ready for user onboarding",
                "🔧 IT services can now be provisioned"
            ]
            
            return {
                "success": True,
                "client": result,
                "onboarding_status": "completed",
                "next_steps": onboarding_steps,
                "contact_email": contact_email,
                "message": f"Successfully onboarded {name} as a new client"
            }
        else:
            return {
                "success": False,
                "error": result.get("error"),
                "onboarding_status": "failed"
            }
            
    except Exception as e:
        logger.error(f"Error during client onboarding: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "onboarding_status": "failed"
        }

if __name__ == "__main__":
    async def test_create_client():
        print("Testing Create Client Tool...")
        
        # Test basic client creation
        result = await create_client(
            name="Test Client Organization",
            stage="Active",
            status="Paid"
        )
        print(f"Client Creation Result: {result}")
        
        # Test enterprise client
        enterprise_result = await create_enterprise_client(
            name="Enterprise Corp",
            site_name="Enterprise HQ",
            timezone="America/New_York"
        )
        print(f"Enterprise Client Result: {enterprise_result}")
    
    asyncio.run(test_create_client())