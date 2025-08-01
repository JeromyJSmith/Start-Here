# CLAUDE.md - Project Configuration for Claude Code

## 🚨 CRITICAL RULES

### Python Package Management
**@PYTHON_UV_RULE.md** - MANDATORY: ALL Python environments MUST use UV

## Project Overview

This is a comprehensive monorepo containing multiple services and frameworks for development, including:
- SuperClaude Framework
- Claude Code UI and related tools
- GenAI Stack
- Various MCP servers and integrations
- Development services and utilities

## Development Standards

### Python Development
- **Package Manager**: UV (MANDATORY - see @PYTHON_UV_RULE.md)
- **Virtual Environments**: Created with `uv venv` only
- **Dependencies**: Managed with `uv pip` commands
- **Lock Files**: `uv.lock` required for all Python projects

### JavaScript/TypeScript Development
- **Package Manager**: npm (pnpm for specific services)
- **Node Version**: 20.19.0+ recommended
- **Testing**: Jest/Vitest for unit tests, Playwright for E2E

### Code Quality
- Run linting and type checking before commits
- Maintain test coverage above 70%
- Follow existing code patterns and conventions

## Monorepo Structure

```
/
├── .claude/                    # Claude Code configuration
│   ├── agents/                # Custom agents
│   ├── CLAUDE.md             # This file
│   └── PYTHON_UV_RULE.md     # Python UV enforcement
├── monorepo/                  # Main monorepo directory
│   └── services/              # Individual services
├── SuperClaude_Framework-master/
├── claude-code-extras/
└── genai-stack-main/
```

## Important Notes

1. **Python Dependencies**: ALWAYS use UV for Python package management
2. **Git Submodules**: Several directories are git submodules - handle with care
3. **Testing**: Run tests after any changes to ensure stability
4. **Security**: Regular dependency updates required