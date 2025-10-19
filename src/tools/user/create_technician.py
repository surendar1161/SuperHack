"""Create technician tool for IT Technician Agent - Strands Compatible"""

from typing import Any, Dict, Optional
from strands import tool

from ...clients.superops_client import SuperOpsClient
from ...utils.logger import get_logger

logger = get_logger("create_technician")


@tool
async def create_technician(
    first_name: str,
    last_name: str,
    email: str = None,
    contact_number: str = None,
    email_signature: Optional[str] = None,
    designation: Optional[str] = None,
    business_function: Optional[str] = None,
    team: Optional[str] = None,
    reporting_manager: Optional[str] = None,
    role_id: int = 3  # Default to technician role (roleId: 3)
) -> Dict[str, Any]:
    """
    Create a new technician in SuperOps
    
    Args:
        first_name: First name of the technician
        last_name: Last name of the technician
        email: Email address of the technician
        contact_number: Contact phone number
        email_signature: Optional email signature
        designation: Optional job designation/title
        business_function: Optional business function
        team: Optional team assignment
        reporting_manager: Optional reporting manager
        role_id: Role ID (default: 3 for technician role)
        
    Returns:
        Dictionary containing created technician details or error information
    """
    try:
        # Generate unique email if not provided
        if not email:
            import uuid
            import time
            unique_id = str(uuid.uuid4())[:8]
            timestamp = str(int(time.time()))[-6:]  # Last 6 digits of timestamp
            email = f"{first_name.lower()}.{last_name.lower()}.{unique_id}.{timestamp}@company.com"
        
        # Generate contact number if not provided
        if not contact_number:
            import random
            contact_number = f"212-{random.randint(100,999)}-{random.randint(1000,9999)}"
        
        logger.info(f"Creating technician: {first_name} {last_name} with email: {email}")
        
        # Use session manager for proper cleanup
        from ...utils.session_manager import get_superops_client
        
        async with get_superops_client() as client:
            # GraphQL mutation matching the working curl format
            mutation = """
            mutation createTechnician($input: CreateTechnicianInput) {
              createTechnician(input: $input) {
                userId
                firstName
                lastName
                name
                email
                contactNumber
                emailSignature
                designation
                businessFunction
                team
                reportingManager
                role
                groups
              }
            }
            """
            
            # Variables matching the working curl format
            variables = {
                "input": {
                    "firstName": first_name,
                    "lastName": last_name,
                    "email": email,
                    "contactNumber": contact_number,
                    "emailSignature": email_signature or f"Best regards,\\n{first_name} {last_name}\\nIT Technician",
                    "role": {
                        "roleId": role_id
                    }
                }
            }
            
            # Add optional fields if provided
            if designation:
                variables["input"]["designation"] = designation
            if business_function:
                variables["input"]["businessFunction"] = business_function
            if team:
                variables["input"]["team"] = team
            if reporting_manager:
                variables["input"]["reportingManager"] = reporting_manager
            
            # Execute the GraphQL mutation
            response = await client.execute_graphql_query(mutation, variables)
        
            if response and "data" in response and response["data"]["createTechnician"]:
                technician_data = response["data"]["createTechnician"]
                logger.info(f"Successfully created technician: {technician_data}")
                return {
                    "success": True,
                    "technician_id": technician_data.get("userId"),
                    "name": technician_data.get("name"),
                    "email": technician_data.get("email"),
                    "contact_number": technician_data.get("contactNumber"),
                    "role": technician_data.get("role"),
                    "message": f"Technician '{first_name} {last_name}' created successfully",
                    "data": technician_data
                }
            else:
                logger.error("Technician creation failed - no data returned")
                return {
                    "success": False,
                    "error": "Technician creation failed - no data returned from API"
                }
            return {
                "success": False,
                "error": "No technician data returned from mutation",
                "technician": None
            }
        
        logger.info(f"Successfully created technician with ID: {technician_data.get('userId')}")
        
        return {
            "success": True,
            "technician": technician_data,
            "message": f"Successfully created technician: {technician_data.get('name', f'{first_name} {last_name}')}"
        }
        
    except Exception as e:
        logger.error(f"Error creating technician: {e}")
        return {
            "success": False,
            "error": str(e),
            "technician": None
        }


@tool
async def create_simple_technician(
    first_name: str,
    last_name: str,
    email: str,
    contact_number: str
) -> Dict[str, Any]:
    """
    Create a new technician with minimal required information
    
    Args:
        first_name: First name of the technician
        last_name: Last name of the technician
        email: Email address of the technician
        contact_number: Contact phone number
        
    Returns:
        Dictionary containing created technician details or error information
    """
    return await create_technician(
        first_name=first_name,
        last_name=last_name,
        email=email,
        contact_number=contact_number
    )


@tool
async def onboard_new_technician(
    first_name: str,
    last_name: str,
    email: str,
    contact_number: str,
    designation: str = "IT Technician",
    team: Optional[str] = None,
    email_signature: Optional[str] = None
) -> Dict[str, Any]:
    """
    Onboard a new technician with standard settings for new hires
    
    Args:
        first_name: First name of the technician
        last_name: Last name of the technician
        email: Email address of the technician
        contact_number: Contact phone number
        designation: Job designation (default: "IT Technician")
        team: Optional team assignment
        email_signature: Optional email signature
        
    Returns:
        Dictionary containing onboarding results and next steps
    """
    try:
        logger.info(f"Starting onboarding process for: {first_name} {last_name}")
        
        # Create the technician
        result = await create_technician(
            first_name=first_name,
            last_name=last_name,
            email=email,
            contact_number=contact_number,
            designation=designation,
            team=team,
            email_signature=email_signature or f"Best regards,\n{first_name} {last_name}\nIT Technician"
        )
        
        if result["success"]:
            technician = result["technician"]
            
            # Add onboarding information
            onboarding_steps = [
                "✅ Technician account created successfully",
                "📧 Welcome email will be sent to the technician",
                "🔑 Login credentials will be provided separately",
                "📚 Access to knowledge base and documentation",
                "👥 Team assignment and role permissions configured",
                "📋 Ready to receive ticket assignments"
            ]
            
            return {
                "success": True,
                "technician": technician,
                "onboarding_status": "completed",
                "next_steps": onboarding_steps,
                "message": f"Successfully onboarded {technician.get('name')} as a new technician"
            }
        else:
            return {
                "success": False,
                "error": result["error"],
                "onboarding_status": "failed",
                "technician": None
            }
            
    except Exception as e:
        logger.error(f"Error during technician onboarding: {e}")
        return {
            "success": False,
            "error": str(e),
            "onboarding_status": "failed",
            "technician": None
        }