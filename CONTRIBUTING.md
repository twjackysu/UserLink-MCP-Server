# Contributing to UserLink MCP Server

Thank you for your interest in contributing to UserLink! We welcome contributions from the community and are grateful for your support.

## 🤝 How to Contribute

### Reporting Bugs

If you find a bug, please create an issue on GitHub with:

- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior vs actual behavior
- Your environment (OS, Python version, etc.)
- Relevant logs or error messages

### Suggesting Features

We love new ideas! To suggest a feature:

1. Check if it's already been suggested in [Issues](https://github.com/yourusername/UserLink-MCP-Server/issues)
2. Create a new issue with the `enhancement` label
3. Describe the feature and its use case
4. Explain why it would be valuable to the project

### Contributing Code

We follow a standard fork-and-pull-request workflow.

## 🔄 Development Workflow

### 1. Fork the Repository

Click the "Fork" button at the top right of the [repository page](https://github.com/yourusername/UserLink-MCP-Server).

### 2. Clone Your Fork

```bash
git clone https://github.com/YOUR-USERNAME/UserLink-MCP-Server.git
cd UserLink-MCP-Server
```

### 3. Add Upstream Remote

```bash
git remote add upstream https://github.com/yourusername/UserLink-MCP-Server.git
```

### 4. Set Up Development Environment

```bash
# Create virtual environment with uv
uv venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies including dev tools
uv pip install -e ".[dev]"
```

### 5. Create a Feature Branch

Always create a new branch for your changes:

```bash
# Keep your main branch in sync
git checkout main
git pull upstream main

# Create a new branch
git checkout -b feature/your-feature-name
# or for bug fixes
git checkout -b fix/bug-description
```

**Branch Naming Convention:**
- `feature/` - New features (e.g., `feature/slack-integration`)
- `fix/` - Bug fixes (e.g., `fix/auth-header-parsing`)
- `docs/` - Documentation updates (e.g., `docs/api-reference`)
- `refactor/` - Code refactoring (e.g., `refactor/provider-pattern`)
- `test/` - Adding tests (e.g., `test/auth-utils`)

### 6. Make Your Changes

Follow these guidelines:

#### Code Style

- Follow PEP 8 Python style guide
- Use type hints for function parameters and return values
- Write descriptive docstrings for classes and functions
- Keep functions focused and small

Example:
```python
async def get_issues(
    self,
    project: Optional[str] = None,
    max_results: int = 50
) -> dict[str, Any]:
    """
    Search Jira issues with filters.

    Args:
        project: Project key to filter by (optional)
        max_results: Maximum number of results (default: 50)

    Returns:
        Search results containing matching issues
    """
    # Implementation
```

#### Code Quality

Run these commands before committing:

```bash
# Format code with black
black src/

# Lint with ruff
ruff check src/

# Type check with mypy (when available)
mypy src/
```

#### Testing

- Add tests for new features
- Ensure existing tests pass
- Aim for good test coverage

```bash
# Run tests (when test suite is available)
pytest
```

### 7. Commit Your Changes

Write clear, meaningful commit messages:

```bash
git add .
git commit -m "feat: add Slack integration support

- Add Slack provider with base client
- Implement channel and message tools
- Update documentation with Slack examples"
```

**Commit Message Convention:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

### 8. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 9. Create a Pull Request

1. Go to your fork on GitHub
2. Click "New Pull Request"
3. Select `main` as the base branch
4. Select your feature branch as the compare branch
5. Fill in the PR template with:
   - **Description**: What does this PR do?
   - **Motivation**: Why is this change needed?
   - **Testing**: How was this tested?
   - **Screenshots**: If applicable
   - **Breaking Changes**: Any breaking changes?

### 10. Code Review Process

- A maintainer will review your PR
- Address any feedback or requested changes
- Push updates to the same branch (they'll appear in the PR automatically)
- Once approved, a maintainer will merge your PR

## 📋 Pull Request Guidelines

### Before Submitting

- [ ] Code follows project style guidelines
- [ ] Code has been formatted with `black`
- [ ] Code passes `ruff` linting
- [ ] All tests pass
- [ ] Documentation has been updated (if needed)
- [ ] Commit messages are clear and descriptive

### PR Best Practices

1. **Keep it focused**: One PR should address one feature/bug
2. **Keep it small**: Smaller PRs are easier to review
3. **Update from main**: Rebase on latest main before submitting
4. **Write tests**: Include tests for new functionality
5. **Update docs**: Document new features or API changes

## 🏗️ Adding a New Provider

To add support for a new SaaS platform:

### 1. Create Provider Structure

```bash
mkdir -p src/providers/newplatform
touch src/providers/newplatform/__init__.py
touch src/providers/newplatform/base.py
touch src/providers/newplatform/service.py
```

### 2. Implement Base Client

Create an HTTP client in `base.py`:

```python
"""Base client for NewPlatform API interactions."""

import httpx
from typing import Any
from src.config import config


class NewPlatformClient:
    """Base client for NewPlatform API requests."""

    def __init__(self, access_token: str) -> None:
        self.access_token = access_token
        self.base_url = "https://api.newplatform.com"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }

    async def get(self, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, **kwargs)
            response.raise_for_status()
            return response.json()
```

### 3. Implement Service Layer

Create business logic in `service.py`:

```python
"""NewPlatform service implementation."""

from typing import Any
from .base import NewPlatformClient


class NewPlatformService:
    def __init__(self, client: NewPlatformClient) -> None:
        self.client = client

    async def get_data(self) -> dict[str, Any]:
        endpoint = "/v1/data"
        return await self.client.get(endpoint)
```

### 4. Register Tools

Add tools to `src/server.py`:

```python
@mcp.tool()
async def newplatform_get_data(context: dict[str, Any] = None) -> dict[str, Any]:
    """Get data from NewPlatform."""
    token = _get_newplatform_token(context or {})
    client = NewPlatformClient(token)
    service = NewPlatformService(client)
    return await service.get_data()
```

### 5. Update Documentation

- Add to README.md supported platforms section
- Add tool examples in the API Reference section
- Update authentication requirements if needed

## 📝 Documentation Guidelines

- Use clear, concise language
- Include code examples where helpful
- Keep documentation up-to-date with code changes
- Add docstrings to all public functions and classes

## 🐛 Development Tips

### Debugging

Set environment variable for verbose logging:
```bash
LOG_LEVEL=DEBUG python -m src.server
```

### Testing with Mock Headers

Create a test script to simulate header injection:

```python
context = {
    "headers": {
        "x-microsoft-graph-token": "test_token_123",
        "x-atlassian-token": "test_token_456",
        "x-atlassian-cloud-id": "cloud-id-789"
    }
}
```

## 🔒 Security

- Never commit sensitive data (tokens, credentials, etc.)
- Use `.env` for local configuration
- Report security vulnerabilities privately to maintainers

## ❓ Questions?

- Open a [Discussion](https://github.com/yourusername/UserLink-MCP-Server/discussions)
- Ask in an existing [Issue](https://github.com/yourusername/UserLink-MCP-Server/issues)

## 📜 Code of Conduct

Be respectful, inclusive, and collaborative. We're all here to build something great together!

---

Thank you for contributing to UserLink! 🎉
