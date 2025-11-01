# 🌉 UserLink MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**UserLink** is an open-source MCP (Model Context Protocol) server that aggregates data from enterprise SaaS platforms (Jira, Confluence, Teams, Outlook) into a unified interface for AI agents and applications.

## 🎯 Why UserLink?

Modern knowledge workers have their data scattered across multiple platforms. UserLink provides:

- **🔌 Unified API**: Single MCP interface for multiple SaaS platforms
- **🤖 AI-Ready**: Designed for AI agents to access workspace data
- **📖 Read-Only**: Safe, non-intrusive data access
- **🔐 Secure**: Stateless design with token-based authentication
- **⚡ Zero Config**: No credentials stored - everything via headers

## ✨ Features

### 19 Built-in Tools

UserLink provides 19 read-only tools across 4 services:

#### Microsoft Teams (4 tools)
- `teams_get_joined_teams` - Get user's teams
- `teams_get_team_channels` - Get channels in a team
- `teams_get_channel_messages` - Get messages from a channel
- `teams_search_messages` - Search messages with filters

#### Microsoft Outlook (3 tools)
- `outlook_get_emails` - Get emails with advanced filtering
- `outlook_get_message` - Get specific email details
- `outlook_get_calendar_events` - Get upcoming calendar events

#### Atlassian Jira (7 tools)
- `jira_search_issues` - Search with filters
- `jira_search_issues_by_jql` - Search with custom JQL
- `jira_count_issues_by_jql` - Count issues
- `jira_get_issue` - Get issue details
- `jira_get_all_projects` - List all projects
- `jira_get_project_issues` - Get project issues
- `jira_get_sprint_issues` - Get sprint issues

#### Atlassian Confluence (5 tools)
- `confluence_search_content` - Search using CQL
- `confluence_get_page` - Get page details
- `confluence_get_page_children` - Get child pages
- `confluence_get_page_comments` - Get page comments
- `confluence_get_spaces` - List spaces

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/twjackysu/UserLink-MCP-Server.git
cd UserLink-MCP-Server

# Create virtual environment with uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv sync
```

### Running the Server

```bash
uv run python -m src.server
```

The server will start using the FastMCP framework with streamable-http transport.

**Note**: Using `uv run` ensures the correct virtual environment is used without needing to activate it manually.

## 🔌 Integration with Your Application

UserLink is designed to work with **connectors** - components in your application that:

1. Handle OAuth flows for each SaaS platform
2. Obtain and manage access tokens
3. Inject authentication headers into MCP requests

### Required Headers

Your connector must inject these headers when calling UserLink tools:

#### For Microsoft Tools
```
x-microsoft-graph-token: <access_token>
```

#### For Atlassian Tools
```
x-atlassian-token: <access_token>
x-atlassian-cloud-id: <cloud_id>
```

**Important**:
- Tokens should NOT include the "Bearer " prefix
- Pass the raw token value directly

### Example Integration

```python
# In your connector/application
context = {
    "headers": {
        "x-microsoft-graph-token": "eyJ0eXAiOiJKV1QiLCJub...",
        "x-atlassian-token": "eyJhbGciOiJSUzI1NiIsInR5cCI6Ikp...",
        "x-atlassian-cloud-id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    }
}

# Call MCP tools with the context
result = await teams_get_joined_teams(context=context)
```

## 🔧 Configuration

### Environment Variables (Optional)

Create a `.env` file to override defaults:

```bash
# Server Configuration
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8000
LOG_LEVEL=INFO
MCP_TRANSPORT="streamable-http"

# Optional: Override API base URLs for testing
# ATLASSIAN_API_BASE_URL=https://api.atlassian.com
# MICROSOFT_GRAPH_API_BASE_URL=https://graph.microsoft.com
```

## 🏗️ Architecture

UserLink follows a clean provider pattern:

```
src/
├── server.py              # MCP server and tool registration
├── config.py              # Configuration management
├── utils/
│   └── auth.py           # Token extraction and validation
└── providers/
    ├── atlassian/
    │   ├── base.py       # Atlassian HTTP client
    │   ├── jira.py       # Jira service
    │   └── confluence.py # Confluence service
    └── microsoft/
        ├── base.py       # Microsoft Graph client
        ├── teams.py      # Teams service
        └── outlook.py    # Outlook service
```

### Design Principles

1. **Zero Authentication Burden**: No OAuth flow handling - purely delegates to your connectors
2. **Token Dependency**: All access tokens come from request headers
3. **Pure Data Proxy**: Focus on data aggregation and standardization
4. **Provider Pattern**: Clean separation between HTTP clients and business logic

## 📖 API Reference

### Error Messages

If headers are missing or invalid, you'll receive clear error messages:

- `Invalid or missing Microsoft Graph token in request headers (x-microsoft-graph-token)`
- `Invalid or missing Atlassian token in request headers (x-atlassian-token)`
- `Invalid or missing Atlassian Cloud ID in request headers (x-atlassian-cloud-id)`

### Tool Examples

#### Search Teams Messages
```python
await teams_search_messages(
    keyword="project update",
    days_back=7,
    max_results=50
)
```

#### Get Filtered Emails
```python
await outlook_get_emails(
    folder="inbox",
    is_read=False,
    days_back=7,
    top=10
)
```

#### Search Jira Issues
```python
await jira_search_issues(
    project="MYPROJ",
    status="In Progress",
    max_results=50
)
```

#### Search Confluence Content
```python
await confluence_search_content(
    cql='type=page AND text~"API documentation"',
    limit=25
)
```

## 🔐 Security

- **Stateless Design**: No credentials or tokens are stored
- **Header-Based Auth**: All authentication via request headers
- **Read-Only Operations**: All tools are safe, non-mutating operations
- **Token Validation**: Basic token format validation before API calls

## 🛣️ Roadmap

- [ ] Add support for more platforms (Slack, Google Workspace, etc.)
- [ ] Implement response caching for performance
- [ ] Add data transformation layer for unified schemas
- [ ] Create Docker deployment templates
- [ ] Add comprehensive test suite
- [ ] Implement rate limiting and retry mechanisms

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

Quick start:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built with:
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server framework
- [httpx](https://github.com/encode/httpx) - Modern HTTP client
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/twjackysu/UserLink-MCP-Server/issues)
- **Discussions**: [GitHub Discussions](https://github.com/twjackysu/UserLink-MCP-Server/discussions)

---

Made with ❤️ by the UserLink community
