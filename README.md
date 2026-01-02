# Python Zendesk SDK

Modern Python SDK for Zendesk API with async support, full type safety, and comprehensive error handling.

## Status: Ready for Read-Only Operations ✅

This project has completed iterations 1-4 and is ready for production use in read-only mode.

### Completed Features ✅

- **Project Infrastructure**: Complete setup with `pyproject.toml`, dependencies, and linting
- **Configuration System**: `ZendeskConfig` with environment variable support and validation
- **Exception Handling**: Comprehensive exception hierarchy for different error types
- **HTTP Client**: Async HTTP client with retry logic, rate limiting, and exponential backoff
- **Pagination**: Both offset-based and cursor-based pagination support
- **Data Models**: Full Pydantic v2 models for Users, Organizations, Tickets, and Comments
- **Read API Methods**: 13 methods for reading data from Zendesk
  - Users: `get_users()`, `get_user()`, `get_user_by_email()`
  - Organizations: `get_organizations()`, `get_organization()`
  - Tickets: `get_tickets()`, `get_ticket()`, `get_user_tickets()`, `get_organization_tickets()`
  - Comments: `get_ticket_comments()`
  - Search: `search()`, `search_users()`, `search_tickets()`, `search_organizations()`
- **Testing Framework**: Full test suite with 128+ passing tests
- **Code Quality**: Black, isort, flake8, and mypy configured

### In Development 🚧

- Write operations (create/update/delete) - planned for future iteration
- Documentation & Examples (Iteration 5)

## Installation

```bash
# Install from PyPI (when published)
pip install python-zendesk-sdk

# Or install from source
git clone <repository-url>
cd python-zendesk-sdk
pip install -e ".[dev]"
```

## Quick Start

```python
import asyncio
from zendesk_sdk import ZendeskClient, ZendeskConfig

async def main():
    # Create configuration
    config = ZendeskConfig(
        subdomain="your-subdomain",
        email="your-email@example.com",
        token="your-api-token",  # or use password="your-password"
    )

    # Use async context manager
    async with ZendeskClient(config) as client:
        # Get users with pagination
        users_paginator = await client.get_users(per_page=10)
        users = await users_paginator.get_page()

        for user in users:
            print(f"User: {user.name} ({user.email})")

        # Get specific ticket
        ticket = await client.get_ticket(ticket_id=12345)
        print(f"Ticket: {ticket.subject}")

        # Search tickets
        results = await client.search_tickets("status:open priority:high")
        for ticket in results:
            print(f"High priority: {ticket.subject}")

asyncio.run(main())
```

## Configuration

The SDK supports multiple ways to configure authentication:

### 1. Direct instantiation
```python
config = ZendeskConfig(
    subdomain="mycompany",
    email="user@example.com",
    token="api_token_here"
)
```

### 2. Environment variables
```bash
export ZENDESK_SUBDOMAIN=mycompany
export ZENDESK_EMAIL=user@example.com
export ZENDESK_TOKEN=api_token_here
```

```python
config = ZendeskConfig()  # Will load from environment
```

### 3. Mixed approach
```python
# Override specific values, rest from environment
config = ZendeskConfig(subdomain="different-subdomain")
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/zendesk_sdk --cov-report=html

# Run specific test file
pytest tests/test_config.py -v
```

### Code Quality

```bash
# Format code
python -m black src tests
python -m isort src tests

# Lint code
python -m flake8 src tests

# Type checking
python -m mypy src
```

### Running All Checks

```bash
# Format, lint, and test
python -m black src tests && python -m isort src tests && python -m flake8 src tests && python -m mypy src && pytest
```

## Project Structure

```
├── src/zendesk_sdk/          # Main package
│   ├── __init__.py           # Public API exports
│   ├── client.py             # Main ZendeskClient class
│   ├── config.py             # Configuration management
│   ├── exceptions.py         # Exception hierarchy
│   └── models/               # Data models
│       ├── __init__.py
│       └── base.py           # Base model class
├── tests/                    # Test suite
├── pyproject.toml            # Project configuration
└── README.md                 # This file
```

## Requirements

- Python 3.8+
- httpx (for async HTTP client)
- pydantic >=2.0 (for data validation)

## Development Roadmap

- [x] **Iteration 1**: Infrastructure Setup
- [x] **Iteration 2**: HTTP Client & Pagination
- [x] **Iteration 3**: Data Models (Users, Tickets, Organizations, Comments)
- [x] **Iteration 4**: Read-Only API Methods & Search
- [ ] **Iteration 5**: Documentation & Examples (in progress)
- [ ] **Future**: Write operations (create/update/delete)

## License

MIT License - see LICENSE file for details.

## Contributing

This project is currently in early development. Contribution guidelines will be added in future iterations.