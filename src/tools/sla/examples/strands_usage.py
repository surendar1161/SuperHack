"""
Example usage of SLA tools with Strands framework

This demonstrates how to use the SLA management tools as proper Strands tools
following the Python tools documentation pattern.
"""

import asyncio
from datetime import datetime
from strands import Agent

# Import the Strands-compatible tool functions
from ..tools import (
    calculate_sla_status,
    calculate_time_remaining,
    check_sla_breach,
    detect_sla_breaches,
    predict_sla_breaches,
    analyze_ticket_sla_risk,
    execute_sla_escalation,
    notify_sla_breach,
    escalate_ticket_priority
)


async def example_sla_agent():
    """Example of using SLA tools in a Strands agent"""
    
    # Create an agent with SLA tools
    sla_agent = Agent(
        name="sla_monitor",
        system_prompt="""
        You are an SLA monitoring specialist. Use the available tools to:
        1. Monitor ticket SLA status
        2. Detect breaches and predict potential breaches
        3. Execute escalations when needed
        4. Notify stakeholders of SLA issues
        
        Always prioritize critical breaches and customer-facing issues.
        """,
        tools=[
            calculate_sla_status,
            calculate_time_remaining,
            check_sla_breach,
            detect_sla_breaches,
            predict_sla_breaches,
            analyze_ticket_sla_risk,
            execute_sla_escalation,
            notify_sla_breach,
            escalate_ticket_priority
        ]
    )
    
    # Example ticket data
    ticket_data = {
        "id": "TICKET-123",
        "number": "T-123",
        "subject": "Server outage in production",
        "priority": "critical",
        "status": "open",
        "createdAt": "2024-01-15T10:00:00Z",
        "assignee": {
            "id": "tech-001",
            "name": "John Doe"
        },
        "customer": {
            "name": "Acme Corp",
            "tier": "premium"
        }
    }
    
    # Example SLA policy
    sla_policy = {
        "id": "policy-critical",
        "name": "Critical Priority SLA",
        "priority_level": "critical",
        "response_time_minutes": 15,
        "resolution_time_hours": 4,
        "business_hours_only": False
    }
    
    # Example usage in agent conversation
    prompt = f"""
    Please monitor the SLA status for this critical ticket:
    
    Ticket: {ticket_data['subject']} (#{ticket_data['number']})
    Priority: {ticket_data['priority']}
    Created: {ticket_data['createdAt']}
    Assigned to: {ticket_data['assignee']['name']}
    
    Actions needed:
    1. Calculate current SLA status
    2. Check if any breaches have occurred
    3. Predict if breaches are likely in the next 2 hours
    4. If breaches are detected, execute appropriate escalations
    5. Notify the assigned technician if immediate action is needed
    
    Provide a comprehensive SLA assessment and recommended actions.
    """
    
    # The agent will automatically use the tools to:
    # - Calculate SLA status using calculate_sla_status()
    # - Check for breaches using check_sla_breach()
    # - Predict future breaches using predict_sla_breaches()
    # - Execute escalations using execute_sla_escalation()
    # - Send notifications using notify_sla_breach()
    
    response = sla_agent(prompt)
    print("SLA Agent Response:", response)
    
    return response


async def example_direct_tool_usage():
    """Example of using SLA tools directly"""
    
    # Example: Calculate SLA status
    ticket_data = {
        "id": "TICKET-456",
        "createdAt": "2024-01-15T14:30:00Z",
        "priority": "high"
    }
    
    sla_policy = {
        "priority_level": "high",
        "response_time_minutes": 60,
        "resolution_time_hours": 8,
        "business_hours_only": True
    }
    
    # Calculate SLA status
    sla_result = await calculate_sla_status(ticket_data, sla_policy)
    print("SLA Status:", sla_result)
    
    # Check for current breaches
    breach_result = await detect_sla_breaches({"priority": "high"})
    print("Breach Detection:", breach_result)
    
    # Predict future breaches
    prediction_result = await predict_sla_breaches(prediction_window_hours=2)
    print("Breach Predictions:", prediction_result)
    
    # If breach detected, execute escalation
    if breach_result.get("breach_count", 0) > 0:
        for breach in breach_result.get("breaches", []):
            escalation_result = await execute_sla_escalation(
                breach_data=breach,
                ticket_data=ticket_data
            )
            print("Escalation Result:", escalation_result)


async def example_integration_with_subagent():
    """Example of integrating SLA tools with a subagent"""
    
    from ...agents.subagents.sla_monitor_agent import SLAMonitorAgent
    from ...agents.config import AgentConfig
    
    # Initialize SLA monitor subagent
    config = AgentConfig()
    sla_monitor = SLAMonitorAgent(config)
    await sla_monitor.start()
    
    # The subagent can now use Strands tools internally
    # while maintaining its message-based architecture
    
    # Example: Force SLA check using Strands tools
    await sla_monitor.force_sla_check("TICKET-789")
    
    # Get current alerts
    alerts = await sla_monitor.get_current_alerts()
    print("Current SLA Alerts:", alerts)
    
    # Stop the subagent
    await sla_monitor.stop()


if __name__ == "__main__":
    # Run examples
    asyncio.run(example_sla_agent())
    asyncio.run(example_direct_tool_usage())
    asyncio.run(example_integration_with_subagent())