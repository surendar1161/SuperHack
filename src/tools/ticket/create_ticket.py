"""Create ticket tool for IT Technician Agent - Strands Compatible"""

from typing import Any, Dict, Optional
from strands import tool

from ...clients.superops_client import SuperOpsClient
from ...models.ticket import TicketCreate, Priority, Status
from ...utils.logger import get_logger

logger = get_logger("create_ticket")




async def _get_available_technician(client: SuperOpsClient, priority: str, category: Optional[str] = None) -> Optional[str]:
    """
    Get an available technician for ticket assignment
    
    Args:
        client: SuperOps client instance
        priority: Priority level of the ticket
        category: Category of the ticket (optional)
        
    Returns:
        User ID of available technician or None if no technician found
    """
    try:
        logger.info(f"Finding available technician for {priority} priority ticket")
        
        # Get list of technicians
        technicians_result = await client.get_technicians(page=1, page_size=50)
        
        if not technicians_result or not technicians_result.get("userList"):
            logger.warning("No technicians found in the system")
            return None
        
        technicians = technicians_result["userList"]
        logger.info(f"Found {len(technicians)} technicians")
        
        # For now, use simple round-robin assignment
        # In a real system, you might consider:
        # - Technician workload
        # - Specialization/skills matching category
        # - Availability status
        # - Priority-based assignment rules
        
        # Priority-based assignment logic
        if priority.upper() in ["CRITICAL", "HIGH"]:
            # For high priority tickets, prefer the first available technician
            for tech in technicians:
                if tech.get("name") and tech.get("email"):
                    # Extract userId from technician data
                    # The API might return userId in different formats
                    user_id = tech.get("userId") or tech.get("id") or tech.get("email")
                    if user_id:
                        logger.info(f"Assigning high priority ticket to: {tech.get('name')} ({user_id})")
                        return str(user_id)
        else:
            # For normal priority, use the first available technician
            for tech in technicians:
                if tech.get("name") and tech.get("email"):
                    user_id = tech.get("userId") or tech.get("id") or tech.get("email")
                    if user_id:
                        logger.info(f"Assigning ticket to: {tech.get('name')} ({user_id})")
                        return str(user_id)
        
        logger.warning("No suitable technician found for assignment")
        return None
        
    except Exception as e:
        logger.error(f"Failed to get available technician: {str(e)}")
        return None


@tool
async def create_ticket(
    title: str,
    description: str,
    priority: str = "MEDIUM",
    requester_email: Optional[str] = None,
    category: Optional[str] = None,
    assigned_to: Optional[str] = None,
    auto_assign: bool = True
) -> Dict[str, Any]:
    """
    Create a new support ticket in SuperOps with automatic technician assignment
    
    Args:
        title: A brief, concise summary of the issue or request (e.g., 'Password Reset Request', 'Printer Not Working')
        description: Full detailed description of the issue, including what the user is experiencing, error messages, and any relevant context
        priority: Priority level based on urgency and impact. Use 'CRITICAL' for system outages, 'HIGH' for urgent issues, 'MEDIUM' for standard requests, 'LOW' for minor issues
        requester_email: Email address of the person requesting support (optional)
        category: Category of the issue - Hardware, Software, Network, Email, Security, Account (optional)
        assigned_to: Specific ID or email of technician to assign ticket to (optional, overrides auto-assignment)
        auto_assign: Whether to automatically assign ticket to an available technician (default: True)
        
    Returns:
        Dictionary containing ticket creation results with success status, ticket ID, assigned technician, and details
    """
    try:
        logger.info(f"Creating ticket: {title}")
        
        # Use session manager for proper cleanup
        from ...utils.session_manager import get_superops_client
        
        async with get_superops_client() as client:
            # Map priority string to enum
            priority_str = priority.upper()
            try:
                priority_enum = Priority[priority_str] if priority_str in Priority.__members__ else Priority.MEDIUM
            except:
                priority_enum = Priority.MEDIUM
            
            # Auto-assign technician if not explicitly provided and auto_assign is True
            assigned_technician = assigned_to
            assigned_technician_name = None
            
            if not assigned_technician and auto_assign:
                logger.info("Auto-assigning ticket to available technician...")
                assigned_technician = await _get_available_technician(client, priority_str, category)
                
                if assigned_technician:
                    # Get technician details for logging
                    try:
                        technicians_result = await client.get_technicians(page=1, page_size=50)
                        if technicians_result and technicians_result.get("userList"):
                            for tech in technicians_result["userList"]:
                                tech_id = tech.get("userId") or tech.get("id") or tech.get("email")
                                if str(tech_id) == str(assigned_technician):
                                    assigned_technician_name = tech.get("name")
                                    break
                    except Exception as e:
                        logger.warning(f"Could not get technician name: {e}")
            
            # Create ticket data object
            ticket_data = TicketCreate(
                title=title,
                description=description,
                priority=priority_enum,
                requester_email=requester_email,
                category=category,
                assigned_to=assigned_technician,
                status=Status.OPEN
            )
            
            # Format input according to SuperOps IT documentation
            graphql_input = {
                "subject": ticket_data.title,
                "description": ticket_data.description,
                "requestType": "Incident",
                "source": "FORM"
            }
            
            # Add technician assignment if available (using the correct structure)
            if assigned_technician:
                graphql_input["technician"] = {
                    "userId": assigned_technician
                }
            
            # Add optional fields if they exist
            if ticket_data.requester_email:
                graphql_input["requesterEmail"] = ticket_data.requester_email
            if ticket_data.category:
                graphql_input["category"] = ticket_data.category
            
            # Create ticket via SuperOps GraphQL client
            result = await client.create_ticket(graphql_input)
        
            ticket_id = result.get('id', 'Unknown ID')
            logger.info(f"Successfully created ticket: {ticket_id}")
            
            # Build response with assignment information
            response = {
                "success": True,
                "ticket_id": ticket_id,
                "ticket_number": result.get("number"),
                "title": title,
                "priority": priority_str,
                "category": category,
                "assigned_to": assigned_technician,
                "assigned_technician_name": assigned_technician_name,
                "auto_assigned": bool(assigned_technician and not assigned_to and auto_assign),
                "message": f"Ticket created successfully: {title}",
                "data": result
            }
            
            # Add assignment details to message
            if assigned_technician:
                if assigned_technician_name:
                    response["message"] += f" (Assigned to: {assigned_technician_name})"
                else:
                    response["message"] += f" (Assigned to: {assigned_technician})"
            
            return response
        
    except Exception as e:
        logger.error(f"Failed to create ticket: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create ticket"
        }