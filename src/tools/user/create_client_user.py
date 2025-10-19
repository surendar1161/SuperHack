"""Create client user tool for IT Technician Agent - Strands Compatible"""

from typing import Any, Dict, Optional
from strands import tool

from ...clients.superops_client import SuperOpsClient
from ...utils.logger import get_logger

logger = get_logger("create_client_user")


@tool
async def create_client_user(
    first_name: str,
    last_name: str,
    email: str = None,
    client_account_id: str = "7206852887935602688",  # Default client account
    contact_number: str = None,
    role_id: str = "5",  # Default to client user role
    reporting_manager: Optional[str] = None,
    site_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new client user in SuperOps
    
    Args:
        first_name: First name of the client user
        email: Email address of the client user
        client_account_id: Account ID of the client organization
        role_id: Role ID for the user (default: "5" for client user role)
        last_name: Optional last name of the client user
        contact_number: Optional contact phone number
        reporting_manager: Optional reporting manager
        site_id: Optional site ID for the user
        
    Returns:
        Dictionary containing created client user details or error information
    """
    try:
        # Generate unique email if not provided
        if not email:
            import uuid
            import time
            unique_id = str(uuid.uuid4())[:8]
            timestamp = str(int(time.time()))[-6:]  # Last 6 digits of timestamp
            email = f"{first_name.lower()}.{last_name.lower()}.{unique_id}.{timestamp}@client.com"
        
        # Generate contact number if not provided
        if not contact_number:
            import random
            contact_number = f"555-{random.randint(100,999)}-{random.randint(1000,9999)}"
        
        logger.info(f"Creating client user: {first_name} {last_name} with email: {email}")
        
        # Use session manager for proper cleanup
        from ...utils.session_manager import get_superops_client
        
        async with get_superops_client() as client:
            # GraphQL mutation for creating client user
            mutation = """
            mutation createClientUser($input: CreateClientUserInput!) {
                createClientUser(input: $input) {
                    userId
                    firstName
                    lastName
                    name
                    email
                    contactNumber
                    client
                }
            }
            """
            
            # Variables for the mutation
            variables = {
                "input": {
                    "firstName": first_name,
                    "lastName": last_name,
                    "email": email,
                    "contactNumber": contact_number,
                    "role": {
                        "roleId": role_id
                    },
                    "client": {
                        "accountId": client_account_id
                    }
                }
            }
            
            # Add optional fields if provided
            if reporting_manager:
                variables["input"]["reportingManager"] = reporting_manager
            if site_id:
                variables["input"]["site"] = {"id": site_id}
            
            # Execute the GraphQL mutation
            response = await client.execute_graphql_query(mutation, variables)
            
            if response and "data" in response and response["data"]["createClientUser"]:
                user_data = response["data"]["createClientUser"]
                logger.info(f"Successfully created client user: {user_data}")
                return {
                    "success": True,
                    "user_id": user_data.get("userId"),
                    "name": user_data.get("name"),
                    "email": user_data.get("email"),
                    "contact_number": user_data.get("contactNumber"),
                    "client_account": user_data.get("client", {}),
                    "message": f"Client user '{first_name} {last_name}' created successfully",
                    "data": user_data
                }
            else:
                logger.error("Client user creation failed - no data returned")
                return {
                    "success": False,
                    "error": "Client user creation failed - no data returned from API"
                }
        
    except Exception as e:
        logger.error(f"Error creating client user: {e}")
        return {
            "success": False,
            "error": str(e),
            "client_user": None
        }


@tool
async def create_simple_client_user(
    first_name: str,
    email: str,
    client_account_id: str
) -> Dict[str, Any]:
    """
    Create a new client user with minimal required information
    
    Args:
        first_name: First name of the client user
        email: Email address of the client user
        client_account_id: Account ID of the client organization
        
    Returns:
        Dictionary containing created client user details or error information
    """
    return await create_client_user(
        first_name=first_name,
        email=email,
        client_account_id=client_account_id
    )


@tool
async def onboard_client_user(
    first_name: str,
    last_name: str,
    email: str,
    client_account_id: str,
    contact_number: Optional[str] = None,
    site_id: Optional[str] = None,
    reporting_manager: Optional[str] = None
) -> Dict[str, Any]:
    """
    Onboard a new client user with complete profile setup
    
    Args:
        first_name: First name of the client user
        last_name: Last name of the client user
        email: Email address of the client user
        client_account_id: Account ID of the client organization
        contact_number: Optional contact phone number
        site_id: Optional site ID for the user
        reporting_manager: Optional reporting manager
        
    Returns:
        Dictionary containing onboarding results and next steps
    """
    try:
        logger.info(f"Starting client user onboarding process for: {first_name} {last_name}")
        
        # Create the client user
        result = await create_client_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            client_account_id=client_account_id,
            contact_number=contact_number,
            site_id=site_id,
            reporting_manager=reporting_manager
        )
        
        if result["success"]:
            client_user = result["client_user"]
            
            # Add onboarding information
            onboarding_steps = [
                "✅ Client user account created successfully",
                "📧 Welcome email will be sent to the user",
                "🔑 Login credentials will be provided via email",
                "🎫 User can now submit support tickets",
                "📞 Contact information configured for support",
                "🏢 User associated with client organization",
                "📋 Ready to access client portal and services"
            ]
            
            return {
                "success": True,
                "client_user": client_user,
                "onboarding_status": "completed",
                "next_steps": onboarding_steps,
                "message": f"Successfully onboarded {client_user.get('name')} as a new client user"
            }
        else:
            return {
                "success": False,
                "error": result["error"],
                "onboarding_status": "failed",
                "client_user": None
            }
            
    except Exception as e:
        logger.error(f"Error during client user onboarding: {e}")
        return {
            "success": False,
            "error": str(e),
            "onboarding_status": "failed",
            "client_user": None
        }


@tool
async def bulk_onboard_client_users(
    users_data: list,
    client_account_id: str
) -> Dict[str, Any]:
    """
    Onboard multiple client users in bulk
    
    Args:
        users_data: List of user dictionaries with firstName, lastName, email, etc.
        client_account_id: Account ID of the client organization
        
    Returns:
        Dictionary containing bulk onboarding results
    """
    try:
        logger.info(f"Starting bulk onboarding for {len(users_data)} client users")
        
        successful_users = []
        failed_users = []
        
        for user_data in users_data:
            try:
                result = await create_client_user(
                    first_name=user_data["firstName"],
                    last_name=user_data.get("lastName"),
                    email=user_data["email"],
                    client_account_id=client_account_id,
                    contact_number=user_data.get("contactNumber"),
                    site_id=user_data.get("siteId"),
                    reporting_manager=user_data.get("reportingManager")
                )
                
                if result["success"]:
                    successful_users.append(result["client_user"])
                else:
                    failed_users.append({
                        "user_data": user_data,
                        "error": result["error"]
                    })
                    
            except Exception as e:
                failed_users.append({
                    "user_data": user_data,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "total_users": len(users_data),
            "successful_count": len(successful_users),
            "failed_count": len(failed_users),
            "successful_users": successful_users,
            "failed_users": failed_users,
            "message": f"Bulk onboarding completed: {len(successful_users)} successful, {len(failed_users)} failed"
        }
        
    except Exception as e:
        logger.error(f"Error during bulk client user onboarding: {e}")
        return {
            "success": False,
            "error": str(e),
            "total_users": len(users_data) if users_data else 0,
            "successful_count": 0,
            "failed_count": len(users_data) if users_data else 0
        }