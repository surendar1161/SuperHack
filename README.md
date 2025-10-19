# SuperOps IT Technician Agent

An AI-powered IT Technician Agent that integrates with the SuperOps SaaS platform to automate and enhance IT operations and administration tasks.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your SuperOps API credentials

# Run the agent
python -m src.main start
```

## 🛠️ Core Features

- **🎟️ Ticket Management**: Create, update, assign, and resolve tickets
- **📋 Task Creation**: Create and manage IT tasks with automated workflows
- **👥 User Management**: Manage technicians and client users
- **💰 Billing & Contracts**: Handle invoices, quotes, and contracts
- **📊 Analytics & Reporting**: Performance metrics and insights
- **🔍 Knowledge Base**: Create and manage IT documentation
- **⚠️ Alerts & Monitoring**: System alerts and notifications
- **⏱️ Time Tracking**: Automated time logging and work tracking

## 📁 Project Structure

```
src/
├── agents/          # AI agent implementations
├── clients/         # SuperOps API clients
├── tools/           # Agent tools by functionality
│   ├── ticket/      # Ticket management
│   ├── task/        # Task creation and management
│   ├── user/        # User management
│   ├── billing/     # Billing and contracts
│   ├── analytics/   # Performance metrics
│   └── knowledge/   # Knowledge base management
├── memory/          # Memory management
├── workflows/       # Business process automation
└── utils/           # Shared utilities

docs/               # Documentation and guides
test_scripts/       # Test and demo scripts
```

## 🔧 Configuration

The agent requires SuperOps API credentials:

- `SUPEROPS_API_KEY`: Your SuperOps API key
- `SUPEROPS_API_URL`: SuperOps API endpoint
- `SUPEROPS_CUSTOMER_SUBDOMAIN`: Your customer subdomain
- `ANTHROPIC_API_KEY`: Claude API key for AI functionality

## 📚 Documentation

Detailed documentation is available in the `docs/` folder:

- [API Documentation](docs/TASK_CREATION_API_DOCUMENTATION.md)
- [Implementation Summaries](docs/)
- [Tool Usage Examples](docs/)

## 🧪 Testing & Demo

Interactive demo and test scripts are in `test_scripts/`:

```bash
# Run interactive demo (perfect for video recording)
python test_scripts/demo_create_task_interactive.py

# Run specific tool tests
python test_scripts/test_create_task_api.py
```

## 🤝 Contributing

1. Follow the existing code structure and patterns
2. Add comprehensive logging and error handling
3. Include type hints and docstrings
4. Test your changes thoroughly

## 📄 License

This project is part of the SuperOps integration initiative.