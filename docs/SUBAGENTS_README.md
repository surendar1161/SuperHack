# Subagents

This directory contains specialized subagents that work alongside the main IT Technician Agent to provide focused functionality.

## SLA Monitor Agent

The `SLAMonitorAgent` is responsible for monitoring SLA compliance and alerting the main agent when breaches occur or are imminent.

### Key Features

- **Continuous Monitoring**: Monitors all active tickets for SLA compliance
- **Breach Detection**: Detects actual and imminent SLA breaches
- **Smart Alerting**: Sends prioritized alerts to the main agent
- **Escalation Management**: Automatically triggers escalations when needed
- **Performance Tracking**: Tracks SLA metrics and performance

### Usage Example

```python
from src.agents.subagents import SLAMonitorAgent
from src.agents.config import AgentConfig

# Initialize the SLA monitor
config = AgentConfig()
sla_monitor = SLAMonitorAgent(config)

# Start monitoring
await sla_monitor.start()

# The agent will automatically:
# 1. Monitor active tickets every minute
# 2. Send alerts when breaches are detected
# 3. Trigger escalations for critical breaches
# 4. Track performance metrics

# Get current SLA status
metrics = sla_monitor.get_sla_metrics()
alerts = await sla_monitor.get_current_alerts()

# Force an immediate SLA check
await sla_monitor.force_sla_check()  # All tickets
await sla_monitor.force_sla_check("TICKET-123")  # Specific ticket
```

### Alert Types

- **Warning**: 30 minutes before SLA breach
- **Critical**: 10 minutes before SLA breach  
- **Breach**: SLA has been breached

### Integration with Main Agent

The SLA monitor communicates with the main IT technician agent through message passing:

```python
# In the main agent controller
await self._send_to_sla_monitor(ticket_data)

# The SLA monitor will send back alerts like:
{
    "alert_type": "breach",
    "ticket_id": "TICKET-123",
    "severity": "critical",
    "time_remaining": -15,  # 15 minutes past SLA
    "escalation_required": true,
    "recommended_actions": [
        "Immediately escalate to senior technician",
        "Notify customer of delay"
    ]
}
```

## Other Subagents

- **MetadataSyncAgent**: Synchronizes metadata between systems
- **EventMonitorAgent**: Monitors system events and triggers
- **TriageAgent**: Handles initial ticket triage and routing

## Architecture Benefits

- **Scalability**: Each subagent can be scaled independently
- **Maintainability**: Focused responsibilities make code easier to maintain
- **Reliability**: Circuit breakers and rate limiting prevent cascading failures
- **Monitoring**: Built-in metrics and health checks for each subagent