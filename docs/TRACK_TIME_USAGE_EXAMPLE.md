# Track Time Tool - Usage Example

## Updated Implementation

The `track_time` tool has been updated to use the correct SuperOps GraphQL API for creating worklog timer entries, based on the working curl command provided.

## API Integration

### GraphQL Mutation Used
```graphql
mutation ($timerEntryInput: CreateWorklogTimerEntryInput!) {
    createWorklogTimerEntry(input: $timerEntryInput) {
        timerId
        billable
        type
        notes
        running
        timespent
        segments { 
            segmentId 
            startTime 
            endTime 
            timespent 
            afterHours 
        }
    }
}
```

### Request Format
```json
{
    "timerEntryInput": {
        "billable": true,
        "notes": "[Troubleshooting] Fixed printer connectivity issue",
        "type": "AUTOMATIC",
        "workItem": {
            "workId": "6028540472074190848",
            "module": "TICKET"
        }
    }
}
```

## Usage Examples

### Basic Time Tracking
```python
from src.tools.tracking import track_time

# Track 1.5 hours of troubleshooting work
result = await track_time(
    ticket_id="6028540472074190848",
    duration=1.5,  # 1.5 hours
    description="Fixed printer connectivity issue",
    activity_type="Troubleshooting",
    billable=True
)

if result["success"]:
    print(f"Tracked {result['duration_formatted']} for ticket {result['ticket_id']}")
    print(f"Timer ID: {result['timer_id']}")
else:
    print(f"Error: {result['error']}")
```

### Different Activity Types
```python
# Research work
await track_time(
    ticket_id="6028540472074190848",
    duration=0.5,  # 30 minutes
    description="Researched network configuration options",
    activity_type="Research",
    billable=True
)

# Implementation work
await track_time(
    ticket_id="6028540472074190848",
    duration=2.0,  # 2 hours
    description="Implemented new firewall rules",
    activity_type="Implementation",
    billable=True
)

# Documentation work
await track_time(
    ticket_id="6028540472074190848",
    duration=0.25,  # 15 minutes
    description="Updated network documentation",
    activity_type="Documentation",
    billable=False
)
```

### With Internal Notes
```python
await track_time(
    ticket_id="6028540472074190848",
    duration=1.0,  # 1 hour
    description="Diagnosed hardware failure",
    activity_type="Troubleshooting",
    billable=True,
    internal_notes="Customer was difficult to work with, required extra patience"
)
```

## Response Format

### Success Response
```json
{
    "success": true,
    "ticket_id": "6028540472074190848",
    "duration": 1.5,
    "duration_hours": 1.5,
    "duration_minutes": 90,
    "duration_formatted": "1h 30m",
    "description": "[Troubleshooting] Fixed printer connectivity issue",
    "activity_type": "Troubleshooting",
    "billable": true,
    "timer_id": "timer_12345",
    "time_entry_id": "timer_12345",
    "running": false,
    "segments": [
        {
            "segmentId": "seg_123",
            "startTime": "2025-01-13T10:00:00Z",
            "endTime": "2025-01-13T11:30:00Z",
            "timespent": 90,
            "afterHours": false
        }
    ],
    "message": "Tracked 1h 30m for ticket 6028540472074190848",
    "data": {
        "timer_id": "timer_12345",
        "billable": true,
        "type": "AUTOMATIC",
        "notes": "[Troubleshooting] Fixed printer connectivity issue",
        "running": false,
        "time_spent": 90
    }
}
```

### Error Response
```json
{
    "success": false,
    "error": "Duration must be greater than 0",
    "message": "Failed to track time - validation error"
}
```

## Activity Types Supported

- **Research** - Investigating issues, reading documentation
- **Troubleshooting** - Diagnosing and fixing problems
- **Implementation** - Installing, configuring, deploying solutions
- **Testing** - Verifying fixes and functionality
- **Documentation** - Writing guides, updating procedures
- **Communication** - Talking with users, coordinating with team

## Validation Rules

- Duration must be greater than 0
- Duration cannot exceed 24 hours
- Ticket ID is required
- Description is required

## Integration with Strands

```python
from strands import Agent
from src.tools.tracking import track_time

# Create agent with time tracking capability
agent = Agent(
    name="it_technician",
    tools=[track_time]
)

# Agent can automatically track time based on user requests
response = agent("I spent 2 hours fixing the server issue for ticket 6028540472074190848")
```

## API Configuration

Make sure your `.env` file contains the correct SuperOps API credentials:

```env
SUPEROPS_API_KEY=api-eyJhbGciOiJSUzI1NiJ9...
SUPEROPS_CUSTOMER_SUBDOMAIN=hackathonsuperhack
```

The tool will automatically use these credentials when making API calls to SuperOps.