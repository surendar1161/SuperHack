# SLA Data Model Strategy

## Current State

The SLA system currently uses **dataclasses** for internal models, which works but lacks:
- Input validation
- Automatic serialization/deserialization
- Type safety with external APIs
- Integration with modern Python tooling

## Recommended Approach: Pydantic Models

### Why Pydantic?

1. **Follows Tech Stack Guidelines**: Pydantic 2.0+ is specified in our tech stack
2. **Validation**: Automatic input validation and type checking
3. **Serialization**: Built-in JSON serialization for API integration
4. **SuperOps Integration**: Easy conversion between API formats and internal models
5. **Strands Compatibility**: Works seamlessly with Strands tool functions

### Implementation Strategy

#### Phase 1: Parallel Implementation (Current)
- Keep existing dataclass models for backward compatibility
- Implement new Pydantic models in `models_v2.py`
- Update Strands tools to use Pydantic models internally
- Maintain dictionary interfaces for Strands tool functions

#### Phase 2: Gradual Migration
- Update SLA tools to use Pydantic models
- Add conversion utilities between old and new models
- Update tests to use new models
- Maintain API compatibility

#### Phase 3: Complete Migration
- Replace dataclass models with Pydantic models
- Remove old model files
- Update all references throughout codebase

## Data Flow Architecture

```
SuperOps API Data (JSON)
         ↓
SuperOpsTicket (Pydantic)
         ↓
SLA Tools (Strands functions)
         ↓
TicketSLAStatus (Pydantic)
         ↓
Dictionary (for Strands return)
```

## Model Categories

### 1. Core SLA Models
- `SLAPolicy` - Policy configuration with validation
- `TicketSLAStatus` - Current SLA status for tickets
- `SLABreach` - Breach incident tracking
- `TechnicianSLAMetrics` - Performance metrics

### 2. SuperOps Integration Models
- `SuperOpsTicket` - Ticket data from SuperOps API
- `SuperOpsUser` - User data from SuperOps API
- `SuperOpsCustomer` - Customer data from SuperOps API

### 3. Configuration Models
- `EscalationRule` - Escalation configuration
- `AlertRule` - Alert configuration
- `DateRange` - Date range queries

## Benefits of This Approach

### 1. Type Safety
```python
# Automatic validation
policy = SLAPolicy(
    id="policy-1",
    name="Critical SLA",
    priority_level="critical",  # Validated against enum
    response_time_minutes=15,   # Must be positive
    resolution_time_hours=4     # Must be > response time
)
```

### 2. Easy API Integration
```python
# From SuperOps API
api_data = {"id": "T-123", "createdAt": "2024-01-15T10:00:00Z", ...}
ticket = SuperOpsTicket(**api_data)

# To Strands tool
result = await calculate_sla_status(ticket.to_sla_dict(), policy.to_dict())
```

### 3. Validation and Error Handling
```python
try:
    policy = SLAPolicy(
        response_time_minutes=-5  # Invalid!
    )
except ValidationError as e:
    # Handle validation errors gracefully
    logger.error(f"Invalid SLA policy: {e}")
```

### 4. Serialization
```python
# Automatic JSON serialization
policy_json = policy.json()
policy_dict = policy.dict()

# Easy database storage
await db.save_sla_policy(policy.dict())
```

## Usage Examples

### In Strands Tools
```python
@tool
async def calculate_sla_status(ticket_data: Dict[str, Any], sla_policy_data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        # Convert to Pydantic models for validation
        ticket = SuperOpsTicket(**ticket_data)
        policy = SLAPolicy(**sla_policy_data)
        
        # Perform calculations with validated data
        sla_status = await _calculate_sla_internal(ticket, policy)
        
        # Return as dictionary for Strands
        return {
            "success": True,
            "sla_status": sla_status.to_dict()
        }
    except ValidationError as e:
        return {
            "success": False,
            "error": f"Invalid input data: {e}"
        }
```

### In Subagents
```python
class SLAMonitorAgent(BaseSubagent):
    async def _check_ticket_sla(self, ticket_data: Dict[str, Any]):
        # Convert to validated model
        ticket = SuperOpsTicket(**ticket_data)
        
        # Get policy
        policy = await self._get_sla_policy(ticket.priority)
        
        # Use Strands tool with validated data
        result = await calculate_sla_status(ticket.to_sla_dict(), policy.to_dict())
        
        if result["success"]:
            sla_status = TicketSLAStatus(**result["sla_status"])
            await self._process_sla_status(sla_status)
```

## Migration Timeline

### Immediate (Current Sprint)
- ✅ Create Pydantic models in `models_v2.py`
- ✅ Update Strands tools to use dictionary interfaces
- ✅ Add conversion utilities

### Next Sprint
- [ ] Update SLA tools to use Pydantic internally
- [ ] Add comprehensive validation
- [ ] Update tests for new models

### Future Sprint
- [ ] Migrate all components to Pydantic models
- [ ] Remove old dataclass models
- [ ] Update documentation

## Conclusion

**Recommendation: Implement Pydantic models** for the SLA system while maintaining backward compatibility. This provides:

1. **Better validation** and error handling
2. **Easier SuperOps API integration**
3. **Type safety** throughout the system
4. **Modern Python practices** aligned with tech stack
5. **Seamless Strands integration**

The hybrid approach allows gradual migration without breaking existing functionality while providing immediate benefits for new development.