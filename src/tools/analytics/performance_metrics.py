"""Performance metrics tool for IT Technician Agent - Strands Compatible"""

from typing import Any, Dict, Optional, List
from datetime import datetime, timedelta
from strands import tool

from ...clients.superops_client import SuperOpsClient
from ...utils.logger import get_logger

logger = get_logger("performance_metrics")


def _parse_date_range(date_range: str) -> tuple[datetime, datetime]:
    """Parse date range string into start and end dates"""
    now = datetime.now()
    
    if date_range == "last_7_days":
        start_date = now - timedelta(days=7)
    elif date_range == "last_30_days":
        start_date = now - timedelta(days=30)
    elif date_range == "last_90_days":
        start_date = now - timedelta(days=90)
    elif date_range == "this_month":
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif date_range == "last_month":
        first_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_date = (first_this_month - timedelta(days=1)).replace(day=1)
        now = first_this_month - timedelta(seconds=1)
    else:
        start_date = now - timedelta(days=30)  # Default to 30 days
    
    return start_date, now


async def _get_tickets_for_period(client: SuperOpsClient, start_date: datetime, end_date: datetime, filters: Dict = None) -> List[Dict]:
    """Get tickets for the specified period"""
    try:
        date_range_str = f"{start_date.isoformat()},{end_date.isoformat()}"
        tickets = await client.get_tickets_by_date_range(date_range_str, filters)
        return tickets
    except Exception as e:
        logger.warning(f"Could not fetch tickets: {e}")
        return []


