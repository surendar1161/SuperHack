"""Get requester roles tool for IT Technician Agent - Strands Compatible"""

from typing import Any, Dict, List, Optional
from strands import tool

from ...clients.superops_client import SuperOpsClient
from ...utils.logger import get_logger

logger = get_logger("get_requester_roles")


@tool
async def get_requester_roles() -> Dict[str, Any]:
    """
    Get list of requester roles from SuperOps with detailed role information
    
    Returns:
        Dictionary containing requester roles list with role details, features, and users
    """
    try:
        logger.info("Fetching requester roles list from SuperOps")
        
        # Use session manager for proper cleanup
        from ...utils.session_manager import get_superops_client
        
        async with get_superops_client() as client:
            # Use the exact GraphQL query from your working curl
            query = """
            query getRequesterRoleList {
              getRequesterRoleList {
                roleId
                name
                description
                roleType {
                    roleTypeId
                    name
                }
                roleFeatureList {
                  feature{
                    name
                  }
                }
                roleUserList
              }
            }
            """
            
            # Execute the GraphQL query directly
            result = await client.execute_graphql_query(query)
            
            if result and result.get("data") and result["data"].get("getRequesterRoleList"):
                requester_roles = result["data"]["getRequesterRoleList"]
                logger.info(f"Successfully retrieved {len(requester_roles)} requester roles")
                return {
                    "success": True,
                    "requester_roles": requester_roles,
                    "total_roles": len(requester_roles),
                    "message": f"Retrieved {len(requester_roles)} requester roles"
                }
            
            logger.error(f"Failed to get requester roles: {result}")
            return {
                "success": False,
                "error": f"Failed to retrieve requester roles: {result}",
                "requester_roles": []
            }
                
    except Exception as e:
        logger.error(f"Error getting requester roles: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "requester_roles": []
        }


@tool
async def get_requester_role_by_id(
    role_id: str
) -> Dict[str, Any]:
    """
    Get specific requester role by role ID
    
    Args:
        role_id: The ID of the requester role to retrieve
        
    Returns:
        Dictionary containing requester role details
    """
    try:
        logger.info(f"Fetching requester role details for ID: {role_id}")
        
        # Get all requester roles and filter by ID
        result = await get_requester_roles()
        
        if result["success"]:
            requester_roles = result["requester_roles"]
            
            # Find the specific requester role
            for role in requester_roles:
                if role.get("roleId") == role_id:
                    logger.info(f"Found requester role: {role.get('name')}")
                    return {
                        "success": True,
                        "requester_role": role,
                        "role_id": role.get("roleId"),
                        "role_name": role.get("name"),
                        "description": role.get("description"),
                        "role_type": role.get("roleType"),
                        "features": role.get("roleFeatureList", []),
                        "users": role.get("roleUserList", []),
                        "message": f"Retrieved requester role: {role.get('name')}"
                    }
            
            logger.warning(f"Requester role not found: {role_id}")
            return {
                "success": False,
                "error": f"Requester role not found: {role_id}",
                "requester_role": None
            }
        else:
            return result
                
    except Exception as e:
        logger.error(f"Error getting requester role {role_id}: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "requester_role": None
        }


@tool
async def get_requester_role_by_name(
    role_name: str
) -> Dict[str, Any]:
    """
    Get requester role by name (case-insensitive search)
    
    Args:
        role_name: The name of the requester role to search for
        
    Returns:
        Dictionary containing requester role details
    """
    try:
        logger.info(f"Searching for requester role by name: {role_name}")
        
        # Get all requester roles and filter by name
        result = await get_requester_roles()
        
        if result["success"]:
            requester_roles = result["requester_roles"]
            
            # Search for requester role by name (case-insensitive)
            search_name = role_name.lower()
            matching_roles = []
            
            for role in requester_roles:
                role_name_lower = role.get("name", "").lower()
                if search_name in role_name_lower:
                    matching_roles.append(role)
            
            if matching_roles:
                if len(matching_roles) == 1:
                    role = matching_roles[0]
                    logger.info(f"Found requester role: {role.get('name')}")
                    return {
                        "success": True,
                        "requester_role": role,
                        "role_id": role.get("roleId"),
                        "role_name": role.get("name"),
                        "description": role.get("description"),
                        "role_type": role.get("roleType"),
                        "features": role.get("roleFeatureList", []),
                        "users": role.get("roleUserList", []),
                        "message": f"Retrieved requester role: {role.get('name')}"
                    }
                else:
                    logger.info(f"Found {len(matching_roles)} matching requester roles")
                    return {
                        "success": True,
                        "requester_roles": matching_roles,
                        "total_matches": len(matching_roles),
                        "message": f"Found {len(matching_roles)} requester roles matching '{role_name}'"
                    }
            else:
                logger.warning(f"No requester roles found matching: {role_name}")
                return {
                    "success": False,
                    "error": f"No requester roles found matching: {role_name}",
                    "requester_roles": []
                }
        else:
            return result
                
    except Exception as e:
        logger.error(f"Error searching requester roles: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "requester_roles": []
        }


