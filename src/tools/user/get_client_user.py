"""Get client user tool for IT Technician Agent - Strands Compatible"""

from typing import Any, Dict, Optional
from strands import tool

from ...clients.superops_client import SuperOpsClient
from ...utils.logger import get_logger

logger = get_logger("get_client_user")


@tool
async def get_client_user(
    user_id: str
) -> Dict[str, Any]:
    """
    Get client user details by user ID
    
    Args:
        user_id: The ID of the client user to retrieve
        
    Returns:
        Dictionary containing client user details with success status
    """
    try:
        logger.info(f"Fetching client user details for ID: {user_id}")
        
        # Use session manager for proper cleanup
        from ...utils.session_manager import get_superops_client
        
        async with get_superops_client() as client:
            # Use the exact GraphQL query from your working curl
            query = """
            query getClientUser($input: ClientUserIdentifierInput!) {
              getClientUser(input: $input) {
                userId
                firstName
                lastName
                name
                email
                contactNumber
                reportingManager
                site
                role
                client
                customFields
              }
            }
            """
            
            variables = {
                "input": {
                    "userId": user_id
                }
            }

            # Execute the GraphQL query directly
            result = await client.execute_graphql_query(query, variables)
            
            if result and result.get("data") and result["data"].get("getClientUser"):
                client_user = result["data"]["getClientUser"]
                logger.info(f"Successfully retrieved client user: {client_user.get('name', 'Unknown')}")
                return {
                    "success": True,
                    "client_user": client_user,
                    "user_id": client_user.get("userId"),
                    "name": client_user.get("name"),
                    "email": client_user.get("email"),
                    "contact_number": client_user.get("contactNumber"),
                    "site": client_user.get("site"),
                    "role": client_user.get("role"),
                    "client": client_user.get("client"),
                    "message": f"Retrieved client user: {client_user.get('name', 'Unknown')}"
                }
            
            logger.error(f"Failed to get client user {user_id}: {result}")
            return {
                "success": False,
                "error": f"Client user not found: {result}",
                "user_id": user_id
            }
                
    except Exception as e:
        logger.error(f"Error getting client user {user_id}: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "user_id": user_id
        }


@tool
async def get_client_users(
    page: int = 1,
    page_size: int = 50,
    site_id: Optional[str] = None,
    client_id: Optional[str] = None,
    search_term: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get list of client users with optional filtering
    
    Args:
        page: Page number for pagination (default: 1)
        page_size: Number of users per page (default: 50)
        site_id: Optional site ID to filter by
        client_id: Optional client ID to filter by
        search_term: Optional search term to filter by name or email
        
    Returns:
        Dictionary containing list of client users with pagination info
    """
    try:
        logger.info(f"Fetching client users list (page {page}, size {page_size})")
        
        # Use session manager for proper cleanup
        from ...utils.session_manager import get_superops_client
        
        async with get_superops_client() as client:
            # Use GraphQL query to get client users list
            query = """
            query getClientUsers($input: ClientUsersInput!) {
              getClientUsers(input: $input) {
                totalCount
                users {
                  userId
                  firstName
                  lastName
                  name
                  email
                  contactNumber
                  reportingManager
                  site {
                    id
                    name
                  }
                  role {
                    roleId
                    name
                  }
                  client {
                    accountId
                    name
                  }
                }
              }
            }
            """
            
            # Build input parameters
            input_params = {
                "page": page,
                "pageSize": page_size
            }
            
            if site_id:
                input_params["siteId"] = site_id
            if client_id:
                input_params["clientId"] = client_id
            if search_term:
                input_params["searchTerm"] = search_term
            
            variables = {
                "input": input_params
            }

            # Execute the GraphQL query
            result = await client.execute_graphql_query(query, variables)
            
            if result and result.get("data") and result["data"].get("getClientUsers"):
                client_users_data = result["data"]["getClientUsers"]
                users = client_users_data.get("users", [])
                total_count = client_users_data.get("totalCount", 0)
                
                logger.info(f"Retrieved {len(users)} client users (total: {total_count})")
                return {
                    "success": True,
                    "client_users": users,
                    "total_count": total_count,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": (total_count + page_size - 1) // page_size,
                    "message": f"Retrieved {len(users)} client users"
                }
            
            logger.error(f"Failed to get client users: {result}")
            return {
                "success": False,
                "error": f"Failed to retrieve client users: {result}",
                "client_users": []
            }
                
    except Exception as e:
        logger.error(f"Error getting client users: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "client_users": []
        }


@tool
async def search_client_users(
    search_term: str,
    search_type: str = "name",
    limit: int = 20
) -> Dict[str, Any]:
    """
    Search for client users by name, email, or other criteria
    
    Args:
        search_term: The term to search for
        search_type: Type of search - name, email, phone, or all (default: name)
        limit: Maximum number of results to return (default: 20)
        
    Returns:
        Dictionary containing matching client users
    """
    try:
        logger.info(f"Searching client users for '{search_term}' by {search_type}")
        
        # Use the get_client_users function with search term
        result = await get_client_users(
            page=1,
            page_size=limit,
            search_term=search_term
        )
        
        if result["success"]:
            users = result["client_users"]
            
            # Additional filtering based on search_type if needed
            if search_type != "all":
                filtered_users = []
                for user in users:
                    if search_type == "name" and search_term.lower() in user.get("name", "").lower():
                        filtered_users.append(user)
                    elif search_type == "email" and search_term.lower() in user.get("email", "").lower():
                        filtered_users.append(user)
                    elif search_type == "phone" and search_term in user.get("contactNumber", ""):
                        filtered_users.append(user)
                    elif search_type == "all":
                        filtered_users.append(user)
                
                users = filtered_users
            
            logger.info(f"Found {len(users)} matching client users")
            return {
                "success": True,
                "client_users": users,
                "search_term": search_term,
                "search_type": search_type,
                "count": len(users),
                "message": f"Found {len(users)} client users matching '{search_term}'"
            }
        else:
            return result
                
    except Exception as e:
        logger.error(f"Error searching client users: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "client_users": []
        }