def _calculate_resolution_metrics(tickets: List[Dict]) -> Dict[str, Any]:
    """Calculate resolution time metrics"""
    resolved_tickets = [t for t in tickets if t.get("status") in ["resolved", "closed"]]
    
    if not resolved_tickets:
        return {
            "total_resolved": 0,
            "average_resolution_time": 0,
            "median_resolution_time": 0,
            "resolution_times_by_priority": {}
        }

    resolution_times = []
    priority_times = {}

    for ticket in resolved_tickets:
        created_at = datetime.fromisoformat(ticket.get("created_at", ""))
        resolved_at = datetime.fromisoformat(ticket.get("resolved_at", ""))
        resolution_time = (resolved_at - created_at).total_seconds() / 3600  # hours
        
        resolution_times.append(resolution_time)
        
        priority = ticket.get("priority", "medium")
        if priority not in priority_times:
            priority_times[priority] = []
        priority_times[priority].append(resolution_time)

    # Calculate statistics
    avg_resolution = sum(resolution_times) / len(resolution_times)
    resolution_times.sort()
    median_resolution = resolution_times[len(resolution_times) // 2]

    # Priority-based averages
    priority_averages = {}
    for priority, times in priority_times.items():
        priority_averages[priority] = sum(times) / len(times)

    return {
        "total_resolved": len(resolved_tickets),
        "average_resolution_time": round(avg_resolution, 2),
        "median_resolution_time": round(median_resolution, 2),
        "resolution_times_by_priority": priority_averages
    }


def _calculate_sla_compliance(tickets: List[Dict]) -> Dict[str, Any]:
    """Calculate SLA compliance metrics"""
    sla_targets = {
        "critical": {"response": 0.25, "resolution": 4},
        "high": {"response": 1, "resolution": 8},
        "medium": {"response": 4, "resolution": 24},
        "low": {"response": 8, "resolution": 72}
    }

    compliance_data = {
        "response_sla_met": 0,
        "resolution_sla_met": 0,
        "total_tickets": len(tickets),
        "compliance_by_priority": {}
    }

    for ticket in tickets:
        priority = ticket.get("priority", "medium").lower()
        created_at = datetime.fromisoformat(ticket.get("created_at", ""))
        
        # Response SLA
        first_response = ticket.get("first_response_time")
        if first_response:
            response_time = (datetime.fromisoformat(first_response) - created_at).total_seconds() / 3600
            if response_time <= sla_targets.get(priority, sla_targets["medium"])["response"]:
                compliance_data["response_sla_met"] += 1

        # Resolution SLA
        if ticket.get("status") in ["resolved", "closed"]:
            resolved_at = datetime.fromisoformat(ticket.get("resolved_at", ""))
            resolution_time = (resolved_at - created_at).total_seconds() / 3600
            if resolution_time <= sla_targets.get(priority, sla_targets["medium"])["resolution"]:
                compliance_data["resolution_sla_met"] += 1

    # Calculate percentages
    total = compliance_data["total_tickets"]
    if total > 0:
        compliance_data["response_sla_percentage"] = round((compliance_data["response_sla_met"] / total) * 100, 2)
        compliance_data["resolution_sla_percentage"] = round((compliance_data["resolution_sla_met"] / total) * 100, 2)
    else:
        compliance_data["response_sla_percentage"] = 0
        compliance_data["resolution_sla_percentage"] = 0

    return compliance_data


def _calculate_ticket_volume_metrics(tickets: List[Dict]) -> Dict[str, Any]:
    """Calculate ticket volume metrics"""
    volume_data = {
        "total_tickets": len(tickets),
        "tickets_by_status": {},
        "tickets_by_priority": {},
        "tickets_by_category": {},
        "daily_volume": {}
    }

    # Group by various dimensions
    for ticket in tickets:
        # Status
        status = ticket.get("status", "unknown")
        volume_data["tickets_by_status"][status] = volume_data["tickets_by_status"].get(status, 0) + 1

        # Priority
        priority = ticket.get("priority", "medium")
        volume_data["tickets_by_priority"][priority] = volume_data["tickets_by_priority"].get(priority, 0) + 1

        # Category
        category = ticket.get("category", "General")
        volume_data["tickets_by_category"][category] = volume_data["tickets_by_category"].get(category, 0) + 1

        # Daily volume
        created_date = datetime.fromisoformat(ticket.get("created_at", "")).date().isoformat()
        volume_data["daily_volume"][created_date] = volume_data["daily_volume"].get(created_date, 0) + 1

    return volume_data


def _calculate_technician_performance(tickets: List[Dict]) -> Dict[str, Any]:
    """Calculate technician performance metrics"""
    technician_data = {}

    for ticket in tickets:
        assignee = ticket.get("assignee", {})
        if not assignee:
            continue

        tech_id = assignee.get("id", "unassigned")
        tech_name = assignee.get("name", "Unknown")

        if tech_id not in technician_data:
            technician_data[tech_id] = {
                "name": tech_name,
                "total_tickets": 0,
                "resolved_tickets": 0,
                "resolution_times": [],
                "tickets_by_priority": {}
            }

        tech_data = technician_data[tech_id]
        tech_data["total_tickets"] += 1

        # Track resolution
        if ticket.get("status") in ["resolved", "closed"]:
            tech_data["resolved_tickets"] += 1
            
            # Calculate resolution time
            created_at = datetime.fromisoformat(ticket.get("created_at", ""))
            resolved_at = datetime.fromisoformat(ticket.get("resolved_at", ""))
            resolution_time = (resolved_at - created_at).total_seconds() / 3600
            tech_data["resolution_times"].append(resolution_time)

        # Track by priority
        priority = ticket.get("priority", "medium")
        tech_data["tickets_by_priority"][priority] = tech_data["tickets_by_priority"].get(priority, 0) + 1

    # Calculate averages and rates
    for tech_id, data in technician_data.items():
        if data["resolution_times"]:
            data["average_resolution_time"] = sum(data["resolution_times"]) / len(data["resolution_times"])
        else:
            data["average_resolution_time"] = 0

        if data["total_tickets"] > 0:
            data["resolution_rate"] = (data["resolved_tickets"] / data["total_tickets"]) * 100
        else:
            data["resolution_rate"] = 0

    return technician_data


@tool
async def performance_metrics(
    date_range: str = "last_30_days",
    metric_types: Optional[List[str]] = None,
    technician_id: Optional[str] = None,
    category_filter: Optional[str] = None,
    priority_filter: Optional[str] = None,
    include_trends: bool = True
) -> Dict[str, Any]:
    """
    Generate performance metrics and analytics for IT operations
    
    Args:
        date_range: Date range for metrics - last_7_days, last_30_days, last_90_days, this_month, last_month
        metric_types: Types of metrics to generate - resolution_time, sla_compliance, ticket_volume, technician_performance, category_analysis
        technician_id: Specific technician ID to analyze (optional, for individual performance)
        category_filter: Filter by ticket category - Hardware, Software, Network, Email, Security, Account
        priority_filter: Filter by priority - LOW, MEDIUM, HIGH, URGENT, CRITICAL
        include_trends: Whether to include trend analysis and comparisons
        
    Returns:
        Dictionary containing performance metrics and analytics data
    """
    try:
        logger.info(f"Generating performance metrics for date range: {date_range}")
        
        # Initialize SuperOps client (in real implementation, this would be injected)
        from ...agents.config import AgentConfig
        config = AgentConfig()
        client = SuperOpsClient(config)
        
        # Default metric types if not provided
        if metric_types is None:
            metric_types = ["resolution_time", "sla_compliance", "ticket_volume"]
        
        # Parse date range
        start_date, end_date = _parse_date_range(date_range)
        
        # Build filters
        filters = {}
        if technician_id:
            filters["assignee_id"] = technician_id
        if category_filter:
            filters["category"] = category_filter
        if priority_filter:
            filters["priority"] = priority_filter.lower()
        
        # Get tickets for the period
        tickets = await _get_tickets_for_period(client, start_date, end_date, filters)
        
        # Generate requested metrics
        metrics = {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "date_range": date_range
            },
            "filters_applied": filters,
            "total_tickets_analyzed": len(tickets)
        }
        
        if "resolution_time" in metric_types:
            metrics["resolution_metrics"] = _calculate_resolution_metrics(tickets)
        
        if "sla_compliance" in metric_types:
            metrics["sla_compliance"] = _calculate_sla_compliance(tickets)
        
        if "ticket_volume" in metric_types:
            metrics["volume_metrics"] = _calculate_ticket_volume_metrics(tickets)
        
        if "technician_performance" in metric_types:
            metrics["technician_performance"] = _calculate_technician_performance(tickets)
        
        logger.info(f"Generated performance metrics for {len(tickets)} tickets")
        
        return {
            "success": True,
            "metrics": metrics,
            "generated_at": datetime.now().isoformat(),
            "message": f"Performance metrics generated for {date_range}"
        }
        
    except Exception as e:
        logger.error(f"Failed to generate performance metrics: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to generate performance metrics for {date_range}"
        }

