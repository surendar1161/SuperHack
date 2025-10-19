# Project Structure & Organization

## Directory Layout

```
src/
├── agents/          # Agent implementations and configurations
│   ├── subagents/   # Specialized sub-agents for specific tasks
│   └── graph/       # Graph-based agent implementations (SLA)
├── clients/         # External API clients (SuperOps, etc.)
│   └── graphql/     # GraphQL queries, mutations, and fragments
├── models/          # Pydantic data models and schemas
├── tools/           # Agent tools organized by functionality
│   ├── ticket/      # Ticket management operations
│   ├── analysis/    # Request analysis and suggestions
│   ├── tracking/    # Time tracking and work logging
│   ├── analytics/   # Performance metrics and reporting
│   └── sla/         # SLA management and monitoring tools
├── memory/          # Memory management and persistence
│   └── stores/      # Specialized storage implementations
├── workflows/       # Business logic and process automation
├── prompts/         # AI prompt templates and management
│   └── templates/   # Categorized prompt templates
└── utils/           # Shared utilities and helpers
```

## Core Modules

### Agents (`src/agents/`)
- **base_agent.py**: Abstract base class with Anthropic client integration
- **it_technician_agent.py**: Enhanced agent with full tool integration
- **config.py**: Agent configuration management using Pydantic
- **subagents/**: Specialized sub-agents for specific tasks
  - **event_monitor_agent.py**: Event monitoring and alerting
  - **metadata_sync_agent.py**: Data synchronization
  - **sla_monitor_agent.py**: SLA monitoring and breach detection

### Clients (`src/clients/`)
- **superops_client.py**: Main SuperOps GraphQL API client
- **robust_superops_client.py**: Enhanced client with retry logic
- **sla_superops_client.py**: SLA-specific API operations
- **mock_superops_client.py**: Mock client for testing
- **exceptions.py**: Custom exception hierarchy (SuperOpsAPIError, AuthenticationError, RateLimitError)
- **graphql/**: GraphQL operations
  - **queries.py**: GraphQL query definitions
  - **mutations.py**: GraphQL mutation definitions
  - **fragments.py**: Reusable GraphQL fragments

### Tools (`src/tools/`)
Organized by functional area with consistent inheritance from `BaseTool`:
- **base_tool.py**: Abstract base class with parameter validation
- **ticket/**: Ticket management operations
  - **create_ticket.py**: Standard ticket creation
  - **create_ticket_robust.py**: Enhanced ticket creation with retry logic
  - **update_ticket.py**: Ticket updates and modifications
  - **assign_ticket.py**: Ticket assignment logic
  - **resolve_ticket.py**: Ticket resolution workflows
- **analysis/**: Request analysis and AI-powered insights
  - **analyze_request.py**: Request categorization and analysis
  - **generate_suggestions.py**: AI-generated troubleshooting suggestions
  - **identify_bottlenecks.py**: Performance bottleneck identification
- **tracking/**: Time and work management
  - **track_time.py**: Time tracking functionality
  - **log_work.py**: Work logging and documentation
  - **monitor_progress.py**: Progress monitoring and reporting
- **analytics/**: Performance metrics and reporting
  - **performance_metrics.py**: Performance data collection
  - **view_analytics.py**: Analytics dashboard and reporting
- **sla/**: SLA management and monitoring
  - **models.py**: SLA-specific data models
  - **interfaces.py**: SLA service interfaces
  - **data_access.py**: SLA data access layer
  - **exceptions.py**: SLA-specific exceptions
  - **tools/**: SLA-specific tools
    - **sla_calculator.py**: SLA calculation logic
    - **breach_detector.py**: SLA breach detection
    - **escalation_manager.py**: Escalation workflows

### Models (`src/models/`)
- **common.py**: Base models and mixins (BaseModel with JSON encoders, TimestampMixin)
- **ticket.py**: Ticket-related data models and enums
- **user.py**: User and technician models
- **asset.py**: IT asset and equipment models

### Memory (`src/memory/`)
- **memory_manager.py**: Central memory coordination
- **models.py**: Memory-specific data models
- **stores/**: Specialized storage implementations
  - **ticket_store.py**: Ticket history and context storage
  - **worklog_store.py**: Work logging and time tracking storage
  - **analytics_store.py**: Performance metrics storage

### Workflows (`src/workflows/`)
- **base_workflow.py**: Abstract workflow foundation
- **ticket_lifecycle.py**: Complete ticket management process
- **escalation.py**: SLA breach and escalation handling
- **auto_assignment.py**: Intelligent ticket routing

### Prompts (`src/prompts/`)
- **prompt_manager.py**: Centralized prompt management
- **templates/**: Categorized prompt templates
  - **ticket_analysis.py**: Ticket analysis prompts
  - **suggestions.py**: Suggestion generation prompts
  - **escalation.py**: Escalation-related prompts

### Utils (`src/utils/`)
- **logger.py**: Rich-formatted logging setup
- **helpers.py**: Common utility functions
- **validators.py**: Data validation utilities
- **formatters.py**: Output formatting utilities
- **constants.py**: Application constants

## Naming Conventions

### Files and Modules
- Use snake_case for all Python files and directories
- Descriptive names that indicate functionality
- Group related functionality in subdirectories
- Suffix tool files with the tool name (e.g., `create_ticket.py`)

### Classes
- PascalCase for class names
- Suffix base classes with "Base" (e.g., `BaseAgent`, `BaseTool`)
- Suffix tools with "Tool" (e.g., `CreateTicketTool`)
- Suffix workflows with "Workflow" (e.g., `TicketLifecycleWorkflow`)
- Suffix agents with "Agent" (e.g., `ITTechnicianAgent`)

### Functions and Methods
- snake_case for function and method names
- Use descriptive verbs (e.g., `create_ticket`, `analyze_request`)
- Async functions prefixed with `async def`
- Private methods prefixed with underscore

### Constants and Enums
- UPPER_CASE for constants
- PascalCase for Enum classes
- Descriptive enum values (e.g., `Priority.HIGH`, `Status.IN_PROGRESS`)

## Import Patterns

### Relative Imports
Use relative imports within the src package:
```python
from .base_agent import BaseAgent
from ..clients.superops_client import SuperOpsClient
from ...utils.logger import get_logger
```

### External Dependencies
Group imports in this order:
1. Standard library imports
2. Third-party imports (anthropic, pydantic, aiohttp, etc.)
3. Local application imports

### Type Hints
- Use type hints for all function parameters and return values
- Import types from `typing` module
- Use `Optional` for nullable parameters
- Use `Dict`, `List`, `Any` for complex types

## Configuration Management

### Environment Variables
- All configuration via environment variables in `.env` file
- Use `python-dotenv` for loading environment variables
- Validate required variables at startup using Pydantic settings
- Provide `.env.example` template with all required variables

### Settings Classes
- Use Pydantic BaseSettings for configuration classes
- Group related settings together (e.g., `AgentConfig`)
- Provide sensible defaults where possible
- Validate configuration on startup

## Testing Structure

### Test Organization
```
tests/
├── unit/            # Unit tests for individual components
│   ├── test_agents/ # Agent-specific tests
│   ├── test_tools/  # Tool-specific tests
│   └── test_utils/  # Utility function tests
├── integration/     # Integration tests with external APIs
└── fixtures/        # Shared test data and fixtures
```

### Test Naming
- Prefix test files with `test_`
- Use descriptive test method names starting with `test_`
- Group tests by functionality in classes
- Use pytest fixtures for setup and teardown

### Async Testing
- Use `pytest-asyncio` for async test support
- Mark async tests with `@pytest.mark.asyncio`
- Mock external API calls using `aiohttp` test utilities

## Documentation Standards

### Docstrings
- Use Google-style docstrings for all public functions and classes
- Include parameter types and descriptions
- Document return values and exceptions
- Provide usage examples for complex functions

### Code Comments
- Explain complex business logic and algorithms
- Document API integration specifics and working formats
- Clarify non-obvious implementation decisions
- Include TODO comments for future improvements

### Type Annotations
- Use comprehensive type hints throughout the codebase
- Import from `typing` module for complex types
- Use `Optional` for nullable parameters
- Document complex type structures in docstrings

## Error Handling Patterns

### Exception Hierarchy
- Custom exceptions in `src/clients/exceptions.py`
- Inherit from appropriate base exceptions
- Provide meaningful error messages
- Include context information in exceptions

### Logging Strategy
- Use Rich-formatted logging throughout
- Log at appropriate levels (DEBUG, INFO, WARNING, ERROR)
- Include context information in log messages
- Use structured logging for better searchability