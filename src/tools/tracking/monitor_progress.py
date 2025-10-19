"""Monitor progress tool for IT Technician Agent - Strands Compatible"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from strands import tool

from ...clients.superops_client import SuperOpsClient
from ...models.ticket import Status, Priority
from ...utils.logger import get_logger

logger = get_logger("monitor_progress")


@tool
async def monitor_progress(
    action: str,
    ticket_id: Optional[str] = None,
    technician_id: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    days_back: int = 30
) -> Dict[str, Any]:
    """
    Monitor ticket progress, SLA compliance, and generate progress reports
    
    Args:
        action: Action to perform - check_sla, get_progress, get_overdue, get_metrics
        ticket_id: ID of specific ticket to check (for check_sla, get_progress)
        technician_id: ID of technician to filter by
        priority: Filter by priority level (LOW, MEDIUM, HIGH, CRITICAL)
        status: Filter by status (OPEN, IN_PROGRESS, WAITING, etc.)
        days_back: Number of days to look back for metrics
        
    Returns:
        Dictionary containing progress monitoring results with success status and details
    """
    try:
        logger.info(f"Monitoring progress with action: {action}")
        
        # Initialize SuperOps client (in real implementation, this would be injected)
        from ...agents.config import AgentConfig
        config = AgentConfig()
        client = SuperOpsClient(config)
        
        action_lower = action.lower()
        
        if action_lower == "check_sla":
            return await _check_sla_compliance(client, ticket_id, technician_id, priority)
        elif action_lower == "get_progress":
            return await _get_ticket_progress(client, ticket_id, technician_id, status)
        elif action_lower == "get_overdue":
            return await _get_overdue_tickets(client, technician_id, priority)
        elif action_lower == "get_metrics":
            return await _get_progress_metrics(client, technician_id, days_back)
        else:
            raise ValueError(f"Unknown action: {action}")
            
    except Exception as e:
        logger.error(f"Failed to monitor progress: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to execute progress monitoring action: {action}"
        }


async def _check_sla_compliance(client: SuperOpsClient, ticket_id: Optional[str], technician_id: Optional[str], priority: Optional[str]) -> Dict[str, Any]:
    """Check SLA compliance for tickets"""
    filters = {}
    
    if ticket_id:
        filters["ticket_id"] = ticket_id
    if technician_id:
        filters["technician_id"] = technician_id
    if priority:
        filters["priority"] = priority
    
    result = await client.check_sla_compliance(filters)
    
    return {
        "success": True,
        "action": "check_sla",
        "filters": filters,
        "compliant_tickets": result.get("compliant", 0),
        "breached_tickets": result.get("breached", 0),
        "at_risk_tickets": result.get("at_risk", 0),
        "compliance_rate": result.get("compliance_rate", 0),
        "message": "SLA compliance check completed",
        "data": result
    }


async def _get_ticket_progress(client: SuperOpsClient, ticket_id: Optional[str], technician_id: Optional[str], status: Optional[str]) -> Dict[str, Any]:
    """Get progress details for specific ticket or tickets"""
    if ticket_id:
        # Single ticket progress
        result = await client.get_ticket_progress(ticket_id)
        
        return {
            "success": True,
            "action": "get_progress",
            "ticket_id": ticket_id,
            "progress_percentage": result.get("progress_percentage", 0),
            "estimated_completion": result.get("estimated_completion"),
            "time_spent": result.get("time_spent", 0),
            "milestones": result.get("milestones", []),
            "message": f"Progress retrieved for ticket {ticket_id}",
            "data": result
        }
    else:
        # Multiple tickets progress summary
        filters = {}
        if technician_id:
            filters["technician_id"] = technician_id
        if status:
            filters["status"] = status
        
        result = await client.get_tickets_progress_summary(filters)
        
        return {
            "success": True,
            "action": "get_progress",
            "filters": filters,
            "total_tickets": result.get("total_tickets", 0),
            "average_progress": result.get("average_progress", 0),
            "tickets_by_progress": result.get("tickets_by_progress", {}),
            "message": "Progress summary retrieved",
            "data": result
        }


async def _get_overdue_tickets(client: SuperOpsClient, technician_id: Optional[str], priority: Optional[str]) -> Dict[str, Any]:
    """Get list of overdue tickets"""
    filters = {}
    
    if technician_id:
        filters["technician_id"] = technician_id
    if priority:
        filters["priority"] = priority
    
    result = await client.get_overdue_tickets(filters)
    overdue_tickets = result.get("tickets", [])
    
    return {
        "success": True,
        "action": "get_overdue",
        "filters": filters,
        "overdue_count": len(overdue_tickets),
        "critical_overdue": len([t for t in overdue_tickets if t.get("priority") == "CRITICAL"]),
        "high_overdue": len([t for t in overdue_tickets if t.get("priority") == "HIGH"]),
        "average_overdue_hours": result.get("average_overdue_hours", 0),
        "message": f"Found {len(overdue_tickets)} overdue tickets",
        "data": result
    }


async def _get_progress_metrics(client: SuperOpsClient, technician_id: Optional[str], days_back: int) -> Dict[str, Any]:
    """Get progress metrics and KPIs"""
    filters = {
        "start_date": (datetime.now() - timedelta(days=days_back)).isoformat(),
        "end_date": datetime.now().isoformat()
    }
    
    if technician_id:
        filters["technician_id"] = technician_id
    
    result = await client.get_progress_metrics(filters)
    
    return {
        "success": True,
        "action": "get_metrics",
        "period_days": days_back,
        "filters": filters,
        "tickets_resolved": result.get("tickets_resolved", 0),
        "average_resolution_time": result.get("average_resolution_time", 0),
        "first_response_time": result.get("first_response_time", 0),
        "sla_compliance_rate": result.get("sla_compliance_rate", 0),
        "productivity_score": result.get("productivity_score", 0),
        "message": f"Progress metrics for last {days_back} days",
        "data": result
    }


