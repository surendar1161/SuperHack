"""
Create Ticket Note Tool - Add notes to tickets in SuperOps
"""
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from src.tools.base_tool import BaseTool
from src.clients.superops_client import SuperOpsClient
from src.utils.logger import get_logger

logger = get_logger(__name__)

class CreateTicketNoteTool(BaseTool):
    """Tool for adding notes to tickets in SuperOps"""
    
    def __init__(self, client: SuperOpsClient):
        super().__init__(
            name="create_ticket_note",
            description="Add notes and comments to tickets for documentation and communication"
        )
        self.client = client
    
    async def execute(self, ticket_id: str, content: str, 
                     added_by_user_id: str = "8275806997713629184",
                     privacy_type: str = "PUBLIC", 
                     added_on: str = None) -> Dict[str, Any]:
        """
        Create a note for a ticket
        
        Args:
            ticket_id: ID of the ticket to add note to
            content: Content of the note
            added_by_user_id: User ID of the person adding the note
            privacy_type: Privacy level (PUBLIC, PRIVATE)
            added_on: Timestamp when note was added (ISO format)
            
        Returns:
            Dict containing note creation result
        """
        try:
            logger.info(f"Creating note for ticket {ticket_id}: {content[:50]}...")
            
            # Connect to SuperOps API
            await self.client.connect()
            
            # Generate timestamp if not provided
            if not added_on:
                added_on = datetime.now().isoformat()
            
            result = await self.client.create_ticket_note(
                ticket_id=ticket_id,
                content=content,
                added_by_user_id=added_by_user_id,
                privacy_type=privacy_type,
                added_on=added_on
            )
            
            # Close the connection
            await self.client.close()
            
            if result and result.get('success'):
                note_data = result.get('note', {})
                
                logger.info(f"Successfully created note: {note_data.get('noteId')} for ticket {ticket_id}")
                
                return {
                    "success": True,
                    "note_id": note_data.get('noteId'),
                    "content": note_data.get('content'),
                    "added_by": note_data.get('addedBy'),
                    "added_on": note_data.get('addedOn'),
                    "privacy_type": note_data.get('privacyType'),
                    "attachments": note_data.get('attachments', []),
                    "ticket_id": ticket_id,
                    "message": f"Note added to ticket {ticket_id} successfully"
                }
            else:
                logger.error("Failed to create ticket note")
                return {
                    "success": False,
                    "error": result.get('error', 'Failed to create ticket note in SuperOps API')
                }
                
        except Exception as e:
            logger.error(f"Error creating ticket note: {str(e)}")
            return {
                "success": False,
                "error": f"Exception occurred: {str(e)}"
            }

# Convenience functions
async def create_ticket_note(ticket_id: str, content: str, 
                           added_by_user_id: str = "8275806997713629184",
                           privacy_type: str = "PUBLIC") -> Dict[str, Any]:
    """Create a note for a ticket"""
    from src.clients.superops_client import SuperOpsClient
    from src.agents.config import AgentConfig
    
    config = AgentConfig()
    client = SuperOpsClient(config)
    tool = CreateTicketNoteTool(client)
    return await tool.execute(
        ticket_id=ticket_id, content=content, 
        added_by_user_id=added_by_user_id, privacy_type=privacy_type
    )

async def add_public_note(ticket_id: str, content: str, 
                         added_by_user_id: str = "8275806997713629184") -> Dict[str, Any]:
    """Add a public note to a ticket"""
    return await create_ticket_note(
        ticket_id=ticket_id,
        content=content,
        added_by_user_id=added_by_user_id,
        privacy_type="PUBLIC"
    )

async def add_private_note(ticket_id: str, content: str, 
                          added_by_user_id: str = "8275806997713629184") -> Dict[str, Any]:
    """Add a private note to a ticket"""
    return await create_ticket_note(
        ticket_id=ticket_id,
        content=content,
        added_by_user_id=added_by_user_id,
        privacy_type="PRIVATE"
    )

async def add_investigation_note(ticket_id: str, findings: str, 
                               next_steps: str = "", 
                               added_by_user_id: str = "8275806997713629184") -> Dict[str, Any]:
    """Add an investigation note with findings and next steps"""
    content = f"Investigation Update:\n\nFindings: {findings}"
    if next_steps:
        content += f"\n\nNext Steps: {next_steps}"
    
    return await create_ticket_note(
        ticket_id=ticket_id,
        content=content,
        added_by_user_id=added_by_user_id,
        privacy_type="PUBLIC"
    )

async def add_resolution_note(ticket_id: str, solution: str, 
                            time_taken: str = "", 
                            added_by_user_id: str = "8275806997713629184") -> Dict[str, Any]:
    """Add a resolution note with solution details"""
    content = f"Resolution:\n\n{solution}"
    if time_taken:
        content += f"\n\nTime taken: {time_taken}"
    
    return await create_ticket_note(
        ticket_id=ticket_id,
        content=content,
        added_by_user_id=added_by_user_id,
        privacy_type="PUBLIC"
    )

async def add_escalation_note(ticket_id: str, reason: str, escalated_to: str,
                             added_by_user_id: str = "8275806997713629184") -> Dict[str, Any]:
    """Add an escalation note"""
    content = f"Ticket Escalated:\n\nReason: {reason}\nEscalated to: {escalated_to}"
    
    return await create_ticket_note(
        ticket_id=ticket_id,
        content=content,
        added_by_user_id=added_by_user_id,
        privacy_type="PUBLIC"
    )

if __name__ == "__main__":
    async def test_create_ticket_note():
        print("Testing Create Ticket Note Tool...")
        
        # Test basic note creation
        result = await create_ticket_note(
            ticket_id="10679116294692864",
            content="The network access points need to be replaced",
            privacy_type="PUBLIC"
        )
        print(f"Note Creation Result: {result}")
        
        # Test investigation note
        investigation_result = await add_investigation_note(
            ticket_id="10679116294692864",
            findings="Network equipment showing signs of hardware failure",
            next_steps="Schedule maintenance window for replacement"
        )
        print(f"Investigation Note Result: {investigation_result}")
    
    asyncio.run(test_create_ticket_note())