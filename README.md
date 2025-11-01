# 🌉 UserLink MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**UserLink** is an open-source MCP (Model Context Protocol) server that aggregates data from enterprise SaaS platforms (Jira, Confluence, Teams, Outlook) into a unified interface for AI agents and applications. It operates purely on **individual user credentials**, allowing AI agents to access only the data that the authenticated user themselves can access.

## 🎯 Why UserLink?

Modern knowledge workers have their data scattered across multiple platforms. UserLink provides:

- **🔌 Unified API**: Single MCP interface for multiple SaaS platforms
- **🤖 AI-Ready**: Designed for AI agents to access workspace data
- **� User-Level Access**: All data access is restricted to what the authenticated user can access (no admin/super-account permissions)
- **�📖 Read-Only**: Safe, non-intrusive data access
- **🔐 Secure**: Stateless design with token-based authentication
- **⚡ Zero Config**: No credentials stored - everything via headers

## ✨ Features

### 15 Built-in Tools

UserLink provides 15 read-only tools across 4 services:

#### Microsoft Teams (4 tools)
- `teams_get_joined_teams` - Get user's teams
- `teams_get_team_channels` - Get channels in a team
- `teams_get_channel_messages` - Search messages (use search_teams_messages for filtering)
- `teams_search_messages` - Search messages with filters

**Example:** "What did the team discuss about the project delay in the last standup?"

#### Microsoft Outlook (3 tools)
- `outlook_get_emails` - Get emails with advanced filtering
- `outlook_get_message` - Get specific email details
- `outlook_get_calendar_events` - Get upcoming calendar events

**Example:** "Summarize action items from my manager's emails this week"

#### Atlassian Jira (7 tools)
- `jira_search_issues` - Search with filters
- `jira_search_issues_by_jql` - Search with custom JQL
- `jira_count_issues_by_jql` - Count issues (returns total count)
- `jira_get_issue` - Get issue details
- `jira_get_all_projects` - List all projects
- `jira_get_project_issues` - Get project issues
- `jira_get_sprint_issues` - Get sprint issues

**Example:** "What are the high-priority blockers preventing this sprint from completing?"

#### Atlassian Confluence (1 tool)
- `confluence_search_content` - Search using CQL

**Example:** "Find the latest architecture decision records for the payment service"

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

1. Handle OAuth flows **for each individual user** on each SaaS platform
2. Obtain and manage **user-specific access tokens**
3. Inject authentication headers into MCP requests

**Key Principle**: UserLink operates on the authenticated user's identity. The tokens you provide determine what data the AI agent can access - exactly matching what that user could access themselves.

### Required Headers

Your connector must inject these headers when calling UserLink tools. **The tokens must be for the individual user whose data should be accessed**:

#### For Microsoft Tools
```
x-microsoft-graph-token: <user_access_token>
```

#### For Atlassian Tools
```
x-atlassian-token: <user_access_token>
x-atlassian-cloud-id: <cloud_id>
```

**Important**:
- Tokens should be **user-specific tokens** obtained through OAuth on behalf of that user
- Tokens should NOT include the "Bearer " prefix
- Pass the raw token value directly
- The accessed data will be limited to what this specific user has permissions for

> **Note**: For connecting this MCP server to VS Code or Claude Desktop, see the configuration example in [`.vscode/mcp.json`](.vscode/mcp.json).

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

##  Security

- **User-Level Access Only**: All data access uses the authenticated user's identity - no admin or super-account permissions
- **Stateless Design**: No credentials or tokens are stored
- **Header-Based Auth**: All authentication via request headers with user-specific tokens
- **Read-Only Operations**: All tools are safe, non-mutating operations
- **Token Validation**: Basic token format validation before API calls
- **Permission-Aware**: The AI agent can only access data that the authenticated user has permission to access

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built with:
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server framework
- [httpx](https://github.com/encode/httpx) - Modern HTTP client
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/twjackysu/UserLink-MCP-Server/issues)