@tool
async def get_requester_roles_summary() -> Dict[str, Any]:
    """
    Get a summary of all requester roles with key statistics and features
    
    Returns:
        Dictionary containing requester roles summary and statistics
    """
    try:
        logger.info("Generating requester roles summary")
        
        # Get all requester roles
        result = await get_requester_roles()
        
        if result["success"]:
            requester_roles = result["requester_roles"]
            
            # Generate summary statistics
            total_roles = len(requester_roles)
            role_names = [role.get("name", "") for role in requester_roles]
            
            # Analyze role types
            role_types = {}
            for role in requester_roles:
                role_type = role.get("roleType", {})
                type_name = role_type.get("name", "Unknown")
                role_types[type_name] = role_types.get(type_name, 0) + 1
            
            # Analyze features
            all_features = set()
            roles_with_features = 0
            for role in requester_roles:
                features = role.get("roleFeatureList", [])
                if features:
                    roles_with_features += 1
                    for feature in features:
                        feature_name = feature.get("feature", {}).get("name", "")
                        if feature_name:
                            all_features.add(feature_name)
            
            # Analyze users
            total_users = 0
            roles_with_users = 0
            for role in requester_roles:
                users = role.get("roleUserList", [])
                if users:
                    roles_with_users += 1
                    total_users += len(users)
            
            summary = {
                "total_requester_roles": total_roles,
                "role_names": role_names,
                "role_types": role_types,
                "features_analysis": {
                    "total_unique_features": len(all_features),
                    "roles_with_features": roles_with_features,
                    "available_features": list(all_features)[:10]  # First 10 features
                },
                "users_analysis": {
                    "total_users_across_roles": total_users,
                    "roles_with_users": roles_with_users,
                    "average_users_per_role": round(total_users / total_roles, 2) if total_roles > 0 else 0
                }
            }
            
            logger.info(f"Generated summary for {total_roles} requester roles")
            return {
                "success": True,
                "summary": summary,
                "requester_roles": requester_roles,
                "message": f"Generated summary for {total_roles} requester roles"
            }
        else:
            return result
                
    except Exception as e:
        logger.error(f"Error generating requester roles summary: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "summary": None
        }


@tool
async def get_roles_by_feature(
    feature_name: str
) -> Dict[str, Any]:
    """
    Get requester roles that have a specific feature
    
    Args:
        feature_name: The name of the feature to search for
        
    Returns:
        Dictionary containing roles that have the specified feature
    """
    try:
        logger.info(f"Finding requester roles with feature: {feature_name}")
        
        # Get all requester roles
        result = await get_requester_roles()
        
        if result["success"]:
            requester_roles = result["requester_roles"]
            matching_roles = []
            
            # Search for roles with the specified feature
            search_feature = feature_name.lower()
            
            for role in requester_roles:
                features = role.get("roleFeatureList", [])
                for feature in features:
                    feature_obj = feature.get("feature", {})
                    current_feature_name = feature_obj.get("name", "").lower()
                    if search_feature in current_feature_name:
                        matching_roles.append(role)
                        break  # Avoid duplicates if role has multiple matching features
            
            logger.info(f"Found {len(matching_roles)} roles with feature '{feature_name}'")
            return {
                "success": True,
                "requester_roles": matching_roles,
                "feature_name": feature_name,
                "total_matches": len(matching_roles),
                "message": f"Found {len(matching_roles)} roles with feature '{feature_name}'"
            }
        else:
            return result
                
    except Exception as e:
        logger.error(f"Error searching roles by feature: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "requester_roles": []
        }