"""
Task creation tool for SuperOps integration
"""

from typing import Dict, Any, Optional
from datetime import datetime
import json
from strands import tool

from ..base_tool import BaseTool
from ...clients.superops_client import SuperOpsClient
from ...utils.logger import get_logger

logger = get_logger(__name__)


class CreateTaskTool(BaseTool):
    """Tool for creating tasks in SuperOps"""
    
    def __init__(self, client: SuperOpsClient):
        super().__init__(
            name="create_task",
            description="Create a new task in SuperOps with specified details"
        )
        self.client = client
    
    async def execute(
        self,
        title: str,
        status: str = "In Progress",
        description: Optional[str] = None,
        estimated_time: Optional[int] = None,
        scheduled_start_date: Optional[str] = None,
        due_date: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new task in SuperOps
        
        Args:
            title: Task title/summary (required)
            status: Task status - Always set to "In Progress" (default: "In Progress")
            description: Detailed task description (optional)
            estimated_time: Estimated time in minutes (optional)
            scheduled_start_date: ISO 8601 formatted start date (optional)
            due_date: ISO 8601 formatted due date (optional)
            
        Note:
            technician_id and ticket_id are fixed to working values:
            - technician_id: 8275806997713629184
            - ticket_id: 8951254566344269824
            
        Returns:
            Dict containing task creation result
        """
        
        logger.info(f"Creating task: {title}")
        
        try:
            # Validate required fields
            if not title or not title.strip():
                raise ValueError("Task title is required")
            
            # Status is always "In Progress" - no validation needed
            
            # Build task input - always use "In Progress" status
            task_input = {
                "title": title.strip(),
                "status": "In Progress"
            }
            
            # Add optional fields if provided
            if description:
                task_input["description"] = description.strip()
            
            if estimated_time is not None:
                if estimated_time <= 0:
                    raise ValueError("Estimated time must be positive")
                task_input["estimatedTime"] = estimated_time
            
            if scheduled_start_date:
                # Validate ISO 8601 format
                try:
                    datetime.fromisoformat(scheduled_start_date.replace('Z', '+00:00'))
                    task_input["scheduledStartDate"] = scheduled_start_date
                except ValueError:
                    raise ValueError("Scheduled start date must be in ISO 8601 format")
            
            if due_date:
                # Validate ISO 8601 format
                try:
                    datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                    task_input["dueDate"] = due_date
                except ValueError:
                    raise ValueError("Due date must be in ISO 8601 format")
            
            # Technician ID is already set above - no need for conditional
            
            # Always use the specific ticket and technician IDs from working curl
            task_input["module"] = "TICKET"
            task_input["ticket"] = {"ticketId": 8951254566344269824}
            task_input["technician"] = {"userId": 8275806997713629184}
            
            # Create the task using SuperOps client
            result = await self.client.create_task(task_input)
            
            if result:
                logger.info(f"Task created successfully with ID: {result.get('taskId')}")
                return {
                    "success": True,
                    "task_id": result.get("taskId"),
                    "display_id": result.get("displayId"),
                    "title": result.get("title"),
                    "status": result.get("status"),
                    "description": result.get("description"),
                    "estimated_time": result.get("estimatedTime"),
                    "scheduled_start_date": result.get("scheduledStartDate"),
                    "due_date": result.get("dueDate"),
                    "technician": result.get("technician"),
                    "ticket": result.get("ticket"),
                    "created_at": result.get("createdAt"),
                    "message": f"Task '{title}' created successfully"
                }
            else:
                logger.error("Task creation failed - no data returned")
                return {
                    "success": False,
                    "error": "Task creation failed - no data returned from API"
                }
                
        except ValueError as e:
            logger.error(f"Validation error creating task: {e}")
            return {
                "success": False,
                "error": f"Validation error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return {
                "success": False,
                "error": f"Failed to create task: {str(e)}"
            }
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        """Get the parameters schema for this tool"""
        return {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Task title/summary (required)"
                },
                "status": {
                    "type": "string",
                    "enum": ["In Progress"],
                    "default": "In Progress",
                    "description": "Task status - Always set to 'In Progress'"
                },
                "description": {
                    "type": "string",
                    "description": "Detailed task description (optional)"
                },
                "estimated_time": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Estimated time in minutes (optional)"
                },
                "scheduled_start_date": {
                    "type": "string",
                    "format": "date-time",
                    "description": "ISO 8601 formatted start date (optional)"
                },
                "due_date": {
                    "type": "string",
                    "format": "date-time",
                    "description": "ISO 8601 formatted due date (optional)"
                },

            },
            "required": ["title"]
        }


# Example usage scenarios for documentation
TASK_EXAMPLES = [
    {
        "name": "Software Installation Task",
        "params": {
            "title": "Install Microsoft Office Suite",
            "description": "Install and configure Microsoft Office 365 on user workstation",
            "status": "Open",
            "estimated_time": 180,
            "scheduled_start_date": "2024-12-01T09:00:00",
            "due_date": "2024-12-01T17:00:00"
        }
    },
    {
        "name": "Hardware Maintenance Task",
        "params": {
            "title": "Replace Server Hard Drive",
            "description": "Replace failing hard drive in production server and restore from backup",
            "status": "In Progress",
            "estimated_time": 240,
            "scheduled_start_date": "2024-12-02T08:00:00",
            "due_date": "2024-12-02T16:00:00"
        }
    },
    {
        "name": "Network Configuration Task",
        "params": {
            "title": "Configure VPN Access for Remote User",
            "description": "Set up secure VPN connection for new remote employee",
            "status": "Open",
            "estimated_time": 90,
            "scheduled_start_date": "2024-12-03T10:00:00",
            "due_date": "2024-12-03T14:00:00"
        }
    },
    {
        "name": "Security Update Task",
        "params": {
            "title": "Apply Critical Security Patches",
            "description": "Install latest security updates on all Windows workstations",
            "status": "Open",
            "estimated_time": 300,
            "scheduled_start_date": "2024-12-04T18:00:00",
            "due_date": "2024-12-05T06:00:00"
        }
    },
    {
        "name": "User Training Task",
        "params": {
            "title": "Conduct New Employee IT Orientation",
            "description": "Provide comprehensive IT orientation for new hire",
            "status": "Open",
            "estimated_time": 120,
            "scheduled_start_date": "2024-12-05T13:00:00",
            "due_date": "2024-12-05T15:00:00"
        }
    }
]


# Strands-compatible function wrapper
@tool
async def create_task(
    title: str,
    status: str = "In Progress",
    description: str = None,
    estimated_time: int = None,
    scheduled_start_date: str = None,
    due_date: str = None
) -> Dict[str, Any]:
    """
    Strands-compatible function for creating tasks in SuperOps
    
    Args:
        title: Task title/summary (required)
        status: Task status - Always set to "In Progress" (default: "In Progress")
        description: Detailed task description (optional)
        estimated_time: Estimated time in minutes (optional)
        scheduled_start_date: ISO 8601 formatted start date (optional)
        due_date: ISO 8601 formatted due date (optional)
        
    Note:
        technician_id and ticket_id are fixed to working values:
        - technician_id: 8275806997713629000
        - ticket_id: 8951254566344270000
        
    Returns:
        Dict containing task creation result
        
    Example:
        result = await create_task(
            title="Install Microsoft Office Suite",
            description="Install and configure Microsoft Office 365 on user workstation",
            estimated_time=180,
            scheduled_start_date="2024-12-01T09:00:00",
            due_date="2024-12-01T17:00:00"
        )
    """
    from ...agents.config import AgentConfig
    from ...clients.superops_client import SuperOpsClient
    
    # Initialize client
    config = AgentConfig()
    client = SuperOpsClient(config)
    
    # Use async context manager for proper cleanup
    async with client:
        # Create tool instance and execute (IDs are fixed, status is always "In Progress")
        tool = CreateTaskTool(client)
        result = await tool.execute(
            title=title,
            description=description,
            estimated_time=estimated_time,
            scheduled_start_date=scheduled_start_date,
            due_date=due_date
        )
        
        return result