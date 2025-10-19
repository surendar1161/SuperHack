# SLA Management Tools

Comprehensive SLA (Service Level Agreement) management tools built for the SuperOps IT Technician Agent, following Strands framework patterns and industry best practices.

## Overview

This package provides both traditional Python classes and Strands-compatible tool functions for:

- **SLA Calculation**: Calculate SLA status, time remaining, and breach detection
- **Breach Detection**: Real-time breach detection and predictive analysis
- **Escalation Management**: Automated escalation workflows and notifications

## Strands Tool Functions

The tools are implemented as proper Strands tools following the [Python tools documentation](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/tools/python-tools/).

### SLA Calculator Tools

```python
from src.tools.sla import calculate_sla_status, calculate_time_remaining, check_sla_breach

# Calculate comprehensive SLA status
result = await calculate_sla_status(ticket_data, sla_policy_data)

# Calculate time remaining until breach
time_result = await calculate_time_remaining(
    created_at_str="2024-01-15T10:00:00Z",
    target_minutes=60,
    business_hours_only=True
)

# Check if SLA is breached
breach_result = await check_sla_breach(
    created_at_str="2024-01-15T10:00:00Z",
    target_minutes=60,
    response_time_str="2024-01-15T11:30:00Z"
)
```

### Breach Detection Tools

```python
from src.tools.sla import detect_sla_breaches, predict_sla_breaches, analyze_ticket_sla_risk

# Detect current SLA breaches
breaches = await detect_sla_breaches({"priority": "high"})

# Predict potential breaches in next 2 hours
predictions = await predict_sla_breaches(prediction_window_hours=2)

# Analyze risk factors for specific ticket
risk_analysis = await analyze_ticket_sla_risk("TICKET-123")
```

### Escalation Management Tools

```python
from src.tools.sla import execute_sla_escalation, notify_sla_breach, escalate_ticket_priority

# Execute full escalation process
escalation_result = await execute_sla_escalation(breach_data, ticket_data)

# Send breach notification
notification_result = await notify_sla_breach(
    ticket_id="TICKET-123",
    breach_type="response",
    severity="critical",
    technician_id="tech-001"
)

# Escalate ticket priority
priority_result = await escalate_ticket_priority(
    ticket_id="TICKET-123",
    current_priority="medium",
    reason="SLA breach detected"
)
```

## Usage in Strands Agents

### Basic Agent Setup

```python
from strands import Agent
from src.tools.sla import (
    calculate_sla_status,
    detect_sla_breaches,
    execute_sla_escalation
)

sla_agent = Agent(
    name="sla_monitor",
    system_prompt="""
    You are an SLA monitoring specialist. Monitor tickets for SLA compliance
    and take appropriate escalation actions when breaches occur.
    """,
    tools=[
        calculate_sla_status,
        detect_sla_breaches,
        execute_sla_escalation
    ]
)

# Use the agent
response = sla_agent("Check SLA status for all critical tickets and escalate any breaches")
```

### Integration with IT Technician Agent

```python
from strands import Agent
from src.tools.sla import *

it_agent = Agent(
    name="it_technician",
    system_prompt="""
    You are an IT technician with SLA monitoring capabilities.
    Always check SLA status when working with tickets.
    """,
    tools=[
        # Regular IT tools...
        calculate_sla_status,
        detect_sla_breaches,
        predict_sla_breaches,
        execute_sla_escalation,
        notify_sla_breach
    ]
)
```

## Tool Function Reference

### calculate_sla_status

Calculate comprehensive SLA status for a ticket.

**Parameters:**
- `ticket_data` (Dict): Ticket information from SuperOps
- `sla_policy_data` (Dict): SLA policy configuration

**Returns:**
- `success` (bool): Whether calculation succeeded
- `sla_status` (Dict): Detailed SLA status information
- `error` (str): Error message if failed

### detect_sla_breaches

Detect current SLA breaches for active tickets.

**Parameters:**
- `ticket_filters` (Dict, optional): Filters for ticket selection

**Returns:**
- `success` (bool): Whether detection succeeded
- `breaches` (List): List of detected breaches
- `breach_count` (int): Number of breaches found

### predict_sla_breaches

Predict potential SLA breaches within a time window.

**Parameters:**
- `prediction_window_hours` (int): Hours to look ahead (default: 2)

**Returns:**
- `success` (bool): Whether prediction succeeded
- `predictions` (List): List of breach predictions
- `prediction_count` (int): Number of predictions made

### execute_sla_escalation

Execute escalation process for an SLA breach.

**Parameters:**
- `breach_data` (Dict): SLA breach information
- `ticket_data` (Dict): Ticket information

**Returns:**
- `success` (bool): Whether escalation succeeded
- `escalation_results` (List): List of escalation actions taken
- `total_actions` (int): Number of actions executed

## Traditional Class Usage

For more complex scenarios, you can still use the traditional Python classes:

```python
from src.tools.sla import SLACalculatorTool, BreachDetectorTool, EscalationManagerTool

# Initialize tools
calculator = SLACalculatorTool()
detector = BreachDetectorTool(sla_data_access, calculator)
escalator = EscalationManagerTool(sla_data_access, superops_client)

# Use tools
sla_status = await calculator.calculate_sla_status(ticket_data, sla_policy)
breaches = await detector.detect_current_breaches()
results = await escalator.process_breach_escalation(breach, ticket_data)
```

## Configuration

### Business Hours Configuration

```python
calculator = SLACalculatorTool()
calculator.configure_business_hours(
    start_hour=9,
    end_hour=17,
    weekdays=[0, 1, 2, 3, 4],  # Monday-Friday
    timezone='UTC'
)
```

### Holiday Configuration

```python
calculator.add_holidays([
    '2024-01-01',  # New Year's Day
    '2024-07-04',  # Independence Day
    '2024-12-25'   # Christmas
])
```

### Risk Level Thresholds

```python
from src.tools.sla.models import RiskLevel

calculator.configure_risk_thresholds({
    RiskLevel.LOW: 0.5,      # > 50% time remaining
    RiskLevel.MEDIUM: 0.25,  # 25-50% time remaining
    RiskLevel.HIGH: 0.1,     # 10-25% time remaining
    RiskLevel.CRITICAL: 0.0  # < 10% time remaining
})
```

## Integration with Subagents

The SLA tools work seamlessly with the SLA Monitor subagent:

```python
from src.agents.subagents import SLAMonitorAgent

# The subagent uses Strands tools internally
sla_monitor = SLAMonitorAgent(config)
await sla_monitor.start()

# Tools are automatically used for monitoring
await sla_monitor.force_sla_check("TICKET-123")
```

## Error Handling

All Strands tool functions return a consistent format:

```python
result = await calculate_sla_status(ticket_data, sla_policy)

if result["success"]:
    # Process successful result
    sla_status = result["sla_status"]
else:
    # Handle error
    error_message = result["error"]
    ticket_id = result.get("ticket_id", "unknown")
```

## Performance Considerations

- Tools include built-in caching for frequently accessed data
- Business hours calculations are optimized for performance
- Batch operations are supported for multiple tickets
- Circuit breaker patterns prevent cascading failures

## Examples

See `src/tools/sla/examples/strands_usage.py` for comprehensive usage examples including:

- Basic Strands agent setup with SLA tools
- Direct tool function usage
- Integration with subagents
- Error handling patterns
- Performance optimization techniques