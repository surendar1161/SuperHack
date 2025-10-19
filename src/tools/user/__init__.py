"""User management tools for IT Technician Agent - Strands Compatible"""

# Strands tool function imports
from .get_technicians import (
    get_technicians,
    find_technician_by_name,
    get_technicians_by_department
)

from .create_technician import (
    create_technician,
    create_simple_technician,
    onboard_new_technician
)

from .create_client_user import (
    create_client_user,
    create_simple_client_user,
    onboard_client_user,
    bulk_onboard_client_users
)

from .get_client_user import (
    get_client_user,
    get_client_users,
    search_client_users
)

from .get_requester_roles import (
    get_requester_roles,
    get_requester_role_by_id,
    get_requester_role_by_name,
    get_requester_roles_summary,
    get_roles_by_feature
)

# All exports
__all__ = [
    "get_technicians",
    "find_technician_by_name",
    "get_technicians_by_department",
    "create_technician",
    "create_simple_technician",
    "onboard_new_technician",
    "create_client_user",
    "create_simple_client_user",
    "onboard_client_user",
    "bulk_onboard_client_users",
    "get_client_user",
    "get_client_users",
    "search_client_users",
    "get_requester_roles",
    "get_requester_role_by_id",
    "get_requester_role_by_name",
    "get_requester_roles_summary",
    "get_roles_by_feature"
]