# Contributing to UserLink MCP Server

Thank you for your interest in contributing! We welcome contributions from the community.

## 🤝 How to Contribute

### Reporting Bugs

Create an issue on GitHub with:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected vs actual behavior

### Suggesting Features

Check [Issues](https://github.com/twjackysu/UserLink-MCP-Server/issues) first, then create a new issue describing the feature and its use case.

### Contributing Code

We follow a standard fork-and-pull-request workflow.

## 🔄 Development Workflow

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR-USERNAME/UserLink-MCP-Server.git
cd UserLink-MCP-Server
git remote add upstream https://github.com/twjackysu/UserLink-MCP-Server.git
```

### 2. Set Up Environment

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv sync
```

### 3. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

Branch naming: `feature/`, `fix/`, `docs/`, `refactor/`, `test/`

### 4. Make Your Changes

- Follow PEP 8 style guide
- Use type hints and descriptive docstrings
- Keep functions focused and small

### 5. Code Quality

```bash
black src/
ruff check src/
```

### 6. Commit and Push

Write clear commit messages:
```bash
git commit -m "feat: description of your changes"
git push origin feature/your-feature-name
```

Commit prefix: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`

### 7. Create a Pull Request

- Describe what your PR does
- Explain the motivation
- Ensure all tests pass

## 📋 Before Submitting

- [ ] Code follows PEP 8 style
- [ ] Code is formatted with `black`
- [ ] Code passes `ruff` linting
- [ ] Documentation is updated if needed

## 🔒 Security

- Never commit sensitive data (tokens, credentials, etc.)
- Use `.env` for local configuration
- Report security vulnerabilities privately

## ❓ Questions?

Ask in a GitHub [Issue](https://github.com/twjackysu/UserLink-MCP-Server/issues) or Discussion.

---

Thank you for contributing to UserLink! 🎉

