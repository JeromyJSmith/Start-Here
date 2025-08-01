# Claude Code Monorepo - Comprehensive User Manual

Welcome to the Claude Code Monorepo System - a comprehensive development environment that brings together AI-powered coding tools, memory systems, and automation services in one unified platform.

## 📚 Table of Contents

### 🚀 Getting Started
- [Quick Start Guide](./quick-start.md) - Get up and running in 5 minutes
- [Installation Guide](./installation.md) - Detailed setup instructions
- [Architecture Overview](./architecture.md) - Understanding the system design

### 🔧 Core Services
- [Claude Code](./services/claude-code.md) - AI-powered coding assistant
- [SuperClaude Framework](./services/superclaude-framework.md) - Enhanced AI framework with personas
- [CLI Tool](./services/cli-tool.md) - Command-line interface with analytics
- [Memory Services](./services/memory-services.md) - Cognee, Memento MCP, and MemOS integration

### 🌐 Web Services
- [ClaudeCodeUI Frontend](./services/frontend.md) - React-based web interface
- [ClaudeCodeUI Backend](./services/backend.md) - Express.js API server
- [Unified Query Service](./services/unified-query-service.md) - Multi-memory system orchestration

### 🤖 AI & Automation
- [GenAI Stack](./services/genai-stack.md) - AI model stack with Ollama
- [LlamaCloud Integration](./services/llamacloud.md) - Document processing and workflows
- [n8n Automation](./services/n8n-automation.md) - Workflow automation nodes

### 📖 Usage Guides
- [Command Reference](./commands/README.md) - All available commands and usage
- [API Reference](./api/README.md) - Complete API documentation
- [Configuration Guide](./configuration.md) - Environment and service configuration
- [Development Workflows](./workflows.md) - Common development patterns

### 🔧 Advanced Topics
- [Docker & Orchestration](./docker.md) - Container management and deployment
- [Memory System Integration](./memory-integration.md) - Working with multiple memory backends
- [MCP Servers](./mcp-servers.md) - Model Context Protocol integrations
- [Performance Optimization](./performance.md) - Tuning and monitoring

### 🛠️ Troubleshooting & Maintenance
- [Troubleshooting Guide](./troubleshooting.md) - Common issues and solutions
- [Monitoring & Logging](./monitoring.md) - System health and debugging
- [Backup & Recovery](./backup-recovery.md) - Data protection strategies

### 🎯 Use Cases & Examples
- [Example Projects](./examples/README.md) - Real-world usage scenarios
- [Best Practices](./best-practices.md) - Recommended patterns and approaches
- [Integration Examples](./integrations.md) - Working with external tools

## 🌟 What Makes This Special?

### Unified AI Development Platform
This monorepo combines multiple AI tools and services into a cohesive development environment:

- **Claude Code**: Core AI coding assistant with terminal and IDE integration
- **SuperClaude Framework**: Enhanced framework with 16 specialized commands and 11 AI personas
- **Memory Systems**: Three different memory backends (Cognee, Memento MCP, MemOS) unified through a single query service
- **Web Interface**: Modern React frontend for visual interaction
- **Analytics Dashboard**: Real-time monitoring and conversation tracking

### Key Features

#### 🧠 Advanced AI Capabilities
- **Smart Personas**: 11 specialized AI personas (architect, frontend, backend, security, etc.)
- **Multi-Memory Integration**: Query across different memory systems simultaneously
- **Context-Aware Processing**: Intelligent document processing with LlamaParse and LlamaDeploy

#### 🔧 Developer-Friendly Tools
- **16 Specialized Commands**: From `/sc:implement` to `/sc:analyze`, covering all development phases
- **Real-Time Analytics**: Monitor Claude Code sessions, token usage, and performance
- **Health Monitoring**: Comprehensive system health checks and diagnostics

#### 🏗️ Production-Ready Architecture
- **Docker Orchestration**: All services containerized with hot-reload in development
- **Scalable Design**: Microservices architecture with proper separation of concerns
- **Monitoring & Observability**: Built-in logging, metrics, and health checks

### Service URLs (Development)
When running the full stack, you'll have access to:

- **Frontend**: http://localhost:5173 - React web interface
- **Backend API**: http://localhost:3000 - REST API server
- **SuperClaude**: http://localhost:8001 - Framework API
- **GenAI Stack**: http://localhost:8003 - AI model stack
- **CLI Analytics**: http://localhost:3001 - Analytics dashboard
- **Memory API**: http://localhost:8500 - Memory service integration
- **Unified Query**: http://localhost:8505 - Multi-memory query orchestration
- **n8n Interface**: http://localhost:5678 - Workflow automation
- **Ollama**: http://localhost:11434 - Local LLM server
- **Neo4j Browser**: http://localhost:7474 - Graph database
- **Dashboard**: http://localhost:8080 - System overview

## 🚀 Quick Start

1. **Clone and Setup**:
   ```bash
   cd monorepo
   make setup
   ```

2. **Start Development Environment**:
   ```bash
   make dev
   ```

3. **Check System Health**:
   ```bash
   make health
   ```

4. **Install Dependencies** (if needed):
   ```bash
   make install-deps
   ```

## 🆘 Need Help?

- **Quick Issues**: Check [Troubleshooting Guide](./troubleshooting.md)
- **Commands**: See [Command Reference](./commands/README.md)
- **Configuration**: Review [Configuration Guide](./configuration.md)
- **Examples**: Browse [Example Projects](./examples/README.md)

## 📋 System Status

### ✅ Production Ready
- Docker orchestration and containerization
- Core Claude Code functionality
- Memory service integration
- Web interface and API server

### 🚧 Active Development
- SuperClaude Framework v3 (recently released)
- Unified Query Service integration
- Advanced analytics features
- Performance optimizations

### 🔮 Roadmap
- SuperClaude v4 with hooks system
- Enhanced MCP server suite
- Cross-platform CLI support
- Advanced workflow automation

---

**Welcome to the future of AI-powered development!** This manual will guide you through every aspect of the Claude Code Monorepo system. Whether you're a new user looking to get started or an advanced developer wanting to integrate with the system, you'll find detailed information and practical examples throughout this documentation.

Let's begin with the [Quick Start Guide](./quick-start.md) to get you up and running in minutes!