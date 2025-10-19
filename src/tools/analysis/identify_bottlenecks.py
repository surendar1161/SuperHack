"""Identify bottlenecks tool for IT Technician Agent - Strands Compatible"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from strands import tool

from ...clients.superops_client import SuperOpsClient
from ...utils.logger import get_logger

logger = get_logger("identify_bottlenecks")


def _build_filters(department_id: Optional[str], technician_id: Optional[str], priority_filter: Optional[str]) -> Dict[str, Any]:
    """Build filter dictionary from parameters"""
    filters = {}
    if department_id:
        filters["department_id"] = department_id
    if technician_id:
        filters["technician_id"] = technician_id
    if priority_filter:
        filters["priority"] = priority_filter
    return filters


def _get_status_threshold(status: str) -> float:
    """Get time threshold for different statuses (in hours)"""
    thresholds = {
        "OPEN": 2.0,  # Should be assigned within 2 hours
        "IN_PROGRESS": 48.0,  # Should show progress within 48 hours
        "WAITING": 24.0,  # Should not wait more than 24 hours
        "RESOLVED": 2.0,  # Should be closed within 2 hours of resolution
    }
    return thresholds.get(status, 24.0)


def _get_status_recommendation(status: str) -> str:
    """Get recommendation for status delays"""
    recommendations = {
        "OPEN": "Implement faster assignment workflows or increase technician availability",
        "IN_PROGRESS": "Improve progress tracking and regular status updates",
        "WAITING": "Set up automated reminders and escalation procedures",
        "RESOLVED": "Streamline ticket closure process and user confirmation"
    }
    return recommendations.get(status, "Review process efficiency for this status")


async def _analyze_ticket_flow_bottlenecks(client: SuperOpsClient, time_period: int, department_id: Optional[str], technician_id: Optional[str], priority_filter: Optional[str]) -> Dict[str, Any]:
    """Analyze ticket flow for bottlenecks"""
    filters = _build_filters(department_id, technician_id, priority_filter)
    
    # Get ticket flow data
    flow_data = await client.get_ticket_flow_analysis(time_period, filters)
    
    bottlenecks = []
    
    # Analyze status transitions
    status_times = flow_data.get("average_status_times", {})
    for status, avg_time in status_times.items():
        if avg_time > _get_status_threshold(status):
            bottlenecks.append({
                "type": "status_delay",
                "status": status,
                "average_time": avg_time,
                "threshold": _get_status_threshold(status),
                "severity": "high" if avg_time > _get_status_threshold(status) * 2 else "medium",
                "recommendation": _get_status_recommendation(status)
            })
    
    # Analyze assignment delays
    assignment_data = flow_data.get("assignment_metrics", {})
    if assignment_data.get("average_assignment_time", 0) > 24:  # 24 hours threshold
        bottlenecks.append({
            "type": "assignment_delay",
            "average_time": assignment_data.get("average_assignment_time"),
            "unassigned_tickets": assignment_data.get("unassigned_count", 0),
            "severity": "high",
            "recommendation": "Implement auto-assignment rules or increase technician availability"
        })
    
    # Analyze first response delays
    response_data = flow_data.get("response_metrics", {})
    if response_data.get("average_first_response", 0) > 4:  # 4 hours threshold
        bottlenecks.append({
            "type": "response_delay",
            "average_time": response_data.get("average_first_response"),
            "severity": "medium",
            "recommendation": "Improve initial response workflows and notifications"
        })
    
    return {
        "success": True,
        "analysis_type": "ticket_flow",
        "time_period": time_period,
        "bottlenecks_found": len(bottlenecks),
        "bottlenecks": bottlenecks,
        "summary_metrics": {
            "total_tickets": flow_data.get("total_tickets", 0),
            "average_resolution_time": flow_data.get("average_resolution_time", 0),
            "tickets_exceeding_sla": flow_data.get("sla_breaches", 0)
        },
        "message": f"Identified {len(bottlenecks)} ticket flow bottlenecks"
    }


async def _analyze_resource_bottlenecks(client: SuperOpsClient, time_period: int, department_id: Optional[str], technician_id: Optional[str], priority_filter: Optional[str]) -> Dict[str, Any]:
    """Analyze resource utilization bottlenecks"""
    filters = _build_filters(department_id, technician_id, priority_filter)
    
    resource_data = await client.get_resource_utilization(time_period, filters)
    
    bottlenecks = []
    
    # Analyze technician capacity
    technician_metrics = resource_data.get("technician_metrics", {})
    for tech_id, metrics in technician_metrics.items():
        utilization = metrics.get("utilization_rate", 0)
        if utilization > 0.9:  # Over 90% utilization
            bottlenecks.append({
                "type": "technician_overload",
                "technician_id": tech_id,
                "utilization_rate": utilization,
                "active_tickets": metrics.get("active_tickets", 0),
                "severity": "high",
                "recommendation": "Redistribute workload or hire additional technicians"
            })
        elif utilization < 0.3:  # Under 30% utilization
            bottlenecks.append({
                "type": "technician_underutilized",
                "technician_id": tech_id,
                "utilization_rate": utilization,
                "severity": "low",
                "recommendation": "Consider reassigning tickets or training for new skills"
            })
    
    # Analyze category distribution
    category_metrics = resource_data.get("category_distribution", {})
    total_tickets = sum(category_metrics.values())
    for category, count in category_metrics.items():
        if count / total_tickets > 0.4:  # Over 40% of tickets in one category
            bottlenecks.append({
                "type": "category_concentration",
                "category": category,
                "percentage": (count / total_tickets) * 100,
                "ticket_count": count,
                "severity": "medium",
                "recommendation": f"Consider specialized team for {category} issues"
            })
    
    return {
        "success": True,
        "analysis_type": "resource_usage",
        "time_period": time_period,
        "bottlenecks_found": len(bottlenecks),
        "bottlenecks": bottlenecks,
        "resource_summary": {
            "total_technicians": len(technician_metrics),
            "average_utilization": sum(m.get("utilization_rate", 0) for m in technician_metrics.values()) / max(len(technician_metrics), 1),
            "peak_categories": sorted(category_metrics.items(), key=lambda x: x[1], reverse=True)[:3]
        },
        "message": f"Identified {len(bottlenecks)} resource utilization bottlenecks"
    }


async def _analyze_resource_bottlenecks(client: SuperOpsClient, time_period: int, department_id: Optional[str], technician_id: Optional[str], priority_filter: Optional[str]) -> Dict[str, Any]:
    """Analyze resource utilization bottlenecks"""
    filters = _build_filters(department_id, technician_id, priority_filter)
    
    resource_data = await client.get_resource_utilization(time_period, filters)
    
    bottlenecks = []
    
    # Analyze technician capacity
    technician_metrics = resource_data.get("technician_metrics", {})
    for tech_id, metrics in technician_metrics.items():
        utilization = metrics.get("utilization_rate", 0)
        if utilization > 0.9:  # Over 90% utilization
            bottlenecks.append({
                "type": "technician_overload",
                "technician_id": tech_id,
                "utilization_rate": utilization,
                "active_tickets": metrics.get("active_tickets", 0),
                "severity": "high",
                "recommendation": "Redistribute workload or hire additional technicians"
            })
        elif utilization < 0.3:  # Under 30% utilization
            bottlenecks.append({
                "type": "technician_underutilized",
                "technician_id": tech_id,
                "utilization_rate": utilization,
                "severity": "low",
                "recommendation": "Consider reassigning tickets or training for new skills"
            })
    
    # Analyze category distribution
    category_metrics = resource_data.get("category_distribution", {})
    total_tickets = sum(category_metrics.values()) if category_metrics else 1
    for category, count in category_metrics.items():
        if count / total_tickets > 0.4:  # Over 40% of tickets in one category
            bottlenecks.append({
                "type": "category_concentration",
                "category": category,
                "percentage": (count / total_tickets) * 100,
                "ticket_count": count,
                "severity": "medium",
                "recommendation": f"Consider specialized team for {category} issues"
            })
    
    return {
        "success": True,
        "analysis_type": "resource_usage",
        "time_period": time_period,
        "bottlenecks_found": len(bottlenecks),
        "bottlenecks": bottlenecks,
        "resource_summary": {
            "total_technicians": len(technician_metrics),
            "average_utilization": sum(m.get("utilization_rate", 0) for m in technician_metrics.values()) / max(len(technician_metrics), 1),
            "peak_categories": sorted(category_metrics.items(), key=lambda x: x[1], reverse=True)[:3]
        },
        "message": f"Identified {len(bottlenecks)} resource utilization bottlenecks"
    }


async def _analyze_technician_bottlenecks(client: SuperOpsClient, time_period: int, department_id: Optional[str], technician_id: Optional[str], priority_filter: Optional[str]) -> Dict[str, Any]:
    """Analyze individual technician performance bottlenecks"""
    filters = _build_filters(department_id, technician_id, priority_filter)
    
    workload_data = await client.get_technician_workload_analysis(time_period, filters)
    
    bottlenecks = []
    
    # Analyze individual technician performance
    for technician in workload_data.get("technicians", []):
        tech_id = technician.get("id")
        metrics = technician.get("metrics", {})
        
        # Check resolution time
        avg_resolution = metrics.get("average_resolution_time", 0)
        team_avg = workload_data.get("team_average_resolution", 0)
        if avg_resolution > team_avg * 1.5:  # 50% above team average
            bottlenecks.append({
                "type": "slow_resolution",
                "technician_id": tech_id,
                "average_resolution_time": avg_resolution,
                "team_average": team_avg,
                "severity": "medium",
                "recommendation": "Provide additional training or mentoring"
            })
        
        # Check ticket backlog
        active_tickets = metrics.get("active_tickets", 0)
        if active_tickets > 20:  # Threshold for high backlog
            bottlenecks.append({
                "type": "high_backlog",
                "technician_id": tech_id,
                "active_tickets": active_tickets,
                "severity": "high",
                "recommendation": "Redistribute tickets or provide additional support"
            })
        
        # Check SLA compliance
        sla_compliance = metrics.get("sla_compliance_rate", 0)
        if sla_compliance < 0.8:  # Below 80% compliance
            bottlenecks.append({
                "type": "sla_compliance_issue",
                "technician_id": tech_id,
                "compliance_rate": sla_compliance,
                "severity": "high",
                "recommendation": "Review workflows and provide SLA training"
            })
    
    return {
        "success": True,
        "analysis_type": "technician_workload",
        "time_period": time_period,
        "bottlenecks_found": len(bottlenecks),
        "bottlenecks": bottlenecks,
        "workload_summary": workload_data.get("summary", {}),
        "message": f"Identified {len(bottlenecks)} technician performance bottlenecks"
    }


async def _analyze_sla_bottlenecks(client: SuperOpsClient, time_period: int, department_id: Optional[str], technician_id: Optional[str], priority_filter: Optional[str]) -> Dict[str, Any]:
    """Analyze SLA compliance bottlenecks"""
    filters = _build_filters(department_id, technician_id, priority_filter)
    
    sla_data = await client.get_sla_compliance_analysis(time_period, filters)
    
    bottlenecks = []
    
    # Overall SLA compliance
    overall_compliance = sla_data.get("overall_compliance_rate", 0)
    if overall_compliance < 0.9:  # Below 90% compliance
        bottlenecks.append({
            "type": "overall_sla_breach",
            "compliance_rate": overall_compliance,
            "breached_tickets": sla_data.get("breached_tickets", 0),
            "severity": "critical",
            "recommendation": "Immediate review of SLA processes and resource allocation"
        })
    
    # Priority-specific SLA issues
    priority_compliance = sla_data.get("compliance_by_priority", {})
    for priority, compliance in priority_compliance.items():
        if compliance < 0.85:  # Below 85% for any priority
            bottlenecks.append({
                "type": "priority_sla_breach",
                "priority": priority,
                "compliance_rate": compliance,
                "severity": "high" if priority in ["CRITICAL", "HIGH"] else "medium",
                "recommendation": f"Focus on {priority} priority ticket handling processes"
            })
    
    # Category-specific SLA issues
    category_compliance = sla_data.get("compliance_by_category", {})
    for category, compliance in category_compliance.items():
        if compliance < 0.8:  # Below 80% for any category
            bottlenecks.append({
                "type": "category_sla_breach",
                "category": category,
                "compliance_rate": compliance,
                "severity": "medium",
                "recommendation": f"Review {category} handling procedures and training"
            })
    
    return {
        "success": True,
        "analysis_type": "sla_compliance",
        "time_period": time_period,
        "bottlenecks_found": len(bottlenecks),
        "bottlenecks": bottlenecks,
        "sla_summary": {
            "overall_compliance": overall_compliance,
            "total_sla_breaches": sla_data.get("total_breaches", 0),
            "worst_performing_category": min(category_compliance.items(), key=lambda x: x[1], default=("None", 1.0))[0]
        },
        "message": f"Identified {len(bottlenecks)} SLA compliance bottlenecks"
    }




@tool
async def identify_bottlenecks(
    analysis_type: str = "all",
    time_period: int = 7,
    department_id: Optional[str] = None,
    technician_id: Optional[str] = None,
    priority_filter: Optional[str] = None
) -> Dict[str, Any]:
    """
    Identify performance bottlenecks in IT support operations
    
    Args:
        analysis_type: Type of analysis ("all", "ticket_flow", "resource_usage", "technician_workload", "sla_compliance")
        time_period: Analysis period in days (default: 7)
        department_id: Optional department filter
        technician_id: Optional technician filter
        priority_filter: Optional priority filter
        
    Returns:
        Dictionary containing bottleneck analysis results
    """
    try:
        from ...agents.config import AgentConfig
        
        # Create SuperOps client
        config = AgentConfig()
        client = SuperOpsClient(config)
        
        logger.info(f"Starting bottleneck analysis: {analysis_type} for {time_period} days")
        
        results = {
            "success": True,
            "analysis_type": analysis_type,
            "time_period": time_period,
            "timestamp": datetime.now().isoformat(),
            "bottlenecks": []
        }
        
        if analysis_type in ["all", "ticket_flow"]:
            flow_results = await _analyze_ticket_flow_bottlenecks(client, time_period, department_id, technician_id, priority_filter)
            results["bottlenecks"].extend(flow_results.get("bottlenecks", []))
        
        if analysis_type in ["all", "resource_usage"]:
            resource_results = await _analyze_resource_bottlenecks(client, time_period, department_id, technician_id, priority_filter)
            results["bottlenecks"].extend(resource_results.get("bottlenecks", []))
        
        if analysis_type in ["all", "technician_workload"]:
            workload_results = await _analyze_technician_bottlenecks(client, time_period, department_id, technician_id, priority_filter)
            results["bottlenecks"].extend(workload_results.get("bottlenecks", []))
        
        if analysis_type in ["all", "sla_compliance"]:
            sla_results = await _analyze_sla_bottlenecks(client, time_period, department_id, technician_id, priority_filter)
            results["bottlenecks"].extend(sla_results.get("bottlenecks", []))
        
        # Sort bottlenecks by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        results["bottlenecks"].sort(key=lambda x: severity_order.get(x.get("severity", "low"), 3))
        
        results["total_bottlenecks"] = len(results["bottlenecks"])
        results["critical_bottlenecks"] = len([b for b in results["bottlenecks"] if b.get("severity") == "critical"])
        results["high_bottlenecks"] = len([b for b in results["bottlenecks"] if b.get("severity") == "high"])
        
        logger.info(f"Bottleneck analysis completed: {results['total_bottlenecks']} bottlenecks found")
        
        return results
        
    except Exception as e:
        logger.error(f"Error in bottleneck analysis: {e}")
        return {
            "success": False,
            "error": str(e),
            "analysis_type": analysis_type,
            "timestamp": datetime.now().isoformat()
        }


async def _analyze_ticket_flow_bottlenecks(client: SuperOpsClient, time_period: int, department_id: Optional[str], technician_id: Optional[str], priority_filter: Optional[str]) -> Dict[str, Any]:
    """Analyze ticket flow bottlenecks"""
    filters = _build_filters(department_id, technician_id, priority_filter)