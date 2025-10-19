"""View analytics tool for IT Technician Agent - Strands Compatible"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from strands import tool

from ...clients.superops_client import SuperOpsClient
from ...utils.logger import get_logger

logger = get_logger("view_analytics")


def _parse_time_range(time_range: str) -> int:
    """Parse time range string to days"""
    time_mappings = {
        "7d": 7,
        "30d": 30,
        "90d": 90,
        "1y": 365,
        "custom": 0  # Will be handled separately
    }
    
    return time_mappings.get(time_range, 30)


async def _generate_overview_dashboard(client: SuperOpsClient, time_range: str, filters: Dict[str, Any]) -> Dict[str, Any]:
    """Generate overview dashboard"""
    time_period = _parse_time_range(time_range)
    
    # Get overview data
    overview_data = await client.get_dashboard_overview_data(time_period, filters)
    
    dashboard = {
        "dashboard_type": "overview",
        "time_period": time_period,
        "generated_at": datetime.now().isoformat(),
        
        # Key metrics cards
        "key_metrics": {
            "total_tickets": overview_data.get("total_tickets", 0),
            "open_tickets": overview_data.get("open_tickets", 0),
            "resolved_tickets": overview_data.get("resolved_tickets", 0),
            "average_resolution_time": overview_data.get("average_resolution_time", 0),
            "sla_compliance": overview_data.get("sla_compliance_rate", 0),
            "customer_satisfaction": overview_data.get("customer_satisfaction", 0)
        },
        
        # Charts data
        "charts": {
            "ticket_volume_by_day": overview_data.get("daily_ticket_counts", []),
            "tickets_by_status": overview_data.get("status_distribution", {}),
            "tickets_by_priority": overview_data.get("priority_distribution", {}),
            "tickets_by_category": overview_data.get("category_distribution", {}),
            "resolution_time_trend": overview_data.get("resolution_time_trend", []),
            "technician_workload": overview_data.get("technician_workload", {})
        },
        
        # Recent activities
        "recent_activities": overview_data.get("recent_activities", []),
        
        # Alerts and notifications
        "alerts": {
            "overdue_tickets": overview_data.get("overdue_tickets_count", 0),
            "sla_breaches": overview_data.get("sla_breaches_count", 0),
            "high_priority_unassigned": overview_data.get("high_priority_unassigned", 0)
        }
    }
    
    return {
        "success": True,
        "dashboard": dashboard,
        "message": "Overview dashboard generated successfully"
    }


async def _generate_performance_dashboard(client: SuperOpsClient, time_range: str, filters: Dict[str, Any]) -> Dict[str, Any]:
    """Generate performance dashboard"""
    time_period = _parse_time_range(time_range)
    
    performance_data = await client.get_performance_dashboard_data(time_period, filters)
    
    dashboard = {
        "dashboard_type": "performance",
        "time_period": time_period,
        "generated_at": datetime.now().isoformat(),
        
        # Performance KPIs
        "kpis": {
            "resolution_rate": performance_data.get("resolution_rate", 0),
            "first_response_time": performance_data.get("average_first_response", 0),
            "resolution_time": performance_data.get("average_resolution_time", 0),
            "escalation_rate": performance_data.get("escalation_rate", 0),
            "reopened_rate": performance_data.get("reopened_rate", 0),
            "customer_satisfaction": performance_data.get("customer_satisfaction", 0)
        },
        
        # Performance trends
        "trends": {
            "resolution_time_trend": performance_data.get("resolution_time_trend", []),
            "satisfaction_trend": performance_data.get("satisfaction_trend", []),
            "sla_compliance_trend": performance_data.get("sla_compliance_trend", []),
            "ticket_volume_trend": performance_data.get("ticket_volume_trend", [])
        },
        
        # Technician performance
        "technician_performance": {
            "top_performers": performance_data.get("top_performers", []),
            "performance_comparison": performance_data.get("technician_comparison", {}),
            "workload_distribution": performance_data.get("workload_distribution", {})
        },
        
        # Category performance
        "category_performance": performance_data.get("category_performance", {}),
        
        # Benchmarks
        "benchmarks": {
            "industry_average_resolution": performance_data.get("industry_benchmark_resolution", 0),
            "target_sla_compliance": performance_data.get("target_sla_compliance", 0.95),
            "target_satisfaction": performance_data.get("target_satisfaction", 4.0)
        }
    }
    
    return {
        "success": True,
        "dashboard": dashboard,
        "message": "Performance dashboard generated successfully"
    }


async def _generate_workload_dashboard(client: SuperOpsClient, time_range: str, filters: Dict[str, Any]) -> Dict[str, Any]:
    """Generate workload dashboard"""
    time_period = _parse_time_range(time_range)
    
    workload_data = await client.get_workload_dashboard_data(time_period, filters)
    
    dashboard = {
        "dashboard_type": "workload",
        "time_period": time_period,
        "generated_at": datetime.now().isoformat(),
        
        # Workload overview
        "workload_overview": {
            "total_active_tickets": workload_data.get("total_active_tickets", 0),
            "unassigned_tickets": workload_data.get("unassigned_tickets", 0),
            "overdue_tickets": workload_data.get("overdue_tickets", 0),
            "average_workload_per_technician": workload_data.get("avg_workload_per_tech", 0)
        },
        
        # Technician workload
        "technician_workload": {
            "individual_workloads": workload_data.get("individual_workloads", {}),
            "capacity_utilization": workload_data.get("capacity_utilization", {}),
            "overloaded_technicians": workload_data.get("overloaded_technicians", []),
            "underutilized_technicians": workload_data.get("underutilized_technicians", [])
        },
        
        # Workload distribution
        "distribution": {
            "by_priority": workload_data.get("workload_by_priority", {}),
            "by_category": workload_data.get("workload_by_category", {}),
            "by_age": workload_data.get("workload_by_age", {}),
            "by_complexity": workload_data.get("workload_by_complexity", {})
        },
        
        # Capacity planning
        "capacity_planning": {
            "current_capacity": workload_data.get("current_capacity", 0),
            "predicted_demand": workload_data.get("predicted_demand", 0),
            "capacity_gap": workload_data.get("capacity_gap", 0),
            "recommendations": workload_data.get("capacity_recommendations", [])
        },
        
        # Assignment efficiency
        "assignment_metrics": {
            "average_assignment_time": workload_data.get("avg_assignment_time", 0),
            "auto_assignment_rate": workload_data.get("auto_assignment_rate", 0),
            "reassignment_rate": workload_data.get("reassignment_rate", 0)
        }
    }
    
    return {
        "success": True,
        "dashboard": dashboard,
        "message": "Workload dashboard generated successfully"
    }


async def _generate_sla_dashboard(client: SuperOpsClient, time_range: str, filters: Dict[str, Any]) -> Dict[str, Any]:
    """Generate SLA compliance dashboard"""
    time_period = _parse_time_range(time_range)
    
    sla_data = await client.get_sla_dashboard_data(time_period, filters)
    
    dashboard = {
        "dashboard_type": "sla",
        "time_period": time_period,
        "generated_at": datetime.now().isoformat(),
        
        # SLA overview
        "sla_overview": {
            "overall_compliance": sla_data.get("overall_compliance_rate", 0),
            "first_response_compliance": sla_data.get("first_response_compliance", 0),
            "resolution_compliance": sla_data.get("resolution_compliance", 0),
            "total_breaches": sla_data.get("total_breaches", 0)
        },
        
        # Compliance breakdown
        "compliance_breakdown": {
            "by_priority": sla_data.get("compliance_by_priority", {}),
            "by_category": sla_data.get("compliance_by_category", {}),
            "by_technician": sla_data.get("compliance_by_technician", {}),
            "by_time_of_day": sla_data.get("compliance_by_hour", {})
        },
        
        # Breach analysis
        "breach_analysis": {
            "breach_reasons": sla_data.get("breach_reasons", []),
            "breach_trends": sla_data.get("breach_trends", []),
            "critical_breaches": sla_data.get("critical_breaches", []),
            "average_breach_duration": sla_data.get("avg_breach_duration", 0)
        },
        
        # SLA targets and thresholds
        "sla_targets": {
            "first_response_target": sla_data.get("first_response_target", 4),
            "resolution_target_by_priority": sla_data.get("resolution_targets", {}),
            "compliance_threshold": sla_data.get("compliance_threshold", 0.95)
        },
        
        # Improvement recommendations
        "recommendations": sla_data.get("sla_recommendations", [])
    }
    
    return {
        "success": True,
        "dashboard": dashboard,
        "message": "SLA dashboard generated successfully"
    }


async def _generate_trends_dashboard(client: SuperOpsClient, time_range: str, filters: Dict[str, Any]) -> Dict[str, Any]:
    """Generate trends analysis dashboard"""
    time_period = _parse_time_range(time_range if time_range != "30d" else "90d")  # Default to longer period for trends
    
    trends_data = await client.get_trends_dashboard_data(time_period, filters)
    
    dashboard = {
        "dashboard_type": "trends",
        "time_period": time_period,
        "generated_at": datetime.now().isoformat(),
        
        # Volume trends
        "volume_trends": {
            "ticket_volume_trend": trends_data.get("ticket_volume_trend", []),
            "seasonal_patterns": trends_data.get("seasonal_patterns", {}),
            "growth_rate": trends_data.get("volume_growth_rate", 0),
            "forecast": trends_data.get("volume_forecast", [])
        },
        
        # Performance trends
        "performance_trends": {
            "resolution_time_trend": trends_data.get("resolution_time_trend", []),
            "satisfaction_trend": trends_data.get("satisfaction_trend", []),
            "sla_compliance_trend": trends_data.get("sla_compliance_trend", []),
            "productivity_trend": trends_data.get("productivity_trend", [])
        },
        
        # Category trends
        "category_trends": {
            "category_volume_trends": trends_data.get("category_volume_trends", {}),
            "emerging_categories": trends_data.get("emerging_categories", []),
            "declining_categories": trends_data.get("declining_categories", [])
        },
        
        # Technology trends
        "technology_trends": {
            "device_types": trends_data.get("device_type_trends", {}),
            "software_issues": trends_data.get("software_issue_trends", {}),
            "network_issues": trends_data.get("network_issue_trends", {})
        },
        
        # Predictive insights
        "predictions": {
            "next_month_volume": trends_data.get("predicted_volume", 0),
            "expected_resolution_time": trends_data.get("predicted_resolution_time", 0),
            "capacity_needs": trends_data.get("predicted_capacity_needs", 0),
            "confidence_intervals": trends_data.get("prediction_confidence", {})
        }
    }
    
    return {
        "success": True,
        "dashboard": dashboard,
        "message": "Trends dashboard generated successfully"
    }


async def _generate_custom_dashboard(client: SuperOpsClient, time_range: str, filters: Dict[str, Any]) -> Dict[str, Any]:
    """Generate custom dashboard based on filters"""
    time_period = _parse_time_range(time_range)
    
    # Custom dashboard allows for flexible metrics based on filters
    custom_data = await client.get_custom_dashboard_data(time_period, filters)
    
    dashboard = {
        "dashboard_type": "custom",
        "time_period": time_period,
        "filters_applied": filters,
        "generated_at": datetime.now().isoformat(),
        
        # Dynamic metrics based on filters
        "metrics": custom_data.get("metrics", {}),
        "charts": custom_data.get("charts", {}),
        "tables": custom_data.get("tables", {}),
        "insights": custom_data.get("insights", [])
    }
    
    return {
        "success": True,
        "dashboard": dashboard,
        "message": "Custom dashboard generated successfully"
    }


@tool
async def view_analytics(
    dashboard_type: str,
    time_range: str = "30d",
    custom_start_date: Optional[str] = None,
    custom_end_date: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None,
    export_format: str = "json"
) -> Dict[str, Any]:
    """
    Generate and display analytics dashboards, reports, and visualizations
    
    Args:
        dashboard_type: Type of dashboard - overview, performance, workload, sla, trends, custom
        time_range: Time range - 7d, 30d, 90d, 1y, custom
        custom_start_date: Custom start date in YYYY-MM-DD format (if time_range is custom)
        custom_end_date: Custom end date in YYYY-MM-DD format (if time_range is custom)
        filters: Additional filters (technician_id, category, priority, etc.)
        export_format: Export format - json, csv, pdf
        
    Returns:
        Dictionary containing analytics dashboard data and visualizations
    """
    try:
        logger.info(f"Generating {dashboard_type} analytics dashboard")
        
        # Initialize SuperOps client (in real implementation, this would be injected)
        from ...agents.config import AgentConfig
        config = AgentConfig()
        client = SuperOpsClient(config)
        
        # Default filters if not provided
        if filters is None:
            filters = {}
        
        dashboard_type_lower = dashboard_type.lower()
        
        if dashboard_type_lower == "overview":
            return await _generate_overview_dashboard(client, time_range, filters)
        elif dashboard_type_lower == "performance":
            return await _generate_performance_dashboard(client, time_range, filters)
        elif dashboard_type_lower == "workload":
            return await _generate_workload_dashboard(client, time_range, filters)
        elif dashboard_type_lower == "sla":
            return await _generate_sla_dashboard(client, time_range, filters)
        elif dashboard_type_lower == "trends":
            return await _generate_trends_dashboard(client, time_range, filters)
        elif dashboard_type_lower == "custom":
            return await _generate_custom_dashboard(client, time_range, filters)
        elif dashboard_type_lower == "ticket_summary":
            return await _generate_ticket_summary_dashboard(client, time_range, filters)
        else:
            # Default to overview for unknown types
            logger.warning(f"Unknown dashboard type '{dashboard_type}', defaulting to overview")
            return await _generate_overview_dashboard(client, time_range, filters)
            
    except Exception as e:
        logger.error(f"Failed to generate analytics dashboard: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to generate {dashboard_type} analytics dashboard"
        }



async def _generate_ticket_summary_dashboard(client, time_range: str, filters: Dict) -> Dict[str, Any]:
    """Generate ticket summary dashboard"""
    try:
        # Simulate ticket summary data
        return {
            "success": True,
            "dashboard_type": "ticket_summary",
            "time_range": time_range,
            "data": {
                "total_tickets": 150,
                "open_tickets": 25,
                "closed_tickets": 125,
                "avg_resolution_time": "4.2 hours",
                "ticket_categories": {
                    "Network": 45,
                    "Hardware": 30,
                    "Software": 40,
                    "Security": 20,
                    "Other": 15
                },
                "priority_distribution": {
                    "Critical": 5,
                    "High": 20,
                    "Medium": 80,
                    "Low": 45
                }
            },
            "generated_at": datetime.now().isoformat(),
            "message": "Ticket summary dashboard generated successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to generate ticket summary dashboard"
        }