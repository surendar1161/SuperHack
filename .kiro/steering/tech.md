# Technology Stack & Build System


use this website to follow strands agent coding in this whole repo 
https://strandsagents.com/latest/documentation/


do not create new python files here after. making use of existing files.


do not implement your own data models. always use superops api and its response to decide on sla , work log entry , ticket , task and other moduels . 

## Core Technologies

### AI & Language Models
- **Anthropic Claude**: Primary LLM (claude-3-5-sonnet-20241022)
- **Strands Framework**: AI agent framework (currently disabled due to compilation issues)

### Backend Stack
- **Python 3.9+**: Primary language with type hints
- **Pydantic 2.0+**: Data validation and serialization
- **SQLAlchemy 2.0+**: Database ORM with async support
- **aiohttp**: Async HTTP client for API integrations
- **Alembic**: Database migrations

### API Integration
- **SuperOps REST API**: Primary integration endpoint (https://api.superops.ai/msp/api)
- **SuperOps GraphQL API**: Advanced queries and mutations (https://api.superops.ai/it)
- **GraphQL Core**: GraphQL query processing
- **gql**: GraphQL client library
- **Authentication**: Bearer token-based API authentication

### CLI & User Interface
- **Typer**: Command-line interface framework
- **Rich**: Beautiful terminal output and formatting

### Development Tools
- **pytest**: Testing framework with async support (pytest-asyncio)
- **black**: Code formatting (line-length: 88)
- **flake8**: Linting
- **mypy**: Type checking with strict settings
- **pre-commit**: Git hooks for code quality

## Common Commands

### Environment Setup
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Development
```bash
# Run the agent
python -m src.main start

# Health check
python -m src.main health-check

# Setup guide
python -m src.main setup
```

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_tools/test_ticket_tools.py

# Run with coverage
pytest --cov=src

# Run async tests
pytest -v --tb=short
```

### Code Quality
```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/

# Run pre-commit hooks
pre-commit run --all-files
```

## Configuration

### Environment Variables
Required variables in `.env` file:
- `SUPEROPS_API_KEY`: SuperOps platform API key
- `SUPEROPS_API_URL`: SuperOps API base URL (default: https://api.superops.ai/msp/api)
- `SUPEROPS_CUSTOMER_SUBDOMAIN`: Customer subdomain (e.g., "hackathon")
- `ANTHROPIC_API_KEY`: Anthropic Claude API key
- `AGENT_MODEL`: Claude model version (default: claude-3-5-sonnet-20241022)
- `AGENT_TEMPERATURE`: Model temperature (default: 0.7)
- `AGENT_MAX_TOKENS`: Max tokens per response (default: 1024)
- `DATABASE_URL`: Database connection string (default: SQLite)
- `LOG_LEVEL`: Logging level (default: INFO)

### Project Configuration
- **pyproject.toml**: Modern Python packaging and tool configuration
- **requirements.txt**: Production dependencies
- **.env.example**: Template for environment variables

## Architecture Patterns

### Async/Await
- All I/O operations use async/await pattern
- aiohttp for non-blocking HTTP requests
- SQLAlchemy async sessions for database operations
- pytest-asyncio for async test support

### Dependency Injection
- Clients passed to tools and agents via constructor
- Configuration objects injected into components
- Mock-friendly design for testing

### Error Handling
- Custom exception hierarchy in `src/clients/exceptions.py`
- Comprehensive logging with Rich formatting
- Graceful degradation for API failures

### Tool Configuration
- Tools inherit from `BaseTool` with standardized interface
- Parameter validation using Pydantic models
- Consistent error handling and logging patterns

## SuperOps API Integration

### Authentication
- Bearer token authentication required
- CustomerSubDomain header required for IT API
- Session cookies may be required for some endpoints

### API Endpoints
- **MSP API**: `https://api.superops.ai/msp/api` (REST)
- **IT API**: `https://api.superops.ai/it` (GraphQL)

### Working Headers Format
```python
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "CustomerSubDomain": "hackathon"
}
```

