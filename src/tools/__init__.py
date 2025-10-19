"""Tools module for IT Technician Agent - Strands Compatible"""

# Strands tool functions
from .ticket import (
    create_ticket,
    update_ticket,
    assign_ticket,
    resolve_ticket,
    categorize_support_request,
    notify_technician_assignment
)

from .tracking import (
    track_time,
    log_work,
    monitor_progress
)

from .analysis import (
    analyze_request,
    generate_suggestions,
    identify_bottlenecks
)

from .analytics import (
    performance_metrics,
    view_analytics
)

from .sla import (
    calculate_sla_status,
    detect_sla_breaches,
    execute_sla_escalation
)

from .user import (
    get_technicians,
    find_technician_by_name,
    get_technicians_by_department,
    create_technician,
    create_simple_technician,
    onboard_new_technician,
    create_client_user,
    create_simple_client_user,
    onboard_client_user,
    bulk_onboard_client_users,
    get_client_user,
    get_client_users,
    search_client_users,
    get_requester_roles,
    get_requester_role_by_id,
    get_requester_role_by_name,
    get_requester_roles_summary,
    get_roles_by_feature
)

from .metadata import (
    get_work_status_list,
    get_work_status_by_name,
    get_work_status_by_state
)

from .billing import (
    create_invoice,
    create_simple_invoice,
    create_quote,
    create_client_contract,
    get_client_contract_list,
    get_client_contract,
    create_simple_contract,
    create_and_retrieve_contract,
    get_payment_terms,
    get_payment_term_by_id,
    get_payment_term_by_name,
    get_payment_terms_summary,
    get_offered_items,
    get_offered_item_by_id,
    search_offered_items,
    get_offered_items_summary
)

from .knowledge import (
    create_kb_article,
    create_simple_kb_article,
    create_troubleshooting_article
)

from .task import (
    create_task
)

from .alerts import (
    get_alerts_list,
    get_alert_by_id
)

# All exports
__all__ = [
    # Ticket tools
    "create_ticket",
    "update_ticket",
    "assign_ticket", 
    "resolve_ticket",
    "categorize_support_request",
    "notify_technician_assignment",
    
    # Tracking tools
    "track_time",
    "log_work",
    "monitor_progress",
    
    # Analysis tools
    "analyze_request",
    "generate_suggestions",
    "identify_bottlenecks",
    
    # Analytics tools
    "performance_metrics",
    "view_analytics",
    
    # SLA tools
    "calculate_sla_metrics",
    "detect_sla_breach",
    "manage_escalation",
    
    # User management tools
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
    "get_roles_by_feature",
    
    # Metadata tools
    "get_work_status_list",
    "get_work_status_by_name",
    "get_work_status_by_state",
    
    # Billing tools
    "create_invoice",
    "create_simple_invoice",
    "create_quote",
    "create_client_contract",
    "get_client_contract_list",
    "get_client_contract",
    "create_simple_contract",
    "create_and_retrieve_contract",
    "get_payment_terms",
    "get_payment_term_by_id",
    "get_payment_term_by_name",
    "get_payment_terms_summary",
    "get_offered_items",
    "get_offered_item_by_id",
    "search_offered_items",
    "get_offered_items_summary",
    
    # Knowledge base tools
    "create_kb_article",
    "create_simple_kb_article",
    "create_troubleshooting_article",
    
    # Alerts tools
    "get_alerts_list",
    "get_alert_by_id",
    
    # Task tools
    "create_task"
]
